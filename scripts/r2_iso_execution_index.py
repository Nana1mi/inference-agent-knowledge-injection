"""Index downloaded ISO observable results and unlabelled GPU navigation cues.

No GPU eligibility decision is generated. Source-code readbacks and agent-written
reports may contain the same words as real measurements, so cues require review.
"""
import hashlib
import json
import re
from collections import Counter
from r2_io import ROOT,RAW,DERIVED,load,dump,now

COMMAND=re.compile(r'(?<![/\w])(?:python(?:3)?\s|pytest\b|nvidia-smi\b|ncu\b|nsys\b|nvprof\b)',re.I)
POSITIVE=re.compile(r'CUDA\s*(?:available|is_available)\s*[:=]?\s*True|\bdevice\s*[:=]\s*[\x22\x27]?(?:cuda|gpu)|\bTFLOPS\b|NVIDIA\s+(?:A100|H100|H200|B200|RTX|L40|A10|V100)|\b(?:cuda|gpu)[\w\s:=-]{0,40}\b\d+(?:\.\d+)?\s*(?:ms|us|µs|seconds)',re.I)
NEGATIVE=re.compile(r'CUDA.*(?:not available|unavailable|False)|(?:No|without)\s+(?:CUDA|GPU)|device\s*[:=]\s*[\x22\x27]?cpu|libcuda\.so.*(?:not found|No such file)|CPU fallback|Found no NVIDIA driver',re.I)

def main():
    rev=load(DERIVED/'r2_iso_index.json')['revision'];sel=load(RAW/'r2_iso'/rev/'selection.json');rows=[];packets=[]
    for c in sel['eligibility_check_order']:
        folder=RAW/'r2_iso'/rev/'candidates'/c['run_path'];trajectory=folder/'trajectory.json'
        row=dict(c,artifact_kind='not_retrieved',execution_result_count=0,positive_cue_count=0,negative_cue_count=0,trajectory_success=None,steps=None)
        if trajectory.exists():
            d=load(trajectory);row.update(artifact_kind='trajectory',trajectory_success=d.get('success'),trajectory_model=d.get('model'),steps=len(d.get('agent_steps',[])))
            row['sha256']=hashlib.sha256(trajectory.read_bytes()).hexdigest()
            for i,s in enumerate(d.get('agent_steps',[])):
                calls=s.get('tool_calls') or [];matches=[t for t in calls if t.get('name','').lower() in ('bash','shell','run','execute_bash') and COMMAND.search(str(t.get('arguments',{}).get('command','')))]
                if not matches:continue
                for j,result in enumerate(s.get('tool_results') or []):
                    value=str(result.get('result') or result.get('error') or '')
                    positive=[(k+1,line) for k,line in enumerate(value.splitlines()) if POSITIVE.search(line)]
                    negative=[(k+1,line) for k,line in enumerate(value.splitlines()) if NEGATIVE.search(line)]
                    row['execution_result_count']+=1;row['positive_cue_count']+=len(positive);row['negative_cue_count']+=len(negative)
                    if positive or negative:
                        packets.append({'order':c['order'],'file':trajectory.relative_to(ROOT).as_posix(),'step':i+1,
                                        'locator':f'/agent_steps/{i}/tool_results/{j}/result','calls':matches,
                                        'positive_lines':positive,'negative_lines':negative,'result':value})
        else:
            files=list(folder.glob('*stdout*')) if folder.exists() else []
            if files:
                f=files[0];value=f.read_text(encoding='utf-8',errors='replace');row['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
                try:d=json.loads(value)
                except json.JSONDecodeError:d=None
                if isinstance(d,dict) and d.get('type')=='result':
                    row.update(artifact_kind='final_result_without_tools',stdout_model_usage=list(d.get('modelUsage',{})),stdout_subtype=d.get('subtype'))
                else:row['artifact_kind']='unstructured_stdout'
        rows.append(row)
    dump(DERIVED/'r2_iso_execution_inventory.json',{'updated_at':now(),'scope':'structural observable export inventory; regex cues are NOT eligibility labels','rows':rows})
    dump(DERIVED/'r2_iso_execution_inputs.json',{'scope':'unlabelled local-only source excerpts for review','packets':packets})
    print('artifacts',dict(Counter(r['artifact_kind'] for r in rows)))
    print('candidate positive-cue orders',[r['order'] for r in rows if r['positive_cue_count']])
    print('downloaded trajectories',sum(r['artifact_kind']=='trajectory' for r in rows),'execution-result packets',sum(r['execution_result_count'] for r in rows),'cue packets',len(packets))

if __name__=='__main__':main()
