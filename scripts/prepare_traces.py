"""Extract observable actions and link tool results to source line numbers; no behavioral labeling."""
import json
from pathlib import Path
from collect_sources import RAW

def main():
    outdir = RAW.parent / 'derived'; outdir.mkdir(exist_ok=True)
    sessions = []
    for path in sorted((RAW / 'kernelbench/traces').glob('*.jsonl')):
        rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
        results = {}
        for line, row in enumerate(rows, 1):
            content = row.get('message', {}).get('content', [])
            if not isinstance(content, list): continue
            for block in content:
                if block.get('type') == 'tool_result':
                    value = block.get('content', '')
                    results[block.get('tool_use_id')] = {'line': line, 'text': value if isinstance(value, str) else json.dumps(value, ensure_ascii=False), 'is_error': block.get('is_error')}
        events = []
        for line, row in enumerate(rows, 1):
            msg = row.get('message', {}); content = msg.get('content', [])
            if not isinstance(content, list): continue
            text = '\n'.join(b.get('text', '') for b in content if b.get('type') == 'text')
            for block in content:
                if block.get('type') != 'tool_use': continue
                events.append({'event_id': len(events) + 1, 'session_id': path.stem, 'raw_file': str(path.relative_to(RAW.parents[1])).replace('\\', '/'),
                               'source_line': line, 'timestamp': row.get('timestamp'), 'tool_name': block.get('name'),
                               'input': block.get('input'), 'preceding_text': text,
                               'result': results.get(block.get('id'))})
        target = outdir / (path.stem + '_events.jsonl')
        target.write_text('\n'.join(json.dumps(e, ensure_ascii=False) for e in events) + '\n', encoding='utf-8')
        view = []
        for e in events:
            command = json.dumps(e['input'], ensure_ascii=False).replace('\\n', ' ')
            result = (e.get('result') or {}).get('text', '').replace('\n', ' ')
            view.append(f"{e['event_id']:03d} L{e['source_line']} {e['tool_name']} {command[:350]}\n  RESULT {result[:250]}\n  TEXT {e['preceding_text'][:250]}")
        target.with_suffix('.txt').write_text('\n'.join(view), encoding='utf-8')
        sessions.append({'session_id': path.stem, 'raw_records': len(rows), 'tool_events': len(events),
                         'first_timestamp': next((r.get('timestamp') for r in rows if r.get('timestamp')), None),
                         'last_timestamp': next((r.get('timestamp') for r in reversed(rows) if r.get('timestamp')), None)})
    (outdir / 'sessions.json').write_text(json.dumps(sessions, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(sessions, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
