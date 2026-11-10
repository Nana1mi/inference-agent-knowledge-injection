"""Index downloaded paper headings, official artifact links and PDF page references."""
import json
import re
from html import unescape
from pathlib import Path
from collect_sources import RAW

def main():
    records = []
    for path in sorted((RAW / 'papers').glob('*.html')):
        if '_abs' in path.stem: continue
        html = path.read_text(encoding='utf-8')
        title = re.search(r'<title>(.*?)</title>', html, re.S)
        links = sorted(set(unescape(x) for x in re.findall(r'href="([^"]+)"', html)
                           if any(s in x for s in ('github.com/', 'huggingface.co/', 'zenodo.org/', 'license', 'creativecommons'))))
        headings = re.findall(r'<h[1-4][^>]*>(.*?)</h[1-4]>', html, re.S)
        headings = [re.sub('<[^>]+>', '', h).strip() for h in headings]
        record = {'file': path.name, 'title': unescape(title.group(1)) if title else None, 'links': links, 'headings': headings}
        records.append(record)
    (RAW / 'paper_index.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    for r in records: print(r['file'], r['title'], '\n', '\n '.join(r['links'][:20]), '\n')
    pdf_text = RAW / 'together/paper.txt'
    if pdf_text.exists():
        for i, page in enumerate(pdf_text.read_text(encoding='utf-8').split('\f'), 1):
            if any(s in page for s in ('25–31', '6.2×', '6.2', '52%', '57%', 'Expert-curated knowledge base.', 'GPU resets.')):
                print('Together PDF physical page', i, page[:140].replace('\n', ' '))

if __name__ == '__main__': main()
