# R1：完整索引与抽样核验

[实验] 采用[官方数据集元数据](https://huggingface.co/api/datasets/Infatoshi/kernelbench-hard-traces?blobs=true)的siblings与同修订递归树做集合核对；原始响应保存在`data/raw/r2_kbh/c2c764c8b5a5fdad493592a2fde1055684e0f064/r2_dataset_info.json`、`r2_tree_basic_0.json`。本轮修订`c2c764c8b5a5fdad493592a2fde1055684e0f064`与第一轮相同，旧快照未覆盖。

## 索引与结局

[实验] 共745个文件，其中740份JSONL轨迹；元数据记录总字节615,621,979。全量索引为[data/derived/r2_kbh_index.json](../../data/derived/r2_kbh_index.json)，每个files元素保留原路径、字节/对象哈希、文件名可识别的模型与任务、硬件目录及outcome_evidence。文件名无法识别的模型不强行归类。

[实验] [官方runs表](https://kernelbench.com/runs)按准确run_id联结，仅覆盖103份：success=82、failure=21、unknown=637。success仅表示表格给出可评分数值；FAIL/ERR标失败；未覆盖则未知。root榜单不能替同名子目录文件赋结局，硬件也不能由同名任务推出。表格动态快照在`r2_runs.html`，联结证据逐条保留在outcome_evidence。

## 已预注册后执行的样本

[实验] 种子2026111101；方案先写入[PROGRESS](../PROGRESS.md)再抽样。GLM在3个已知失败与10个已知成功的框内按3+3分层随机抽样，任务覆盖不足才整体重抽；第一次即满足条件。选中GLM覆盖5个任务。再在共同任务框内随机选择KDA、top-k、MoE三任务各一Claude与一Codex，并补2个不同任务的DeepSeek。这里只对已知榜单结局的条件抽样框描述，不能推广到全部GLM文件。

[实验] 选中14份全部取得，合计23,239,934字节；未下载完整615,621,979字节数据集。每份的抽样层、结局出处、种子和blob哈希见[selection.json](../../data/raw/r2_kbh/c2c764c8b5a5fdad493592a2fde1055684e0f064/selection.json)。同URL连接重置后成功重试保留在`r2_manifest.jsonl`与PROGRESS失败表，没有换样。

| ID | 模型（文件名） | 任务 | 榜单结局 | decision_step数 | 含thinking块的步骤 |
|---|---|---|---|---:|---:|
| K01 | glm-5.3 | 02_kda_cutlass | failure | 389 | 229 |
| K02 | glm-5.2 | 06_sonic_moe_swiglu | failure | 180 | 132 |
| K03 | glm-5.3 | 06_sonic_moe_swiglu | failure | 205 | 111 |
| K04 | glm-5.2 | 03_paged_attention | success | 214 | 134 |
| K05 | glm-5.3 | 05_topk_bitonic | success | 287 | 148 |
| K06 | glm-5.2 | 07_w4a16_gemm | success | 192 | 102 |
| K07 | claude-opus-4-8 | 02_kda_cutlass | failure | 292 | 0 |
| K08 | gpt-5.6-sol | 02_kda_cutlass | failure | 180 | 0 |
| K09 | claude-opus-5 | 05_topk_bitonic | success | 561 | 371 |
| K10 | gpt-5.6-sol | 05_topk_bitonic | success | 220 | 109 |
| K11 | claude-opus-4-8 | 06_sonic_moe_swiglu | failure | 96 | 0 |
| K12 | gpt-5.6-sol | 06_sonic_moe_swiglu | failure | 230 | 177 |
| K13 | deepseek-v4-flash-0731 | 05_topk_bitonic | success | 178 | 139 |
| K14 | deepseek-v4.1-flash-1017 | 06_sonic_moe_swiglu | success | 121 | 95 |

## 推理可见性与边界

[实验] 实际导出中6份GLM及2份DeepSeek都有长明文thinking；K09 Claude也有长明文，K10/K12 Codex主要为短标题摘要，K07/K08/K11没有thinking块。结构计数见[r2_kbh_format_audit.json](../../data/derived/r2_kbh_format_audit.json)，不能把thinking块数等同“实质推理可见”标签或完整内部思维。R3逐步结合公开理由判定reasoning_visible，初始要求中“闭源均加密”不作为数据事实。

[实验] 选中14份共3345个decision_step。一个step是工具返回边界间连续assistant记录，保留所有原始行号和tool_use_id配对。提取脚本不生成语义标签；未复核步骤不出现在新增标注中，覆盖状态见[r2_review_coverage.json](../../data/derived/r2_review_coverage.json)。本报告只核验R1，不能表示R2–R6已完成。

[推断] 同题对照控制了优化目标，但没有控制模型版本、设备占用、运行预算、工具环境和日期；R4只能逐任务比较观察分布。榜单最终失败与导出中的中间PASS/计分OK分列，不人为选择较好结局。
