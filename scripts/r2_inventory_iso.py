"""Index formal run artifact names first, then collect small exported summaries only."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from r2_io import RAW,ROOT,DERIVED,fetch,load,dump

COMMIT='0a6716bba4361f1ebe9366e1e2a33ffbb913dced'
REPO='Lossfunk/ISO-Bench'

def main():
    p=argparse.ArgumentParser();p.add_argument('--summaries',action='store_true');args=p.parse_args()
    roots=load(RAW/'iso_current/runs.json');all_files=[]
    for item in roots['tree']:
        if item['type']!='tree':continue
        name=item['path']
        if name=='sglang':tree=load(RAW/'iso_current/sglang_tree.json')
        else:
            path=fetch(f"https://api.github.com/repos/{REPO}/git/trees/{item['sha']}?recursive=1",f'r2_iso/{COMMIT}/r2_tree_{name}.json')
            if not path:continue
            tree=load(path)
        if tree.get('truncated'):raise ValueError('Truncated formal runs subtree '+name)
        all_files.extend(dict(x,path=f"{name}/{x['path']}") for x in tree['tree'] if x['type']=='blob')
    groups={}
    for f in all_files:
        path=f['path'];parts=path.split('/')
        if len(parts)<6:continue
        key='/'.join(parts[:5]);group=groups.setdefault(key,{'run_path':key,'engine_directory':parts[0], 'agent_directory':parts[1], 'model_directory':parts[2], 'task':parts[4],'artifacts':[]})
        group['artifacts'].append(f)
    index={'revision':COMMIT,'repository':REPO,'runs':list(groups.values()),'files':all_files,'metadata_only':True}
    dump(DERIVED/'r2_iso_artifact_index.json',index)
    print('formal run groups',len(groups),'artifact names',Counter(f['path'].rsplit('/',1)[-1] for f in all_files).most_common(18))
    print('agents',Counter(x['agent_directory'] for x in groups.values()))
    if args.summaries:
        targets=[f for f in all_files if f['path'].endswith(('run_summary.json','metrics.json','result.json','results.json')) and f.get('size',0)<100000]
        def get(f):
            path=f['path'];fetch(f'https://raw.githubusercontent.com/{REPO}/{COMMIT}/ISO-Bench/state/runs/{path}',f'r2_iso/{COMMIT}/summaries/{path}')
        with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(get,targets))
        print('small exported summaries attempted',len(targets))

if __name__=='__main__':main()
