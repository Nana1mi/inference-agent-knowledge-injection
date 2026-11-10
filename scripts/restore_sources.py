"""Restore locally archived public sources from their recorded official URLs.

Downloaded third-party text is not bundled in the public repository. A changed
response is retained separately rather than presented as the frozen snapshot.
"""
import argparse
import hashlib
import json
import time
import urllib.request
from pathlib import Path
from collect_sources import TextParser

ROOT = Path(__file__).resolve().parents[1]

def extract_html_text(target, item):
    if 'html' not in item.get('content_type', ''):
        return
    destination = target.with_suffix('.txt')
    if destination.exists():
        return
    parser = TextParser()
    parser.feed(target.read_text(encoding='utf-8', errors='replace'))
    content = '\n'.join(line.strip() for line in ''.join(parser.parts).splitlines() if line.strip())
    destination.write_text(content, encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, help='Limit missing source downloads for a small smoke check')
    args = parser.parse_args()
    manifest = ROOT / 'data/raw/manifest.jsonl'
    snapshots = {}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        item = json.loads(line)
        if item.get('status') == 200:
            snapshots[item['path']] = item
    results = []
    attempted = 0
    for relative, item in snapshots.items():
        target = (ROOT / relative).resolve()
        if not target.is_relative_to((ROOT / 'data/raw').resolve()):
            raise ValueError('Manifest path outside data/raw')
        if target.exists():
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            if digest == item['sha256']:
                extract_html_text(target, item)
            results.append({'path': relative, 'status': 'already_matches' if digest == item['sha256'] else 'existing_hash_differs'})
            continue
        if args.limit is not None and attempted >= args.limit:
            continue
        attempted += 1
        record = {'path': relative, 'url': item['url']}
        try:
            request = urllib.request.Request(item['url'], headers={'User-Agent': 'InferenceKnowledgeResearch/1.0'})
            with urllib.request.urlopen(request, timeout=45) as response:
                content = response.read()
            target.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256(content).hexdigest()
            if digest == item['sha256']:
                target.write_bytes(content)
                extract_html_text(target, item)
                record['status'] = 'restored_exact_snapshot'
            else:
                target.with_name(target.name + '.changed').write_bytes(content)
                record.update(status='source_changed_saved_separately', observed_sha256=digest)
            print(record['status'], relative, flush=True)
        except Exception as exc:
            record.update(status='failed', error=f'{type(exc).__name__}: {exc}')
            print('failed', relative, flush=True)
        results.append(record)
        time.sleep(3.1)
    output = ROOT / 'data/derived/restore_results.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Restore audit:', output)

if __name__ == '__main__':
    main()
