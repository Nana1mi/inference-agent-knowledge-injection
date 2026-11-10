"""Audit current Round 2 evidence while explicitly reporting incomplete task gates."""
import hashlib
import json
from r2_io import ROOT,RAW,DERIVED,ROUND,load,dump,now

def main():
    errors=[];counts={};idx=load(DERIVED/'r2_kbh_index.json');rev=idx['revision'];sel=load(RAW/'r2_kbh'/rev/'selection.json')
    chosen={s['file'] for s in sel['selected']};on_disk={p.relative_to(RAW/'r2_kbh'/rev/'traces').as_posix() for p in (RAW/'r2_kbh'/rev/'traces').rglob('*.jsonl')}
    if chosen!=on_disk:errors.append('KBH selected/downloaded paths differ')
    for s in sel['selected']:
        p=RAW/'r2_kbh'/rev/'traces'/s['file'];data=p.read_bytes()
        if len(data)!=s['size']:errors.append('KBH byte count '+s['file'])
        if not s.get('lfs') and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=s['blob_id']:errors.append('KBH blob SHA '+s['file'])
    glm=[s for s in sel['selected'] if s['sampling_group']=='GLM']
    if len(glm)<6 or len({s['task'] for s in glm})<4 or {s['outcome'] for s in glm}!={'success','failure'}:errors.append('GLM quota')
    if len(sel['pair_tasks'])!=3:errors.append('paired tasks quota')
    for t in sel['pair_tasks']:
        if not all(any(s['task']==t and s['model_family']==m for s in sel['selected']) for m in ('glm','claude','gpt')):errors.append('incomplete pair '+t)
    counts['kbh_selected']=len(chosen);counts['kbh_trace_index']=idx['trace_count'];counts['kbh_bytes']=sum(s['size'] for s in sel['selected'])
    schema=load(ROOT/'data/annotations/r2_schema.json');old=load(ROOT/'data/annotations/schema.json')
    for field,definition in old['properties'].items():
        if field!='unit' and schema['properties'][field]!=definition:errors.append('old field definition changed '+field)
    sessions={s['session_id']:s for s in load(DERIVED/'r2_sessions.json')};stepcache={}
    rows=[json.loads(l) for l in (ROOT/'data/annotations/r2_kernelbench.jsonl').read_text(encoding='utf-8').splitlines()]
    seen=set()
    check={'string':lambda x:isinstance(x,str),'boolean':lambda x:isinstance(x,bool),'null':lambda x:x is None,'integer':lambda x:isinstance(x,int) and not isinstance(x,bool),'number':lambda x:isinstance(x,(int,float)) and not isinstance(x,bool),'array':lambda x:isinstance(x,list)}
    for r in rows:
        key=(r['session_id'],r['step_id'])
        if key in seen:errors.append('duplicate review '+str(key))
        seen.add(key)
        if set(schema['required'])-r.keys() or r.keys()-schema['properties'].keys():errors.append('schema fields '+str(key))
        for k,v in r.items():
            definition=schema['properties'][k]
            if 'enum' in definition and v not in definition['enum']:errors.append('enum '+str(key)+' '+k)
            if 'type' in definition:
                types=definition['type'] if isinstance(definition['type'],list) else [definition['type']]
                if not any(check[t](v) for t in types):errors.append('type '+str(key)+' '+k)
        sid=r['session_id']
        if sid not in stepcache:stepcache[sid]={s['step_id']:s for s in map(json.loads,(ROOT/sessions[sid]['step_file']).read_text(encoding='utf-8').splitlines())}
        g=stepcache[sid][r['step_id']]
        digest=hashlib.sha256(json.dumps(g,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        if digest!=r['review_input_sha256']:errors.append('stale review input '+str(key))
        if r['source_lines']!=g['source_lines']:errors.append('review locator '+str(key))
        if r['annotation_method']!='研究助理逐项复核':errors.append('non-reviewed semantic record '+str(key))
        if r['duration_seconds'] is not None:errors.append('unvalidated duration '+str(key))
    coverage=load(DERIVED/'r2_review_coverage.json');counts['reviewed_kbh_steps']=len(rows);counts['required_kbh_steps']=sum(s['steps'] for s in sessions.values())
    gates={'R1_index_sample_and_hashes':not errors,'R2_gpu_eligible_sample':False,'R3_complete_review':coverage['status']=='complete',
           'R3_blind_repeat_agreement':(DERIVED/'r2_agreement.json').exists(),
           'R4_analysis':(ROUND/'R4_analysis.md').exists(),'R5_full_scan_and_review':False,'R6_one_page_brief':(ROUND/'00_brief.md').exists()}
    report={'updated_at':now(),'status':'errors' if errors else 'in_progress','scope':'current structural provenance/schema/sample checks; incomplete gates explicitly retained, not a completion certificate',
            'counts':counts,'gates':gates,'errors':errors}
    dump(DERIVED/'r2_validation.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
