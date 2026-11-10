# 11月16日讨论材料：知识注入的首轮研究

2026-11-10完成本轮调研与公开数据分析；T4交付设计，未运行GPU实验。

**初步判断 `[推断]`：研究重点应从“给多少知识”转为“哪个决策点需要哪条可验证知识”。** Together的负消融与VibeServe的正线索并不矛盾：任务、已有能力、知识内容和预算不同。当前最值得测的是固定问题能否促使agent验证假设，以及同内容按需卡与预加载的差别；本轮尚未证明它们有效。[T3综述与原文定位](T3_knowledge_injection_review.md)

## 各任务结论

- **T1**：核查全部起点及补充来源；取得KernelBench原始JSONL、ISO-Bench正式运行JSON和InferenceBench压缩episode，各抽两份导出；项目开源、支持日志、发布完整会话是三回事。[清单](T1_trace_inventory.md)
- **T2**：交付schema与真实示例；KernelBench443次调用（31条逐项复核，其余初标）、ISO58个step与InferenceBench21个episode分开统计；两个kernel样本先实现后细分profile，ISO两例被API400中止且一例只测CPU。不能代表无知识agent偏好。[编码方案](T2_codebook.md)、[分析](T2_trace_analysis.md)
- **T3**：Together原文是“有库相对无库的加速比低25–31%”；6.2×/4.9×是ensemble比较；KernelSeek人工提问结果不能当成自动问题库的已验证收益；整理五个可检验假设。[综述](T3_knowledge_injection_review.md)
- **T5**：37题是10接入、20优化、7回退；全部manifest已解析；评分隔离、guard workload和交替计时值得借鉴。3090仅筛移植候选，改模型/后端后不能冒充官方成绩。[两页笔记](T5_rsi_bench_notes.md)、[逐题硬件附表](T5_task_feasibility.md)
- **T6**：整理词表裁剪、EOS、状态污染、假首token、模型替换与改评分等案例；本地审计另见候选导入时修改全局数值开关、影响reference的风险；尚未独立复现，不能推断作弊意图。[目录](T6_reward_hacking_catalog.md)
- **T7**：SEIS论文harness与项目链接的早期scaffold对应关系尚未核实；VibeSys插口丰富但有额外策略混杂；Apple/Pier更适合借评测契约。最终底座选择**待讨论**。[比较](T7_base_framework_eval.md)
- **T4（可选）**：本机是RTX5080 Laptop 16GB，非目标3090；opencode1.3.3可执行、provider未测。已交协议、四张技术卡及正确性门设计；未安装引擎、未实现/运行评分器，没有pilot结果。[设计报告](T4_pilot_report.md)

## 最有希望的两个假设与下一步

1. **H1 决策点固定问题。** [推断] 不规定优化方向，只要求给出证据和可反驳预测；优先看首改前可定位证据、有效验证循环，防止只增加文字回答。
2. **H2 同内容不同渠道。** [推断] C0目标、C1可查询技术卡、C2正文预加载；同agent/模型/底座/工具/预算，记录实际读取和采用。区分熟悉任务与陌生API，避免把内容差异当渠道差异。

[推断] 在团队指定3090/固定mini-sglang版本上，先做原版与独立verifier烟测，再按3个seed块随机条件顺序，每条件3会话、每会话45分钟；C0–C2共6.75h agent时间，评分准备另计。样本只看流程与初步信号，不宣称显著优胜。reference在独立干净进程生成；评分脚本在agent目录外，每次从只读副本恢复；全词表logits、生成decode、EOS、跨请求状态全部门控后才记有效性能。完整协议见T4。

## 需要团队回答

- 框架代码和已有trace能否供本课题使用？同agent/引擎/硬件的自有trace更能支持受控比较。
- 实际硬件、模型、workload与SGLang/mini-sglang版本是什么？是否有可用3090或同等指定实验环境？
- agent harness是什么？GLM用哪个provider/协议、哪个固定模型snapshot、什么预算接入？
- 知识注入以最终有效加速比、同收益所需轮数/时间、失败率还是正确性通过率为主指标？允许哪些数值/精度变化？
- 优先研究miner、optimizer还是accumulation？是否接受先做短问题干预，底座如何冻结？

## 阻塞与边界

部分原始trace仅作者声明公开但未定位；若干下载连接中断、Semantic Scholar限流，均记录URL/错误/时间。未恢复来源不编造数据；规则初标尚无独立复标，压缩episode不能还原原始调用；没有人类对照轨迹，不能定量比较人机流程。T4实测及评分器实现未完成。复现入口 [README](../README.md)、完整过程/异常 [PROGRESS](PROGRESS.md)。

方法使用literature-review、paper-lookup、hypothesis-generation技能，工具来源及最新元数据见T3末节；所有外部数字的URL/章节和证据限制在各详细报告，不作为本地实验成绩。
