# T4：知识注入预实验设计与环境核查

状态：**仅实验设计；未启动agent优化或GPU实验，无条件间结果**。2026-11-10。依据PLAN的可选任务与“资源不可用则设计交付”原则；不擅自把目标硬件换成另一型号。

## 环境事实 `[实验]`

只读核查脚本：`python scripts/check_environment.py`，结果见 [environment.json](../data/derived/environment.json)。本机是 **RTX 5080 Laptop，16303 MiB**，opencode **1.3.3** 可执行。计划指定RTX3090，本机不符合；远程3090地址、模型/provider授权与团队harness尚未给出，未假定存在可用远程机，也未读取密钥或调用付费模型。opencode命令存在不代表其provider已可用。

[推断] 因此本轮不执行C0–C3，不填写加速比、正确率或耗时对比。不能将公开KernelBench统计冒充本地pilot。

## 冻结实验协议（待讨论后实测）

目标为mini-sglang/Qwen3-0.6B/单RTX3090；先验证原引擎，若确实不能运行才退nano-vllm，记录报错与版本。底座选择见T7，尚未拍板。以下时长为 `[推断]` 预算：原版与评估器准备/烟测约1–2h；C0–C2每会话45分钟、每臂3次，共9会话=6.75h agent墙钟，另计构建/评分；可选C3加3会话=2.25h。预计至少一个工作日级别GPU窗口，未申请或占用。

| 条件 | 唯一变化 | 控制 |
|---|---|---|
| C0 | 只给目标、独立评分接口、正确性契约 | 不提供额外优化卡；原始引擎代码/必要运行文档仍可读，不声称完全无先验 |
| C1 | 可查询 [技术卡目录](../data/knowledge_cards/README.md) 的提示 | 与C2使用相同内容、版本、卡数量和可见工具；记录读取哪些卡 |
| C2 | 同批卡正文放入初始prompt | 不额外提供C1没有的示例、结论或测量结果 |
| C3（可选） | 修改前固定提问：“当前瓶颈是什么，证据在哪？什么结果会推翻它？” | 不由人按中间结果临时添加专家建议；是否加入C3在开始前冻结 |

每个独立会话使用新git worktree/干净进程/无历史memory。3个seed块内随机排序条件，逐次冷却/清理GPU进程并记录频率、温度、功耗、软件栈。相同agent/provider/model snapshot、prompt主体、工具权限、时间/API/token预算和停止规则。若CLI不支持seed，不伪称模型采样相同：seed只用于任务/顺序，记录无法控制的模型随机性。

`opencode run --model <provider/model> --format json ...` 是经Context7核对的非交互入口；实测前仍须检查安装版本的`run --help`并做无GPU最小烟测。不能拿当前dev文档直接保证1.3.3全部旗标相同。[官方CLI文档](https://opencode.ai/docs/cli/)、[本轮Context7依据](https://github.com/anomalyco/opencode/blob/dev/packages/web/src/content/docs/cli.mdx)

## 独立正确性门（设计要求，尚未实现/运行）

1. **全词表数值。** reference在候选导入前于干净独立进程/容器计算；同一输入和baseline token序列逐decode位置对齐，记录完整logit维度、KL(reference||candidate)、top-1一致率、NaN/Inf。不要比较候选各自自由生成的不同位置。容差须由原版/合法数值实现校准，并在看到条件结果前冻结；SEIS附录D阈值可作参考，不能直接当本任务标准。[SEIS附录D](https://arxiv.org/html/2610.04646v1#A4)
2. **生成任务。** 独立保留未向agent暴露的短计算、代码、多语言等prompt；覆盖prefill和多步decode，检查任务输出而非只答选择题。包括低频token与特殊符号；输入/输出均留原始token ID。
3. **EOS。** 预先确认原版会正常结束的短prompt；候选必须正常结束，不能用固定长度benchmark替代。检查EOS ID没有被裁剪/屏蔽。
4. **状态隔离。** A/B/A不同长度与内容、冷热cache、连续新请求及适度并发；复位后对照baseline，检查挂起/污染/复用过期metadata。
5. **静态与运行契约。** 输出head覆盖完整词表、权重与模型身份正确；禁止改评分脚本/请求/参考数值开关/计时定义。静态shape通过仍需随机稀有token数值probe。
6. **性能。** 正确性全过后才计最终有效速度；包含prefill、decode及draft/verify真实成本，核对完成token数。warm-up与测量分离，baseline/候选交替重复；同时保留固定长度与自然EOS口径，不把kernel峰值当服务加速。

## 文件保护与运行隔离

[推断] canonical脚本、请求、reference产物置于worktree之外、由agent无写权限的账户/只读挂载管理；**每次评分前从只读副本恢复并校验hash**，另起干净评分进程。agent只取得评分RPC/命令入口，不取得修改verifier进程、环境或canonical数据的权限。日志记录评分器版本、候选commit和输入hash。reference与候选不得共享可被导入代码改变的math flags、import hooks或缓存。

正确性失败/超时/崩溃保留记录；最终加速按预先冻结的baseline回退规则报告，并单列失败率。agent可读公开开发测试，但holdout与canonical只在外部评分。进入独立会话前恢复原始版本；不可沿用上个条件的代码或learning.md。

## 记录与分析计划

[推断] 保存完整JSONL工具输入/返回、版本、每轮commit/diff、开发反馈、独立门控结果、测量原始样本。用T2 schema标注并区分工具调用与episode；异步任务要有开始/完成/等待ID，才能计算phase时间。

主分析是轨迹：首改前有数据证据的会话比例、首个正确改动时间、profile→假设→修改→验证的完整循环数、无效测量/回滚、知识有效采用及被推翻的结论。最终有效加速为次指标。未产生正确改动的会话在45分钟右删失，不只取成功会话的平均耗时；每臂3次只展示个体点/差值，不声称统计显著。问题条件的“回答了问题”不自动算有证据。

## 未完成与交接

GPU实测、mini-sglang/nano-vllm安装、评分器实现/容差校准、provider最小烟测均未执行。它们是可选T4的后续工作，不是已交付功能。需要团队确认目标3090环境、baseline commit、agent/provider/model、允许的数值变化与主指标。设计对应 [pilot_protocol.json](../data/experiments/pilot_protocol.json)；正式运行前在PROGRESS新增已冻结计划及预计时长，再启动GPU。
