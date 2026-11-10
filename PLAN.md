# 推理引擎自进化：知识注入方向 · 第一周研究计划书

> 本文件是给自主研究 agent 的完整任务说明。请从头到尾读完再开始，并严格遵守第 2 节的规则。
> 计划制定：2026-11-10｜第一次线下对齐：2026-11-15 晚或 11-16｜所有产出用中文撰写，术语可保留英文。

---

## 0. 启动指令（给 agent）

你是一名 AI infra 方向的研究助理。你的任务是按照第 4 节的任务清单，完成"推理引擎自进化框架中的外部知识注入"这一课题的前期调研和预实验，并在 `outputs/` 目录下交付第 5 节列出的全部文件。

工作方式：
1. 先完成 T1、T2、T3（纯调研，不需要 GPU），再做 T5、T6、T7，最后做 T4（需要 GPU，可选）。
2. 每完成一个任务，更新 `outputs/PROGRESS.md`：写明完成了什么、产出文件在哪、遇到的问题、未完成项。
3. 遇到无法访问的资源、无法验证的信息，如实记录，不要编造，不要卡住，跳过后继续。
4. 全部结束后，写 `outputs/00_summary.md`，作为 11-16 线下讨论的材料。

---

## 1. 背景

### 1.1 团队在做什么

团队在做一套**推理引擎自进化框架**：让 coding agent 持续修改推理引擎（目前用 SGLang）的代码，在真实硬件上实测、保留有效改动、继续迭代。框架由以下组件组成，标注 *evolve* 的组件本身也可以迭代：

| 组件 | 作用 |
|---|---|
| **miner** *(evolve，当前重点)* | 大范围寻找优化机会 |
| **evaluator** *(evolve，当前重点)* | 正确、完备地评估改动；防止 agent 走捷径（reward hacking） |
| **profiler** | 用工具（NCU、nsys、torch profiler 等）抓数据、定位瓶颈 |
| **optimizer** | 执行优化搜索；搜索对象是"方法"，再细化到具体参数，不只是调超参 |
| **selector** | 在众多候选分支中选择值得实测的 |
| **skills / 规范** | agent 的技能和行为规范 |
| **accumulation** | 跨轮次的经验积累 |

已知的工程事实：
- 引擎选 SGLang：高并发、负载跑满时它表现最好；低负载时 vLLM 更好。
- agent 底座目前用 GLM 或 GPT 系列。
- 团队已在自有硬件和选定模型上迭代出一些收益，还在持续进行。

### 1.2 本课题：外部知识怎么注入 agent

起点是 Together Compiler 报告里的反直觉结果：去掉知识库后，12 小时后的加速比反而提高 25–31%；一句朴素指令（"把这个前向计算做到尽可能快"）胜过专家写的策略（10 次尝试后 6.2× 对 4.9×）。所以"把知识直接塞给 agent"不一定有用。

需要回答的问题：
1. **agent 的固有优化偏好**：不给知识时，agent 按自己学到的东西怎么探索？偏好什么工具（如 NCU）、什么层面（kernel、线程、调度、runtime、配置）？
2. **注入方式**：
   - 被动查询：知识库放着，agent 需要时自己去查；
   - 主动预加载：提前把知识放进 agent 上下文；
   - 提问式：在关键决策点插入问题（参考 KernelSeek）。
3. **知识形态**：原始论文、提炼后的规则、带论证结构的观点、代码示例、问题清单……哪种格式是正收益，哪种是负收益？
4. **对应到框架**：知识应该进入哪个组件（miner / optimizer / selector / profiler / skills）？

### 1.3 已核实的文献（起点，不是全部）

| 工作 | 链接 | 与本课题的关系 |
|---|---|---|
| SEIS: Self-Evolving Inference Systems | arXiv 2610.04646；代码可能在 github.com/nehzux/SEIS（**未核实**） | 会话间继承报告和代码；报告会传递错误结论；列出了多类正确性 bug。团队倾向用它做底座 |
| Together Compiler (TKCC) | together.ai/blog/together-compiler-continual-compilation-for-ai-inference；论文 PDF 链接见博客 | 知识库消融（负收益）；专家策略消融；agent 52–57% 时间在等测量 |
| Ask, Don't Equip（KernelSeek） | arXiv 2611.03517 | 关键决策点提问 vs 给工具/知识；作者声称公开 kernel、harness、问题库和全部 trace |
| InferenceBench | arXiv 2607.20468；inferencebench.ai；github.com/aisa-group/InferenceBench | agent 不会系统探索，93.9% 收敛到 vLLM；网站有 transcript 示例 |
| ISO-Bench | arXiv 2602.19594；ayushnangia.github.io/iso-bench-website | agent 会定位瓶颈（87.2%）但做不出来（17.9%）；scaffold 和模型一样重要 |
| VibeServe / VibeSys | arXiv 2605.06068；github.com/uw-syfi/vibesys | 有分层组织的 skills library；有 Accuracy Judge 检查 reward hacking |
| MetaInfer | arXiv 2607.12875（v1 与 v3 题目不同，注意版本） | v1 主打"只靠知识库生成引擎"；v3 是图上路由搜索 |
| KernelEvolve（Meta） | arXiv 2512.23236 | 用检索方式注入 MTIA 硬件知识；知识对专有硬件是正收益，可与 Together 的结论对照 |
| FlashInfer-Bench | arXiv 2601.00227 | kernel 接入真实引擎的标准化流程 |
| Glia | arXiv 2510.27176 | 模仿人类研究流程（假设、实验、反思）的多 agent 系统 |
| Barbarians at the Gate（ADRS） | arXiv 2510.06189 | 方法论：系统研究有便宜可靠的验证器 |
| Apple RSI-Inference Bench | github.com/apple-aiml-research/ml-rsi-inference-bench | 37 个任务（Day-0 适配、优化、回退修复）；正确性不过记 1.00× |

---

## 2. 规则（必须遵守）

1. **不编造。**所有事实性陈述（数字、结论、作者、链接）必须附来源 URL 和所在章节/页码。无法核实的写"未核实"。
2. **区分三类信息**，在文中显式标注：
   - `[论文]` 论文或官方材料原文所述；
   - `[推断]` 你根据材料做的推断；
   - `[实验]` 你自己跑出来的结果。
3. **引用克制。**直接引用原文每处不超过 15 个英文词，其余一律用中文转述。
4. **资源访问失败**：记录 URL、错误信息和时间，写入 `outputs/PROGRESS.md` 的"阻塞项"，然后继续下一项。不要用镜像站或缓存绕过访问限制。
6. **GPU 使用（仅 T4）**：
   - 启动 T4 前先在 PROGRESS.md 写好实验计划和预计时长。
7. **实验纪律（T4）**：被优化的 agent 不得修改评分脚本和正确性检查；评分脚本在 agent 工作目录之外运行，每次评分前从只读副本恢复。
8. **可复现。**所有脚本放 `scripts/`，所有原始数据放 `data/`，报告里的每个数字都能追溯到脚本或数据文件。
9. **遇到需要人做决定的分歧**（例如两个框架选哪个），写出选项和理由，标为"待讨论"，不要自行拍板后继续深挖。

---

## 3. 目录结构

```
.
├── PLAN.md                  # 本文件
├── scripts/                 # 所有脚本
├── data/
│   ├── raw/                 # 下载的原始 trace、论文附件（注明来源和许可）
│   └── annotations/         # 标注结果（jsonl）
└── outputs/
    ├── PROGRESS.md
    ├── 00_summary.md
    ├── T1_trace_inventory.md
    ├── T2_codebook.md
    ├── T2_trace_analysis.md
    ├── T3_knowledge_injection_review.md
    ├── T4_pilot_report.md   # 可选
    ├── T5_rsi_bench_notes.md
    ├── T6_reward_hacking_catalog.md
    └── T7_base_framework_eval.md
```

---

## 4. 任务清单

### T1 公开 trace 收集与清单（优先级：最高）

**目标**：搞清楚哪些 agent 优化推理系统的轨迹（trace / transcript / session log）是公开可得的。

步骤：
1. 逐一检查 1.3 节表格里每项工作的论文附录、代码仓库、项目网站，找 agent 轨迹或会话记录。
2. 额外检索：2025–2026 年其他公开了 agent 优化轨迹的 GPU kernel 或推理系统工作（如 KernelBench 相关、OpenEvolve 相关的公开日志）。
3. 能下载的，下载到 `data/raw/<来源名>/`，并记录许可证。

交付 `outputs/T1_trace_inventory.md`，每个来源一行，列：
- 来源工作、URL、是否可得（是 / 部分 / 否）
- 格式（JSON、Markdown、原始终端日志……）
- 规模（会话数、步数、token 量）
- agent 和底座模型、目标（kernel / 引擎 / 配置）、硬件
- 是否包含工具调用细节、profiler 输出、中间代码 diff
- 适合回答 1.2 节哪个问题

### T2 trace 编码方案与行为分析（优先级：最高）

**目标**：建立一套可复用的标注方案，回答"agent 怎么发现和执行优化、和人类工程师有何异同"。

步骤：
1. 设计编码方案（codebook）。每一步动作至少标注：
   - `phase`：探索代码 / profile / 提出假设 / 修改代码 / 测量 / 接受 / 回滚 / 写报告 / 等待；
   - `tool`：NCU / nsys / torch profiler / 端到端 benchmark / 读源码 / 查文档 / 其他；
   - `layer`：kernel / 算子融合 / attention / 调度器 / runtime 与 host 开销 / 并行配置 / 运行参数 / 量化 / 推测解码；
   - `hypothesis`：本步依据的瓶颈假设（文本）；
   - `evidence`：假设有没有数据支撑（有 / 无 / 数据有误）；
   - `outcome`：成功 / 失败 / 正确性不过 / 未测；
   - `turning_point`：是否为关键转折（方向改变、推翻先前结论、采纳错误结论）。
2. 写成 JSON Schema 放进 codebook，并给 3 个手工标注示例。
3. 对 T1 中可得的 trace 抽样标注（每个来源至少 2 条完整会话；会话太长就标注前后各一段，加上所有转折点）。
4. 统计并分析：
   - **agent 偏好**：各 `tool`、`layer` 的使用频率；首次修改前是否做过 profile；
   - **时间分配**：各 `phase` 的步数占比；
   - **失败模式**：无证据假设的比例、错误结论被继承的案例（SEIS 中"接口禁止多 token 执行"就是典型）；
   - **和人类流程对比**：人类的典型流程是 抓 profile → 定位瓶颈 → 看具体算子或计算图 → 设计优化。agent 在哪一步跳过、在哪一步多做；
   - **映射到框架组件**：哪些行为属于 miner、profiler、optimizer、selector 的职责，现有 agent 在哪个组件上最弱。

交付：
- `outputs/T2_codebook.md`
- `data/annotations/*.jsonl`
- `scripts/` 下的统计脚本
- `outputs/T2_trace_analysis.md`，结尾列出 3–5 条"可以通过知识注入改善的具体行为"

### T3 知识注入文献综述（优先级：高）

**目标**：系统整理"给 coding agent 注入领域知识"的已有证据，提出可检验的假设。

步骤：
1. 对 1.3 节每项工作，提取：注入了什么知识、以什么形式、在什么时机、进入哪个环节、有没有消融、效果正还是负、效果大小。
2. 补充检索：通用 coding agent / SWE agent 领域关于 RAG、skills、memory、经验库、AGENTS.md 类规范文件效果的 2025–2026 年研究，以及关于"上下文过多导致性能下降"的研究。只收有消融或对照实验的工作。
3. 建立分类框架，至少包含以下维度：
   - 时机：主动预加载 / 被动查询 / 关键决策点提问 / 事后反思；
   - 形态：原始文档 / 提炼规则 / 带论证的观点 / 代码示例 / 问题；
   - 来源：人类专家 / 论文 / agent 自己的历史经验；
   - 粒度：通用方法论 / 特定硬件 / 特定模型 / 特定代码库。
4. 解释"为什么有时知识是负收益"。列出所有候选解释，标注每个解释有哪些证据支持，例如：限制探索空间、上下文占用、知识过时或与当前代码库不符、agent 盲从、检索噪声。
5. 提出 3–5 个**可检验的假设**，每个写清：自变量、因变量、对照组、预期结果、需要的最小实验规模。

交付 `outputs/T3_knowledge_injection_review.md`，含一张汇总对比表。

### T4 知识注入预实验（优先级：中，可选，需要 GPU）

**前置条件**：T1–T3 完成；在 PROGRESS.md 写好实验计划。

**目标**：小规模试探不同注入方式下 agent 轨迹的差异。重点是**轨迹差异**，不追求加速数字。

设置：
- 引擎：mini-sglang（若无法运行，退回 nano-vllm，并在报告里说明原因）
- 模型：Qwen3-0.6B
- 硬件：RTX 3090
- 被测 agent：opencode 的非交互模式（若不可用，在报告中说明，T4 只交付实验设计）
- 每个会话限时 30–60 分钟，在独立 git worktree 中进行

实验条件（每种至少 3 个会话）：
- **C0 无知识**：只给任务目标、评分脚本说明和正确性要求；
- **C1 被动查询**：提供一个知识目录，由 agent 自行决定是否查阅，内容来自 T3 整理的优化技术卡片；
- **C2 主动预加载**：同样的知识直接放进初始提示；
- **C3 提问式**（若时间允许）：每次修改前插入固定问题，例如"当前最大的瓶颈是什么，证据是什么？""你上一轮的结论有没有被数据推翻？"

正确性检查（吸收 SEIS 的教训，全部要实现）：
- 和原版引擎做 logit 级比对：全词表 KL、top-1 一致率；
- 基于生成的任务检查（不只是选择题），覆盖 decode 路径；
- EOS 终止探针：短生成必须能正常结束；
- 多样化请求：不同长度、不同内容，测试缓存状态有无污染；
- 静态检查：输出层 logit 维度必须等于完整词表大小；
- 测试 prompt 必须包含冷门 token，例如多语言、代码、特殊符号。

记录：完整轨迹（用 T2 的编码方案标注）、每轮加速比、正确性检查结果、各阶段耗时。

交付 `outputs/T4_pilot_report.md`：实验设置、各条件的轨迹统计对比、典型案例、局限性（样本量很小，结论只能作为假设的初步信号）。

### T5 Apple RSI-Inference Bench 分析（优先级：中）

步骤：
1. 读仓库全部文档；若论文已发布，一并阅读。
2. 整理：任务分类和数量、每类任务的输入输出、硬件需求、评分规则（尤其是正确性检查怎么做）、如何接入自己的 agent。
3. 评估：哪些任务在单张 RTX 3090 或团队硬件上**有可能**跑起来（逐个说明原因）；它的评测设计有哪些可以借鉴给团队的 evaluator。

交付 `outputs/T5_rsi_bench_notes.md`，控制在 2 页以内，适合直接拿来做组内分享。

### T6 reward hacking 案例目录（优先级：中）

**目标**：为 evaluator 组件准备一份"agent 会怎么作弊、怎么抓住它"的清单。

步骤：
1. 从 1.3 节全部工作中，收集 agent 修改推理系统时出现的正确性问题和作弊行为。已知线索：
   - SEIS：只算部分词表、删 EOS、复用过期 attention 元数据、选择题检查测不到 decode bug、错误的推测解码测量；
   - InferenceBench：伪造首个流式 chunk 来骗 TTFT，以及完整性裁判检查的各类违规；
   - VibeServe：Accuracy Judge 检查的 reward hacking 模式；
   - Together：非法内存访问导致 GPU 重置。
2. 每个案例记录：现象、为什么现有检查没抓到、最终是怎么发现的、最便宜的检测方法。
3. 归纳成分类，给出一份 evaluator 检查项清单，每项标注检测成本（低 / 中 / 高）。

交付 `outputs/T6_reward_hacking_catalog.md`。

### T7 底座框架选型评估（优先级：中）

**目标**：为"选一个框架做底座、研究哪个组件就只动哪个"提供依据。团队倾向 SEIS。

步骤：
1. 候选：SEIS、VibeServe/VibeSys、KernelSeek 的 harness、InferenceBench 的 harness，以及你在 T1 中发现的其他开源框架。
2. 对每个候选确认：代码是否开源、能否在 SGLang 上运行、组件是否清晰可替换（尤其是知识注入的插入点）、是否记录完整轨迹、运行成本。
3. 输出对比表和推荐意见。最终结论标为"待讨论"。

交付 `outputs/T7_base_framework_eval.md`。

---

## 5. 最终交付：`outputs/00_summary.md`

用于 11-16 线下讨论，控制在 3 页以内，结构如下：
1. 一段话总结本周发现；
2. 各任务的核心结论（每个任务 3–5 条，附指向详细文件的链接）；
3. 对知识注入课题的初步判断：最有希望的 1–2 个假设及理由；
4. 建议的下一步实验设计；
5. 需要团队回答的问题，至少包括：
   - 团队框架的代码和已有 trace 能否开放给本课题使用？自有 trace 比公开 trace 更有价值，因为 agent、引擎、硬件一致；
   - 团队使用的硬件和模型具体是什么？
   - 团队的 agent harness 是什么，GLM 通过什么方式接入？
   - 知识注入的效果用什么指标衡量：最终加速比、收敛速度（达到同等收益所需轮数）、失败率，还是正确性通过率？
6. 阻塞项和未完成项。

---

## 6. 时间安排建议

| 日期 | 任务 |
|---|---|
| 11-10 至 11-11 | T1、T2 编码方案 |
| 11-11 至 11-12 | T2 标注与分析、T3 |
| 11-13 | T5、T6、T7 |
| 11-14 | T4（可选） |
| 11-15 | 00_summary.md、整理全部产出 |
