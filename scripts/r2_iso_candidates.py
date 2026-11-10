"""Freeze seeded ISO eligibility-check order; fetch only the next ordered candidates.

GPU eligibility is supplied by separate explicit review, never by this downloader.
"""
import argparse
import hashlib
import json
import random
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from r2_io import ROOT,RAW,DERIVED,load,dump,fetch,now

SEED=2026111102

def freeze_order():
    idx=load(DERIVED/'r2_iso_index.json');art=load(DERIVED/'r2_iso_artifact_index.json');rev=idx['revision']
    dest=RAW/'r2_iso'/rev/'selection.json'
    if dest.exists():return load(dest)
    targets={f['path'] for f in art['files'] if f['path'].endswith(('run_summary.json','metrics.json','result.json','results.json')) and f.get('size',0)<100000}
    attempted={r['path'].split('/summaries/',1)[1] for r in map(json.loads,(RAW/'r2_manifest.jsonl').read_text(encoding='utf-8').splitlines()) if '/summaries/' in r.get('path','')}
    missing=targets-attempted
    if missing:raise RuntimeError(f'Full metadata acquisition not yet attempted for {len(missing)} files; do not sample time-biased partial frame')
    frame_bytes=(DERIVED/'r2_iso_index.json').read_bytes()
    dump(RAW/'r2_iso'/rev/'r2_frozen_sampling_frame.json',idx)
    artifacts={r['run_path']:r for r in art['runs']};strata=defaultdict(list)
    rng=random.Random(SEED)
    for r in idx['runs']:
        names=set(r['available_artifacts'])
        if r['success'] and r.get('agent') and r.get('model') and ('trajectory.json' in names or any('stdout' in n for n in names)):
            strata[(r['agent'],r['model'])].append(r['run_path'])
    keys=sorted(strata);rng.shuffle(keys)
    for key in keys:
        strata[key].sort();rng.shuffle(strata[key])
    order=[]
    while any(strata.values()):
        for key in keys:
            if strata[key]:order.append({'order':len(order)+1,'run_path':strata[key].pop(),'agent':key[0],'model':key[1]})
    plan={'revision':rev,'repository':art['repository'],'seed':SEED,'prepared_at':now(),
          'sampling_frame_sha256':hashlib.sha256(frame_bytes).hexdigest(),
          'scheme':'seeded within exported agent/model strata; seeded strata round-robin; manually confirm observed GPU measurements in this order',
          'success_definition':'export /agent/status==success; GPU proof independently required',
          'quota':{'minimum_sessions':6,'minimum_successful_with_gpu':4,'minimum_agent_or_model_categories':2},
          'eligibility_check_order':order,'selected':[],'inspected_candidates':[],
          'old_api400_runs':'data/raw/iso_current/selection.json; retained in old annotations, excluded from round2 behavioral stats'}
    dump(dest,plan);print('frozen eligibility frame',len(order),'runs',len(keys),'strata')
    return plan

def download(plan,through,trace_only=False):
    rev=plan['revision'];repo=plan['repository'];art=load(DERIVED/'r2_iso_artifact_index.json');runs={r['run_path']:r for r in art['runs']}
    todo=plan['eligibility_check_order'][:through]
    failures=defaultdict(int)
    for r in map(json.loads,(RAW/'r2_manifest.jsonl').read_text(encoding='utf-8').splitlines()):
        if r['status']=='failed':failures[r['path']]+=1
    def collect(c):
        files=runs[c['run_path']]['artifacts'];byname={f['path'].rsplit('/',1)[-1]:f for f in files}
        trace=next((byname[n] for n in ['trajectory.json','claude_stdout.json','claude_stdout.jsonl','codex_stdout.json','codex_stdout.jsonl','openhands_stdout.json','openhands_stdout.jsonl','trae_stdout.txt'] if n in byname and byname[n].get('size',0)>0),None)
        if trace is None:trace=next((f for f in files if 'stdout' in f['path'] and f.get('size',0)>0),None)
        chosen=([trace] if trace else [])+[byname[n] for n in ['journal.json','model_patch.diff'] if n in byname and byname[n].get('size',0)>0 and (not trace_only or (RAW/f'r2_iso/{rev}/candidates/{byname[n]["path"]}').exists())]
        record=dict(c,artifacts=[])
        for f in chosen:
            rel=f'r2_iso/{rev}/candidates/{f["path"]}'
            path=RAW/rel
            if not path.exists() and failures['data/raw/'+rel]>=2:path=None
            else:path=fetch(f'https://raw.githubusercontent.com/{repo}/{rev}/ISO-Bench/state/runs/{f["path"]}',rel)
            record['artifacts'].append({'upstream_path':f['path'],'bytes':f.get('size'),'blob_sha':f['sha'],'local_file':path.relative_to(ROOT).as_posix() if path else None})
        return record
    with ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(collect,todo))
    plan['inspected_candidates']=records
    plan['last_acquisition_trace_only']=trace_only
    dump(RAW/'r2_iso'/rev/'selection.json',plan)
    print('downloaded/attempted candidate prefixes',len(records),'not final selected sample')

def main():
    p=argparse.ArgumentParser();p.add_argument('--through',type=int,default=0);p.add_argument('--trace-only',action='store_true');a=p.parse_args()
    plan=freeze_order()
    if a.through:download(plan,a.through,a.trace_only)
    print('next',plan['eligibility_check_order'][:3])

if __name__=='__main__':main()
