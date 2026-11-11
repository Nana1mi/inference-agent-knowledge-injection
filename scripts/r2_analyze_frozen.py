"""Describe frozen primary step labels; no label inference or causal estimates."""
import hashlib
import json
from collections import Counter, defaultdict
from r2_io import ROOT, DERIVED, load, dump, now


def distribution(rows, field):
    return dict(Counter(str(r[field]) for r in rows))


def first(rows, predicate):
    return next((r['step_id'] for r in rows if predicate(r)), None)


def summarize(rows):
    hypotheses = [r for r in rows if r['hypothesis'] is not None]
    return {
        'steps': len(rows), 'sessions': sorted({r['session_id'] for r in rows}),
        'phase': distribution(rows, 'phase'), 'tool': distribution(rows, 'tool'),
        'layer': distribution(rows, 'layer'),
        'hypothesis_steps': len(hypotheses),
        'hypothesis_origin': distribution(hypotheses, 'hypothesis_origin'),
        'hypothesis_source_all_steps': distribution(rows, 'hypothesis_source'),
        'hypothesis_source_nonnull_hypotheses': distribution(hypotheses, 'hypothesis_source'),
        'reasoning_visible': sum(r['reasoning_visible'] for r in rows),
        'state_tamper_risk': sum(r['state_tamper_risk'] for r in rows),
        'duration_seconds': None,
    }


def main():
    frozen = ROOT / 'data/annotations/r2_frozen'
    manifest = load(frozen / 'manifest.json')
    for a in manifest['artifacts']:
        if hashlib.sha256((ROOT / a['snapshot']).read_bytes()).hexdigest() != a['sha256']:
            raise ValueError('Frozen snapshot changed')
    rows = [json.loads(l) for l in (frozen / 'first_pass.jsonl').read_text(encoding='utf-8').splitlines()]
    sessions = {s['session_id']: s for s in load(frozen / 'sessions.json')}
    events = load(frozen / 'knowledge_sources.json')['events']
    groups = defaultdict(list)
    bysession = defaultdict(list)
    for r in rows:
        s = sessions[r['session_id']]['selection']
        groups[s['model_from_filename']].append(r)
        bysession[r['session_id']].append(r)
    assert len(rows) == 3345 and len(sessions) == 14
    assert {(e['session_id'], e['step_id']) for e in events} == {
        (r['session_id'], r['step_id']) for r in rows if r['knowledge_access']}
    session_stats = []
    source_kinds = sorted({e['source_kind'] for e in events})
    for sid, s in sessions.items():
        rr = sorted(bysession[sid], key=lambda r: r['step_id'])
        ee = [e for e in events if e['session_id'] == sid]
        code = first(rr, lambda r: r['phase'] == '修改代码')
        candidate = first(rr, lambda r: r['candidate_edit'])
        profile = first(rr, lambda r: r['phase'] == 'profile')
        measured_profile = first(rr, lambda r: r['phase'] == 'profile' and r['outcome'] == '成功')
        first_knowledge = {}
        for kind in source_kinds:
            match = [e for e in ee if e['source_kind'] == kind]
            if match:
                step = min(e['step_id'] for e in match)
                first_knowledge[kind] = {
                    'step': step,
                    'before_phase_counts': dict(Counter(r['phase'] for r in rr if r['step_id'] < step)),
                    'event_ids': [e['event_id'] for e in match if e['step_id'] == step],
                }
        session_stats.append({
            'session_id': sid, 'model': s['selection']['model_from_filename'],
            'family': s['selection']['model_family'], 'task': s['selection']['task'],
            'published_outcome': s['selection']['outcome'], **summarize(rr),
            'first_code_edit': code, 'first_formal_candidate_edit': candidate,
            'first_profile_attempt': profile, 'first_successful_profile_step': measured_profile,
            'successful_profile_before_code_edit': measured_profile is not None and code is not None and measured_profile < code,
            'successful_profile_before_formal_candidate_edit': measured_profile is not None and candidate is not None and measured_profile < candidate,
            'first_knowledge_access': first_knowledge,
            'source_events': len(ee), 'source_event_use': dict(Counter(e['knowledge_use'] for e in ee)),
            'source_kind_counts': dict(Counter(e['source_kind'] for e in ee)),
            'raw_file': s['raw_file'], 'source_url': rr[0]['source_url'],
        })
    pair_tasks = load(ROOT / 'data/raw/r2_kbh' / rows[0]['raw_file'].split('/')[3] / 'selection.json')['pair_tasks']
    knowledge_by_kind = {
        kind: {'events': sum(e['source_kind'] == kind for e in events),
               'use': dict(Counter(e['knowledge_use'] for e in events if e['source_kind'] == kind)),
               'sessions': sorted({e['session_id'] for e in events if e['source_kind'] == kind})}
        for kind in source_kinds
    }
    knowledge_by_outcome = {}
    for outcome in sorted({s['selection']['outcome'] for s in sessions.values()}):
        ids = {sid for sid, s in sessions.items() if s['selection']['outcome'] == outcome}
        ee = [e for e in events if e['session_id'] in ids]
        knowledge_by_outcome[outcome] = {
            'sessions': sorted(ids), 'events': len(ee),
            'use': dict(Counter(e['knowledge_use'] for e in ee)),
        }
    output = {
        'generated_at': now(), 'status': 'draft_descriptive_statistics',
        'frozen_manifest': 'data/annotations/r2_frozen/manifest.json',
        'unit': 'one primary label per decision step; not tool-call counts or wall time',
        'overall': summarize(rows),
        'by_exact_model': {m: summarize(rr) for m, rr in sorted(groups.items())},
        'by_session': session_stats,
        'paired_tasks': {task: [s for s in session_stats if s['task'] == task] for task in pair_tasks},
        'knowledge': {'steps': 84, 'events': len(events), 'by_kind': knowledge_by_kind,
                      'by_published_outcome': knowledge_by_outcome,
                      'event_provenance': events},
        'limits': ['Fixed outcome-stratified convenience frame, not population preferences',
                   'Task-constrained layers; no causal knowledge-effect estimate',
                   'First code edit includes helper probes, formal candidate edit is reported separately',
                   'Label-level successful profiling; does not certify profiler quality or exclusive GPU access',
                   'All durations remain null; 150-step blind-repeat agreement pending'],
    }
    dump(DERIVED / 'r2_analysis.json', output)
    print('Exact models', {m: len(rr) for m, rr in groups.items()})
    for s in session_stats:
        print(s['session_id'], s['model'], s['task'], 'first edit/candidate/profile=',
              s['first_code_edit'], s['first_formal_candidate_edit'], s['first_successful_profile_step'],
              'knowledge=', {k: v['step'] for k, v in s['first_knowledge_access'].items()},
              'uses=', s['source_event_use'])
    print('Knowledge by kind', knowledge_by_kind)
    print('Knowledge by outcome', knowledge_by_outcome)


if __name__ == '__main__':
    main()
