# T1：公开优化轨迹清单

检索截止：2026-11-10（香港时间）。`否` 表示本次官方来源检索未取得，不等于证实不存在；`部分` 明确区分论文叙事、压缩 episode、代码历史和原始会话。所有可用性结论属于 `[实验]` 本次资源检查，文献描述属于 `[论文]`。下载来源、许可说明、时间、SHA256 见 [manifest.jsonl](../data/raw/manifest.jsonl)。

## 核心清单

| 工作及官方定位 | 可得性、格式、规模 | Agent / 目标 / 硬件 | 工具细节 / profiler / 中间 diff | 对应研究问题与许可 |
|---|---|---|---|---|
| [SEIS](https://arxiv.org/html/2610.04646v1) §3、§5–6、附录C/H；[项目仓库](https://github.com/nehzux/SEIS) README | 部分：论文逐 session 汇总与失败叙事；主 Qwen 矩阵记录 480 sessions；本次未取得对应完整原始导出 | 论文 Opus/GPT；mini-sglang；H100，具体模型/CLI见§3.4 | 论文有案例及统计；仓库根树主要是项目网页。README 链接另一 scaffold，不等于该矩阵原始日志 | 经验继承、错误传递、evaluator；论文许可见原页；项目根未见 LICENSE |
| [Together Compiler](https://www.together.ai/together-compiler-paper) §4.4、附录C.2–C.3、Fig.14 | 部分：报告和轨迹图/统计可得；没有取得逐条会话下载 | Claude Code ensemble；forward/kernel/并行配置；NVIDIA/AMD/Trainium，逐设置见报告 | 有 profiler 图与典型动作叙述；非完整工具事件或代码 diff 数据集 | 注入负收益、等待成本；报告未核实再分发许可 |
| [KernelSeek](https://arxiv.org/html/2611.03517v1) §4 Release、§5.3–5.4、附录D/E | 部分：论文声称发布 kernels/harness/question bank/all traces；本次未定位官方 artifact URL；附录含问题库与轨迹统计 | Claude Code/Cursor；FlashAttention CUDA forward；Hopper/Blackwell | 论文给工具计数、关键案例和标签方法；本次无可下载原始会话，不把“声明发布”记为“已取得” | 关键时点提问、停滞、错误上限；kernel Apache-2.0 是论文声明，未取得许可文件 |
| [InferenceBench](https://arxiv.org/html/2607.20468) §5、附录F；[查看器数据](https://inferencebench.ai/data/trajectories.json) | 部分：已下载 JSON，461 run、5,659 episode；本次标注前两 run 的全部 7/14 episode；不是原始逐调用 transcript | 多模型/CLI，所选 Fable 5.1 Max；引擎/配置；论文主设置单 H100 | 命令模板、工具 mix、摘要、score 可见；数值/路径被抽象，无完整 profiler/diff | 探索宽度、selector、配置偏好；代码仓 Apache-2.0，网站 JSON 许可未核实 |
| [ISO-Bench](https://arxiv.org/html/2602.19594) §3–5、附录A；[正式SGLang运行目录](https://github.com/Lossfunk/ISO-Bench/tree/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang) | **是（抽样下载）**：未截断SGLang子树含220个trajectory.json，取按路径排序前两份完整导出，48/10个agent_step；完整工具输入/返回、消息、最终状态可见，两例实际API400中止 | 所取目录TRAE，metadata为Bedrock Claude Sonnet4.5；SGLang LoRA/logits路径；硬件未核实，一例微基准明确CPU | 可见源码view/替换、CPU微基准和API错误；不是GPU端到端收益复现。根递归树被截断，改用浅层树定位；另一个ISO-Bench/ISO-Bench不自动混同 | 执行/协议失败、测量设备、知识示例影响；论文§A.1声明代码Apache-2.0、数据CC BY4.0，仓库中各artifact许可仍需核验 |
| [VibeServe/VibeSys](https://arxiv.org/html/2605.06068) §3、§4.3、附录B/D；[仓库](https://github.com/uw-syfi/vibesys) | 部分：代码、skills、judge prompts；论文迭代图/表；本次未在发布树确认研究运行的完整会话包 | 论文 Scenario A Codex GPT-5.5 Medium；LLM serving；H100 等，跨平台见§4 | 系统支持轨迹/事件存储，不代表实验 trace 已公开；见代码和论文迭代统计 | 分层 skills、角色和评估；代码 MIT，第三方另计 |
| [MetaInfer v1](https://arxiv.org/html/2607.12875v1) §3–5；[v3](https://arxiv.org/html/2607.12875v3) §3–4；[v1仓库](https://github.com/MetaInfer/MetaInfer) | 部分：两版全文、仓库 metadata；未取得原始优化会话；两版必须分开 | v1知识 toolbox，v3图上模型/硬件协同搜索；具体运行条件见各版本 | 算法和结果，缺少本次可标注工具流水 | 知识形态/路由；仓库 metadata 与论文版本对应关系未核实 |
| [KernelEvolve](https://arxiv.org/html/2512.23236) §3.2.3–3.2.4、§5 | 否：本次未定位生产系统逐会话数据。引用的 KernelAgent/TritonBench 不是该生产运行日志 | Claude/GPT/CWM 等；DLRM kernels；MTIA/NVIDIA/AMD | 描述知识检索、profiling和搜索元数据，非原始公开 trace | 专有硬件知识与公开硬件的边界；生产资料再分发许可未核实 |
| [FlashInfer-Bench](https://arxiv.org/html/2601.00227) 正文系统/评测章节；[仓库](https://github.com/flashinfer-ai/flashinfer-bench) | 部分：论文和框架代码入口可访问；benchmark solution/artifact 不自动算 agent 会话，本次未取得完整会话 | kernel生成/部署评估，硬件按题 | 定义、实现、workload及测量机制；不是决策过程记录 | evaluator及kernel接入；许可以仓库 LICENSE 为准，本次不推定 trace 许可 |
| [Glia](https://arxiv.org/html/2510.27176) 系统设计及实验章节 | 部分：论文实验流程/案例；本次未定位配套完整会话下载 | 多角色系统设计/优化，具体任务硬件见实验设置 | 研究流程叙述，不作为逐调用标注样本 | 假设/反思/角色设计；论文许可见原页 |
| [ADRS / Barbarians](https://arxiv.org/html/2510.06189) 系统方法/实验章节 | 部分：论文方法和案例；所引 OpenEvolve 仓库不等同各实验的完整日志 | 系统程序搜索，非全为LLM serving | 进化/验证方法；本次无逐条研究会话包 | 便宜可靠验证器的适用边界；论文许可见原页 |
| [Apple RSI-Inference Bench](https://github.com/apple-aiml-research/ml-rsi-inference-bench) README、tasks、third_party/pier/README | 部分：任务、评分与 runner 可得；本次未确认已发布参赛 agent 的完整运行日志 | 多 agent 接口；vLLM/SGLang；H100/B200 | verifier、task manifests和轨迹格式支持可审计，不等于已发布轨迹 | evaluator、接入自己的agent；Apple Sample Code License，Pier另见其LICENSE |

## 补充来源

| 来源 | 本次取得内容 | 字段覆盖及限制 |
|---|---|---|
| [KernelBench-Hard](https://kernelbench.com/runs)、[官方数据集](https://huggingface.co/datasets/Infatoshi/kernelbench-hard-traces) README/data card | **是**：两个完整 JSONL 导出，KDA 和 FP8 GEMM；858/478 原始记录、290/153 tool_call，详见 [sessions.json](../data/derived/sessions.json)；下载修订 `c2c764c8b5a5fdad493592a2fde1055684e0f064` | Claude Opus 4.8 / Claude Code，两个任务均写明 RTX PRO 6000 SM120；工具输入/返回、中间完整文件或编辑块可见；KDA 有 nsys 启动及自制逐 kernel 计时。闭源模型思维不可见，数据有脱敏；消息时间戳与内嵌日志时间不一致，原因未核实。MIT data card，不推及上游模型/库 |
| [smth-fun scaffold](https://github.com/smth-fun/self-evolving-inference-system) README、posts、run_trial.sh | 部分：已下载 README、posts、启动脚本；mini-sglang trial-10 分支入口 | README实验是 RTX PRO 6000 Blackwell，不能冒充 SEIS 论文 H100 矩阵。learning.md/分支代码属于报告/实现，不是完整原始会话；README写MIT，但根LICENSE未见 |
| [OpenEvolve](https://github.com/algorithmicsuperintelligence/openevolve) 仓库树/examples | 部分：框架/示例入口；本次未取得与具体推理优化实验严格对应的完整 agent 会话 | 代码、候选日志和模型工具 transcript 是不同数据层；不能仅凭支持 logging 认定含 NCU 或自然语言决策轨迹 |

## 下载与规模口径

[实验] InferenceBench 网站正文显示的 scored runs、原论文 main-condition runs 和 atlas runs 是不同分母；本地 JSON 计数由 `inspect_inventory.py` 重建。KernelBench metadata列出740个JSONL文件，网页榜单行数与它们不应混同；文件列表与样本规则保存在 `dataset.json/selection.json`，本轮只下载两条会话，不声称下载整个数据集。原始token总量未计算；各论文未提供可核验的完整会话规模者记未核实，不由PDF页数推算token。

[推断] 用于行为分析应优先采用带可配对输入/返回的原始 JSONL；压缩 episode 用作补充。研究“无知识偏好”还必须控制初始 prompt、SOTA 示例、预装 memory 和工具权限，本轮公开样本不足以识别该因果问题。

访问异常按时间保存在 [PROGRESS.md](PROGRESS.md) 阻塞项与原始 manifest；没有使用镜像站或缓存绕过访问限制。仓库修订、下载许可、筛选范围见各 `data/raw/<来源>/selection.json`。未公开或未定位的会话没有伪造占位 JSONL。
