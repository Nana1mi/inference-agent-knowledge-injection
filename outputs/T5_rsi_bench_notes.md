# T5：Apple RSI-Inference Bench 组内分享笔记

2026-11-10；正文为两页以内的短讲稿，逐任务依据另见 [37任务硬件附表](T5_task_feasibility.md)。代码快照：`1a38072fbe284234c874356b86c9df666a5a79a3`。`[论文]` 此处包含官方仓库原述，`[推断]` 是迁移判断；没有运行任务。

## 它测什么

[论文] 37题分为Day-0模型接入10、推理优化20、回退修复7；vLLM20、SGLang17。输入是固定引擎版本、模型/权重、任务说明、公开workload与1–8张H100/B200；输出是修改后的真实引擎/patch，独立verifier重新构建、启动和测量。论文入口仍标coming soon，不把仓库当作已经发表的论文。[README “The Benchmark / Evaluate Your Own Model”](https://github.com/apple-aiml-research/ml-rsi-inference-bench/blob/1a38072fbe284234c874356b86c9df666a5a79a3/README.md)

| 轨道 | 要交什么 | 官方聚合 |
|---|---|---|
| Day-0 | 模型真实接入、组件与服务契约均通过 | pass@1，partial算失败 |
| 优化 | 同一引擎/模型/任务约束下改善服务指标 | 对baseline的实测加速比，跨题几何均值 |
| 回退修复 | 修复变慢路径，同时保住guard workload及数值语义 | 同上；baseline/候选需在同轮真实GPU比较 |

[论文] README要求优化/修复正确性不过记1.00×。**任务内部可能把失败写成reward=0，再由汇总映射至baseline比率；不能把reward直接解释为speedup。** 回退题还含noise floor、guard band、真实性门；以每题task.toml/tests为准。[README评分图替代文本](https://github.com/apple-aiml-research/ml-rsi-inference-bench/blob/1a38072fbe284234c874356b86c9df666a5a79a3/README.md)、[回退题instruction Scoring](https://github.com/apple-aiml-research/ml-rsi-inference-bench/blob/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/regression_multimodal_prefill_ttft/instruction.md)

## 正确性与如何接agent

[论文] 没有一个覆盖全37题的统一容差：Day-0的组件契约/状态生命周期/服务输出检查与优化题logits/logprobs比较不同。例：LLaDA2优化manifest列logits容差/通过率；多模态回退题比较固定prompt的logprobs并检查未计分guard请求；模型接入题还有独立上游/参考组件。[LLaDA2 correctness节](https://github.com/apple-aiml-research/ml-rsi-inference-bench/blob/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/optimize_llada2_mini_1xh100_sglang_open/task.toml)、[Kimi state_lifecycle README](https://github.com/apple-aiml-research/ml-rsi-inference-bench/blob/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/support_kimi_linear_48b_4xh100_vllm/tests/eval/kimi_linear/state_lifecycle/README.md)

[论文] 仓库在Pier（Harbor兼容）上运行。README给出的入口是 `uv run pier run -p tasks/<task> --env docker --agent <agent> --model <model>`；vendored Pier支持opencode等CLI并产生增强ATIF轨迹，provider配置通过agent专用kwargs传入。[README Run](https://github.com/apple-aiml-research/ml-rsi-inference-bench/blob/1a38072fbe284234c874356b86c9df666a5a79a3/README.md)、[Pier “Agent runtime configuration”](https://github.com/apple-aiml-research/ml-rsi-inference-bench/blob/1a38072fbe284234c874356b86c9df666a5a79a3/third_party/pier/README.md)。该命令是上游原示例，本机未验证；GLM接入仍需团队明确provider接口。

## 单3090/团队硬件的选择

[推断] 本次全部37份manifest已解析，逐题判断在附表。最值得先做**移植可行性**验证的是4B多模态TTFT回退；8B+EAGLE3与gpt-oss-20b MXFP4为有条件候选：前者还需drafter/KV内存，后者manifest权重约12.8GiB但原缺陷在Hopper Triton路径，能放权重不等于3090可执行。其余多卡/大模型题不宜原样搬到单3090；例如LLaDA2 16.1B BF16权重粗估32.2GB，已经超出24GB设计预算。[逐题task.toml及理由](T5_task_feasibility.md)

[推断] 团队若有匹配H100/B200，先选SGLang题并验证nop/oracle与固定baseline，而不是先跑全部题。README图示“up to 8h”是概述，manifest常设agent timeout 30,000秒（约8.33h），构建/verifier另有预算，不能按8h估全流程成本。[例如LLaDA2 agent/environment/verifier节](https://github.com/apple-aiml-research/ml-rsi-inference-bench/blob/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/optimize_llada2_mini_1xh100_sglang_open/task.toml)

## 给团队evaluator借鉴

[推断] 保留三件事：独立重建并评分最终提交；baseline/候选交替计时并控制warm-up；性能主workload之外设guard workload。另补本课题需要的全词表维度、EOS、跨请求污染、干净进程oracle和记忆证据链接。不可用LLM judge替代确定性数值检查。可先借鉴评分契约，底座框架选型仍待讨论。

阅读边界：已遍历仓库完整文件树、下载并解析全部task.toml，检查README、Pier接入及可访问的任务说明/README/测试入口；部分嵌套文档网络中断，详见PROGRESS。**没有声称完整审计所有源码、下载全部权重或验证官方运行结果。** 根许可为Apple Sample Code License，第三方另计。[LICENSE](https://github.com/apple-aiml-research/ml-rsi-inference-bench/blob/1a38072fbe284234c874356b86c9df666a5a79a3/LICENSE)
