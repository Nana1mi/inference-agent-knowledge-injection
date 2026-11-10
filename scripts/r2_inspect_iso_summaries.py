"""Reconcile metadata fields from small official run exports; no inferred success labels."""
from collections import Counter
from r2_io import RAW,DERIVED,load,dump

def main():
    artifact=load(DERIVED/'r2_iso_artifact_index.json');revision=artifact['revision'];rows=[]
    for run in artifact['runs']:
        rel=run['run_path']+'/run_summary.json';path=RAW/'r2_iso'/revision/'summaries'/rel
        row={k:v for k,v in run.items() if k!='artifacts'};row.update(agent=None,model=None,task_id=None,item_id=None,human_commit=None,success=None,gpu_measurement=None,status_evidence=None,gpu_evidence=None)
        if path.exists():
            d=load(path);agent=d.get('agent',{});status=agent.get('status')
            row.update(agent=d.get('meta',{}).get('agent'),model=d.get('meta',{}).get('model_full') or d.get('meta',{}).get('model'),task_id=d.get('meta',{}).get('task_id'),item_id=d.get('meta',{}).get('item_id'),human_commit=d.get('commits',{}).get('human'),export_status=status,
                       success=True if status=='success' else False if status in ('failed','failure','error','timeout','max_steps_exceeded') else None,
                       status_evidence={'file':path.relative_to(RAW.parents[1]).as_posix(),'pointer':'/agent/status','value':status},summary=d)
        row['available_artifacts']=[a['path'].rsplit('/',1)[-1] for a in run['artifacts']]
        rows.append(row)
    dump(DERIVED/'r2_iso_index.json',{'revision':revision,'runs':rows,'success_definition':'only /agent/status==success; not patch existence or commit inferred','gpu_definition':'only exported observed execution evidence; unknown until checked, task mentions do not qualify'})
    observed=[r for r in rows if r['status_evidence']]
    print('indexed',len(rows),'summaries retrieved',len(observed),'status',Counter(r.get('export_status') for r in observed))
    print('successful agent/model',Counter((r.get('agent'),r.get('model')) for r in observed if r['success']))
    review=RAW.parents[1]/'data/annotations/r2_iso_eligibility_reviews.json'
    if review.exists() and (RAW/'r2_iso'/revision/'selection.json').exists():
        from r2_apply_iso_reviews import main as apply_reviews
        apply_reviews()

if __name__=='__main__':main()
