"""Fetch dataset metadata and leaderboard only, never trace contents at this stage."""
import json
import re
from collections import Counter
from r2_io import RAW,DERIVED,fetch,load,dump,now

REPO='Infatoshi/kernelbench-hard-traces'

def main():
    meta=fetch(f'https://huggingface.co/api/datasets/{REPO}?blobs=true','r2_kbh/r2_current_dataset_info.json')
    if not meta: return
    info=load(meta);sha=info['sha'];folder=RAW/'r2_kbh'/sha
    dump(folder/'r2_dataset_info.json',info)
    files=[];url=f'https://huggingface.co/api/datasets/{REPO}/tree/{sha}?recursive=true&expand=false&limit=1000';page=0
    while url:
        path=fetch(url,f'r2_kbh/{sha}/r2_tree_basic_{page}.json')
        if not path:break
        payload=load(path)
        if not isinstance(payload,list):raise ValueError('Expected a list of file metadata')
        files.extend(payload)
        manifest=[json.loads(s) for s in (RAW/'r2_manifest.jsonl').read_text(encoding='utf-8').splitlines()]
        rec=next((r for r in reversed(manifest) if r.get('path')==path.relative_to(RAW.parents[1]).as_posix()),None)
        link=(rec or {}).get('next_link') or ''
        match=re.search(r'<([^>]+)>;\s*rel="next"',link);url=match.group(1) if match else None;page+=1
    board=fetch('https://kernelbench.com/runs','r2_kbh/r2_runs.html')
    hard=fetch('https://kernelbench.com/hard','r2_kbh/r2_hard.html')
    dump(DERIVED/'r2_kbh_metadata_inventory.json',{'dataset':REPO,'revision':sha,'accessed_at':now(),'files':files,
         'siblings':info.get('siblings'),'tree_pages':page,'trace_contents_downloaded':False,
         'leaderboard_path':board.relative_to(RAW.parents[1]).as_posix() if board else None})
    print('REVISION',sha,'files',len(files),'siblings',len(info.get('siblings',[])))
    names=[f.get('path') for f in files if f.get('type')=='file']
    print('EXAMPLES',json.dumps(names[:8],ensure_ascii=False))
    print('JSONL',sum(str(n).endswith('.jsonl') for n in names))

if __name__=='__main__':main()
