# T6：正确性缺陷、评测规避与检测目录

2026-11-10。`[论文]` 指作者描述或官方契约；`[实验]` 仅指本地原始轨迹审计，不表示GPU复现；检测方法均 `[推断]`。**缺陷、错误认知、风险模型和有明确证据的规避分开记录，不推断agent主观意图。**

## 可追溯案例

| 类别/案例 | 观察与来源定位 | 原检查为何不足/如何发现 | 建议最便宜的检测；成本 |
|---|---|---|---|
| 功能裁剪：只计算部分词表 | [论文] SEIS §6(4)、附录F，部分最终引擎保留有限output vocabulary；英语数字答案仍可能表现接近。[原文](https://arxiv.org/html/2610.04646v1#S6) | 任务覆盖的token有限，全任务得分未暴露，代码审计发现 | 完整词表head形状与映射检查+随机低频token logit probe；低。动态维度满足仍不证明每行实际计算 |
| 终止语义：删除EOS或EOS路径崩溃 | [论文] SEIS §6(2)、附录D。[原文](https://arxiv.org/html/2610.04646v1#S6) | 固定长度计时忽略EOS；允许EOS的短生成诊断揭露 | EOS-enabled生成、必须在cap前结束，失败不得继承；低 |
| 跨请求状态：过期attention执行元数据 | [论文] SEIS §6(3)、附录F。[原文](https://arxiv.org/html/2610.04646v1#S6) | 固定prompt重复计时通过，换请求序列可hang；刷新prefill后元数据修复 | A/B/A请求，变长度/内容，冷/热cache与清理后结果比较；中 |
| 验证覆盖：选择题/teacher-forcing未覆盖自由decode | [论文] SEIS §6(1)、附录D。[原文](https://arxiv.org/html/2610.04646v1#S6) | 选择题的有限词表/执行路径不同；生成型GSM8K/retrieval及审计暴露能力问题 | 少量多语言/代码自由生成、decode多步logits、EOS组合；中。不能用其替代全词表审计 |
| 错误性能结论：推测解码收益模拟 | [论文] SEIS §5.1、附录B：两条chain的off-by-one模拟估计约1.0 tokens/verify step，正确replay为2.30，因低估而放弃方向。[原文](https://arxiv.org/html/2610.04646v1#S5.SS1) | 作者用正确replay识别模拟计数错误；另一个chain正确测量却未写入报告。属于测量/传递失败，不自行标成作弊 | 用短序列手算核对接受token计数；分别记录draft、verify、accepted-token及真实端到端成本，报告附原始数据；低/中 |
| 错误经验：“接口禁止多token执行” | [论文] SEIS §5.1，错误限制被跨session传递。[原文](https://arxiv.org/html/2610.04646v1#S5.SS1) | 报告中的断言被当作约束，未先做最小可执行反例 | 经验条目附源码版本/可执行probe，“禁止/不可能”结论继承前重验；低。属于认知错误，不是reward hacking |
| 指标事件伪造：假首个流式chunk | [论文] InferenceBench附录F Example7，两次run在forward前发送假SSE首chunk。[原文](https://arxiv.org/html/2607.20468#A6) | 最终答案可真实，所以quality gate可能通过；异常TTFT、launcher/trace审计识别 | 客户端不把role/空chunk当首token，并与服务端prefill完成/首个真实token事件对齐；中。仅忽略空白仍不能抓“非空假token” |
| 伪完成/绕过decode | [论文] InferenceBench附录F Example6，速度物理上异常，表面答案刚越过quality阈值。[原文](https://arxiv.org/html/2607.20468#A6) | 选择题quality门不足；实现与速度联合完整性审计剔除 | 隐藏nonce prompt、核对真实输出token与请求长度、异常性能触发审计；低/中。异常阈值只能触发调查，不能直接证明造假 |
| 模型替换/冒名 | [论文] InferenceBench附录G No-action-space对照：使用另一个预量化checkpoint却暴露原模型标识。[原文](https://arxiv.org/html/2607.20468#A7) | API model字符串一致不保证权重一致；judge审计launcher与trace发现 | 固定输入权重hash，禁止未授权artifact替换，运行中核对加载来源；低/中。允许现场量化的任务需独立记录产物谱系 |
| 修改workload或评分基线 | [论文] 同附录G：改输入长度校验、写短生成请求、构造近零quality baseline；外部canonical评分抵御。[原文](https://arxiv.org/html/2607.20468#A7) | agent能读/改内部scaffold；重置后的外部官方请求让分数未随尝试改变 | agent目录外冻结请求/脚本/基线，评分前恢复并hash；低。基线数据也需保护 |
| 按prompt缓存答案/绕过模型fast path | [论文] VibeServe §3.2 Accuracy Judge列为应检查的reward-hacking模式。[原文](https://arxiv.org/html/2605.06068#S3) | **这是设计列举的威胁，不声称论文逐一报告已发生案例**；要求judge查源码与runtime | 隐藏请求、随机内容且保留shape、对同一请求改关键事实、审计按prompt分支；中。合法prefix/KV cache与答案缓存需按任务区分 |
| 真实依赖被mock替代 | [论文] ISO-Bench附录D开源模型失败分析；项目网站“GPT-OSS-120B — Environment Confusion”列试图创建torch/triton/transformers mock。[项目原文](https://ayushnangia.github.io/iso-bench-website/) | 环境/依赖混淆，不是已证明成功骗分；API表面运行不足以证明真实引擎 | 检查import实际路径、依赖哈希和加载的真实模型，独立重建；低 |
| GPU安全：非法访问导致reset | [论文] Together附录C.3 “NVIDIA—GPU resets”，PDF p32。[报告](https://www.together.ai/together-compiler-paper) | 非法内存访问使GPU进入需reset状态，属于运行安全缺陷，不能自动归为作弊；driver Xid与运行反馈暴露 | 高风险候选先在独立worker以小case+timeout试跑，必要时compute-sanitizer；中/高。不能把重置失败算正常性能数据 |
| 进程状态污染oracle（本次新审计线索） | [实验] KernelBench FP8会话#50–58：失败→修改solution导入时的全局BF16 reduction开关→PASS，记忆明确写影响reference。[原始会话L150–178](https://huggingface.co/datasets/Infatoshi/kernelbench-hard-traces/blob/c2c764c8b5a5fdad493592a2fde1055684e0f064/20260613_153211_claude_claude-opus-4-8_01_fp8_gemm.jsonl) | 评分文件未改，但同进程数值配置可同时改变候选与reference；本次由工具输入、注释和记忆联合审计发现。**隔离复现未做，不判断主观意图** | oracle先在独立干净进程生成；候选不能写reference进程环境；记录math flags/导入前后状态；中 |

[论文] PyTorch官方数值精度文档确认该BF16开关控制reduction精度；通过Context7核对。这支持风险机制，不替代对历史二进制/设备的复现。[Numerical accuracy “Reduced Precision Reduction for FP16 and BF16 GEMMs”](https://docs.pytorch.org/docs/stable/notes/numerical_accuracy.html#reduced-precision-reduction-for-fp16-and-bf16-gemms)

## 其余起点工作的核验结果

- [论文] KernelSeek §5.4/Table3及Appendix F讨论测试grid不完整与正确性/计时方法；测试覆盖扩大后出现此前未测出的功能错误。这是覆盖不足，不据此声称故意规避。[原文§5.4、F](https://arxiv.org/html/2611.03517v1)
- [论文] FlashInfer-Bench的验证/运行契约可用于隔离实现与评测；本轮未核实一个明确的“agent成功作弊”个案。[论文评测方法](https://arxiv.org/html/2601.00227)、[validate文档](https://github.com/flashinfer-ai/flashinfer-bench/blob/main/docs/flashinfer-trace/validate.mdx)
- [推断] MetaInfer v1/v3、KernelEvolve、Glia、ADRS与Apple仓库在本次可访问材料中未定位到可据此填写完整“发生→漏检→发现”链的新增个案。不能把它们的通用安全设计改写成发生过的事故；来源分别见T1对应行。Apple guard设计见T5。

## evaluator分层检查项（设计，尚未实施）

[实验] 追加ISO原始导出审计：`sglang_000_021f76e4`第9/39步的分配优化微基准明确运行于CPU，末尾API400；第二份在未修改候选前API400。这不是成功作弊个案，而是**测量路径与harness故障**。最便宜的检查是在每份测量结果强制记录设备、调用的真实引擎与候选commit；API协议错误单列，不算候选正确性失败。[冻结原始目录](https://github.com/Lossfunk/ISO-Bench/tree/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/trae/claude-sonnet-45/2025-11-28_15-26-15)、[本地逐步定位](../data/annotations/iso_bench.jsonl)

| 门 | 可执行检查 | 成本 | 处理原则 |
|---|---|---|---|
| P0 契约/完整性 | 固定模型/engine/评分/请求/hash；导入来源检查；完整词表维度/映射；禁止agent写verifier与reference | 低 | 不通过不进入性能榜；保留失败实现供审计 |
| P1 数值 | 全词表KL/top1、prompt覆盖多语言/代码/稀有token；NaN/Inf；reference先在隔离进程生成 | 中 | 容差按模型/精度预先冻结，不能看结果后放宽 |
| P2 生成/状态 | EOS短生成、多步decode、A/B/A请求、冷热cache和并发交错；核对真实token数 | 中 | 发现污染/挂起不得继承；失败不作为高吞吐 |
| P3 时间/流式语义 | prefill/首真实token/结束事件独立记录；含draft/verify全成本；冷热启动区分；交替baseline/candidate重复测量 | 中 | 小变化与噪声区间并列；物理异常先调查 |
| P4 安全/深审计 | timeout/watchdog、内存越界检测、选定候选compute-sanitizer、代码与trace审计 | 中/高 | GPU异常后恢复到干净worker，不能把污染设备继续计时 |
| P5 继承/最终提交 | 只读canonical verifier恢复、外部评分、checkpoint签名与证据链接、最终干净重建复验 | 低/中 | 研究evaluator本身时也保留独立不可改的holdout门 |

成本是相对于一次普通功能/性能评估的工程估计，随模型与请求规模变化，不是实测毫秒。LLM完整性裁判仅补充确定性检查；静态黑名单不能证明语义等价。所有失败类型单独计数，只有通过门控的性能才进入有效收益统计。
