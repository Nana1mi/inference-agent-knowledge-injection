# 推理引擎知识注入：首轮研究交付

从 [讨论摘要](outputs/00_summary.md) 开始；范围、异常与缺口见 [进度](outputs/PROGRESS.md)，任务原文见 [PLAN](PLAN.md)。中文报告均在 `outputs/`。

第二轮正在进行：已完成14份KernelBench-Hard轨迹的抽样与文件校验，逐步复核1741/3345步，第二轮分析和简报尚未完成。抽样见 [第二轮抽样说明](outputs/round2/r2_sampling.md)，完整状态见 [校验记录](data/derived/r2_validation.json)；该记录不是完成证明。

本轮完成公开材料核验、可得轨迹的描述性编码、知识注入综述、Apple基准分析、评测规避目录和底座比较。**T4仅设计，无本地GPU优化结果。** 所有framework建议为待讨论；未安装/运行外部框架、未调用付费agent、未向外部发送团队消息。

## GitHub 发布范围

公开仓库包含本研究的报告、脚本、标注、统计和来源/抽样清单，以及报告所需的只读硬件/CLI版本记录。第三方论文全文、PDF、下载的仓库文件、原始会话及其派生原文副本保留本地，不随仓库再分发。报告中的原始来源链接仍可用于核验。

克隆仓库后可运行 `python scripts/restore_sources.py`，按已保存的官方URL和SHA256恢复原始文件；`--limit 1`可先小规模检查。来源内容若变化，脚本保存为`.changed`并记录差异，不冒充冻结快照。部分动态页面可能无法逐字节恢复。下文的离线重建/完整快照校验以所需来源已恢复为前提；已发布的validation.json是原研究工作区的校验记录。

## 目录

- `data/raw/`：官方原始响应、论文HTML/PDF、仓库文档、公开会话；`manifest.jsonl`记录URL、时间、许可、SHA256和失败。
- `data/derived/`：提取的事件、统计、37题manifest索引和环境核查。不是原始实验数据。
- `data/annotations/`：编码schema及JSONL，明确区分规则初标和逐项复核、tool_call和episode。
- `data/extractions/`：文献证据ledger及Together PDF精确页码。
- `data/knowledge_cards/`、`data/experiments/`：未执行pilot的候选干预材料和协议。
- `scripts/`：可复现采集/提取/统计/校验脚本；不执行下载的第三方代码。

## 本地重建（不联网、不使用GPU）

Python 3.11+，统计/编码脚本只依赖标准库。本机用Python3.13运行；Windows若缺时区数据库需安装tzdata。以下按顺序运行：

```text
python scripts/prepare_traces.py
python scripts/annotate_traces.py
python scripts/annotate_iso.py
python scripts/analyze_traces.py
python scripts/build_codebook.py
python scripts/build_trace_report.py
python scripts/inspect_rsi.py
python scripts/build_rsi_appendix.py
python scripts/build_evidence.py
python scripts/validate_deliverables.py
```

报告正文的原文核验和逐项判断不可由规则脚本代替。初标频率不是人工双人标注真值；无工具耗时的记录不估计时间占比；公开会话中的PASS不表示本机GPU复现。

## 重新采集

需要公开网络。采集函数对已存在文件复用快照，错误只记录不采用镜像。URL/版本与选择规则写在脚本和每源selection里；要取新版本请使用新目录保存，避免覆盖研究冻结快照。未声明许可的材料仅作本地研究，不假设可再分发。

```text
python scripts/collect_sources.py --papers
python scripts/collect_repositories.py seis inferencebench rsi vibesys iso iso_data seis_scaffold
python scripts/collect_supplement.py
python scripts/collect_traces.py
python scripts/inspect_sources.py
```

额外站点/官方小文档使用 `collect_sources.py URL RELATIVE_PATH`、`complete_metadata.py`、`collect_final_docs.py`。ISO的递归树会截断，必须参考 `collect_iso_release.py` 的浅层遍历，不可将截断列表当完整仓库。发现式web检索及Semantic Scholar限流见 [SEARCH_LOG](outputs/SEARCH_LOG.md)。

Together PDF文本/所检查的页图由 `python scripts/extract_pdf.py` 重建，需要系统Poppler工具；不影响已经保存文本上的统计重建。只读环境探测用 `python scripts/check_environment.py`，不会启动优化或读取凭据。

## 许可与方法

上游代码、数据、论文各自许可不同，见manifest和来源LICENSE/data card；本目录没有统一替上游授予权限。不要把公开网页等同开放许可，也不要把API返回空/失败等同论文或轨迹不存在。

本研究使用literature-review、paper-lookup、hypothesis-generation技能的核验/设计流程；引用的软件方法来源为 [Scientific Agent Skills](https://arxiv.org/abs/2609.00065)，2026，当前v2；不是本课题的效果实验样本。
