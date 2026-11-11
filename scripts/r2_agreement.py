"""Score separately authored repeat labels only after all 150 are complete."""
import hashlib
import json
from collections import Counter
from r2_io import ROOT, DERIVED, load, dump, now


def score(pairs):
    a, b = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    n = len(pairs)
    observed = sum(x == y for x, y in pairs) / n
    chance = sum(a[k] * b[k] for k in a.keys() | b.keys()) / (n * n)
    return {'n': n, 'agreement': observed, 'chance_agreement': chance,
            'kappa': (observed - chance) / (1 - chance) if chance != 1 else None,
            'undefined_reason': 'single-constant marginal distributions: Pe=1' if chance == 1 else None,
            'first_counts': dict(a), 'repeat_counts': dict(b),
            'confusion': [{'first': x, 'repeat': y, 'count': v} for (x, y), v in Counter(pairs).items()]}


def main():
    manifest = load(DERIVED / 'r2_blind_selection.json')
    for pathkey, hashkey in [('packet', 'packet_sha256'), ('key', 'key_sha256')]:
        if hashlib.sha256((ROOT / manifest[pathkey]).read_bytes()).hexdigest() != manifest[hashkey]:
            raise ValueError('Blind packet/key changed')
    path = ROOT / 'data/annotations/r2_blind_reviews.jsonl'
    if not path.exists():
        raise SystemExit('150-step repeat has not been authored; no agreement values generated')
    expected = {r['blind_id']: r for r in load(ROOT / manifest['key'])}
    repeats = [json.loads(l) for l in path.read_text(encoding='utf-8').splitlines() if l.strip()]
    byid = {r['blind_id']: r for r in repeats}
    if len(repeats) != len(byid) or set(byid) != set(expected) or len(repeats) != 150:
        raise ValueError('Need exactly150 unique, matching blind repeat IDs')
    schema = load(ROOT / 'data/annotations/r2_frozen/schema.json')['properties']
    fields = manifest['repeat_fields']
    for blind_id, r in byid.items():
        if r.get('review_input_sha256') != expected[blind_id]['review_input_sha256']:
            raise ValueError('Repeat source hash mismatch')
        if set(r['labels']) != set(fields) or not r.get('rationale', '').strip():
            raise ValueError('Incomplete repeat labels/rationale')
        for field, value in r['labels'].items():
            d = schema[field]
            if 'enum' in d and value not in d['enum']:
                raise ValueError('Invalid repeat enum ' + field)
            if d.get('type') == 'boolean' and not isinstance(value, bool):
                raise ValueError('Invalid repeat boolean ' + field)
    encode = lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True)
    results = {field: score([(encode(expected[k]['expected'][field]), encode(byid[k]['labels'][field]))
                             for k in expected]) for field in fields}
    dump(DERIVED / 'r2_agreement.json', {
        'status': 'complete', 'scored_at': now(), 'steps': 150, 'fields': results,
        'design': 'same AI annotator, enriched diagnostic strata; not independent human raters or population kappa',
        'selection_sha256': hashlib.sha256((DERIVED / 'r2_blind_selection.json').read_bytes()).hexdigest(),
        'repeat_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    })
    print('Scored150 separately authored repeats; agreement saved')


if __name__ == '__main__':
    main()
