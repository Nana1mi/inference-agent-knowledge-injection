"""Prepare 150 unique field-enriched steps; do not expose first-pass labels."""
import hashlib
import json
import math
import random
import uuid
from collections import Counter, defaultdict
from r2_io import ROOT, DERIVED, load, dump, now

FIELDS = ['phase', 'tool', 'layer', 'hypothesis_origin', 'evidence', 'outcome',
          'turning_point', 'reasoning_visible', 'hypothesis_source', 'knowledge_access',
          'knowledge_use', 'state_tamper_risk', 'candidate_edit', 'component']


def main():
    frozen = ROOT / 'data/annotations/r2_frozen'
    rows = [json.loads(l) for l in (frozen / 'first_pass.jsonl').read_text(encoding='utf-8').splitlines()]
    sessions = {s['session_id']: s for s in load(frozen / 'sessions.json')}
    raw = {sid: {r['step_id']: r for r in map(json.loads, (ROOT / s['step_file']).read_text(encoding='utf-8').splitlines())}
           for sid, s in sessions.items()}
    rng = random.Random(2026111105)
    blind_rng = random.Random(2026111106)
    total = sum(s['steps'] for s in sessions.values())
    fractions = {sid: 8 * s['steps'] / total for sid, s in sessions.items()}
    quotas = {sid: 3 + math.floor(v) for sid, v in fractions.items()}
    for sid in sorted(sessions, key=lambda sid: (-(fractions[sid] % 1), sid))[:50 - sum(quotas.values())]:
        quotas[sid] += 1
    assert sum(quotas.values()) == 50
    chosen = []
    seen = set()
    for field in ['knowledge_use', 'hypothesis_source', 'state_tamper_risk']:
        for sid in sorted(sessions):
            pools = defaultdict(list)
            for r in rows:
                key = (r['session_id'], r['step_id'])
                if r['session_id'] == sid and key not in seen:
                    pools[str(r[field])].append(r)
            for values in pools.values():
                rng.shuffle(values)
            categories = sorted(pools)
            if field == 'knowledge_use':
                categories = [c for c in categories if c != '不适用'] + ['不适用']
            picked = []
            # Reserve a not-applicable control when the knowledge pool allows it.
            reserve = pools['不适用'].pop() if field == 'knowledge_use' and pools.get('不适用') else None
            target = quotas[sid] - int(reserve is not None)
            while len(picked) < target:
                active = [c for c in categories if pools.get(c)]
                if not active:
                    raise ValueError('Insufficient unselected steps in session')
                if field == 'knowledge_use' and any(c != '不适用' for c in active):
                    active = [c for c in active if c != '不适用']
                for category in active:
                    if len(picked) == target:
                        break
                    picked.append(pools[category].pop())
            if reserve is not None:
                picked.append(reserve)
            for r in picked:
                key = (sid, r['step_id'])
                assert key not in seen
                seen.add(key)
                chosen.append((field, r))
    assert len(chosen) == len(seen) == 150
    blind_rng.shuffle(chosen)
    packets, keyrows = [], []
    for field, r in chosen:
        sid, step = r['session_id'], r['step_id']
        blind_id = 'B-' + uuid.UUID(int=blind_rng.getrandbits(128)).hex[:16]
        g = raw[sid][step]
        packets.append({'blind_id': blind_id, 'current': g,
                        'context_before': [raw[sid][i] for i in range(max(1, step - 2), step)],
                        'context_after': [raw[sid][i] for i in range(step + 1, min(sessions[sid]['steps'], step + 2) + 1)],
                        'raw_only_session_context': sessions[sid]['step_file'],
                        'instruction': 'Use only raw context and codebook; never open the first-pass key while repeating labels.'})
        keyrows.append({'blind_id': blind_id, 'session_id': sid, 'step_id': step,
                        'selection_field': field, 'expected': {f: r[f] for f in FIELDS},
                        'review_input_sha256': r['review_input_sha256']})
    packet_path = DERIVED / 'r2_review_inputs/blind150.json'
    key_path = ROOT / 'data/annotations/r2_blind_key.json'
    # Never silently replace a packet/key once repeat work has begun.
    for path, value in [(packet_path, packets), (key_path, keyrows)]:
        if path.exists() and load(path) != value:
            raise ValueError('Existing blind selection differs: ' + str(path))
        if not path.exists():
            dump(path, value)
    manifest = {
        'prepared_at': now(), 'steps': 150, 'selection_seed': 2026111105, 'blind_seed': 2026111106,
        'focus_field_slots': dict(Counter(field for field, _ in chosen)),
        'by_session': dict(sorted(Counter(r['session_id'] for _, r in chosen).items())),
        'per_session_per_field_quota': quotas, 'repeat_fields': FIELDS,
        'packet': packet_path.relative_to(ROOT).as_posix(),
        'packet_sha256': hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        'key': key_path.relative_to(ROOT).as_posix(),
        'key_sha256': hashlib.sha256(key_path.read_bytes()).hexdigest(),
        'first_pass_manifest_sha256': hashlib.sha256((frozen / 'manifest.json').read_bytes()).hexdigest(),
        'status': 'prepared_not_reannotated',
        'limits': ['First-pass labels used only for enriched sampling, omitted from the raw repeat packet',
                   'Same AI annotator; context memory cannot be eliminated',
                   'Unweighted kappa will describe this enriched diagnostic sample, not all 3345 steps'],
    }
    existing = DERIVED / 'r2_blind_selection.json'
    if existing.exists():
        manifest['prepared_at'] = load(existing)['prepared_at']
    dump(existing, manifest)
    print('Prepared150 raw-only packets; session counts', manifest['by_session'])
    print('No first-pass labels or selection-focus mapping printed')


if __name__ == '__main__':
    main()
