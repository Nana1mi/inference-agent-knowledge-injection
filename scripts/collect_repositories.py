"""Download a bounded research snapshot from official repositories, without running their code."""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from collect_sources import RAW, fetch

REPOS = {
    'seis': 'nehzux/SEIS', 'rsi': 'apple-aiml-research/ml-rsi-inference-bench',
    'inferencebench': 'aisa-group/InferenceBench', 'vibesys': 'uw-syfi/vibesys',
    'iso': 'ISO-Bench/ISO-Bench', 'iso_data': 'ISO-Bench/analysis-data',
    'seis_scaffold': 'smth-fun/self-evolving-inference-system',
}

def collect(name):
    repo = REPOS[name]
    meta_path = fetch(f'https://api.github.com/repos/{repo}', f'{name}/repo.json')
    if not meta_path: return
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    tree_path = fetch(f"https://api.github.com/repos/{repo}/git/trees/{meta['default_branch']}?recursive=1", f'{name}/tree.json')
    if not tree_path: return
    tree = json.loads(tree_path.read_text(encoding='utf-8'))
    if tree.get('truncated'): raise RuntimeError('truncated tree: ' + repo)
    commit = tree['sha']
    license_note = (meta.get('license') or {}).get('spdx_id', '未声明根许可；不授权再分发')
    selected = []
    for entry in tree['tree']:
        p = entry['path']
        if entry['type'] != 'blob': continue
        take = p in ('README.md', 'LICENSE', 'LICENSE.md', 'CITATION.cff')
        if name == 'rsi':
            take |= p.endswith(('.md', 'task.toml')) and not p.startswith('third_party/')
            take |= p == 'third_party/pier/README.md'
            take |= p.endswith(('test.sh', 'test_outputs.py'))
        if name == 'inferencebench': take |= p.endswith(('.md', '.py', '.yaml', '.sh'))
        if name == 'vibesys':
            take |= p.startswith('docs/') and p.endswith('.md')
            take |= ('judge' in p.lower() or 'skill' in p.lower()) and p.startswith('src/') and entry.get('size', 0) < 80000
        if name == 'iso': take |= p.endswith('.md')
        if name == 'seis_scaffold': take |= p.endswith(('.md', '.sh')) or p == '.gitmodules'
        if take: selected.append(p)
    (RAW / name / 'selection.json').write_text(json.dumps({'repo': repo, 'commit': commit, 'license': license_note, 'paths': selected}, ensure_ascii=False, indent=2), encoding='utf-8')
    def retrieve(p):
        return fetch(f'https://raw.githubusercontent.com/{repo}/{commit}/{p}', f'{name}/files/{p}', license_note)
    with ThreadPoolExecutor(max_workers=4) as pool: list(pool.map(retrieve, selected))
    print(f'{name}: {commit} {len(selected)} selected files', flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('names', nargs='+', choices=REPOS)
    for name in parser.parse_args().names: collect(name)
