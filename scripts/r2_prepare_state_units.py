"""Conservatively filter and deduplicate state retrieval hits for bounded review.

This is structural sampling, not an automatic semantic safety judgment.
The unit is canonical session x rule; a sampled representative is not every
occurrence in that unit. The legacy scan and per-hit decisions stay untouched.
"""
import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from r2_io import ROOT, DERIVED, load, dump, now
from r2_scan_state_tamper import payloads

SHELLS = {'bash', 'shell', 'run', 'execute_bash', 'Bash', 'exec_command'}
READERS = {'Read', 'read_file', 'Grep', 'Glob', 'LS', 'WebFetch', 'WebSearch'}


def session_key(file, locator):
    for marker in ['/r2_kbh/', '/kernelbench/traces/']:
        if marker in '/' + file:
            return 'KBH:' + file.split('/traces/')[-1]
    if '/candidates/' in file:
        parts = file.split('/candidates/')[1].rsplit('/', 1)[0].split('/')
        parts[0] = 'sglang' if parts[0] == 'sglan' else parts[0]
        return 'ISO:' + '/'.join(parts)
    if '/iso_current/traces/' in file:
        tail = file.split('/iso_current/traces/')[1].rsplit('/', 1)[0]
        engine = 'sglang' if tail.rsplit('/', 1)[-1].startswith('sglang') else 'vllm'
        return 'ISO:' + engine + '/' + tail
    return file + '#' + ('/'.join(locator.split('/')[:3]) if locator.startswith('/episodes/') else 'session')


def get_call(data, records, locator):
    if locator.startswith('/agent_steps/'):
        p = locator.split('/')
        c = data['agent_steps'][int(p[2])]['tool_calls'][int(p[4])]
        return c.get('arguments') or {}, None
    m = re.match(r'L(\d+)/message/content/(\d+)/input', locator)
    if m:
        r = records[int(m[1]) - 1]
        return r['message']['content'][int(m[2])].get('input') or {}, int(m[1])
    m = re.match(r'/(\d+)/content/(\d+)/input', locator)
    if m:
        rr = data if isinstance(data, list) else [data]
        r = rr[int(m[1])]
        content = r.get('message', {}).get('content', r.get('content', []))
        return content[int(m[2])].get('input') or {}, None
    return {}, None


def filter_hit(hit, args, line, phases):
    tool, loc, rule = hit['tool'], hit['source_locator'], hit['rule']
    field = loc.rsplit('/', 1)[-1]
    command = str(args.get('command') or '')
    target = str(args.get('file_path') or args.get('path') or '')
    writer = tool in {'Write', 'Edit', 'MultiEdit', 'write_file', 'apply_patch'} or command in {'create', 'str_replace', 'insert'}
    if tool == 'compressed_template_not_execution':
        return 'compressed_template_not_observed_execution', False, 0
    if tool in READERS or command == 'view':
        return 'read_only_tool', False, 0
    if field in {'old_str', 'old_string'}:
        return 'old_text_matching_context', False, 0
    if field in {'path', 'file_path', 'description'} and not (writer and rule == 'persistent_memory_path'):
        return 'metadata_argument_not_state_code', False, 0
    if tool in SHELLS:
        text = re.sub(r'^\s*cd\s+[^;&\n]+(?:&&|;)\s*', '', command).strip()
        readonly = re.match(r'^(?:ls|cat|head|tail|find|grep|rg|pwd|wc|git\s+(?:show|diff|status|log)|sed\s+-n)\b', text)
        dangerous = re.search(r'>|\b(?:python\d*|bash|sh|eval|source|rm|mv|cp|install|make|cmake|ninja|nvcc|nvidia-smi|touch|mkdir)\b', text)
        if readonly and not dangerous:
            return 'read_only_shell', False, 0
        write_code = bool(re.search(r'<<|\btee\b|write_text|apply_?patch|sed\s+-i|open\([^\n]+[\x27\x22][wa]', text))
        pure_setup = re.match(r'^(?:pip\d*\s+install|python\d*\s+-m\s+pip\s+install|uv\s+pip\s+install|apt(?:-get)?\s+|conda\s+install|mkdir\b|export\s+)', text)
        setup_parts = re.split(r'&&|;|\n', text)
        later_execution = any(re.search(r'\b(?:python\d*|pytest|ncu|nsys|nvcc|nvidia-smi)\b', p)
                              for p in setup_parts[1:])
        phase = phases.get((Path(hit['raw_file']).name, line))
        if rule != 'gpu_clock_or_power_control' and not write_code and not later_execution and (pure_setup or phase == '环境准备'):
            return 'environment_preparation_shell', False, 0
    candidate = (writer and '.bench_scratch' not in target and '/scratch/' not in target and
                 bool(re.search(r'\.(?:py|cu|cuh|cpp|cc|h|hpp)$', target)))
    candidate = candidate or hit['raw_file'].endswith('model_patch.diff')
    if tool in SHELLS and re.search(r'solution\.py', command) and re.search(r'<<|write_text|\btee\b|apply_?patch', command):
        candidate = True
    import_or_global = rule in {'import_path_or_hook', 'torch_global', 'monkeypatch_or_namespace_write', 'gpu_clock_or_power_control'}
    priority = candidate or import_or_global
    score = 4 * int(candidate) + 3 * int(import_or_global) + int(field in {'new_str', 'new_string', 'content', 'file_text'})
    return None, priority, score


def allocate(groups, n):
    counts = Counter(g['rule'] for g in groups)
    q = {k: 1 for k in counts}
    left = n - len(q)
    weights = {k: counts[k] - 1 for k in q}
    total = sum(weights.values())
    fractions = {k: left * weights[k] / total for k in q}
    for k in q:
        q[k] += math.floor(fractions[k])
    for k in sorted(q, key=lambda k: (-(fractions[k] % 1), k))[:n - sum(q.values())]:
        q[k] += 1
    return q


def main():
    scan = load(DERIVED / 'r2_state_tamper_hits.json')
    frozen = ROOT / 'data/annotations/r2_frozen/first_pass.jsonl'
    phases = {}
    for r in map(json.loads, frozen.read_text(encoding='utf-8').splitlines()):
        for n in r['source_lines']:
            phases[Path(r['raw_file']).name, n] = r['phase']
    byfile = defaultdict(list)
    for h in scan['hits']:
        byfile[h['raw_file']].append(h)
    groups, excluded = {}, []
    for file, hits in byfile.items():
        path = ROOT / file
        text = path.read_text(encoding='utf-8', errors='replace')
        try:
            data = json.loads(text)
            records = []
        except ValueError:
            data = {}
            records = []
            for line in text.splitlines():
                try:
                    records.append(json.loads(line))
                except ValueError:
                    records.append({})
        values = {p: (tool, v) for p, tool, v in payloads(path)}
        for h in hits:
            args, line = get_call(data, records, h['source_locator'])
            why, priority, score = filter_hit(h, args, line, phases)
            if why:
                excluded.append({'hit_id': h['hit_id'], 'rule': h['rule'], 'reason': why})
                continue
            session = session_key(file, h['source_locator'])
            key = session + '\0' + h['rule']
            unit = groups.setdefault(key, {'unit_id': hashlib.sha256(key.encode()).hexdigest()[:20],
                                          'session': session, 'rule': h['rule'], 'priority': False,
                                          'members': [], 'representative_score': -1})
            unit['members'].append(h['hit_id'])
            unit['priority'] |= priority
            if score > unit['representative_score']:
                tool, value = values[h['source_locator']]
                assert value.splitlines()[h['payload_line'] - 1] == h['line']
                unit['representative_score'] = score
                unit['representative'] = {**h, 'raw_file_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                          'payload_sha256': hashlib.sha256((tool + '\0' + value).encode()).hexdigest()}
    units = sorted(groups.values(), key=lambda g: g['unit_id'])
    priority = [g for g in units if g['priority']]
    rng = random.Random(2026111107)
    n = min(150, len(priority))
    chosen = []
    quotas = allocate(priority, n) if n < len(priority) else dict(Counter(g['rule'] for g in priority))
    for rule, q in sorted(quotas.items()):
        chosen.extend(rng.sample([g for g in priority if g['rule'] == rule], q))
    selected_ids = {g['unit_id'] for g in chosen}
    rest = [g for g in units if g['unit_id'] not in selected_ids]
    calibration = random.Random(2026111108).sample(rest, min(50, len(rest)))
    assert len(calibration) == 50
    result = {
        'prepared_at': now(), 'status': 'sampled_not_reviewed', 'legacy_hits': len(scan['hits']),
        'excluded_hits': len(excluded), 'exclusion_reasons': dict(Counter(h['reason'] for h in excluded)),
        'retained_hits': sum(len(g['members']) for g in units), 'deduplicated_units': len(units),
        'unit': 'canonical session x scan rule', 'rule_units': dict(Counter(g['rule'] for g in units)),
        'priority_units': len(priority), 'priority_sample': len(chosen), 'random_sample': len(calibration),
        'priority_seed': 2026111107, 'random_seed': 2026111108,
        'priority_quotas': quotas, 'priority_sample_ids': [g['unit_id'] for g in chosen],
        'random_sample_ids': [g['unit_id'] for g in calibration],
        'random_frame_units': len(rest), 'units': units, 'excluded': excluded,
        'limits': ['Structural filtering may miss semantic low-risk or high-risk distinctions',
                   'Classification of a representative is not adjudication of every occurrence in its unit',
                   'Priority strata are purposive; do not combine them with random50 to estimate population FPR',
                   'Unclassified units need no exhaustive review under the amended scope'],
    }
    path = DERIVED / 'r2_state_units.json'
    if path.exists():
        previous = load(path)
        if (ROOT / 'data/annotations/r2_state_unit_reviews.jsonl').exists():
            if any(previous[k] != result[k] for k in ['priority_sample_ids', 'random_sample_ids', 'units', 'excluded']):
                raise ValueError('Cannot change the state review frame after judgments have begun')
        result['prepared_at'] = previous['prepared_at']
    dump(path, result)
    print({k: result[k] for k in ['legacy_hits', 'excluded_hits', 'exclusion_reasons', 'retained_hits',
                                  'deduplicated_units', 'priority_units', 'priority_sample', 'random_sample']})


if __name__ == '__main__':
    main()
