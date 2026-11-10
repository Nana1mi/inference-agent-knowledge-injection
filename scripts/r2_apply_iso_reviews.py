"""Attach explicit eligibility review to full ISO index with pinned evidence locators."""
import hashlib
from r2_io import ROOT,RAW,DERIVED,load,dump

def main():
    idx=load(DERIVED/'r2_iso_index.json');rev=idx['revision'];plan=load(RAW/'r2_iso'/rev/'selection.json');review=load(ROOT/'data/annotations/r2_iso_eligibility_reviews.json')
    order={c['order']:c for c in plan['eligibility_check_order']};runs={r['run_path']:r for r in idx['runs']}
    seen=set()
    for r in review['reviews']:
        n=r['order']
        if n in seen:raise ValueError('duplicate candidate review')
        seen.add(n);candidate=order[n];row=runs[candidate['run_path']];evidence=[]
        folder=RAW/'r2_iso'/rev/'candidates'/candidate['run_path']
        for locator in r['evidence']:
            name=locator.split('#')[0].split(':')[0];path=folder/name
            if not path.exists():raise ValueError('missing eligibility evidence '+str(path))
            if '#/' in locator:
                node=load(path)
                for token in locator.split('#',1)[1].split('/')[1:]:
                    token=token.replace('~1','/').replace('~0','~')
                    node=node[int(token)] if isinstance(node,list) else node[token]
            evidence.append({'local_file':path.relative_to(ROOT).as_posix(),'locator':locator,
                             'source_url':f'https://raw.githubusercontent.com/Lossfunk/ISO-Bench/{rev}/ISO-Bench/state/runs/{candidate["run_path"]}/{name}',
                             'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        row['gpu_measurement']=r['gpu_measurement'];row['gpu_evidence']=evidence
        row['eligibility_review']={'order':n,'eligible_success_gpu':r['eligible_success_gpu'],'reason':r['reason'],'reviewer':review['reviewer']}
        for field in ('gpu_execution_confirmed','gpu_timing_valid','measurement_scope'):
            if field in r:
                row[field]=r[field]
        if (folder/'trajectory.json').exists():
            d=load(folder/'trajectory.json');row['trajectory_success']=d.get('success');row['status_conflict']=row['success'] is not None and d.get('success') is not None and row['success']!=d['success']
            row['trajectory_model']=d.get('model')
        if r.get('model_source_conflict'):
            stdout=load(folder/r['model_usage_artifact']);row['stdout_model_usage']=list(stdout.get('modelUsage',{}));row['model_source_conflict']=True
    dump(DERIVED/'r2_iso_index.json',idx)
    print('manual eligibility reviews',len(seen),'confirmed successful GPU',sum(r['eligible_success_gpu'] for r in review['reviews']))

if __name__=='__main__':main()
