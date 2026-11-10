"""Navigate complete, identical tool arguments; never assign review judgments.

Only the display is grouped. Every occurrence retains its own ID, input field,
target and tool feedback. The cache contains upstream text and stays local.
"""
import argparse
import csv
import hashlib
import json
from collections import defaultdict

from r2_io import ROOT, DERIVED, dump, load
from r2_scan_state_tamper import payloads


def digest_payload(tool, value):
    return hashlib.sha256((tool + '\0' + value).encode()).hexdigest()


def collect_groups():
    scan = load(DERIVED / 'r2_state_tamper_reviewed.json')
    byfile = defaultdict(list)
    for hit in scan['hits']:
        if hit['review'] is None:
            byfile[hit['raw_file']].append(hit)
    groups = {}
    for file, hits in byfile.items():
        values = {loc: (tool, value) for loc, tool, value in payloads(ROOT / file)}
        for hit in hits:
            tool, value = values[hit['source_locator']]
            if tool != hit['tool'] or value.splitlines()[hit['payload_line'] - 1] != hit['line']:
                raise ValueError('scan/source mismatch ' + hit['hit_id'])
            digest = digest_payload(tool, value)
            group = groups.setdefault(digest, {
                'group_sha256': digest, 'tool': tool, 'payload': value, 'occurrences': [],
            })
            group['occurrences'].append({k: hit[k] for k in [
                'hit_id', 'raw_file', 'source_locator', 'payload_line', 'rule',
            ]})
    result = sorted(groups.values(), key=lambda g: (-len(g['occurrences']), g['group_sha256']))
    dump(DERIVED / 'r2_review_inputs/state_payload_groups.json', result)
    return result


def show_group(group):
    print('GROUP', group['group_sha256'], 'TOOL', group['tool'])
    print('\n'.join(f'{i}: {line}' for i, line in enumerate(group['payload'].splitlines(), 1)))
    positions = defaultdict(list)
    for hit in group['occurrences']:
        positions[hit['raw_file'], hit['source_locator']].append(hit)
    for (file, loc), hits in positions.items():
        print('POSITION', file, loc)
        if loc.startswith('/agent_steps/'):
            parts = loc.split('/')
            step = load(ROOT / file)['agent_steps'][int(parts[2])]
            call = step['tool_calls'][int(parts[4])]
            print('ARGS', {k: v for k, v in call['arguments'].items() if k not in {
                'file_text', 'new_str', 'old_str', 'new_string', 'old_string', 'content',
            }})
            for i, feedback in enumerate(step.get('tool_results') or []):
                if feedback.get('call_id') != call.get('call_id'):
                    continue
                print('FEEDBACK', f'/agent_steps/{parts[2]}/tool_results/{i}', {
                    'success': feedback.get('success'),
                    'result_begin': str(feedback.get('result') or '')[:160],
                    'error_begin': str(feedback.get('error') or '')[:240],
                })
        else:
            print('Tool feedback is not attached here; inspect the full source trace.')
        print('HITS', [(h['hit_id'], h['payload_line'], h['rule']) for h in hits])


def verify_batch():
    authored = load(ROOT / 'data/annotations/r2_state_payload_review_batches.json')
    scan = load(DERIVED / 'r2_state_tamper_hits.json')
    hits = {h['hit_id']: h for h in scan['hits']}
    judgments = {}
    with (ROOT / 'data/annotations/r2_state_tamper_reviews.tsv').open(encoding='utf-8') as f:
        for row in csv.reader(f, delimiter='\t'):
            if row and not row[0].startswith('#'):
                if len(row) != 3 or row[0] in judgments:
                    raise ValueError('invalid/duplicate judgment row')
                judgments[row[0]] = row[1:]
    values = {}
    file_hashes = {}
    seen = set()
    positions = set()
    payload_hashes = set()
    for review in authored['reviews']:
        payload_hashes.add(review['tool_payload_sha256'])
        for position in review['positions']:
            file, loc = position['raw_file'], position['source_locator']
            if (file, loc) in positions:
                raise ValueError('duplicate reviewed position')
            positions.add((file, loc))
            if file not in values:
                values[file] = {p: (t, v) for p, t, v in payloads(ROOT / file)}
                file_hashes[file] = hashlib.sha256((ROOT / file).read_bytes()).hexdigest()
            if position['raw_file_sha256'] != file_hashes[file]:
                raise ValueError('source file hash mismatch ' + file)
            tool, value = values[file][loc]
            if tool != review['tool'] or digest_payload(tool, value) != review['tool_payload_sha256']:
                raise ValueError('complete tool argument hash mismatch ' + loc)
            for key in position['hit_ids']:
                if key in seen:
                    raise ValueError('duplicate explicit hit ID ' + key)
                seen.add(key)
                hit = hits[key]
                if (hit['raw_file'], hit['source_locator']) != (file, loc):
                    raise ValueError('hit belongs to another source position ' + key)
                if tool != hit['tool'] or value.splitlines()[hit['payload_line'] - 1] != hit['line']:
                    raise ValueError('source line mismatch ' + key)
                if judgments[key][0] != review['classification']:
                    raise ValueError('authored/TSV judgment mismatch ' + key)
                if not judgments[key][1].strip() or not position['reviewed_feedback'].strip():
                    raise ValueError('missing per-occurrence reason/feedback ' + key)
                if (review['rationale'] not in judgments[key][1] or
                        position['reviewed_feedback'] not in judgments[key][1]):
                    raise ValueError('batch/TSV reason or feedback mismatch ' + key)
    counts = {'reviewed_hits': len(seen), 'distinct_tool_payloads': len(payload_hashes),
              'distinct_input_positions': len(positions)}
    if any(authored[k] != v for k, v in counts.items()):
        raise ValueError('declared batch coverage mismatch')
    result = {'status': 'passed', **counts,
              'scope': 'authored IDs, complete input/source hashes, locations and TSV associations only',
              'not_certified': ['semantic judgment quality', 'GPU measurement validity', 'full R5 completion']}
    dump(DERIVED / 'r2_state_payload_audit_validation.json', result)
    print(json.dumps(result, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--group', nargs='+', help='Exact SHA256 from the navigation inventory')
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--verify-batch', action='store_true')
    args = parser.parse_args()
    if args.verify_batch:
        verify_batch()
        return
    groups = collect_groups()
    if args.group:
        found = {g['group_sha256']: g for g in groups}
        for digest in args.group:
            show_group(found[digest])
    else:
        print('Pending hits', sum(len(g['occurrences']) for g in groups), 'complete arguments', len(groups))
        for group in groups[:args.limit]:
            positions = {(h['raw_file'], h['source_locator']) for h in group['occurrences']}
            print(group['group_sha256'], 'hits', len(group['occurrences']), 'positions', len(positions),
                  'lines', len(group['payload'].splitlines()), 'tool', group['tool'],
                  'begin', repr(group['payload'][:120]))


if __name__ == '__main__':
    main()
