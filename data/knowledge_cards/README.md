# T4候选知识卡（研究材料，尚未证明有效）

全部 `[推断]` 作为干预材料编写；C1与C2应读取**完全相同版本**。当前不是生产优化建议，卡片不能替代测量；硬件/引擎不匹配时先验证前提。正式实验前冻结文件内容和hash，禁止按中间结果改卡。

## K1：先把测量定位到当前瓶颈

- 命题：端到端收益须在同一workload/计时边界确认，逐kernel计时用于定位。
- 来源：[SEIS Fig3、附录E](https://arxiv.org/html/2610.04646v1)；[Together C.3/Table6](https://www.together.ai/together-compiler-paper)。两者均区分GPU工作与完整执行。
- 适用：计时已排除编译/加载且warm-up稳定；记录input/output长度、batch、cache状态。
- 提问：哪个阶段占主导？当前证据来自真实关键路径还是孤立microbenchmark？
- 反证：kernel变快但端到端不变，或收益只在热cache/固定prompt出现。
- 最小probe：交替重复baseline/候选端到端计时，保留每次样本；不要把重叠kernel时长简单相加当墙钟。

## K2：检查host与执行开销，但不预设必须融合

- 命题：大量短kernel时，launch/host开销可能重要；融合或graph是否有效须实测。
- 来源：[SEIS §4.2、Fig3](https://arxiv.org/html/2610.04646v1)、[KernelSeek §5.4/Table3](https://arxiv.org/html/2611.03517v1)。
- 适用：目标后端支持相关graph/执行模式，实际profile显示host空隙或短kernel。
- 提问：时间是否花在kernel之外？更改后跨输入/请求仍正确吗？
- 反证：瓶颈在长GEMM/带宽，或graph捕获/缓存破坏动态状态。
- 最小probe：分段计时+新输入replay；不能缓存旧输出伪装复用。

## K3：把“不能做”的经验作为可反驳命题

- 命题：历史接口/硬件限制需要commit与可执行反例probe，不应永久禁止探索方向。
- 来源：[SEIS §5.1、附录B](https://arxiv.org/html/2610.04646v1) 的错误接口限制与后续重测。
- 适用：当前任务确需突破某项既有假设，不为了形式每轮重测全部经验。
- 提问：这是任务契约、当前实现限制，还是未经测量的判断？哪个最小试验能区分？
- 反证：固定契约确实不允许，或最新实现probe明确失败；应记录失败条件而不是推广成硬件不可能。
- 最小probe：读当前接口并写独立scratch调用；未经数值验证不得进入性能评分。

## K4：正确性同时约束数值、生成与状态

- 命题：固定prompt/选择题或单次PASS不能证明完整引擎语义。
- 来源：[SEIS §6、附录D/F](https://arxiv.org/html/2610.04646v1)、[InferenceBench附录F](https://arxiv.org/html/2607.20468)。
- 适用：所有改变kernel、词表、decode、cache、streaming或math mode的候选。
- 提问：完整词表/EOS/跨请求/真实首token事件是否仍保持？reference是否被候选进程影响？
- 反证：任一隐藏生成/状态probe失败，或只修改评估口径才通过。
- 最小probe：调用外部只读verifier；不能为了对齐reference去改评分进程的math flags。
