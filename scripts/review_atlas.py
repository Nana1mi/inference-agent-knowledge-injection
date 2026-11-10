"""Review the first two released InferenceBench episode sequences, preserving uncertainty."""
import json
from collect_sources import RAW

def main():
    d = json.loads((RAW / 'inferencebench/trajectories.json').read_text(encoding='utf-8'))
    index = {e['id']: e for e in d['episodes']}
    for r in d['runs'][:2]:
        print('RUN', r['id'], 'outcome', r['outcome'])
        for key in r['episode_ids']:
            e = index[key]
            print(json.dumps({k: e[k] for k in ('id', 'idx', 'intent', 'strategy_family', 'n_events', 'n_edits', 'summary', 'cmd_templates')}, ensure_ascii=False))

if __name__ == '__main__': main()
