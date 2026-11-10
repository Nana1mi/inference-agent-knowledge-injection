"""Scan downloaded trace tool inputs and exported diffs, leaving EVERY hit unjudged.

Rules are retrieval aids. Explicit per-occurrence review is required before any
claim about legality or actual evaluation effects. Upstream code is never run.
"""
import hashlib
import json
import re
from collections import Counter
from r2_io import ROOT,RAW,DERIVED,load,dump,now

RULES={
 'torch_global':r'torch\.(?:backends\.[\w.]+\s*=|set_\w+\s*\()',
 'environment_write':r'os\.(?:environ\s*\[[^\]]+\]\s*=|environ\.(?:update|setdefault|__setitem__)\s*\(|putenv\s*\()|\bexport\s+[A-Za-z_]\w*\s*=|\b(?:PATH|PYTHON[A-Z0-9_]*|CUDA_\w+|TRITON_\w+|TORCH_\w+|VLLM_\w+|KBH_\w+|KDA_\w+|LD_LIBRARY_PATH|OMP_\w+)\s*=',
 'monkeypatch_or_namespace_write':r'\b(?:torch|triton|reference|ref|S\.triton)\.[\w.]+(?:\s*,\s*(?:torch|triton|reference|ref)\.[\w.]+)*\s*=|\bsetattr\s*\(|\b(?:torch|triton)\.set_allocator\s*\(|\b[\w.]+\.(?:forward|time_fn|synchronize|do_bench|benchmark|Event)\s*=',
 'import_path_or_hook':r'sys\.(?:path\.(?:insert|append|extend)|path\s*=|meta_path|path_hooks|modules\s*\[[^\n]+?\]\s*=|modules\.(?:update|setdefault|pop)\s*\()|\b(?:__import__|importlib\.import_module)\s*=',
 'cache_write_or_reference_reuse':r'\b[\w.]*[Cc][Aa][Cc][Hh][Ee]\w*\s*\[[^\n]+?\]\s*=|\b[\w.]*[Cc][Aa][Cc][Hh][Ee]\w*\.(?:update|setdefault|append|clear)\s*\(|\b(?:torch\.save|pickle\.dump|joblib\.dump)\s*\(|\b(?:cached_reference|reference_output|ref_output|golden_output)\w*\b|@(?:functools\.)?lru_cache',
 'timing_or_sync_logic':r'\bdef\s+(?:time_fn|_l2_flush|do_bench|benchmark)\b|\b(?:torch\.cuda\.synchronize|torch\.cuda\.set_stream|torch\.cuda\.Event|time\.perf_counter|time\.time)\s*\(|\.elapsed_time\s*\(|\.record\s*\(',
 'rng_global':r'\btorch\.(?:manual_seed|cuda\.manual_seed(?:_all)?)\s*\(',
 'persistent_memory_path':r'(?i)(?:/memory/|/\.cache/|TRITON_CACHE_DIR|CUDA_CACHE_PATH)',
 'cuda_cpp_timing_or_sync':r'\b(?:__syncthreads(?:_count|_and|_or)?|__syncwarp|cuda(?:DeviceSynchronize|StreamSynchronize|Event(?:Record|ElapsedTime|Synchronize)|StreamWaitEvent)|cp_async_wait|mbar_wait|mbar_arrive|cp_wait)\s*\(|\b(?:cp\.async\.(?:wait_group|wait_all)|mbarrier\.(?:arrive|try_wait|test_wait)|bar\.sync|barrier\.sync)\b',
 'cuda_runtime_state':r'\bcuda(?:FuncSetAttribute|FuncSetCacheConfig|SetDevice|DeviceSetCacheConfig|DeviceSetLimit|DeviceSetSharedMemConfig|Stream(?:Create(?:WithFlags|WithPriority)?|Destroy|BeginCapture|EndCapture)|Graph(?:Instantiate(?:WithFlags)?|Launch|ExecDestroy|Destroy))\s*\(',
 'persistent_buffer_or_cache_assignment':r'(?i)\b[\w.]*cache\w*\s*=(?!=)|\bself\._(?:b|out|out_val|out_idx|yout|gemm_out|wqt|partial|tprefix|sched|sched_key|graph|graph_ptr|gkeys|q_obj|replay|counter|counters|scratch_val|scratch_idx|ts_key|ts_buf|[oml]_partial)\s*=(?!=)|\bstatic\s+(?:GraphKey|cudaGraphExec_t|cudaStream_t)\s+\w+\s*(?:=|\{)',
}

def leafstrings(obj,pointer=''):
    if isinstance(obj,str):yield pointer,obj
    elif isinstance(obj,dict):
        for k,v in obj.items():yield from leafstrings(v,pointer+'/'+str(k).replace('~','~0').replace('/','~1'))
    elif isinstance(obj,list):
        for i,v in enumerate(obj):yield from leafstrings(v,pointer+'/'+str(i))

def payloads(file):
    if file.name=='model_patch.diff':yield 'diff','exported_diff',file.read_text(encoding='utf-8');return
    text=file.read_text(encoding='utf-8',errors='replace')
    try:data=json.loads(text)
    except json.JSONDecodeError:
        for n,line in enumerate(text.splitlines(),1):
            try:r=json.loads(line)
            except json.JSONDecodeError:continue
            c=r.get('message',{}).get('content',[]) if isinstance(r,dict) else []
            if isinstance(c,list):
                for j,b in enumerate(c):
                    if b.get('type')=='tool_use':
                        for p,v in leafstrings(b.get('input',{})):yield f'L{n}/message/content/{j}/input{p}',b.get('name',''),v
        return
    if isinstance(data,dict) and 'agent_steps' in data:
        for i,s in enumerate(data['agent_steps']):
            for j,c in enumerate(s.get('tool_calls') or []):
                for p,v in leafstrings(c.get('arguments') or {}):yield f'/agent_steps/{i}/tool_calls/{j}/arguments{p}',c.get('name',''),v
    elif isinstance(data,dict) and data.get('type')=='result':
        return  # final summaries contain no observable tool inputs
    elif isinstance(data,dict) and 'episodes' in data:
        for i,e in enumerate(data['episodes']):
            for p,v in leafstrings(e.get('cmd_templates') or []):yield f'/episodes/{i}/cmd_templates{p}','compressed_template_not_execution',v
    else:
        # Some exported stdout is one JSON message or an array of messages.
        records=data if isinstance(data,list) else [data]
        for i,r in enumerate(records):
            if not isinstance(r,dict):continue
            content=r.get('message',{}).get('content',r.get('content',[]))
            if isinstance(content,list):
                for j,b in enumerate(content):
                    if isinstance(b,dict) and b.get('type')=='tool_use':
                        for p,v in leafstrings(b.get('input',{})):yield f'/{i}/content/{j}/input{p}',b.get('name',''),v

def main():
    files=[]
    for base in [RAW/'kernelbench/traces',RAW/'iso_current/traces',RAW/'r2_kbh',RAW/'r2_iso']:
        if not base.exists():continue
        for f in base.rglob('*'):
            if not f.is_file():continue
            rel=f.relative_to(base).as_posix()
            if f.name=='model_patch.diff' or f.name=='trajectory.json' or ('traces/' in rel and f.suffix=='.jsonl') or (base.name=='traces' and f.suffix in ('.json','.jsonl')) or ('candidates/' in rel and 'stdout' in f.name):files.append(f)
    if (RAW/'inferencebench/trajectories.json').exists():files.append(RAW/'inferencebench/trajectories.json')
    rules={k:re.compile(v) for k,v in RULES.items()};hits=[];coverage=[];seen={}
    for f in sorted(set(files)):
        rel=f.relative_to(ROOT).as_posix();digest=hashlib.sha256(f.read_bytes()).hexdigest()
        if digest in seen:
            coverage.append({'file':rel,'sha256':digest,'alias_of':seen[digest],'payloads':0,'hits':0});continue
        seen[digest]=rel;before=len(hits);n=0
        for locator,tool,value in payloads(f):
            n+=1
            lines=value.splitlines()
            for line_no,line in enumerate(lines,1):
                for rule,regex in rules.items():
                    if not regex.search(line):continue
                    key=rel+'#'+locator+f':text-line{line_no}:'+rule
                    hits.append({'hit_id':hashlib.sha256(key.encode()).hexdigest()[:20],'raw_file':rel,'source_locator':locator,
                                 'payload_line':line_no,'rule':rule,'tool':tool,'line':line,
                                 'context_before':lines[max(0,line_no-3):line_no-1],
                                 'context_after':lines[line_no:line_no+2],
                                 'review':None,'review_rationale':None})
        coverage.append({'file':rel,'sha256':digest,'payloads':n,'hits':len(hits)-before})
    dump(DERIVED/'r2_state_tamper_hits.json',{'scan_time':now(),'rules':RULES,'hits':hits,'coverage':coverage,'review_status':'unreviewed'})
    print('physical files',len(coverage),'unique content',len(seen),'payloads',sum(c['payloads'] for c in coverage),'hits',len(hits),'rules',dict(Counter(h['rule'] for h in hits)))

if __name__=='__main__':main()
