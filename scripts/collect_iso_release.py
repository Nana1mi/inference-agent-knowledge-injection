"""Traverse shallow official trees to avoid treating a truncated recursive listing as complete."""
import json
from collect_sources import RAW, fetch

def main():
    d=json.loads((RAW/'iso_current/tree.json').read_text(encoding='utf-8'))
    subtree=next(x for x in d['tree'] if x['path']=='ISO-Bench' and x['type']=='tree')
    p=fetch(f"https://api.github.com/repos/Lossfunk/ISO-Bench/git/trees/{subtree['sha']}",'iso_current/root.json')
    if p:
        t=json.loads(p.read_text(encoding='utf-8'))
        print('ISO-Bench root',[(x['path'],x['type']) for x in t['tree']])
        state=next(x for x in t['tree'] if x['path']=='state')
        q=fetch(f"https://api.github.com/repos/Lossfunk/ISO-Bench/git/trees/{state['sha']}",'iso_current/state.json')
        if q:
            state_tree=json.loads(q.read_text(encoding='utf-8'))
            print('state',[(x['path'],x['type']) for x in state_tree['tree']])
            runs=next(x for x in state_tree['tree'] if x['path']=='runs')
            rp=fetch(f"https://api.github.com/repos/Lossfunk/ISO-Bench/git/trees/{runs['sha']}",'iso_current/runs.json')
            if rp:
                rd=json.loads(rp.read_text(encoding='utf-8'))
                print('runs',[(x['path'],x['type']) for x in rd['tree']][:35])
                engine=next(x for x in rd['tree'] if x['path']=='sglang')
                et=fetch(f"https://api.github.com/repos/Lossfunk/ISO-Bench/git/trees/{engine['sha']}?recursive=1",'iso_current/sglang_tree.json')
                if et:
                    ed=json.loads(et.read_text(encoding='utf-8'))
                    print('sglang count',len(ed.get('tree',[])),'truncated',ed.get('truncated'))
                    traces=[x for x in ed.get('tree',[]) if x['path'].endswith('trajectory.json')]
                    print('trajectories',[(x['path'],x.get('size')) for x in traces[:8]])
                    selected=traces[:2]
                    for x in selected:
                        url=f"https://raw.githubusercontent.com/Lossfunk/ISO-Bench/{d['sha']}/ISO-Bench/state/runs/sglang/{x['path']}"
                        fetch(url,'iso_current/traces/'+x['path'])
                    (RAW/'iso_current/selection.json').write_text(json.dumps({'commit':d['sha'],'sglang_subtree_truncated':ed.get('truncated'),'available_sglang_trajectory_files':len(traces),'selection':'sglang subtree lexicographic first two trajectory.json; no outcome selection','paths':selected},ensure_ascii=False,indent=2),encoding='utf-8')
        fetch(f"https://raw.githubusercontent.com/Lossfunk/ISO-Bench/{d['sha']}/ISO-Bench/README.md",'iso_current/README.md')

if __name__=='__main__':main()
