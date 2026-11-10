"""Bounded trace review views; pass --details event IDs for complete event payloads."""
import argparse
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser(); p.add_argument('task'); p.add_argument('--details', nargs='*', type=int); args = p.parse_args()
    for file in sorted((ROOT / 'data/derived').glob('*' + args.task + '*_events.jsonl')):
        events = [json.loads(l) for l in file.read_text(encoding='utf-8').splitlines()]
        for e in events:
            if args.details:
                if e['event_id'] in args.details: print(json.dumps(e, ensure_ascii=False, indent=2))
                continue
            inp = e['input'] or {}; desc = inp.get('description') or inp.get('file_path') or inp.get('subject') or inp.get('command', '')[:90]
            result = (e.get('result') or {}).get('text', '').replace('\n', ' ')
            if result.startswith('Command running'): result = '[后台任务已启动]'
            print(f"{e['event_id']:03d} L{e['source_line']} {e['tool_name']} {desc[:100]} | {result[:130]}")

if __name__ == '__main__': main()
