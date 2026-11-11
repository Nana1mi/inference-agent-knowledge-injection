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
        if r['phase']=='写报告' and g['calls'] and all(c['name']=='TaskOutput' for c in g['calls']):errors.append('report phase on wait-only tools '+str(key))
        digest=hashlib.sha256(json.dumps(g,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        if digest!=r['review_input_sha256']:errors.append('stale review input '+str(key))
        if r['source_lines']!=g['source_lines']:errors.append('review locator '+str(key))
        if r['annotation_method']!='研究助理逐项复核':errors.append('non-reviewed semantic record '+str(key))
        if r['duration_seconds'] is not None:errors.append('unvalidated duration '+str(key))
    coverage=load(DERIVED/'r2_review_coverage.json');counts['reviewed_kbh_steps']=len(rows);counts['required_kbh_steps']=sum(s['steps'] for s in sessions.values())
    iso_reviews=load(ROOT/'data/annotations/r2_iso_eligibility_reviews.json')['reviews']
    counts['reviewed_iso_eligibility_candidates']=len(iso_reviews)
    counts['confirmed_successful_gpu_candidates']=sum(r['eligible_success_gpu'] for r in iso_reviews)
    counts['selected_iso_sessions']=len(load(RAW/'r2_iso'/load(DERIVED/'r2_iso_index.json')['revision']/'selection.json')['selected'])
    state_coverage=load(DERIVED/'r2_state_review_coverage.json')
    counts['required_state_scan_hits']=state_coverage['required_hits'];counts['reviewed_state_scan_hits']=state_coverage['reviewed_hits']
    expected_steps={(sid,g['step_id']) for sid,s in sessions.items()
                    for g in map(json.loads,(ROOT/s['step_file']).read_text(encoding='utf-8').splitlines())}
    kbh_first_pass_complete=coverage['status']=='complete' and seen==expected_steps and not errors
    scope=load(DERIVED/'r2_scope_update.json') if (DERIVED/'r2_scope_update.json').exists() else None
    if scope and scope['version']==2:
        frozen=load(ROOT/scope['kbh']['manifest']);frozen_ok=True
        for artifact in frozen['artifacts']:
            for key in ('source','snapshot'):
                if hashlib.sha256((ROOT/artifact[key]).read_bytes()).hexdigest()!=artifact['sha256']:
                    errors.append('frozen artifact changed '+artifact[key]);frozen_ok=False
        frozen_ok=frozen_ok and frozen['sessions']==14 and frozen['steps']==3345 and len(rows)==3345
        iso=load(DERIVED/'r2_iso_field_decisions.json') if (DERIVED/'r2_iso_field_decisions.json').exists() else None
        iso_done=False
        if iso:
            auto_ids={r['order'] for r in iso['automatic_rows']};manual_ids={r['order'] for r in iso_reviews}
            selection=load(RAW/'r2_iso'/load(DERIVED/'r2_iso_index.json')['revision']/'selection.json')
            expected_ids={r['order'] for r in selection['eligibility_check_order']}
            iso_done=(len(auto_ids)==433 and len(manual_ids)==400 and not auto_ids & manual_ids and
                      auto_ids | manual_ids==expected_ids and selection['selected']==iso['selected'] and
                      iso['status']=='complete_under_scope_amendment' and (ROUND/'R2_iso_summary.md').exists())
            for row in iso['automatic_rows']:
                for evidence in [row['success_evidence']]+row['gpu_evidence']:
                    path=ROOT/evidence['file']
                    if hashlib.sha256(path.read_bytes()).hexdigest()!=evidence['sha256']:
                        errors.append('ISO field source hash changed');iso_done=False
                    node=load(path)
                    for token in evidence['pointer'].split('/')[1:]:
                        node=node[int(token)] if isinstance(node,list) else node[token]
                    if node!=evidence['value']:
                        errors.append('ISO field locator mismatch');iso_done=False
            counts['automatically_decided_iso_candidates']=len(auto_ids)
            counts['total_decided_iso_candidates']=len(auto_ids | manual_ids)
            counts['iso_original_quota_shortfall']=iso['shortfall']
        repeat_ready=False;agreement=False
        if (DERIVED/'r2_blind_selection.json').exists():
            blind=load(DERIVED/'r2_blind_selection.json')
            repeat_ready=blind['steps']==150 and len(blind['by_session'])==14
            for pathkey,hashkey in [('packet','packet_sha256'),('key','key_sha256')]:
                if hashlib.sha256((ROOT/blind[pathkey]).read_bytes()).hexdigest()!=blind[hashkey]:
                    errors.append('blind packet/key changed');repeat_ready=False
            packets=load(ROOT/blind['packet'])
            if len(packets)!=150 or len({p['blind_id'] for p in packets})!=150 or set(blind['focus_field_slots'].values())!={50}:
                errors.append('blind150 uniqueness/field quotas');repeat_ready=False
            raw_fields={'step_id','source_lines','thoughts','texts','calls','source_timestamp'}
            if any(set(r)-raw_fields for p in packets for r in [p['current']]+p['context_before']+p['context_after']):
                errors.append('non-raw fields in blind packet');repeat_ready=False
            if (DERIVED/'r2_agreement.json').exists():
                agreed=load(DERIVED/'r2_agreement.json')
                repeat=ROOT/'data/annotations/r2_blind_reviews.jsonl'
                agreement=(repeat_ready and agreed.get('status')=='complete' and agreed.get('steps')==150 and
                           set(agreed.get('fields',{}))==set(blind['repeat_fields']) and repeat.exists() and
                           hashlib.sha256(repeat.read_bytes()).hexdigest()==agreed.get('repeat_sha256') and
                           all(v['n']==150 for v in agreed.get('fields',{}).values()))
        analysis=load(DERIVED/'r2_analysis.json') if (DERIVED/'r2_analysis.json').exists() else None
        draft=(bool(analysis) and frozen_ok and analysis['overall']['steps']==3345 and
               analysis['knowledge']['events']==85 and (ROUND/'R4_analysis.md').exists())
        final_review=load(DERIVED/'r2_analysis_review.json') if (DERIVED/'r2_analysis_review.json').exists() else {}
        bounded=load(DERIVED/'r2_state_bounded_validation.json') if (DERIVED/'r2_state_bounded_validation.json').exists() else {}
        brief=load(DERIVED/'r2_brief_validation.json') if (DERIVED/'r2_brief_validation.json').exists() else {}
        state_units=load(DERIVED/'r2_state_units.json') if (DERIVED/'r2_state_units.json').exists() else None
        state_ready=False
        if state_units:
            unit_ids={u['unit_id'] for u in state_units['units']}
            priority_ids=set(state_units['priority_sample_ids']);random_ids=set(state_units['random_sample_ids'])
            state_ready=(len(priority_ids)==150 and len(random_ids)==50 and not priority_ids & random_ids and
                         priority_ids | random_ids<=unit_ids and len(unit_ids)==state_units['deduplicated_units'])
            members=[h for u in state_units['units'] for h in u['members']]
            excluded=[h['hit_id'] for h in state_units['excluded']]
            if (len(members)!=len(set(members)) or set(members)&set(excluded) or
                    len(members)+len(excluded)!=state_units['legacy_hits'] or
                    len({(u['session'],u['rule']) for u in state_units['units']})!=len(unit_ids)):
                errors.append('R5 unit partition/dedup');state_ready=False
            counts['state_deduplicated_units']=len(unit_ids)
            counts['state_priority_review_target']=len(priority_ids)
            counts['state_random_review_target']=len(random_ids)
        counts['legacy_state_scan_hits']=counts.pop('required_state_scan_hits')
        counts['legacy_reviewed_state_scan_hits']=counts.pop('reviewed_state_scan_hits')
        counts['blind_repeat_target_steps']=150
        counts['blind_repeat_completed_steps']=150 if agreement else 0
        counts['state_new_scope']={'unit':'session x rule','priority_cap':150,'random_sample':50}
        gates={'R1_index_sample_and_hashes':not errors,'R2_amended_export_census':iso_done,
               'R3_frozen_kbh_first_pass':kbh_first_pass_complete and frozen_ok,
               'R3_blind_repeat_prepared':repeat_ready,'R3_blind_repeat_agreement':agreement,
               'R4_draft':draft,'R4_final_analysis':draft and agreement and final_review.get('status')=='final' and
                   final_review.get('analysis_sha256')==hashlib.sha256((DERIVED/'r2_analysis.json').read_bytes()).hexdigest() and
                   final_review.get('report_sha256')==hashlib.sha256((ROUND/'R4_analysis.md').read_bytes()).hexdigest(),
               'R5_sampling_prepared':state_ready,
               'R5_bounded_audit':state_ready and bounded.get('status')=='complete' and bounded.get('random_reviewed_units')==50 and
                                  0<bounded.get('priority_reviewed_units',0)<=150 and (ROUND/'R5_state_tamper.md').exists(),
               'R6_one_page_brief':brief.get('status')=='complete'}
    else:
        gates={'R1_index_sample_and_hashes':not errors,'R2_gpu_eligible_sample':False,
               'R3_kbh_first_pass_complete':kbh_first_pass_complete,'R3_complete_review':False,
               'R3_blind_repeat_agreement':False,'R4_analysis':False,
               'R5_full_scan_and_review':False,'R6_one_page_brief':False}
    report={'updated_at':now(),'status':'errors' if errors else 'in_progress','scope':'current structural provenance/schema/sample checks; incomplete gates explicitly retained, not a completion certificate',
            'counts':counts,'gates':gates,'errors':errors}
    dump(DERIVED/'r2_validation.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
