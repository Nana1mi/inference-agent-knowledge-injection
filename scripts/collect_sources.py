"""Retrieve official sources once; record hashes, timestamps and failures. Stdlib only."""
import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
        if tag in ('p', 'div', 'section', 'h1', 'h2', 'h3', 'h4', 'li', 'tr'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip = max(0, self.skip - 1)
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

def fetch(url, relative, license_note='未核实；仅本地研究，不授权再分发'):
    path = RAW / relative
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {'url': url, 'path': str(path.relative_to(ROOT)).replace('\\', '/'),
              'accessed_at': datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat(),
              'license': license_note}
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'InferenceKnowledgeResearch/1.0 (public academic research)'})
        with urllib.request.urlopen(request, timeout=45) as response:
            content = response.read()
            record.update(status=response.status, final_url=response.url,
                          content_type=response.headers.get('Content-Type', ''), bytes=len(content),
                          sha256=hashlib.sha256(content).hexdigest())
        path.write_bytes(content)
        if 'html' in record['content_type']:
            parser = TextParser(); parser.feed(content.decode('utf-8', errors='replace'))
            text = '\n'.join(line.strip() for line in ''.join(parser.parts).splitlines() if line.strip())
            path.with_suffix('.txt').write_text(text, encoding='utf-8')
        print(f"OK {relative} {len(content)}", flush=True)
    except Exception as exc:
        record.update(status='failed', error=f'{type(exc).__name__}: {exc}')
        print(f"FAIL {url} {record['error']}", flush=True)
        path = None
    RAW.mkdir(parents=True, exist_ok=True)
    with (RAW / 'manifest.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + '\n')
    return path

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('url', nargs='?'); parser.add_argument('path', nargs='?')
    parser.add_argument('--papers', action='store_true'); args = parser.parse_args()
    if args.papers:
        ids = ['2610.04646', '2611.03517', '2607.20468', '2602.19594', '2605.06068',
               '2607.12875v1', '2607.12875v3', '2512.23236', '2601.00227', '2510.27176', '2510.06189', '2609.00065']
        for paper_id in ids:
            fetch('https://arxiv.org/abs/' + paper_id, 'papers/' + paper_id + '_abs.html', '参见原始页面 License 链接')
            time.sleep(3.1)
            fetch('https://arxiv.org/html/' + paper_id, 'papers/' + paper_id + '.html', '参见原始页面 License 链接')
            time.sleep(3.1)
    elif args.url and args.path:
        fetch(args.url, args.path)
    else: parser.error('provide URL PATH or --papers')

if __name__ == '__main__': main()
