"""Execute the preregistered stratified random design, without accessing trace content."""
import random
from collections import Counter
from r2_io import RAW,DERIVED,ROOT,load,dump,now

SEED=2026111101

def main():
    progress=(ROOT/'outputs/PROGRESS.md').read_text(encoding='utf-8')
    if str(SEED) not in progress:raise RuntimeError('Sampling plan/seed not recorded')
    index=load(DERIVED/'r2_kbh_index.json');rng=random.Random(SEED)
    allrows=[r for r in index['files'] if r['kind']=='trace'];known=[r for r in allrows if r['outcome']!='unknown']
    success=sorted([r for r in known if r['model_family']=='glm' and r['outcome']=='success'],key=lambda r:r['file'])
    failure=sorted([r for r in known if r['model_family']=='glm' and r['outcome']=='failure'],key=lambda r:r['file'])
    if len(success)<3 or len(failure)<3:raise RuntimeError('Insufficient quota; report shortfall, do not silently relax')
    for attempt in range(1,100001):
        glm=rng.sample(failure,3)+rng.sample(success,3)
        tasks={r['task'] for r in glm}
        paired=sorted(t for t in tasks if all(any(r['model_family']==f and r['task']==t for r in known) for f in ('claude','gpt')))
        if len(tasks)>=4 and len(paired)>=3:break
    else:raise RuntimeError('No valid random design')
    chosen=[dict(r,sampling_group='GLM') for r in glm];pair_tasks=rng.sample(paired,3)
    for task in pair_tasks:
        for family in ('claude','gpt'):
            frame=sorted([r for r in known if r['model_family']==family and r['task']==task],key=lambda r:r['file'])
            chosen.append(dict(rng.choice(frame),sampling_group='paired_'+family))
    frame=sorted([r for r in known if r['model_family']=='deepseek' and r['task'] in tasks],key=lambda r:r['file'])
    for supplementary_attempt in range(1,100001):
        extra=rng.sample(frame,2)
        if len({r['task'] for r in extra})==2:break
    chosen.extend(dict(r,sampling_group='supplement_deepseek') for r in extra)
    out={'dataset':index['dataset'],'revision':index['revision'],'seed':SEED,'selected_at':now(),
         'method':'conditional stratified random sample; sorted frame then random draws, never lexicographic first-k selection',
         'glm_condition_attempts':attempt,'supplement_condition_attempts':supplementary_attempt,
         'quota':{'glm_success':3,'glm_failure':3,'minimum_glm_tasks':4,'paired_tasks':3,'closed_per_paired_task':2,'supplement_deepseek':2},
         'pair_tasks':pair_tasks,'selected':chosen}
    dump(RAW/'r2_kbh'/index['revision']/'selection.json',out)
    print('selected',len(chosen),'GLM tasks',len(tasks),'random attempts',attempt,'bytes',sum(r['size'] for r in chosen))
    for r in chosen:print(r['sampling_group'],r['model_from_filename'],r['task'],r['outcome'],r['file'])

if __name__=='__main__':main()
