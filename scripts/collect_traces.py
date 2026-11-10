"""Choose trace sessions before annotation; deterministic sample, not representative."""
import json
import re
from concurrent.futures import ThreadPoolExecutor
from collect_sources import RAW, fetch

def main():
    meta = json.loads((RAW / 'kernelbench/dataset.json').read_text(encoding='utf-8'))
    names = [s['rfilename'] for s in meta['siblings'] if s['rfilename'].endswith('.jsonl')]
    # Two different kernel tasks from one model/harness; lexicographic earliest releases.
    chosen = []
    for task in ('01_', '02_'):
        subset = sorted(n for n in names if 'claude_claude-opus-4-8' in n and task in n)
        if not subset: subset = sorted(n for n in names if task in n)
        if subset: chosen.append(subset[0])
    if len(chosen) != 2: chosen = sorted(names)[:2]
    selection = {'dataset': meta['id'], 'commit': meta['sha'], 'license': meta.get('cardData', {}).get('license'),
                 'selection_rule': '优先 Claude Opus 4.8 的 01、02 任务，各取按文件名排序首个；不足则全库首两个。探索性方便样本。',
                 'available_jsonl_files': len(names), 'selected': chosen}
    (RAW / 'kernelbench/selection.json').write_text(json.dumps(selection, ensure_ascii=False, indent=2), encoding='utf-8')
    def get(name):
        fetch(f"https://huggingface.co/datasets/{meta['id']}/resolve/{meta['sha']}/{name}", 'kernelbench/traces/' + name, 'MIT（dataset card；不推及模型及上游代码）')
    with ThreadPoolExecutor(max_workers=2) as pool: list(pool.map(get, chosen))
    # A failed request is logged and skipped, without a mirror or cached copy.
    # Replace missing sessions by the next official dataset session, documenting the change.
    missing = [n for n in chosen if not (RAW / 'kernelbench/traces' / n).exists()]
    replacements = []
    for name in missing:
        candidates = sorted(n for n in names if n not in chosen and 'claude_claude-opus-4-8' in n)
        if candidates:
            replacement = candidates[0]; get(replacement); replacements.append({'failed': name, 'replacement': replacement})
    selection['replacements'] = replacements
    (RAW / 'kernelbench/selection.json').write_text(json.dumps(selection, ensure_ascii=False, indent=2), encoding='utf-8')
    fetch(f"https://huggingface.co/datasets/{meta['id']}/resolve/{meta['sha']}/README.md", 'kernelbench/README.md', 'MIT（dataset card）')

if __name__ == '__main__': main()
