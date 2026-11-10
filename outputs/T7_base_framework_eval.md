# T7：底座框架评估——最终选择待讨论

2026-11-10。这里只做静态源码/文档核验，**未安装或运行任何候选框架**。所有“适合作底座、改造量与成本”均 `[推断]`，开源/接口事实标 `[论文]`（含官方仓库）。证据快照与修订见 `data/raw/<来源>/`。

## 比较表

| 候选与证据 | 公开代码/许可状态 | SGLang适配与可替换性 | 知识插入点与完整轨迹 | 成本与未决事项 |
|---|---|---|---|---|
| **SEIS论文系统**：[§3.3、附录H](https://arxiv.org/html/2610.04646v1)、[项目README](https://github.com/nehzux/SEIS/blob/d0a1d665be5a2d71831d76406dfaca9b02495aa3/README.md) | [论文] 项目根主要是网页；README链接另一公开scaffold。**本次未核实论文完整harness/480会话的对应发布包**；网页根license未见 | [论文] 论文优化mini-sglang，不能直接当作生产SGLang；分session/同步/继承描述清楚，公开模块实现完整对应关系未核实 | [推断] session初始化、报告继承、跨chain同步是自然实验点；论文报告并不等于本次取得完整原始trace | [论文] 主实验H100、单请求小模型，记录多session；[推断] 单次运行可缩小，但应先取得作者/团队固定版本，避免重建研究对象 |
| **项目链接的smth-fun scaffold**：[README/run_trial.sh](https://github.com/smth-fun/self-evolving-inference-system/tree/bf2ddc5c5882a2573756b744c0e88c1b154739fa) | [论文] 启动shell、CLAUDE规范、posts、mini-sglang submodule；README声称MIT，根独立LICENSE未见。不是SEIS论文版本已认证复现 | [论文] README任务是mini-sglang；启动shell调用Claude并指向CLAUDE.md，benchmark执行细节不在该shell；[推断] 脚本短，但miner/profiler/selector未拆成独立组件 | [论文] learning.md作为跨trial记忆，run_trial.sh将stream-json写入每trial的history.jsonl；[推断] 可加入C0–C3，但事件完整性/恢复过程仍需烟测 | [推断] 小模型单卡适合机制pilot；需补独立oracle、完整性门、日志与预算控制，不能因README写frozen就认定已实现进程隔离 |
| **VibeSys/VibeServe**：[论文§3](https://arxiv.org/html/2605.06068#S3)、[仓库README](https://github.com/uw-syfi/vibesys/blob/73eaa071fbe5678a1e1a1ae2fe4b9ea7bed66e04/README.md) | [论文] 真实源码MIT；论文版本与本次main已演进，必须固定commit | [论文] 论文含SGLang修改场景；源码orchestration有多种policy、judge/skill选择。不是装好就等于团队SGLang任务 | [论文] `src/vibesys/run/skill_sources.py`、`orchestration/skill_selection.py`、policy prompts提供明确知识来源/路由/角色插口；代码含transcript/event设施。已发布研究运行的全量日志未核实 | [推断] 实现最丰富但有容器/多角色/API成本、已有策略混杂；研究单一注入变量要冻结其余policy，先做最小nop/基线 |
| **KernelSeek harness**：[§2.2、§4 Release、附录D/F](https://arxiv.org/html/2611.03517v1) | [论文] 声称Apache-2.0发布kernels/harness/question bank/trace；本次无官方artifact定位，代码可运行性未核实 | [论文] 目标是独立FlashAttention forward，不是全SGLang；[推断] 可借问题库，接真实引擎需重建task adapter | [推断] 修改前/停滞/上限声明是自然插点；不能说自问bank已完成与人工提问等效对照；完整轨迹仅作者声明 | [推断] 未取得artifact前不选为可运行底座；Hopper/Blackwell kernel不直接迁到3090 |
| **InferenceBench harness**：[README](https://github.com/aisa-group/InferenceBench/blob/108ec747fab0bd92fd9de501f62157d074c50ed5/README.md)、`agents/opencode/solve.sh`、`src/run_task.sh` | [论文] Apache-2.0，容器/runner/质量门/完整性judge都可取得 | [论文] 任务输出OpenAI兼容server，含SGLang容器与baseline；agent solve脚本可替换，[推断] 更适合框架/配置探索，不自然对应团队持续改SGLang代码 | [论文] 初始prompt生成与solve入口可修改，CLI transcript用于分析；本次网站是压缩episode，[推断] 自有试验须保存原始事件，而不只留atlas | [论文] README要求Linux/Apptainer、H100或A100映像、调度脚本原用HTCondor、judge凭据；[推断] 单3090迁移需改镜像/模型/预算，结果另报 |
| **ISO-Bench**：[README/正式运行目录](https://github.com/Lossfunk/ISO-Bench/tree/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench) | [论文] 真实harness与运行导出公开，论文§A.1声明代码Apache-2.0/数据CC BY4.0；各artifact许可文件未全核验 | [论文] 支持SGLang/vLLM任务与多agent，bench/tasks/config分离；[推断] 更适合评估修复任务，跨轮自进化需加accumulation/selector | [实验] 两份trajectory.json含LLM输入/响应、工具结果与最终状态；[推断] 可在任务与agent config处注入，但必须审计example diff/基线状态以免先验污染 | [实验] 两份样本终止于工具协议API400，一份只测CPU；[推断] 需先修复/冻结协议与GPU测量，不能把失败都归因模型 |
| **Apple RSI + Pier**：[README](https://github.com/apple-aiml-research/ml-rsi-inference-bench/blob/1a38072fbe284234c874356b86c9df666a5a79a3/README.md)、[Pier](https://github.com/apple-aiml-research/ml-rsi-inference-bench/blob/1a38072fbe284234c874356b86c9df666a5a79a3/third_party/pier/README.md) | [论文] Apple Sample Code License；Pier第三方许可分开 | [论文] 真实SGLang/vLLM任务，task/agent/verifier分离；[推断] evaluator底座最直接，但不是跨session自进化框架 | [论文] 支持opencode与增强ATIF；[推断] 可在任务/agent提示层注入，但保护tests与canonical来源，记录provider/model/prompt hash | [论文] manifest固定H100/B200、多题多卡、agent常30,000s另加构建评分；[推断] 搬全套成本高，可借任务契约与轨迹格式 |
| **OpenEvolve**：[README、attention示例](https://github.com/algorithmicsuperintelligence/openevolve/tree/main/examples/attention_optimization) | [论文] 框架与示例源码公开；具体许可文本本次未下载核实，不由“开源”推定再分发权 | [论文] 通用程序进化/评估示例；[推断] 能包外部SGLang evaluator，但不等于内置完整引擎harness | [推断] prompt、候选生成、评估反馈和历史选择可插知识；候选/fitness日志未必保留coding-agent全工具过程 | [推断] 最小搜索循环容易理解，研究“方法”而非只调参需扩展候选表示；默认搜索policy是额外混杂 |
| **FlashInfer-Bench**：[Trace/Validate文档](https://github.com/flashinfer-ai/flashinfer-bench/tree/15618a67e8d7b7f49ca61b5ba3b9f26a876d0bee/docs/flashinfer-trace) | [论文] metadata声明Apache-2.0，源码与格式公开 | [论文] kernel definition/workload/solution/evaluation契约；[推断] 有利于独立kernel接入验证，不是全引擎多组件优化agent | [论文] 这里Trace是一次kernel工作负载与实现/评估记录，**不是agent会话trace**；[推断] 适合作profiler/evaluator适配器 | [推断] 需要真实引擎回放与端到端回归，不能把kernel分数直接当服务收益 |

## 三个备选路线，待讨论

1. **保留团队倾向，先核实SEIS对应实现。** [推断] 若团队已有可运行SEIS派生框架与trace，在其session初始化/记忆读取处做注入最能固定agent、引擎与硬件；先拿到固定commit与独立评分接口。没有这些前，不自行认定项目链接的早期scaffold就是论文harness。
2. **以VibeSys作为研究容器。** [推断] 已有知识路由/skills/角色接口，适合研究知识进入哪个组件；代价是框架较重，必须冻结policy、角色、测量预算，避免同时研究scaffold。
3. **小型mini-sglang scaffold + 独立evaluator。** [推断] 先用最短循环检验H1/H2，借Apple/InferenceBench的评分隔离契约与ATIF字段；它是机制预实验方案，不能冒充完整production SGLang或SEIS复现。

本次**没有选择并安装任何一个底座**。建议讨论顺序：团队现有接口和trace是否可用 → 需要研究哪个组件 → 能固定哪些条件 → 再选择框架；不用跨论文速度排行榜替代选型。

## 进入实测前的可复核验收

[推断] 对最终候选统一做一次小预算smoke：冻结commit/子模块/依赖；no-op能运行且正确；外部verifier能拒绝词表裁剪与oracle状态污染；原始工具调用/结果/耗时/版本可导出；C0/C1/C2只改注入路径，其余prompt和预算一致。需要人决策的引擎、provider、硬件与评分指标保留待讨论；T4未启动GPU。
