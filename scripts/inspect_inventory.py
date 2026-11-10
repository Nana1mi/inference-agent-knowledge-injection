"""Summarize public artifact structures without dumping large datasets."""
import json
from collect_sources import RAW

def main():
    p = RAW / 'inferencebench/trajectories.json'
    if p.exists():
        d = json.loads(p.read_text(encoding='utf-8'))
        print('InferenceBench keys', list(d))
        for k in ('runs', 'episodes'):
            print(k, len(d.get(k, [])))
            print(json.dumps(d.get(k, [])[:2], ensure_ascii=False, indent=2)[:10000])
    for name in ('rsi', 'iso', 'iso_data', 'iso_current', 'vibesys'):
        path = RAW / name / 'tree.json'
        if path.exists():
            d = json.loads(path.read_text(encoding='utf-8'))
            print(name, d.get('sha'), len(d.get('tree', [])), 'truncated', d.get('truncated'))
            paths = [e for e in d.get('tree', []) if any(s in e['path'].lower() for s in ('trace', 'transcript', 'analysis-data', 'trajectory', 'readme'))]
            print(json.dumps(paths[:18], ensure_ascii=False)[:4000])

if __name__ == '__main__': main()
