# R2：ISO导出字段结案与样本缺口

2026-11-11｜按用户修订停止人工翻找，保留400份既有判断，余433份只读取结构字段。

[实验] 833个候选全部已处理，字段与逐文件SHA256见[自动判定表](../../data/derived/r2_iso_field_decisions.json)。自动处理433份：381份字段报告流程成功，52份trajectory.success=false，与summary成功字段冲突；433份均无受支持的显式GPU测量字段，因此GPU标为unknown，不能解释为全部未用GPU。未扫描工具正文、自然语言摘要或代码关键词补标签。

[实验] 合并既有判断后，480份保留成功流程字段、353份失败；这是不同层级导出字段的状态汇总，不是性能优化成功率。GPU证据状态为332份未测、500份unknown、1份已核可靠GPU完成计时。全部成功流程导出都用于上述元数据统计，逐步行为分析仍以冻结的KBH样本为主。

[实验] 所有可用的合格GPU会话均已选入[selection.json](../../data/raw/r2_iso/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/selection.json)：I01，原顺位84，TRAE/GPT-5。原最低6份会话仍缺5份，4份成功GPU会话缺3份，2类agent/model缺1类；按用户指示如实保留缺口。已有400份人工复核没有推翻、扩大或继续翻找。

[实验] I01只支持孤立采样函数的GPU微基准，不能据此估计ISO中的模型或scaffold行为分布。第一轮两份API400原标注继续保留在独立文件，不合并入本轮KBH行为统计。[原人工证据与I01定位](../../data/annotations/r2_iso_eligibility_reviews.json)，[首轮ISO标注](../../data/annotations/iso_bench.jsonl)。

[论文] ISO-Bench第5.1节表3报告：TRAE/GPT-5在vLLM的True Success为17.9%，定义同时要求命中正确瓶颈和取得可测性能提升；同一配置在SGLang为86.7%，并非全基准统一低成功率。第4.3节说明正式patch评测另外在H100上执行。[论文v1，第4.3、5.1节及表3](https://arxiv.org/html/2602.19594v1#S5.T3)。官方HTML快照保存在data/raw/r2_iso/paper_2602.19594v1.html，获取记录见r2_manifest.jsonl。

[推断] 本次可核的成功GPU会话不足，与论文在vLLM上观察到的低True Success在方向上相符；但导出可观测性、agent流程状态和论文正式patch评分的定义、环境、分母不同，不能把1/833作为论文成功率的复现，也不能把unknown都归失败。论文SGLang结果较高，同样不由本次日志缺口否定。

[实验] 复现：`python scripts/r2_finalize_iso_fields.py`。自动字段白名单、优先级、冲突及unknown原因均在脚本和逐行判定表中；没有执行任何上游代码或GPU实验。
