"""All steps of two ISO-Bench exports, reviewed at agent_step granularity."""
import json
from collect_sources import RAW,ROOT

LABELS={
 'sglang_000_021f76e4':{
  '探索代码':[1,2,3,4,12,13,14,17,18,22,25,30,35,36,37,41,42,43,44],
  '环境准备':[5,7], '修改代码':[6,8,10,11,15,26,38,45],
  '测量':[9,16,27,39,46], '提出假设':[19,20,21,23,24],
  '接受':[28,29,31,32,33,34,47], '写报告':[40], '其他':[48]},
 'sglang_001_09deb20d':{'探索代码':[1,2,3,4,9],'环境准备':[5,7],'修改代码':[6,8],'其他':[10]}
}

def main():
    selection=json.loads((RAW/'iso_current/selection.json').read_text(encoding='utf-8')); rows=[]
    for file in sorted((RAW/'iso_current/traces').rglob('trajectory.json')):
        d=json.loads(file.read_text(encoding='utf-8')); sid=file.parent.name
        local=file.relative_to(ROOT).as_posix();path=file.relative_to(RAW/'iso_current/traces').as_posix()
        source=f"https://github.com/Lossfunk/ISO-Bench/blob/{selection['commit']}/ISO-Bench/state/runs/sglang/{path}"
        for i,step in enumerate(d['agent_steps'],1):
            phase=next(k for k,v in LABELS[sid].items() if i in v);tool='其他';layer='runtime 与 host 开销'
            calls=step.get('tool_calls') or [];results=step.get('tool_results') or []
            content=(step.get('llm_response') or {}).get('content') or ''
            values='\n'.join(str(r.get('result') or r.get('error') or '') for r in results)
            candidate=any(c.get('name')=='str_replace_based_edit_tool' and c.get('arguments',{}).get('command')=='str_replace' and '/python/sglang/' in c.get('arguments',{}).get('path','') for c in calls)
            if phase=='探索代码':tool='读源码'
            elif phase=='测量':tool='正确性检查' if i in (27,46) else 'kernel benchmark'
            if phase in ('其他','环境准备'):layer='不可判定'
            if phase=='修改代码' and not candidate:layer='测量工具'
            outcome='未测'
            if step.get('error') or any(r.get('success') is False for r in results):outcome='失败'
            hypothesis=None;origin='missing';evidence='不适用'
            rationale='逐项复核可见调用、返回与agent文字；不把源码编辑/提交或API状态当独立评分成功。'
            turning=False
            if sid=='sglang_000_021f76e4':
                if i==9:rationale='明确是CPU微基准；不是目标GPU端到端瓶颈证据。'
                if i in (10,11,15):
                    hypothesis={10:'避免被随后覆盖的张量清零分配',11:'在prepare_lora_batch使用empty替代zeros',15:'用zero_替代赋值清零'}[i]
                    origin='explicit';evidence='有' if i in (10,11) else '无';turning=i in (10,15)
                    rationale='可见文字解释与源码修改；前序CPU probe只支持CPU局部操作，不证明GPU服务收益。' if i!=15 else '此处只有可能更快的假设，尚未有该替换独立计时；保留清零语义。'
                if i in (19,20,21,23,24):
                    args=calls[0].get('arguments',{}) if calls else {}
                    hypothesis='审查现有分配/初始化与example diff，寻找可避免操作' if i!=23 else '考虑替换ones相关分配，但需判断是否真的减少操作'
                    origin='explicit';evidence='不可判定';rationale='sequentialthinking可见显式推断，但不自动当数据支撑；不在报告复刻长段思维。'
                if i==27:rationale='自制局部正确性测试返回匹配，不是引擎官方独立门；故不赋整体成功。'
                if i==36:turning=True;rationale='agent意识到相对base的diff含超出其本轮改动的内容，转而比对HEAD~1。'
                if i==39:rationale='综合脚本仍明确输出on cpu，不能推出GPU服务加速。'
                if i==48:rationale='导出末尾API400：tool_use与tool_result配对协议错误；success=false，不能当成候选算法失败。'
            elif i==10:rationale='导出末尾API400：错误tool_result空content；没有候选源码修改及性能实测，success=false。'
            rows.append(dict(source='ISO-Bench',unit='agent_step',session_id=sid,step_id=i,
              raw_file=local,source_locator=f'/agent_steps/{i-1}',source_line=None,result_line=None,source_url=source,
              phase=phase,tool=tool,layer=layer,hypothesis=hypothesis,hypothesis_origin=origin,evidence=evidence,
              outcome=outcome,turning_point=turning,component='optimizer' if phase=='修改代码' else 'profiler' if phase=='测量' else 'selector' if phase=='接受' else 'accumulation' if phase=='写报告' else 'miner',
              annotation_method='研究助理逐项复核',annotation_rationale=rationale,candidate_edit=candidate,duration_seconds=None))
    (ROOT/'data/annotations/iso_bench.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
    print('ISO-Bench',len(rows),'agent_steps, two exported sessions; both API-aborted')

if __name__=='__main__':main()
