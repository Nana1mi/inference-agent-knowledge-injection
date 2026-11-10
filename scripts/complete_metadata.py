"""Finish small official manifests and record source licensing without running external code."""
import json
from concurrent.futures import ThreadPoolExecutor
from collect_sources import RAW, fetch

def main():
    tree=json.loads((RAW/'rsi/tree.json').read_text(encoding='utf-8'))
    missing=[x['path'] for x in tree['tree'] if x['path'].startswith('tasks/') and x['path'].endswith('/task.toml') and not (RAW/'rsi/files'/x['path']).exists()]
    for p in missing: fetch(f"https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/{tree['sha']}/{p}",f'rsi/files/{p}','Apple Sample Code License（根 LICENSE）')
    urls=[('https://kernelbench.com/hard','kernelbench/hard.html'),('https://api.github.com/repos/algorithmicsuperintelligence/openevolve','openevolve/repo.json'),
          ('https://api.github.com/repos/algorithmicsuperintelligence/openevolve/git/trees/main?recursive=1','openevolve/tree.json'),
          ('https://api.github.com/repos/flashinfer-ai/flashinfer-bench/git/trees/main?recursive=1','flashinfer/tree.json'),
          ('https://ayushnangia.github.io/iso-bench-website/','iso/project.html')]
    with ThreadPoolExecutor(max_workers=3) as pool: list(pool.map(lambda pair: fetch(*pair),urls))

if __name__=='__main__': main()
