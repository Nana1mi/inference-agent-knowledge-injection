"""Summarize the completed KBH metadata/sampling audit without behavioral inference."""
from collections import Counter
from r2_io import ROOT,RAW,DERIVED,ROUND,load

def main():
    d=load(DERIVED/'r2_kbh_index.json');rev=d['revision'];sel=load(RAW/'r2_kbh'/rev/'selection.json');sessions=load(DERIVED/'r2_sessions.json')
    traces=[x for x in d['files'] if x['kind']=='trace'];outcomes=Counter(x['outcome'] for x in traces)
    total=sum(x['size'] for x in d['files']);samplebytes=sum((ROOT/s['raw_file']).stat().st_size for s in sessions)
    body=f'''# R1：完整索引与抽样核验

[实验] 采用[官方数据集元数据](https://huggingface.co/api/datasets/Infatoshi/kernelbench-hard-traces?blobs=true)的siblings与同修订递归树做集合核对；原始响应保存在`data/raw/r2_kbh/{rev}/r2_dataset_info.json`、`r2_tree_basic_0.json`。本轮修订`{rev}`与第一轮相同，旧快照未覆盖。

## 索引与结局

[实验] 共{d['file_count']}个文件，其中{d['trace_count']}份JSONL轨迹；元数据记录总字节{total:,}。全量索引为[data/derived/r2_kbh_index.json](../../data/derived/r2_kbh_index.json)，每个files元素保留原路径、字节/对象哈希、文件名可识别的模型与任务、硬件目录及outcome_evidence。文件名无法识别的模型不强行归类。

[实验] [官方runs表](https://kernelbench.com/runs)按准确run_id联结，仅覆盖{d['leaderboard_rows']}份：success={outcomes['success']}、failure={outcomes['failure']}、unknown={outcomes['unknown']}。success仅表示表格给出可评分数值；FAIL/ERR标失败；未覆盖则未知。root榜单不能替同名子目录文件赋结局，硬件也不能由同名任务推出。表格动态快照在`r2_runs.html`，联结证据逐条保留在outcome_evidence。

## 已预注册后执行的样本

[实验] 种子{sel['seed']}；方案先写入[PROGRESS](../PROGRESS.md)再抽样。GLM在3个已知失败与10个已知成功的框内按3+3分层随机抽样，任务覆盖不足才整体重抽；第一次即满足条件。选中GLM覆盖5个任务。再在共同任务框内随机选择KDA、top-k、MoE三任务各一Claude与一Codex，并补2个不同任务的DeepSeek。这里只对已知榜单结局的条件抽样框描述，不能推广到全部GLM文件。

[实验] 选中14份全部取得，合计{samplebytes:,}字节；未下载完整{total:,}字节数据集。每份的抽样层、结局出处、种子和blob哈希见[selection.json](../../data/raw/r2_kbh/{rev}/selection.json)。同URL连接重置后成功重试保留在`r2_manifest.jsonl`与PROGRESS失败表，没有换样。

| ID | 模型（文件名） | 任务 | 榜单结局 | decision_step数 | 含thinking块的步骤 |
|---|---|---|---|---:|---:|
'''
    for s in sessions:
        x=s['selection'];body+=f"| {s['session_id']} | {x['model_from_filename']} | {x['task']} | {x['outcome']} | {s['steps']} | {s['visible_thinking_steps']} |\n"
    body+='''
## 推理可见性与边界

[实验] 实际导出中6份GLM及2份DeepSeek都有长明文thinking；K09 Claude也有长明文，K10/K12 Codex主要为短标题摘要，K07/K08/K11没有thinking块。结构计数见[r2_kbh_format_audit.json](../../data/derived/r2_kbh_format_audit.json)，不能把thinking块数等同“实质推理可见”标签或完整内部思维。R3逐步结合公开理由判定reasoning_visible，初始要求中“闭源均加密”不作为数据事实。

[实验] 选中14份共3345个decision_step。一个step是工具返回边界间连续assistant记录，保留所有原始行号和tool_use_id配对。提取脚本不生成语义标签；未复核步骤不出现在新增标注中，覆盖状态见[r2_review_coverage.json](../../data/derived/r2_review_coverage.json)。本报告只核验R1，不能表示R2–R6已完成。

[推断] 同题对照控制了优化目标，但没有控制模型版本、设备占用、运行预算、工具环境和日期；R4只能逐任务比较观察分布。榜单最终失败与导出中的中间PASS/计分OK分列，不人为选择较好结局。
'''
    ROUND.mkdir(exist_ok=True,parents=True);(ROUND/'r2_sampling.md').write_text(body,encoding='utf-8');print('KBH sampling report written',samplebytes)

if __name__=='__main__':main()
