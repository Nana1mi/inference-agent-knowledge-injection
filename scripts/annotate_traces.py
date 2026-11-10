"""Transparent structural coding plus explicit analyst overrides. Not an LLM judge."""
import json
import re
from pathlib import Path
from collect_sources import RAW, ROOT

OUT = ROOT / 'data/annotations'
PHASES = ['探索代码','profile','提出假设','修改代码','测量','接受','回滚','写报告','等待','环境准备','其他']
TOOLS = ['NCU','nsys','torch profiler','端到端 benchmark','kernel benchmark','正确性检查','读源码','查文档','其他']
LAYERS = ['kernel','算子融合','attention','调度器','runtime 与 host 开销','并行配置','运行参数','量化','推测解码','测量工具','其他','不可判定']

def structural(e):
    inp = e.get('input') or {}; name = e['tool_name']
    cmd = inp.get('command', ''); path = inp.get('file_path', '')
    desc = inp.get('description', ''); result = (e.get('result') or {}).get('text', '')
    phase, tool = '其他', '其他'
    is_poll = bool(re.match(r'\s*(until |sleep )', cmd))
    is_log = '/tmp/claude-' in path or bool(re.match(r'\s*(cat |tail |grep |sed )', cmd) and '.output' in cmd)
    is_empty = not result or any(s in result for s in ('completed with no output', 'file unchanged', 'shorter than the provided offset'))
    candidate_edit = path.endswith('/solution.py') and name in ('Write', 'Edit')
    shell_edit = bool(re.search(r'(sed -i|cp |python - <<|python3? -c)', cmd)) and 'solution.py' in cmd
    if name in ('Read', 'Grep', 'Glob'): phase, tool = '探索代码', '读源码'
    if name == 'Bash': phase, tool = '探索代码', '读源码'
    if name in ('Write', 'Edit') or shell_edit: phase, tool = '修改代码', '其他'
    if '/memory/' in path or ('memory' in desc.lower() and ('update' in desc.lower() or 'append' in desc.lower())): phase, tool = '写报告', '其他'
    if is_log: phase, tool = ('等待', '其他') if is_empty or result.startswith('Command running') else ('测量', 'kernel benchmark')
    if re.search(r'\bncu\s+(--|uv|python)|\bncu\s+--', cmd): phase, tool = 'profile', 'NCU'
    elif re.search(r'\bnsys (profile|stats)', cmd): phase, tool = 'profile', 'nsys'
    elif re.search(r'torch\.profiler|torch profiler', cmd): phase, tool = 'profile', 'torch profiler'
    elif re.search(r'uv run python (bench_kernels|prof_cumulative)\.py', cmd) or desc.lower().startswith(('measure shape', 'measure cast', 'measure shape0', 'measure shape1', 'measure shape2')):
        phase, tool = 'profile', 'kernel benchmark'
    elif not is_poll and not is_log and name == 'Bash' and re.search(r'(uv run python.*(check\.py|benchmark\.py|bench_quick\.py|tuner\d?\.py|tune\.py)|correctness|smoke test)', cmd + ' ' + desc, re.I):
        phase, tool = '测量', '正确性检查' if 'check.py' in cmd or 'correctness' in desc.lower() else 'kernel benchmark'
    if is_poll: phase, tool = '等待', '其他'
    if candidate_edit: phase, tool = '修改代码', '其他'
    if name in ('TaskCreate', 'TaskUpdate', 'ToolSearch'): phase, tool = '其他', '其他'
    if phase == '探索代码' and any(s in (cmd + path).lower() for s in ('cutlass/include', 'cutlass/examples', 'site-packages')): tool = '查文档'
    layer = 'kernel'
    if '02_kda' in e['session_id']: layer = 'attention'
    if phase == '等待' or phase == '其他': layer = '不可判定'
    if 'graph' in desc.lower() or 'graph' in Path(path).name.lower(): layer = 'runtime 与 host 开销'
    if path and not path.endswith('/solution.py') and name in ('Write', 'Edit') and '/memory/' not in path: layer = '测量工具'
    outcome = '未测'
    if re.search(r'(^|\n|\t)PASS(?:\s|$)', result): outcome = '成功'
    elif 'FAIL:' in result or 'tolerance exceeded' in result: outcome = '正确性不过'
    elif (e.get('result') or {}).get('is_error') or any(s in result for s in ('Traceback (most recent', 'Command timed out', '<tool_use_error>Blocked')): outcome = '失败'
    return dict(phase=phase, tool=tool, layer=layer, hypothesis=None, hypothesis_origin='missing',
                evidence='不适用', outcome=outcome, turning_point=False, component='optimizer' if phase=='修改代码' else 'profiler' if phase in ('profile','测量') else 'accumulation' if phase=='写报告' else 'miner',
                annotation_method='规则初标', annotation_rationale='只按可见工具调用和返回值编码；未推断隐含思维。')

# Reviewed against raw tool inputs/results. Hypothesis wording inferred from edits is explicitly tagged.
OVERRIDES = {
 '02_kda': {
  19: dict(turning_point=True, hypothesis='以 prepare/scan 两 kernel 实现 chunk KDA', hypothesis_origin='inferred', evidence='无', annotation_rationale='首次候选实现；前序有数学原型验证，但未见性能瓶颈数据。'),
  46: dict(turning_point=True, hypothesis='由两 kernel 改为三 kernel 分解', hypothesis_origin='inferred', evidence='有', annotation_rationale='对照事件45已有逐形状计时，源码改为 prepare/state/output 分解；不等于机制已验证。'),
  60: dict(phase='profile', tool='kernel benchmark', evidence='有', annotation_rationale='读取 A/B/C 逐 kernel 实测计时；B 耗时占主导。'),
  61: dict(turning_point=True, hypothesis='预计算 kd/decay，减少 state kernel 内重复计算', hypothesis_origin='inferred', evidence='有', annotation_rationale='结合事件60计时和61–66连续 diff 解读；只确认数据先于编辑。'),
  75: dict(phase='profile', tool='kernel benchmark', evidence='有', annotation_rationale='逐 kernel 计时更新，仍需官方端到端计时验证。'),
  79: dict(evidence='有', annotation_rationale='同时给出数值误差与端到端计时，不能用微基准替代官方得分。'),
  81: dict(turning_point=True, layer='runtime 与 host 开销', hypothesis='用 CUDA graph 减少 host launch 开销', hypothesis_origin='inferred', evidence='有', annotation_rationale='事件80读取计时 harness 后修改 graph 路径；新输入 replay 检查见82/86。'),
  118: dict(phase='profile', tool='nsys', turning_point=True, annotation_rationale='可见 nsys profile 实际启动；非仅提及工具名。'),
  130: dict(turning_point=True, hypothesis='尝试 BF16 替代 TF32 的计算路径', hypothesis_origin='inferred', evidence='有', annotation_rationale='前序有 cumulative 计时，结合130–131源码变更。'),
  171: dict(turning_point=True, hypothesis='减少 Neumann 迭代次数', hypothesis_origin='inferred', evidence='有', annotation_rationale='联合171–175；182展示不同迭代次数误差，189完整检查 PASS。'),
  197: dict(turning_point=True, hypothesis='减少重复指数计算', hypothesis_origin='inferred', evidence='有', annotation_rationale='前序196逐 kernel 计时，197–201改写指数计算。'),
  209: dict(turning_point=True, hypothesis='以矩阵乘法替代 cumsum', hypothesis_origin='inferred', evidence='有', annotation_rationale='结合209修改及217计时；不能把该尝试直接记为成功。'),
  218: dict(turning_point=True, hypothesis='把 cumsum 替代方案移到 output kernel', hypothesis_origin='inferred', evidence='有', annotation_rationale='217前一方案慢，218改另一个 kernel；原 A 路径回退需结合后续源码确认。'),
  266: dict(turning_point=True, hypothesis='调整 kd 布局降低 state 访问成本', hypothesis_origin='inferred', evidence='有', annotation_rationale='261逐 kernel 计时后，266–270转置布局，277/279反馈。'),
  283: dict(evidence='有', outcome='成功', annotation_rationale='完整检查 PASS 和重复官方 benchmark 均可见；成功仅指检查返回。'),
  290: dict(evidence='有', outcome='成功', annotation_rationale='会话末尾保留 PASS 和最终逐形状计时；非本地 GPU 重跑。'),
 },
 '01_fp8': {
  14: dict(phase='测量', tool='正确性检查', evidence='有', annotation_rationale='用 FP8 roundtrip 测数值误差与权重 dtype，属于数值探针，不是性能 profile。'),
  22: dict(turning_point=True, hypothesis='保留 BF16 权重精度，先用 CUTLASS BF16 GEMM 实现', hypothesis_origin='explicit', evidence='有', annotation_rationale='源码注释明确依赖事件14的 dtype/roundtrip 测量。'),
  50: dict(outcome='正确性不过', annotation_rationale='odd-K 形状检查明确报告 tolerance exceeded。'),
  51: dict(phase='测量', tool='正确性检查', evidence='有', annotation_rationale='比较 padding 与不同 reference 的数值差异。'),
  52: dict(phase='测量', tool='正确性检查', evidence='有', annotation_rationale='单独探测进程级 BF16 reduction 开关对参考结果的影响。'),
  53: dict(turning_point=True, hypothesis='改变全局 reduction 开关，使 reference 与候选数值对齐', hypothesis_origin='explicit', evidence='有', layer='runtime 与 host 开销', annotation_rationale='源码注释与事件58记忆明确说会影响 reference；这是评测污染风险，尚未在隔离进程独立复现。'),
  58: dict(turning_point=True, hypothesis=None, hypothesis_origin='missing', evidence='不适用', annotation_rationale='将会影响 reference 的数值开关写入跨会话记忆；不能断言后续会话已继承。'),
  65: dict(turning_point=True, hypothesis='尝试 StreamK 改善负载分配', hypothesis_origin='inferred', evidence='有', annotation_rationale='前序57已有基准计时，61–64读示例后改候选。'),
  90: dict(turning_point=True, hypothesis='按形状选择 skinny split-K 路径', hypothesis_origin='inferred', evidence='有', annotation_rationale='86/89 sweep 数据先于90候选整合。'),
  101: dict(phase='profile', tool='kernel benchmark', evidence='有', annotation_rationale='cast/GEMM/full-forward 分项计时；首次细分性能 profile。'),
  103: dict(turning_point=True, hypothesis='自定义 cast 减少转换开销', hypothesis_origin='inferred', evidence='有', annotation_rationale='101拆分计时后，103–106编辑 cast 路径。'),
  118: dict(turning_point=True, hypothesis='skinny 路径采用 FP32 split-K 输出', hypothesis_origin='inferred', evidence='有', annotation_rationale='117 tuner 数据先于118/119编辑。'),
  142: dict(turning_point=True, hypothesis='缓存临时 workspace 减少分配开销', hypothesis_origin='inferred', evidence='有', layer='runtime 与 host 开销', annotation_rationale='141拆分计时后修改；仅有后续PASS不足以证明跨输入缓存安全。'),
  146: dict(phase='测量', tool='kernel benchmark', evidence='有', annotation_rationale='三次重复计时可见；不是重新运行所得。'),
  153: dict(phase='测量', tool='正确性检查', outcome='成功', evidence='有', annotation_rationale='最终 PASS；不等于隔离 oracle 下通过。'),
 }
}

def kernelbench():
    records = []
    selection = json.loads((RAW / 'kernelbench/selection.json').read_text(encoding='utf-8'))
    for file in sorted((ROOT / 'data/derived').glob('*_events.jsonl')):
        for line in file.read_text(encoding='utf-8').splitlines():
            e = json.loads(line); row = structural(e)
            for task, overrides in OVERRIDES.items():
                if task in e['session_id'] and e['event_id'] in overrides:
                    row.update(overrides[e['event_id']]); row['annotation_method'] = '研究助理逐项复核'
            row.update(source='KernelBench-Hard', unit='tool_call', session_id=e['session_id'], step_id=e['event_id'],
                       raw_file=e['raw_file'], source_locator=f"L{e['source_line']}", source_line=e['source_line'],
                       result_line=(e.get('result') or {}).get('line'),
                       source_url=f"https://huggingface.co/datasets/Infatoshi/kernelbench-hard-traces/blob/{selection['commit']}/{e['session_id']}.jsonl",
                       candidate_edit=(e['tool_name'] in ('Write','Edit') and (e['input'] or {}).get('file_path','').endswith('/solution.py')),
                       duration_seconds=None)
            records.append(row)
    return records

def inferencebench():
    d = json.loads((RAW / 'inferencebench/trajectories.json').read_text(encoding='utf-8')); index = {e['id']: e for e in d['episodes']}
    # Each tuple was reviewed against the published summaries and command templates.
    labels = [
      [('环境准备','其他','其他'),('探索代码','读源码','量化'),('探索代码','读源码','量化'),('测量','端到端 benchmark','推测解码'),('测量','端到端 benchmark','运行参数'),('环境准备','其他','runtime 与 host 开销'),('写报告','其他','运行参数')],
      [('探索代码','读源码','其他'),('环境准备','其他','其他'),('修改代码','其他','量化'),('测量','端到端 benchmark','量化'),('修改代码','其他','量化'),('环境准备','其他','运行参数'),('测量','正确性检查','运行参数'),('接受','其他','运行参数'),('测量','端到端 benchmark','运行参数'),('修改代码','其他','runtime 与 host 开销'),('接受','其他','运行参数'),('环境准备','其他','runtime 与 host 开销'),('环境准备','其他','runtime 与 host 开销'),('等待','其他','不可判定')]
    ]
    records=[]
    for ridx, run in enumerate(d['runs'][:2]):
        for eid, triple in zip(run['episode_ids'], labels[ridx], strict=True):
            e = index[eid]; phase, tool, layer = triple
            records.append(dict(source='InferenceBench atlas', unit='episode', session_id=run['id'], step_id=e['idx']+1,
              raw_file='data/raw/inferencebench/trajectories.json', source_locator=f"/episodes[id={eid}]", source_line=None, result_line=None,
              source_url='https://inferencebench.ai/data/trajectories.json', phase=phase, tool=tool, layer=layer,
              hypothesis=None, hypothesis_origin='missing', evidence='不可判定', outcome='未测',
              turning_point=eid in ('ep_0_3','ep_1_2','ep_1_5','ep_1_9'),
              component='optimizer' if phase=='修改代码' else 'profiler' if phase=='测量' else 'selector' if phase=='接受' else 'miner',
              annotation_method='研究助理逐项复核', annotation_rationale='仅复核官方压缩 episode 摘要及命令模板；不能补全原始工具调用，也不能用 had_eval 或 score 证明正确性通过。',
              candidate_edit=None, duration_seconds=None, upstream_event_count=e['n_events'], upstream_label_source=e.get('label_source')))
    return records

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, rows in [('kernelbench',kernelbench()), ('inferencebench_episodes', inferencebench())]:
        (OUT / (name+'.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
        print(name, len(rows), 'reviewed',sum(r['annotation_method']=='研究助理逐项复核' for r in rows))
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema','title':'优化轨迹编码 v1.0','type':'object',
      'required':['source','unit','session_id','step_id','raw_file','source_locator','source_url','phase','tool','layer','hypothesis','hypothesis_origin','evidence','outcome','turning_point','component','annotation_method','annotation_rationale','duration_seconds'],
      'properties':{ 'source':{'type':'string'}, 'unit':{'enum':['tool_call','episode','agent_step']}, 'session_id':{'type':'string'},
        'step_id':{'type':'integer','minimum':1},'raw_file':{'type':'string'},'source_locator':{'type':'string'},'source_url':{'type':'string','format':'uri'},
        'source_line':{'type':['integer','null']},'result_line':{'type':['integer','null']},'candidate_edit':{'type':['boolean','null']},
        'upstream_event_count':{'type':'integer','minimum':1},'upstream_label_source':{'type':['string','null']},
        'phase':{'enum':PHASES},'tool':{'enum':TOOLS},'layer':{'enum':LAYERS},'hypothesis':{'type':['string','null']},
        'hypothesis_origin':{'enum':['explicit','inferred','missing']},'evidence':{'enum':['有','无','数据有误','不可判定','不适用']},
        'outcome':{'enum':['成功','失败','正确性不过','未测']},'turning_point':{'type':'boolean'},
        'component':{'enum':['miner','profiler','optimizer','selector','accumulation','skills']},
        'annotation_method':{'enum':['规则初标','研究助理逐项复核']},'annotation_rationale':{'type':'string'},'duration_seconds':{'type':['number','null'],'minimum':0}},'additionalProperties':False}
    (OUT/'schema.json').write_text(json.dumps(schema,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__': main()
