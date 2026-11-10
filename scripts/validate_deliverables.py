"""Offline integrity audit: source references, schema fields, counts, hashes and artifact links.

This checks the restricted schema actually used here; it is not a general JSON Schema engine.
It does not verify scientific truth or GPU correctness.
"""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote
from collect_sources import ROOT, RAW

REQUIRED=['PROGRESS.md','00_summary.md','T1_trace_inventory.md','T2_codebook.md','T2_trace_analysis.md',
          'T3_knowledge_injection_review.md','T4_pilot_report.md','T5_rsi_bench_notes.md','T6_reward_hacking_catalog.md','T7_base_framework_eval.md']

def main():
    errors=[]; counts={}; source_cache={}
    for name in REQUIRED:
        p=ROOT/'outputs'/name
        if not p.exists() or p.stat().st_size==0: errors.append('missing output '+name)
    schema=json.loads((ROOT/'data/annotations/schema.json').read_text(encoding='utf-8'))
    seen=set()
    typecheck={'string':lambda x:isinstance(x,str),'integer':lambda x:isinstance(x,int) and not isinstance(x,bool),
               'boolean':lambda x:isinstance(x,bool),'number':lambda x:isinstance(x,(int,float)) and not isinstance(x,bool),'null':lambda x:x is None}
    for path in sorted((ROOT/'data/annotations').glob('*.jsonl')):
        rows=[]
        for ln,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
            r=json.loads(line);rows.append(r);key=(r['source'],r['session_id'],r['step_id'])
            if key in seen:errors.append(f'duplicate annotation {key}')
            seen.add(key)
            missing=set(schema['required'])-r.keys();extra=r.keys()-schema['properties'].keys()
            if missing or extra:errors.append(f'{path.name}:{ln} schema fields missing={missing}, extra={extra}')
            for field,value in r.items():
                rule=schema['properties'].get(field,{})
                if 'enum' in rule and value not in rule['enum']:errors.append(f'{path.name}:{ln} invalid {field}')
                if 'type' in rule:
                    types=rule['type'] if isinstance(rule['type'],list) else [rule['type']]
                    if not any(typecheck[t](value) for t in types):errors.append(f'{path.name}:{ln} type {field}')
                if 'minimum' in rule and value is not None and isinstance(value,(int,float)) and value<rule['minimum']:errors.append(f'{path.name}:{ln} minimum {field}')
            raw=ROOT/r['raw_file']
            if not raw.exists():errors.append('missing raw '+str(raw));continue
            if r['unit']=='tool_call':
                if raw not in source_cache:source_cache[raw]=[json.loads(x) for x in raw.read_text(encoding='utf-8').splitlines()]
                original=source_cache[raw][r['source_line']-1]
                blocks=original.get('message',{}).get('content',[])
                calls=[x for x in blocks if x.get('type')=='tool_use'] if isinstance(blocks,list) else []
                if not calls:errors.append(f'{path.name}:{ln} source line is not tool call')
                if r.get('result_line'):
                    result=source_cache[raw][r['result_line']-1]
                    results=result.get('message',{}).get('content',[])
                    if not any(b.get('type')=='tool_result' and b.get('tool_use_id') in {c.get('id') for c in calls} for b in results):errors.append(f'{path.name}:{ln} mismatched tool result')
            elif r['unit']=='episode':
                if raw not in source_cache:source_cache[raw]=json.loads(raw.read_text(encoding='utf-8'))
                eid=re.search(r'id=([^\]]+)',r['source_locator']).group(1)
                if not any(e['id']==eid and e['run_id']==r['session_id'] for e in source_cache[raw]['episodes']):errors.append('bad episode '+eid)
            elif r['unit']=='agent_step':
                if raw not in source_cache:source_cache[raw]=json.loads(raw.read_text(encoding='utf-8'))
                index=int(r['source_locator'].rsplit('/',1)[1]);steps=source_cache[raw]['agent_steps']
                if index>=len(steps) or steps[index]['step_number']!=r['step_id']:errors.append('bad agent_step '+str(key))
        counts[path.stem]=len(rows)
    manifest=[json.loads(l) for l in (RAW/'manifest.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    audited=0
    for r in manifest:
        if r['status']!=200:continue
        p=ROOT/r['path']
        if not p.exists():errors.append('missing snapshot '+r['path']);continue
        if hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:errors.append('hash mismatch '+r['path'])
        audited+=1
    for p in [ROOT/'README.md',*sorted((ROOT/'outputs').glob('*.md'))]:
        body=p.read_text(encoding='utf-8')
        for link in re.findall(r'\]\(([^)]+)\)',body):
            if link.startswith(('http:','https:','#','mailto:')):continue
            target=unquote(link.split('#')[0])
            if target and not (p.parent/target).exists():errors.append(f'{p.name}: broken local link {link}')
        if body.count('```')%2:errors.append('unclosed code fence '+p.name)
        if '\ufffd' in body:errors.append('replacement character '+p.name)
    tasks=json.loads((ROOT/'data/derived/rsi_tasks.json').read_text(encoding='utf-8'))
    if len(tasks)!=37:errors.append(f'expected37 Apple task manifests, got {len(tasks)}')
    evidence=json.loads((ROOT/'data/extractions/evidence.json').read_text(encoding='utf-8'))
    for e in evidence:
        if not (ROOT/e['local_source']).exists():errors.append('missing evidence source '+e['local_source'])
    stats=json.loads((ROOT/'data/derived/statistics.json').read_text(encoding='utf-8'))
    for group,n in counts.items():
        if stats.get(group,{}).get('total')!=n:errors.append('stale stats '+group)
        for key in ('phase','tool','layer'):
            if sum(stats.get(group,{}).get(key,{}).values())!=n:errors.append('denominator mismatch '+group+'/'+key)
    report={'status':'passed' if not errors else 'failed','scope':'offline data/schema/source-line/hash/local-link/count audit; not scientific validation or GPU testing',
            'annotation_counts':counts,'successful_snapshots_hashed':audited,'historical_access_failures':sum(r['status']=='failed' for r in manifest),
            'rsi_tasks':len(tasks),'errors':errors}
    (ROOT/'data/derived/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(bool(errors))

if __name__=='__main__':main()
