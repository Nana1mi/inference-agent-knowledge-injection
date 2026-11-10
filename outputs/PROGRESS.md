# 研究进度

日期：2026-11-10（Asia/Hong_Kong）。依据 [PLAN.md](../PLAN.md) 执行；公开来源是待核验线索。

## 执行记录

- 启动：已完整读取计划；创建来源采集脚本，逐条记录 URL、访问时间、哈希、许可及访问失败。先 T1–T3，再 T5–T7，最后检查可选 T4。
- T1：完成官方来源清单与下载核验，产出 `T1_trace_inventory.md`。取得 KernelBench 两份完整工具会话、InferenceBench 的公开压缩 episode 数据；其余来源的原始会话缺口明确列出。
- T2：完成 schema/codebook、两个来源各两条会话序列的标注及统计；KernelBench 443次调用中31条逐项复核，其余规则初标；InferenceBench 21个episode逐项复核。保留初标局限，不虚构时间分配或无证据假设率。
- T1/T2追加核验：通过浅层树绕过GitHub递归返回截断（不是访问限制），在ISO官方正式SGLang运行目录取得两份trajectory.json，48/10个agent_step全部逐项复核；均以API400中止，CPU微基准不记为GPU收益。现在三个来源各两份导出，粒度分开统计。
- T3：完成原始12项与补充对照文献的分类综述、竞争解释及5个可检验假设。更正Together知识库百分比分母和ensemble比较口径；KernelEvolve定性主张不充当等预算定量消融。
- T5：已解析全部37份task.toml，交付短讲稿及逐任务硬件可行性附表；部分嵌套文档访问中断保留记录。
- T6：交付案例目录与分层evaluator清单；新增GEMM导入时改全局数值状态的风险审计线索，未声称GPU独立复现。
- T7：完成静态对比与备选路线，选择标为待讨论；不把SEIS项目链接的早期scaffold当成论文矩阵harness已认证复现。
- T4计划/预计时长：C0–C2各3会话、每会话45分钟，共6.75h agent时间，基线/评分准备约1–2h；可选C3再2.25h。只读环境核查显示本机为RTX5080 Laptop而非RTX3090；opencode1.3.3存在，provider未测。因此不启动GPU；交付设计报告、协议JSON与技术卡，实测和评分器实现未完成。
- 研究边界：2025-01-01 至 2026-11-10 的公开研究；官方论文、项目和仓库优先。单研究者范围综述，不能声称穷尽或代表全部 agent。事实采用 `[论文]`，本地描述性统计采用 `[实验]`，设计与解释采用 `[推断]`。
- 汇总：`00_summary.md`已完成，包含每项发现、优先假设、下步协议及团队待讨论项；独立离线完整性终验通过，具体范围见validation.json，不代表GPU复现。

## 阻塞项

原始访问失败均逐条保留下表；同一路径后来取得的标为已恢复，其余保持未取得。不使用镜像或缓存绕过限制。全部成功请求/哈希见 `data/raw/manifest.jsonl`。

| 时间（香港） | URL | 错误 | 当前状态 |
|---|---|---|---|
| 2026-11-10T22:49:17.565205+08:00 | https://arxiv.org/abs/2607.20468 | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1032)> | 本次未取得 |
| 2026-11-10T22:51:41.854594+08:00 | https://arxiv.org/abs/2601.00227 | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:52:49.306139+08:00 | https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/regression_async_spec_decode_throughput/instruction.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:53:36.495177+08:00 | https://raw.githubusercontent.com/smth-fun/self-evolving-inference-system/bf2ddc5c5882a2573756b744c0e88c1b154739fa/CLAUDE.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:53:36.743407+08:00 | https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/support_deepseek_v4_flash_4xb200_sglang/tests/eval/deepseek_v4_flash/kernels/README.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:53:55.471207+08:00 | https://huggingface.co/datasets/Infatoshi/kernelbench-hard-traces/resolve/c2c764c8b5a5fdad493592a2fde1055684e0f064/20260613_153211_claude_claude-opus-4-8_01_fp8_gemm.jsonl | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同一路径后来已取得 |
| 2026-11-10T22:54:11.824618+08:00 | https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/support_gpt_oss_120b_4xh100_sglang/tests/eval/gpt_oss/README.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:54:30.274561+08:00 | https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/support_kimi_linear_48b_4xh100_vllm/environment/eval/kimi_linear/reference/router-semantics.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:54:30.704948+08:00 | https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/support_kimi_linear_48b_4xh100_vllm/environment/eval/kimi_linear/serving/README.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:54:36.633925+08:00 | https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/support_kimi_linear_48b_4xh100_vllm/tests/_upstream/PROVENANCE.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:54:40.481994+08:00 | https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/support_kimi_linear_48b_4xh100_vllm/tests/eval/kimi_linear/kda/README.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:54:42.299695+08:00 | https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/support_kimi_linear_48b_4xh100_vllm/tests/eval/kimi_linear/reference/router-semantics.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:54:49.469866+08:00 | https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/support_minimax_m3_4xb200_vllm/environment/eval/minimax_m3/msa/README.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:55:03.036401+08:00 | https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/support_minimax_m3_4xb200_vllm/tests/public/datasets/gsm8k/README.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:55:14.697514+08:00 | https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/support_qwen38_flash_next_4xb200_vllm/environment/lock/RESOLVED.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:55:19.965834+08:00 | https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/support_qwen38_flash_next_4xb200_vllm/task.toml | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同一路径后来已取得 |
| 2026-11-10T22:54:45.449336+08:00 | https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/support_kimi_linear_48b_4xh100_vllm/tests/lock/RESOLVED.md | TimeoutError: The read operation timed out | 本次未取得 |
| 2026-11-10T22:55:37.815509+08:00 | https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/support_sd3_2xh100_sglang/tests/test.sh | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:55:40.756252+08:00 | https://raw.githubusercontent.com/apple-aiml-research/ml-rsi-inference-bench/1a38072fbe284234c874356b86c9df666a5a79a3/third_party/pier/examples/tasks/hello-world-no-internet/tests/test.sh | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:56:05.812752+08:00 | https://raw.githubusercontent.com/uw-syfi/vibesys/73eaa071fbe5678a1e1a1ae2fe4b9ea7bed66e04/LICENSE | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:56:05.812306+08:00 | https://raw.githubusercontent.com/uw-syfi/vibesys/73eaa071fbe5678a1e1a1ae2fe4b9ea7bed66e04/README.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:56:10.393360+08:00 | https://raw.githubusercontent.com/uw-syfi/vibesys/73eaa071fbe5678a1e1a1ae2fe4b9ea7bed66e04/docs/contributing/clients-architecture.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:56:14.256283+08:00 | https://raw.githubusercontent.com/uw-syfi/vibesys/73eaa071fbe5678a1e1a1ae2fe4b9ea7bed66e04/docs/contributing/domains.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:56:22.301302+08:00 | https://raw.githubusercontent.com/uw-syfi/vibesys/73eaa071fbe5678a1e1a1ae2fe4b9ea7bed66e04/docs/contributing/orchestration-runtime.md | URLError: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1032)> | 本次未取得 |
| 2026-11-10T22:56:27.310549+08:00 | https://raw.githubusercontent.com/uw-syfi/vibesys/73eaa071fbe5678a1e1a1ae2fe4b9ea7bed66e04/docs/contributing/remote-slurm-execution.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T23:03:29.207957+08:00 | https://api.github.com/repos/algorithmicsuperintelligence/openevolve | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-10T22:57:05.787707+08:00 | https://api.github.com/repos/ISO-Bench/ISO-Bench/git/trees/main?recursive=1 | IncompleteRead: IncompleteRead(9568256 bytes read) | 本次未取得 |
| 2026-11-10T23:06:46.460264+08:00 | https://api.github.com/repos/ISO-Bench/analysis-data | HTTPError: HTTP Error 404: Not Found | 本次未取得 |
| 2026-11-10T23:11:07.444997+08:00 | https://api.semanticscholar.org/graph/v1/paper/search?query=coding+agent+retrieval+augmented+memory+ablation&fields=title%2Cyear%2CexternalIds%2Curl&limit=10&year=2025-2026 | HTTPError: HTTP Error 429:  | 本次未取得 |
| 2026-11-10T23:11:13.421088+08:00 | https://api.semanticscholar.org/graph/v1/paper/search?query=agent+skills+context+files+coding&fields=title%2Cyear%2CexternalIds%2Curl&limit=10&year=2025-2026 | HTTPError: HTTP Error 429:  | 本次未取得 |
| 2026-11-10T23:13:09.564460+08:00 | https://raw.githubusercontent.com/flashinfer-ai/flashinfer-bench/15618a67e8d7b7f49ca61b5ba3b9f26a876d0bee/README.md | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |

其他证据缺口：KernelSeek官方artifact未定位；SEIS论文矩阵原始日志与对应harness未取得；完整公开源未取得的原因见T1。Semantic Scholar限流不解释为没有文献。GitHub连接器的部分大树请求等待后取消，未将取消解释为资源不存在；ISO原始递归树明确truncated=true。

## 未完成项与交付边界

- T4可选实测未运行，评分器未实现/运行；已交设计、环境记录、协议和知识卡，原因是指定3090环境不可用。
- 原始轨迹无法取得的来源不能满足逐会话标注；已对实际可取得来源抽取两条序列，并明确压缩episode的限制。不伪造数据补齐来源。
- KernelBench结构性标注主要是规则初标，尚无独立第二标注者；不能将初标统计当作普遍agent特性。
- Apple全部37份task.toml已解析，但网络中断的嵌套说明/源码未声称全部读完；未进行框架安装、nop/oracle、硬件兼容或GPU复现。
- 底座、团队硬件/模型/provider、主指标待讨论；本轮没有替团队拍板。

## 复现与终验

离线终验已运行，结果见 `data/derived/validation.json`：标注字段/类型与原始定位、工具返回配对、快照SHA256、37题计数、统计分母及本地链接。该检查不验证科学真伪或GPU正确性。采集失败不影响已保存样本的离线重建。脚本语法编译通过；Together PDF按PDF技能提取并目视核对p10，关键数字页码已建ledger。

最后汇总时间：2026-11-10T23:26:04.830474+08:00。
