"""Fetch small documentation artifacts selected from previously inspected official trees."""
import json
from concurrent.futures import ThreadPoolExecutor
from collect_sources import RAW, fetch

JOBS={
 'flashinfer':('flashinfer-ai/flashinfer-bench',['README.md','docs/flashinfer-trace/trace.mdx','docs/flashinfer-trace/validate.mdx']),
 'openevolve':('algorithmicsuperintelligence/openevolve',['README.md','examples/attention_optimization/README.md']),
}

def main():
    todo=[]
    for name,(repo,paths) in JOBS.items():
        tree=json.loads((RAW/name/'tree.json').read_text(encoding='utf-8'))
        for p in paths: todo.append((f"https://raw.githubusercontent.com/{repo}/{tree['sha']}/{p}",f'{name}/files/{p}'))
    with ThreadPoolExecutor(max_workers=3) as pool: list(pool.map(lambda p:fetch(*p),todo))
    fetch('https://raw.githubusercontent.com/MetaInfer/MetaInfer/master/README.md','metainfer/README.md')

if __name__=='__main__': main()
