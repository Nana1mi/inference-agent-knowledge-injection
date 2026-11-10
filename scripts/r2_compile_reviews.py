"""Compile explicitly authored per-step review TSV; never infer semantic labels.

TSV columns: step phase tool layer origin source evidence outcome flags use
hypothesis rationale followup component. '-' explicitly means null/no flags.
"""
import argparse
import csv
import hashlib
import json
from r2_io import ROOT,DERIVED,load,dump

PH=dict(zip('EPHCMARWTNO',['探索代码','profile','提出假设','修改代码','测量','接受','回滚','写报告','等待','环境准备','其他']))
TOOL=dict(zip('NSPBKVDJO',['NCU','nsys','torch profiler','端到端 benchmark','kernel benchmark','正确性检查','读源码','查文档','其他']))
LAYER=dict(zip('KFADHPCQXMOU',['kernel','算子融合','attention','调度器','runtime 与 host 开销','并行配置','运行参数','量化','推测解码','测量工具','其他','不可判定']))
ORIGIN={'e':'explicit','i':'inferred','m':'missing'}
SOURCE=dict(zip('pcriu',['profile 数据','读源码','参考实现或 SOTA','模型先验','不可判定']))
EVIDENCE=dict(zip('ynwux',['有','无','数据有误','不可判定','不适用']))
OUTCOME=dict(zip('sfcu',['成功','失败','正确性不过','未测']))
USE=dict(zip('canrx',['照搬','改写适配','读了但没用','读了并明确反驳','不适用']))
COMPONENT=dict(zip('mposak',['miner','profiler','optimizer','selector','accumulation','skills']))

def compile_session(session,allow_partial=False):
    sid=session['session_id'];rawrows=[json.loads(l) for l in (ROOT/session['step_file']).read_text(encoding='utf-8').splitlines()]
    stepmap={r['step_id']:r for r in rawrows}
    path=ROOT/'data/annotations/r2_reviews'/f'{sid}.tsv'
    if not path.exists():return []
    rows=[];seen=set()
    for ln,c in enumerate(csv.reader(path.read_text(encoding='utf-8').splitlines(),delimiter='\t'),1):
        if not c or c[0].startswith('#'):continue
        if len(c)!=14:raise ValueError(f'{sid}:{ln} expected14 columns got{len(c)}')
        step,phase,tool,layer,origin,source,evidence,outcome,flags,use,hyp,rationale,followup,component=c
        i=int(step)
        if i in seen:raise ValueError(f'duplicate {sid} step{i}')
        seen.add(i);g=stepmap[i]
        if flags!='-' and (set(flags)-set('vckst')):raise ValueError(f'bad flags {flags}')
        hyp=None if hyp=='-' else hyp
        if (origin=='m')!=(hyp is None):raise ValueError(f'hypothesis/origin mismatch {sid}:{i}')
        if ('k' in flags)!=(use!='x'):raise ValueError(f'knowledge access/use mismatch {sid}:{i}')
        if hyp is None and (source!='u' or evidence!='x'):raise ValueError(f'no hypothesis but nonnull source/evidence {sid}:{i}')
        r={
            'source':'KernelBench-Hard','unit':'decision_step','session_id':sid,'step_id':i,
            'raw_file':session['raw_file'],'source_locator':'L'+str(g['source_lines'][0])+'–L'+str(g['source_lines'][-1]),
            'source_url':'https://huggingface.co/datasets/Infatoshi/kernelbench-hard-traces/resolve/'+session['raw_file'].split('/')[3]+'/'+session['selection']['file'],
            'source_line':g['source_lines'][0],'result_line':next((x['result']['line'] for x in g['calls'] if x.get('result')),None),
            'candidate_edit':'c' in flags,'phase':PH[phase],'tool':TOOL[tool],'layer':LAYER[layer],
            'hypothesis':hyp,'hypothesis_origin':ORIGIN[origin],'evidence':EVIDENCE[evidence],'outcome':OUTCOME[outcome],
            'turning_point':'t' in flags,'component':COMPONENT[component],'annotation_method':'研究助理逐项复核',
            'annotation_rationale':rationale,'duration_seconds':None,'reasoning_visible':'v' in flags,
            'hypothesis_source':SOURCE[source],'knowledge_access':'k' in flags,'knowledge_use':USE[use],
            'state_tamper_risk':'s' in flags,'source_lines':g['source_lines'],
            'tool_result_lines':[x['result']['line'] for x in g['calls'] if x.get('result')],
            'review_input_sha256':hashlib.sha256(json.dumps(g,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
            'review_pass':'first','knowledge_followup_locator':None if followup=='-' else followup,
            'reasoning_visibility_note':'导出中有可读实质分析或公开理由；不保证内部推理完整' if 'v' in flags else '本步未见实质推理；动作播报、短标题或工具参数不计',
        }
        rows.append(r)
    if not allow_partial and set(stepmap)!=seen:raise ValueError(f'{sid} unreviewed steps {sorted(set(stepmap)-seen)}')
    return sorted(rows,key=lambda r:r['step_id'])

def main():
    p=argparse.ArgumentParser();p.add_argument('--allow-partial',action='store_true');args=p.parse_args()
    sessions=load(DERIVED/'r2_sessions.json');allrows=[];coverage=[]
    for s in sessions:
        rows=compile_session(s,args.allow_partial);allrows+=rows
        coverage.append({'session_id':s['session_id'],'required':s['steps'],'reviewed':len(rows),'complete':len(rows)==s['steps']})
    target=ROOT/'data/annotations/r2_kernelbench.jsonl'
    target.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in allrows),encoding='utf-8')
    dump(DERIVED/'r2_review_coverage.json',{'status':'complete' if all(c['complete'] for c in coverage) else 'partial','sessions':coverage})
    print('explicit reviewed records',len(allrows),'of',sum(s['steps'] for s in sessions),'complete sessions',sum(c['complete'] for c in coverage))

if __name__=='__main__':main()
