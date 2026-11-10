"""Display unlabelled ISO execution evidence for manual GPU eligibility review."""
import argparse
import json
import re
from r2_io import ROOT,RAW,DERIVED,load

NAV=re.compile(r'cuda|gpu|nvidia|benchmark|latency|speedup|elapsed|seconds|milliseconds|microseconds|\bms\b|\bus\b|perf_counter',re.I)

def main():
    p=argparse.ArgumentParser();p.add_argument('start',type=int);p.add_argument('end',type=int);p.add_argument('--full',action='store_true');p.add_argument('--executions',action='store_true');p.add_argument('--outline',action='store_true',help='All visible calls/errors, without replaying embedded model prompts');p.add_argument('--step',type=int);p.add_argument('--result-limit',type=int,default=2200);a=p.parse_args()
    rev=load(DERIVED/'r2_iso_index.json')['revision'];plan=load(RAW/'r2_iso'/rev/'selection.json')
    for c in plan['eligibility_check_order']:
        if not a.start<=c['order']<=a.end:continue
        folder=RAW/'r2_iso'/rev/'candidates'/c['run_path'];print('\nCANDIDATE',c['order'],c['agent'],c['model'],c['run_path'])
        if not folder.exists():print('not yet downloaded');continue
        traj=folder/'trajectory.json'
        if traj.exists():
            d=load(traj);print('trajectory fields success=',d.get('success'),'steps=',len(d.get('agent_steps',[])),'model=',d.get('model'))
            for i,s in enumerate(d.get('agent_steps',[])):
                if a.step is not None and a.step!=i+1:continue
                calls=s.get('tool_calls') or [];results=s.get('tool_results') or []
                inp=json.dumps(calls,ensure_ascii=False)
                if a.outline:
                    if not a.full:
                        call_summaries=[]
                        for call in calls:
                            args=call.get('arguments') or {}
                            command=str(args.get('command') or '')
                            if len(command)>320:command=command[:60]+' [...] '+command[-260:]
                            path=str(args.get('path') or args.get('file_path') or '')
                            call_summaries.append([call.get('name'),command,path[-100:]])
                        print('STEP',i+1,'pointer',f'/agent_steps/{i}','CALLS',call_summaries,
                              'FEEDBACK',[(r.get('success'),len(str(r.get('result') or '')),
                                           str(r.get('error') or '')[-160:]) for r in results],
                              'ERROR',str(s.get('error') or '')[:400])
                        continue
                    print('STEP',i+1,'pointer',f'/agent_steps/{i}',
                          'calls',len(calls),'results',len(results),'error',str(s.get('error') or '')[:500])
                    for j,call in enumerate(calls):
                        args=call.get('arguments') or {}
                        print(' CALL',j,call.get('name'),'path',args.get('path') or args.get('file_path'),
                              'command',str(args.get('command') or ''),
                              'argument_keys',list(args))
                    for j,result in enumerate(results):
                        print(' FEEDBACK',j,'success',result.get('success'),
                              'result_chars',len(str(result.get('result') or '')),
                              'error_chars',len(str(result.get('error') or '')),
                              'error_end',str(result.get('error') or '')[-350:])
                    continue
                if a.executions:
                    commands=[str(t.get('arguments',{}).get('command','')) for t in calls if t.get('name') in ('bash','execute_bash','shell','run')]
                    if not any(re.search(r'\bpython(?:3)?\s|\bpytest\b|\bnvidia-smi\b|\bncu\b|\bnsys\b',c) for c in commands):continue
                    print('STEP',i+1,'COMMAND',commands if a.full else str(commands)[:600])
                    for j,r in enumerate(results):
                        print('FEEDBACK',j,'success',r.get('success'))
                        for field in ('result','error'):
                            v=str(r.get(field) or '')
                            if not v:continue
                            print(field.upper(),'pointer',f'/agent_steps/{i}/tool_results/{j}/{field}')
                            print(v if a.full else v[:a.result_limit]+('\n[...]\n'+v[-min(600,a.result_limit//2):] if len(v)>a.result_limit else ''))
                    continue
                hits=[]
                for j,r in enumerate(results):
                    values=[(field,str(r.get(field) or '')) for field in ('result','error')]
                    if NAV.search(inp) or any(NAV.search(value) for _,value in values):
                        for field,result in values:
                            if not result:continue
                            lines=result.splitlines();found=[(k+1,line) for k,line in enumerate(lines) if NAV.search(line)]
                            hits.append((j,field,result,found))
                if hits:
                    print('STEP',i+1,'CALLS',inp if a.full else inp[:400])
                    for j,field,result,found in hits:
                        print(field.upper(),'pointer',f'/agent_steps/{i}/tool_results/{j}/{field}')
                        if a.full:print(result)
                        else:
                            for n,line in found[:24]:print(f'  text-line{n}:',line[:500])
                            if not found:print('  (triggered by input; result)',result[:500])
                            if len(found)>24:print('  ...',len(found)-24,'additional matching lines; expand --full')
        else:
            for file in folder.glob('*stdout*'):
                print('STDOUT',file.name,'bytes',file.stat().st_size);value=file.read_text(encoding='utf-8',errors='replace')
                try:
                    parsed=json.loads(value)
                    if isinstance(parsed,dict) and parsed.get('type')=='result' and not a.full:
                        print({k:parsed.get(k) for k in ('type','subtype','is_error','num_turns')},'modelUsage',list(parsed.get('modelUsage',{})))
                        print('FINAL SUMMARY ONLY:',str(parsed.get('result',''))[:min(1600,a.result_limit)])
                    else:print(value if a.full else value[:a.result_limit])
                except json.JSONDecodeError:print(value if a.full else value[:a.result_limit])
            if not list(folder.glob('*stdout*')):print('no trajectory/stdout retrieved')

if __name__=='__main__':main()
