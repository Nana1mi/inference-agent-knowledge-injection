"""Inspect appendix anchors and concise report length; no network or inference."""
import json
import re
from collect_sources import ROOT,RAW

def main():
    for ident in ('2607.20468','2610.04646'):
        html=(RAW/'papers'/f'{ident}.html').read_text(encoding='utf-8')
        headings=[]
        for m in re.finditer(r'<section\b([^>]+)>',html):
            attrs=m.group(1)
            if 'ltx_appendix' in attrs:
                sid=re.search(r'id="([^"]+)"',attrs)
                title=re.search(r'<h[1-4][^>]*>(.*?)</h[1-4]>',html[m.end():],re.S)
                headings.append((sid.group(1) if sid else None,re.sub('<[^>]+>','',title.group(1))[:120] if title else None))
        print(ident,headings)
    for name in ('00_summary.md','T5_rsi_bench_notes.md'):
        text=(ROOT/'outputs'/name).read_text(encoding='utf-8');plain=re.sub(r'\]\([^)]*\)',']',text)
        print(name,'body_characters_excluding_link_urls',len(plain),'Chinese characters',len(re.findall(r'[\u4e00-\u9fff]',plain)))

if __name__=='__main__':main()
