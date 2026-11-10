# ISO-Bench证据核验进度（阶段记录）

[实验] 当前确认1份有可靠CUDA完成计时的成功候选，尚未完成最终抽样。以下是本地读取导出文件的结果，不是本机GPU复现；完整索引见[运行索引](../../data/derived/r2_iso_index.json)，逐条理由与定位见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

## 覆盖与缺口

[实验] 正式目录冻结在`Lossfunk/ISO-Bench`的`0a6716bba4361f1ebe9366e1e2a33ffbb913dced`。完整artifact索引有1562个运行目录，实际取得1466份summary：833份导出success、632份error、1份max_steps；96个目录没有已取得summary。success只说明导出记载的agent流程状态，不代表GPU优化有效。来源字段和文件哈希在[索引](../../data/derived/r2_iso_index.json)，抽样框与种子在[selection](../../data/raw/r2_iso/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/selection.json)；[正式目录来源](https://github.com/Lossfunk/ISO-Bench/tree/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs)。

[实验] 已按预先冻结的833个success候选顺序完成资格普查文件的下载尝试及同源重试：取得442份trajectory、248份仅含最终result的输出、139份其他文本输出；3个目录没有非空轨迹/标准输出，另1份trajectory两次访问后仍未取得（候选213）。仅有最终摘要的导出不能补写成逐步工具轨迹。计数见[导出盘点](../../data/derived/r2_iso_execution_inventory.json)，请求/失败见[manifest](../../data/raw/r2_manifest.jsonl)。

[实验] 目前60个候选已有逐条资格判断，确认合格1份；最终`selected`仍为空。不能把下载数量、关键词命中数或summary成功数当成合格样本数。关键词导航之外，新增数字计时导航得到304个候选、811个返回片段，尚未逐一复核；未检出关键词不等于没有GPU测量。该导航由`scripts/r2_iso_measurement_queue.py`生成，原文片段只保留本地。

## 已复核的三个关键区别

| 冻结顺位 | 观察与定位 | 当前处理 |
|---|---|---|
| 84，TRAE / GPT-5 | summary和trajectory均记成功；step17脚本仅在CUDA可用时运行并打印GPU分支，对CUDA张量计时且每轮同步。step18返回两组GPU秒数。 | 计入可靠GPU微基准候选；只测孤立采样函数，使用导入stub，不外推为完整引擎的端到端收益。 |
| 392，TRAE / GPT-5 | step12脚本实际选择CUDA，step15返回设备与两组秒数；两个计时循环均仅用主机时钟，没有区间末同步或CUDA事件。step14只修改正确性判断。 | 确认CUDA执行，但不把主机提交秒数当可靠设备完成测量；不用于补齐可靠GPU测量配额。 |
| 623，TRAE / Sonnet 4.5 | step34明确CUDA不可用；step46脚本将设备回退到CPU，却保留固定的“GPU”行标签；step47打印相应数值。trajectory本身记失败，与summary成功冲突。 | 保留CPU/标签和状态冲突，不计成功GPU测量。 |

[实验] 三例的原始导出分别为[候选84](https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2026-01-23_21-19-19/vllm_core-0005/trajectory.json)、[候选392](https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2026-01-23_21-19-19/vllm_core-0006/trajectory.json)、[候选623](https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/claude-sonnet-45/2025-11-28_02-25-29/vllm_bedrock_sonnet45-0051/trajectory.json)。上述step从1开始，JSON指针的agent_steps索引从0开始；全部精确指针和SHA256保存在资格复核及运行索引。

[论文] PyTorch官方CUDA说明指出设备执行通常异步，未经同步的主机时间可能不准确；文档展示CUDA事件及等待完成的计时方式。这里用它解释计时语义，不声称已核实每份ISO环境的PyTorch版本：[CUDA说明的Asynchronous execution](https://github.com/pytorch/pytorch/blob/v2.11.0/docs/source/notes/cuda.rst)。冻结原文与中文笔记见[API证据笔记](../../data/extractions/r2_state_docs_notes.json)。

## 接下来的核验

[推断] 仍需按冻结顺位复核数字计时及其实际脚本，将设备选择、完成同步、测量对象与导出结局关联，才能确定最终样本和真实缺口。目前不能宣称正式目录绝无其他GPU会话，也不能用CPU或未同步提交计时降低标准凑够4份。第一轮两份API 400保留在原标注中，继续排除于本轮行为统计。
