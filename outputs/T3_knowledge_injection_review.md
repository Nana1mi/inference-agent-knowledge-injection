# T3：知识注入的证据、边界与可检验假设

截止：2026-11-10；范围综述，单研究助理筛选，未做独立双人筛选、注册或meta-analysis。`[论文]` 包含作者官方报告；`[推断]` 包含本研究的分类、解释和设计；本轮没有知识注入干预实验。来源身份/版本见 [paper_index.json](../data/raw/paper_index.json)，下载和检索快照见 `data/raw/`；提取表见 [evidence.json](../data/extractions/evidence.json)。

## 方法与纳入边界

[推断] 问题：固定agent、任务、硬件和评估预算时，外部知识的内容、形态与进入时机怎样影响探索、验证与正确性？先逐项核验PLAN的官方论文/项目/代码，再以关键词检索2025–2026年的 coding-agent context/RAG/skills/memory/ablation/context length。发现性搜索使用web索引，身份与结论回到arXiv全文、作者官方报告和仓库核验。搜索式、日期及快照见 [检索记录](SEARCH_LOG.md)。这不是穷尽的系统综述；没有据搜索引擎排名排除潜在反例。

对补充研究只纳入有明确对照或消融的全文；纯工具介绍、社区经验、只有摘要无法检查对照的研究不进入效果证据。PLAN指定但没有知识消融的工作仍列为**架构/行为线索**，不冒充知识因果证据。ACE的AppWorld结果属于相邻agent领域；Context Rot属于受控长上下文任务，不能直接外推到引擎优化。

## 原始起点研究的比较表

下表“进入组件”是 `[推断]` 的统一映射，其余机制/结果是 `[论文]`。未报告意味着本次定位的正文没有可引用的独立效果量，不等于证明没有效果。

| 工作、原文定位 | 知识、形态、来源/粒度 | 时机 → 组件 | 对照与效果 | 证据边界 |
|---|---|---|---|---|
| [Together](https://www.together.ai/together-compiler-paper) §4.4 p10、C.2 pp27–29、Fig.5 | 专家kernel配方/代码/论文摘要/厂商文档；图组织Markdown+YAML；硬件/模型特定 | 导航知识库；另有预置专家策略 → miner/optimizer/accumulation | 有库在12h时的加速比**相对无库低25–31%**；朴素目标ensemble 6.2×、专家分工ensemble 4.9×（10 trials） | 不是“移除后提高同一百分比”；不是单agent 6.2×对4.9×。知识库和策略是不同消融，不能合并解释 |
| [SEIS](https://arxiv.org/html/2610.04646v1) §3.3、§5、附录C | agent报告、代码和经验；代码库/模型特定 | 跨session加载/跨chain同步 → accumulation/miner/selector | 链式积累优于独立尝试；错误接口限制也会继承 | 同时继承代码和报告，不能分离“文本知识”的效应；会话/同步链相依；不是规范随机多次重复 |
| [KernelSeek](https://arxiv.org/html/2611.03517v1) §2.3–2.5、§5.3、§6 | 人类问题、后提炼问题库/skill；通用GPU方法+架构checklist | 停滞/声明上限/测量决策点提问 → miner/profiler/optimizer | 同任务工具丰富自主baseline约0.50×FA3，提问引导路径1.13×，见摘要/§5.3 | 每臂单run、前端/人类引导/先前工作混杂；自动问题库替代人的固定四臂实验尚未执行，不能声称自问已获同样收益 |
| [InferenceBench](https://arxiv.org/html/2607.20468) §5、No-action-space prompt ablation/Table19 | 初始action-space枚举、工具/评估协议；人写运行规则 | 预加载 → miner/selector/skills | 原论文169/180最终用vLLM；移除action-space的对照对不同模型影响不同并出现完整性违规 | 有协议对照但不是纯知识库消融；93.9%只属原论文main pool，不套到更新网站 |
| [ISO-Bench](https://arxiv.org/html/2602.19594) §5、人工分析与附录 | 任务、代码、优化位置和scaffold；人类commit作参照 | 初始任务+交互工具 → miner/optimizer | 定位正确但实现失败，scaffold影响明显；未提取独立知识注入效应 | 本文的17.9%等数值属于其成功标准和分析集合，不能作为所有agent通用率 |
| [VibeServe](https://arxiv.org/html/2605.06068) §3.3、§4.3、附录B | 成熟引擎源码/研究提炼的分层skills，含兼容性与工具指导；硬件/引擎特定 | 按需技能指导 → miner/profiler/optimizer | no-skill约35轮停在1,100tok/s，full在60轮/25h达到约10k；Scenario A/同一agent设置 | 对照支持此pipeline中的skills重要，但达到轮数/累计时间不同；不拿吞吐比当通用纯知识收益 |
| [MetaInfer v1](https://arxiv.org/html/2607.12875v1) 方法/实验；[v3](https://arxiv.org/html/2607.12875v3) 方法/实验 | v1知识式SKILL toolbox；v3转为模型/硬件协同图搜索 | v1规则/知识指导；v3路径选择 → miner/selector | 版本标题与方法已改变，未提取可比的独立知识消融效果 | 不能把v3的结果背书给v1“仅凭知识”主张；版本关系本身不等于方法复现 |
| [KernelEvolve](https://arxiv.org/html/2512.23236) §3.2.3–3.2.4、§5 | 硬件约束、专有API、优化示例；专家资料/MTIA特定 | 检索增强prompt合成；错误/利用率触发查询 → optimizer/profiler | 作者述无MTIA文档会生成GPU式Triton导致失败，检索后能正确实现；未定位等预算知识消融的数值表 | 支持“补齐未知API”的必要性线索；生产整体加速不能全部归因RAG，不与Together做跨工作因果比较 |
| [FlashInfer-Bench](https://arxiv.org/html/2601.00227) 系统设计/评测章节 | kernel定义、workload、参考与解决方案格式 | 任务契约/验证 → evaluator/optimizer | 标准化评估与接入流程，非知识注入对照 | 能作为干净验证器设计来源，不能提供注入收益量 |
| [Glia](https://arxiv.org/html/2510.27176) 系统设计/实验 | 假设、实验、反思及多角色流程；agent自身经验 | 迭代反思 → miner/optimizer/accumulation | 存在系统组件比较；本轮未提取保持其他部分不变的外部知识效果量 | “模拟研究流程”不是证明所有反思文本有用 |
| [ADRS](https://arxiv.org/html/2510.06189) 系统研究方法/实验 | 程序搜索与可执行评估反馈 | 候选→验证→保留 → optimizer/selector | 提供验证器适用性方法依据；非领域知识注入对照 | 可验证性是任务前提，不保证评价目标完整 |
| [Apple RSI](https://github.com/apple-aiml-research/ml-rsi-inference-bench) README、tasks | 冻结引擎/任务规范/独立verifier | 任务与评估约束 → skills/evaluator | 仓库未定位知识消融论文；README论文仍为coming soon | 是可借鉴的benchmark工程，不充当注入正负效果证据 |

## 补充对照研究

| 研究/原文定位 | 对照与结果 `[论文]` | 对本课题的意义 `[推断]` 与局限 |
|---|---|---|
| [Evaluating AGENTS.md](https://arxiv.org/html/2602.11988) 当前版本摘要、§4–5/Tables3/6 | 无文件/LLM生成/开发者提供；总体未见稳定成功收益，平均成本增逾20%；代理遵循指令并增加探索/测试 | 服从与多做动作不等于最终收益；仓库概述可能重复已能读到的信息。需保留文件来源差异，不沿用早期版本宣传数字 |
| [Two-Agent Ablation](https://arxiv.org/html/2607.27250) §3、§4 | none/always_on/selective，288个可评正确性cell；correctness未出现可测改善（作者只支持一定等效界限），效率用291个完成run | selective的知识语料有时比always_on更广，内容与渠道不完全正交；不能把统计不显著解释成严格零效应，任务难度带也因agent而异 |
| [When Instruction Files Go Stale](https://arxiv.org/html/2611.09802) 摘要、Results/Tables | 同代码同任务下stale/corrected/removed；22维护任务、732轨迹；过时测试指令约增加2个工具调用，其余案例未检出差异 | 版本不符有可测过程成本，但效应不是在所有类型错误中成立；最终成功率可能遮住恢复成本 |
| [CODESKILL](https://arxiv.org/html/2605.25430) §4、Table2 | 冻结下游agent，比多粒度skill提取、演化、维护；提取37.88→加演化39.53→完整维护40.35平均pass rate | 技能库质量/去冗余可优于直接堆历史；这含训练出的管理策略，不能当作人工写几张卡就必获同样改善 |
| [Demystifying Agent Skills](https://arxiv.org/html/2608.14036) §3–4、Table1、Fig3 | 对同源经验的workflow memory与skill做受控比较；matched skills高6.06个百分点；候选池5→100时actual-use precision平均29.6%→3.3%，成功率并未随之下降 | 表达和检索是不同瓶颈；检索命中/调用本身不是知识使用的充分指标。模型配对在RQ4改变，不能把跨RQ绝对值直接比较 |
| [ACE](https://arxiv.org/html/2510.04618) §4.6/Table3、A.5 | Generator/Reflector/Curator，增量更新和迭代精炼组件对照；反馈质量不足时适应也可能退化（Table2） | 保留可追溯的局部经验优于无约束重写是候选设计；AppWorld/领域任务并非引擎优化，无单独可归因给检索的统一效果量 |
| [Context Rot](https://research.trychroma.com/context-rot) Experiments、Limitations | 检索/重复词/LongMemEval等控制长度与干扰的任务，随输入增长可靠性下降 | 支持上下文负担的可能机制；不证明Together负收益就由token长度造成，也没有coding-agent的直接收益量 |

纯RAG在**推理系统优化agent**中的独立、等内容、等预算对照仍是本次检索的证据缺口；不以普通代码补全或生产部署宣传代替。

## 分类框架

[推断] 对每张知识卡至少记录四维：

- **时机**：主动预加载、被动查询、决策点提问、事后反思；另记是否每轮重复和检索触发条件。
- **形态**：原始文档、提炼规则、带证据/反例的观点、可执行代码、问题。原始轨迹不能直接当作已验证规则。
- **来源**：人类专家、论文/厂商规范、agent历史；带原文URL、commit、测量工作负载和可信状态。
- **粒度**：通用方法论、硬件特定、模型特定、代码库特定；强制标记不适用条件与失效版本。

知识卡建议字段：claim、source、version、scope、evidence、counterexample、verification_probe、status。status=待证/已在指定设置复验/已推翻；可以携带反证，不能只积累“不要尝试”。

## 为什么有时负收益：竞争解释

| 候选机制 `[推断]` | 支持与反证 `[论文]` | 用什么区分 |
|---|---|---|
| 专家预设限制搜索空间 | Together固定策略浪费尝试；但InferenceBench去action-space也会伤表现/完整性 | 等内容仅变陈述式策略/开放问题，测优化层次分布和不同方法数 |
| 上下文占用降低推理可靠性 | Context Rot受控长度实验；AGENTS成本上升；均非Together中介因果证据 | 有关知识 vs 等长无关内容 vs 短目标，记录上下文token和正确率 |
| 导航与检索成本超过复用价值 | Together C.2解释找可复用项耗时；Demystifying检索精度与最终成功脱钩 | 固定token数，oracle选卡 vs 自动检索；测检索耗时和有效采用率 |
| 过时/条件不匹配 | Stale指令的部分案例有恢复成本；skills brittle assumptions；MTIA文档又可补缺 | 匹配/故意错架构卡；统计编译失败、前提检查和回滚 |
| 盲从、自我确认与失败记忆固化 | SEIS错误接口限制继承；本地GEMM数值开关被写memory | 等内容，绝对禁令 vs 带反证/版本卡；测反例探针及结论修订 |
| 不是缺知识，而是缺执行能力 | ISO定位/实现落差；Two-Agent任务失败分类 | 相同知识下提供可执行验证探针 vs 只给解释；看实现通过率 |
| 预算、工具、难度和测量口径混杂 | KernelSeek单臂/前端/人类引导差异；VibeServe轮数差异；版本会变 | 同任务/同seed块、相同wallclock/API/GPU预算，随机顺序，冻结harness |
| 知识有用但评分没有覆盖正确性 | SEIS词表限制漏检；InferenceBench伪首token | 正确性与完整性先门控，再计性能；分析被门控拒绝率 |

这些机制可并存。没有中介干预或等条件对照前，不把任一机制当作Together结果的已知原因。

## 五个可检验假设

以下全部 `[推断]`，为探索性预实验；规模是诊断流程的预算下限，**不是功效计算或通用统计最低数**。实验单位是独立agent会话，同一会话内多次benchmark不增加独立样本数；任务/seed按块配对，执行顺序随机，提示与停止规则预先冻结。

| 假设 | 自变量/对照 | 因变量、预期、可推翻信号 | 最小试验布局 |
|---|---|---|---|
| H1 决策点问题提升证据检查而不窄化方向 | C0目标 vs 固定问题；同模型/预算，无人工按结果调题 | 主指标：首次候选前有可定位瓶颈证据的会话率；次指标：有效优化层/方法数、正确率。预计证据率升；若仅语言回答增加而可执行probe不增则不支持 | 3个seed块×2臂=6会话，先看能否可靠编码；独立重复扩大后才能推断效果 |
| H2 按需卡优于等内容预加载，且依赖任务陌生度 | C0/C1被动/C2主动，内容完全同一批卡，记录真实读取 | 主指标：首个正确改动的受限平均时间/60分钟内成功率；预计熟悉任务预加载成本大、陌生API卡有益；若收益只来自额外token预算则不能支持渠道解释 | 至少熟悉/陌生各3个seed块×3臂=18会话；单RTX3090 pilot只做其中一类时不估计交互 |
| H3 带证据和反例的经验减少错误继承 | 同一经验命题：绝对规则 vs version+证据+反例卡；固定有效信息量并报告长度差 | 主指标：反证可见后仍保留错误结论的链比例；预期下降；若差异完全由字数或多花验证时间解释则不确定 | 3个seed块×2臂×2轮=12session；按chain分析，不把轮数当独立样本 |
| H4 自动检索的瓶颈是相关性而非缺文档 | 固定知识池：oracle匹配卡 vs 自动检索 vs无卡；控制返回token上限 | 主指标：采用后通过独立验证的候选率；预期oracle优于噪声检索；若命中率变而正确收益不变则“命中就是收益”被否定 | 3个seed块×3臂=9会话；与H2分开，避免同时改内容与渠道 |
| H5 验证型技能比策略菜单更可靠 | 等长“要做哪些优化” vs “如何验证瓶颈/正确性”的技能；同插入点 | 主指标：每有效候选的GPU测量次数与正确性拒绝率；预期少走无效测量、正确率不下降；若减少测量只是少探索则不支持 | 3个seed块×2臂=6会话，加无技能臂则9；初步只报差值/个体点 |

优先 H1 与 H2：前者干预短且易固定，后者直接检验同知识的渠道差异。暂不同时检验五个假设。性能以通过全部门控后的最终加速比为次指标；缺失/超时/不通过按预先规则报告，不能剔除坏会话。pilot报每次结果和不确定性，不做小样本“显著胜出”宣称。正式规模需据pilot的方差、相关结构和团队关心的最小效应再估算。

## 方法工具说明

本研究使用 literature-review、paper-lookup、hypothesis-generation 技能组织核验和设计；它们没有代替独立专家复核。软件方法来源：[Kassis, Agarwal, He, Patel & Brueckner，Scientific Agent Skills](https://arxiv.org/abs/2609.00065)，2026，当前记录v2；本报告仅引用该工具来源，不将其纳入知识注入效果对照表。
