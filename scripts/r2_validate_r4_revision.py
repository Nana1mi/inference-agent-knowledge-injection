"""Check R4 provenance, partitions and pre-decision timing; not semantic certification."""
import hashlib
import json
from collections import Counter
from r2_io import ROOT, DERIVED, ROUND, load, dump


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    errors = []

    def check(condition, label):
        if not condition:
            errors.append(label)

    frozen = ROOT / 'data/annotations/r2_frozen/manifest.json'
    manifest = load(frozen)
    for a in manifest['artifacts']:
        check(sha(ROOT / a['snapshot']) == a['sha256'], 'frozen artifact ' + a['snapshot'])
    review_path = ROOT / 'data/annotations/r2_r4_evidence_reviews.json'
    review = load(review_path)
    aggregate = load(DERIVED / 'r2_r4_analysis.json')
    first = load(ROOT / 'data/annotations/r2_frozen/knowledge_sources.json')['events']
    old = {e['event_id']: e for e in first}
    sessions = review['sessions']
    events = review['knowledge_events']
    check(review['frozen_manifest_sha256'] == sha(frozen), 'review frozen manifest hash')
    check(aggregate['review_sha256'] == sha(review_path), 'aggregate review hash')
    check(len(sessions) == len({s['session_id'] for s in sessions}) == 14, '14 unique sessions')
    check(len(events) == len({e['event_id'] for e in events}) == 85, '85 unique source events')
    check({e['event_id'] for e in events} == set(old), 'source event coverage')
    cache = {s['session_id']: [json.loads(l) for l in (DERIVED / 'r2_review_inputs' / (s['session_id'] + '.jsonl')).read_text(encoding='utf-8').splitlines()] for s in sessions}

    def pin(sid, p):
        row = cache[sid][p['step'] - 1]
        check(row['step_id'] == p['step'], f'{sid} packet step {p["step"]}')
        check(row['source_lines'] == p['source_lines'], f'{sid} packet lines {p["step"]}')
        digest = hashlib.sha256(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        check(digest == p['review_input_sha256'], f'{sid} packet hash {p["step"]}')
        result_lines = [c['result']['line'] for c in row['calls'] if c.get('result') and c['result'].get('line')]
        check(result_lines == p['tool_result_lines'], f'{sid} return lines {p["step"]}')

    for s in sessions:
        sid = s['session_id']
        for field in ['first_write_evidence', 'attempt_evidence', 'performance_edit_evidence']:
            for p in s[field]:
                pin(sid, p)
        attempt = s['first_profile_attempt_step']
        check(s['attempt_before_first_code_write'] == (attempt is not None and attempt < s['first_code_write_step']), sid + ' attempt timing')
        check(s['first_performance_edit_step'] in [p['step'] for p in s['performance_edit_evidence']], sid + ' performance edit provenance')
        check(s['first_performance_edit_step'] not in s['excluded_correct_baseline_steps'], sid + ' baseline exclusion')
        if s['profile_support_before_first_performance_edit']:
            check(bool(s['support_steps']) and all(p < s['first_performance_edit_step'] for p in s['support_steps']), sid + ' pre-edit profile support')
            check(bool(s['support_note']), sid + ' profile link explanation')
    for e in events:
        original = old[e['event_id']]
        for field in ['source_lines', 'tool_result_lines', 'review_input_sha256', 'raw_file', 'source_url']:
            check(e[field] == original[field], e['event_id'] + ' original ' + field)
        if e['source_kind'] == '参考实现':
            check(not e['included'], e['event_id'] + ' reference excluded')
        if not e['included']:
            check(bool(e.get('exclusion_reason')), e['event_id'] + ' exclusion reason')
            continue
        check(e['consultation_kind'] in ['SOTA入口', '文档'], e['event_id'] + ' consultation kind')
        check(e['adoption_level'] is None or e['adoption_level'] in review['definitions']['adoption_levels'], e['event_id'] + ' four levels')
        for p in e['followup_evidence']:
            pin(e['session_id'], p)
        if e['adoption_level'] == '借用思路':
            a = e.get('idea_evidence', {})
            check(a.get('origin') in ['thought', 'code_comment'], e['event_id'] + ' visible idea evidence')
            if a:
                row = cache[e['session_id']][a['step'] - 1]
                pool = '\n'.join(t['text'] for t in row['thoughts']) if a['origin'] == 'thought' else '\n'.join(str(c['input']) for c in row['calls']).replace('\\n', '\n')
                check(bool(a['excerpt']) and a['excerpt'] in pool, e['event_id'] + ' exact visible excerpt')
                if a['origin'] == 'code_comment':
                    check(any(a['excerpt'] in line and line.lstrip('+ ').startswith(('#', '//')) for line in pool.splitlines()), e['event_id'] + ' actual code comment')
                check(a['source_lines'] == row['source_lines'], e['event_id'] + ' idea lines')
    inc = [e for e in events if e['included']]
    check(aggregate['consultation_events'] == len(inc) == 38, '38 consultation events')
    check(aggregate['document_events'] == sum(e['consultation_kind'] == '文档' for e in inc) == 25, '25 documents')
    check(sum(e['source_kind'] == '参考实现' for e in events) == 21, '21 reference background events')
    sota = [e for e in inc if e['consultation_kind'] == 'SOTA入口']
    check(len(sota) == 13, '13 SOTA')
    unused = [e for e in sota if e['adoption_level'] == '读了未用']
    check(len(unused) == 10 and all(e.get('nonadoption_reason_category') in ['硬件或接口不适用', 'agent明确拒绝', '无迹可循'] for e in unused), '10 individual SOTA reasons')
    expected = {('K01', 'K07'), ('K01', 'K08'), ('K05', 'K09'), ('K05', 'K10'), ('K02', 'K11'), ('K02', 'K12'), ('K03', 'K11'), ('K03', 'K12')}
    check({(l, r) for _, l, r in review['closed_model_pairs']} == expected, 'eight GLM-closed task pairs')
    for grouping, field in [('by_group', 'model_group'), ('by_exact_model', 'model')]:
        check(sum(q['n'] for q in aggregate[grouping].values()) == 14, grouping + ' denominator')
        for group, q in aggregate[grouping].items():
            members = [s for s in sessions if s[field] == group]
            check(set(q['sessions']) == {s['session_id'] for s in members}, group + ' members')
            check(q['profile_attempt_before_first_modification'] == sum(s['attempt_before_first_code_write'] for s in members), group + ' profile A')
            check(q['profile_support_before_first_performance_edit'] == sum(s['profile_support_before_first_performance_edit'] for s in members), group + ' profile B')
            for kind, name in [('SOTA入口', 'sota'), ('文档', 'documents')]:
                evs = [e for e in inc if e[field] == group and e['consultation_kind'] == kind]
                counts = Counter(e['adoption_level'] for e in evs)
                check(q[name]['events'] == len(evs) == sum(q[name]['levels_then_ungraded']), group + ' event partition ' + kind)
                check(q[name]['levels_then_ungraded'] == [counts[k] for k in review['definitions']['adoption_levels']] + [counts[None]], group + ' four-level counts ' + kind)
    result = {'status': 'passed' if not errors else 'errors', 'scope': 'R4 structural/provenance/timing consistency only; manual semantic decisions remain reviewable; blind kappa pending',
              'review_sha256': sha(review_path), 'aggregate_sha256': sha(DERIVED / 'r2_r4_analysis.json'),
              'report_sha256': sha(ROUND / 'R4_analysis.md'), 'errors': errors}
    dump(DERIVED / 'r2_r4_revision_validation.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
