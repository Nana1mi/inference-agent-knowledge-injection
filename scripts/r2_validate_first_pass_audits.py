"""Check authored correction/event provenance, without assigning semantic labels.

Requires the frozen local review packets and raw traces. Passing these checks
does not certify annotation quality, blind agreement, or Round 2 completion.
"""
import hashlib
import json
import re
import subprocess
from collections import Counter

from r2_io import ROOT, DERIVED, dump, load


def read_rows(text):
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    result = {(row['session_id'], row['step_id']): row for row in rows}
    if len(result) != len(rows):
        raise ValueError('duplicate annotated step')
    return result


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    annotations = ROOT / 'data/annotations'
    current = read_rows((annotations / 'r2_kernelbench.jsonl').read_text(encoding='utf-8'))
    corrections = load(annotations / 'r2_first_pass_corrections.json')
    commit = corrections['baseline_commit']
    require(re.fullmatch(r'[0-9a-f]{7,40}', commit), 'invalid baseline commit')
    previous = subprocess.run(
        ['git', 'show', f'{commit}:data/annotations/r2_kernelbench.jsonl'],
        cwd=ROOT, capture_output=True, text=True, encoding='utf-8', check=True,
    )
    baseline = read_rows(previous.stdout)
    require(current.keys() == baseline.keys(), 'baseline/current step sets differ')
    packets = {}
    for sid, _ in current:
        if sid not in packets:
            packets[sid] = {
                row['step_id']: row for row in map(
                    json.loads,
                    (DERIVED / 'r2_review_inputs' / f'{sid}.jsonl').read_text(
                        encoding='utf-8').splitlines(),
                )
            }

    for (sid, step), row in current.items():
        packet = packets[sid][step]
        digest = hashlib.sha256(json.dumps(
            packet, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        require(row['review_input_sha256'] == digest, f'packet hash {sid}:{step}')

    logged = set()
    for entry in corrections['corrections']:
        key = (entry['session_id'], entry['step_id'])
        field = entry['field']
        token = (*key, field)
        require(token not in logged, f'duplicate correction {token}')
        logged.add(token)
        require(baseline[key][field] == entry['before'], f'before mismatch {token}')
        require(current[key][field] == entry['after'], f'after mismatch {token}')
        require(entry['before'] != entry['after'], f'no-op correction {token}')
        for name in ['source_lines', 'review_input_sha256']:
            require(entry[name] == baseline[key][name] == current[key][name],
                    f'correction provenance mismatch {token} {name}')
        require(entry['reason'].strip(), f'empty correction reason {token}')

    changed = {
        (*key, field)
        for key, row in current.items()
        for field in row.keys() | baseline[key].keys()
        if row.get(field) != baseline[key].get(field)
    }
    require(changed == logged,
            f'unlogged or stale differences: {sorted(changed ^ logged)}')

    source_review = load(annotations / 'r2_knowledge_source_reviews.json')
    events = source_review['events']
    event_ids = set()
    event_steps = set()
    raw_lines = {}
    for event in events:
        key = (event['session_id'], event['step_id'])
        row = current[key]
        require(row['knowledge_access'], f'event without knowledge access {key}')
        event_steps.add(key)
        expected_id = f'{key[0]}:{key[1]}:{event["source_kind"]}'
        require(event['event_id'] == expected_id and expected_id not in event_ids,
                f'invalid/duplicate source event {expected_id}')
        event_ids.add(expected_id)
        require(event['knowledge_use'] in {
            '照搬', '改写适配', '读了但没用', '读了并明确反驳'},
            f'invalid knowledge use {expected_id}')
        for name in ['raw_file', 'source_url', 'source_lines',
                     'tool_result_lines', 'review_input_sha256']:
            require(event[name] == row[name], f'event provenance {expected_id} {name}')
        require(event['followup_locator'] and event['rationale'],
                f'missing source-event rationale {expected_id}')
        method = event['access_method']
        require(method in {'主动工具读取', '主动调用Skill后返回正文'},
                f'invalid access method {expected_id}')
        if method == '主动调用Skill后返回正文':
            context = event['knowledge_content_context_lines']
            require(len(context) == 1, f'ambiguous Skill context {expected_id}')
            line = context[0]
            require(event['knowledge_content_locator'] == f'L{line}/message/content',
                    f'Skill context locator {expected_id}')
            path = event['raw_file']
            if path not in raw_lines:
                raw_lines[path] = (ROOT / path).read_text(encoding='utf-8').splitlines()
            raw = raw_lines[path][line - 1]
            require(hashlib.sha256(raw.encode()).hexdigest() ==
                    event['knowledge_content_record_sha256'],
                    f'Skill context hash {expected_id}')
            record = json.loads(raw)
            content = record['message']['content']
            packet = packets[key[0]][key[1]]
            require(record['type'] == 'user' and isinstance(content, str),
                    f'Skill content record {expected_id}')
            require(any(c['name'] == 'Skill' for c in packet['calls']),
                    f'no explicit Skill call {expected_id}')
            require(any(c['line'] == line and c['content'] == content
                        for c in packet['context_messages']),
                    f'Skill content missing from packet {expected_id}')

    knowledge_steps = {key for key, row in current.items() if row['knowledge_access']}
    require(event_steps == knowledge_steps, 'source-event knowledge-step coverage mismatch')
    actual_coverage = {
        'knowledge_steps': len(knowledge_steps),
        'source_category_events': len(events),
        'kbh_sessions': len({key[0] for key in current}),
    }
    require(actual_coverage == source_review['coverage'], 'source-event declared coverage')
    result = {
        'status': 'passed', 'baseline_commit': commit,
        'annotated_steps': len(current), 'logged_corrections': len(logged),
        'corrections_by_field': dict(Counter(e['field'] for e in corrections['corrections'])),
        **actual_coverage,
        'source_events_by_kind': dict(Counter(e['source_kind'] for e in events)),
        'access_methods': dict(Counter(e['access_method'] for e in events)),
        'not_certified': ['semantic annotation quality', 'blind agreement', 'Round 2 completion'],
    }
    dump(DERIVED / 'r2_first_pass_audit_validation.json', result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
