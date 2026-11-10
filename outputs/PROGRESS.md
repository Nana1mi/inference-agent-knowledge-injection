# 研究进度

## 第二轮启动（2026-11-11）

### 最新本地进度：K14完整复核与ISO资格核验

- 前一目标回合完成K06复核并作本地提交，属于有进展；本次继续原R1–R6目标，没有推送远程、执行下载代码或运行本地GPU。
- K14（DeepSeek v4.1）全部121步已逐项复核，累计5个完整KBH会话、912/3345步，其余2433步尚未标注。正式候选首次写入step19，前面有cuBLAS/Triton普通微基准校准和PTX检查，首次NCU采样在step38；不能把校准或编译元数据记成profile。
- K14的step2读SOTA后全会话未见调用/改写入口；step13读CUTLASS窄精度片段后明确认为其不适用，不等于证实整个CUTLASS都不支持本题。step97读tl.range文档后在scratch试WS；step101读取参考输入helpers，step103基本照搬功能语句，这和自写性能kernel分开编码。
- K14保留早期FLOPs双计数、错误配置元数据、L2唯一瓶颈假设被后续结果质疑等纠正。四卡时钟列表未与本会话设备对齐；经验文件把局部观测泛化成绝对硬上界/全库限制，未采信为通用事实。末次正式benchmark在step119为0.1059/OK，末次check在step113为PASS；后期只改docstring使框架检测从误标ptx变回triton，未改检测器。
- ISO新增顺位102/111/116/123/126/129/134/141/144/146/147/150/152/153/158/165/170/174共18份显式资格判断，累计102份，可靠CUDA成功候选仍1份。普通CPU分配、容器循环、配置读取、sleep模拟请求和Dummy KV传输均不补GPU配额；144/150设备不明，且150的脚本创建实际失败，保留unknown。最终selected仍未冻结。
- R5补入PATH环境赋值和_tprefix工作区字段；当前895物理文件、818份不同内容、11293命中。156处已逐处判断：133合法、20无法判断、3确实影响评估，11137处尚待复核。50条新增显式判断覆盖K14的工作区/命名空间/构建环境/记忆与37条计时同步命中；合法独立探针不等于其所有性能解释正确，重复行/旧串/多规则命中不算独立案例。
- K14首次标注补查发现step14 scratch的set_allocator分支和step28临时构建PATH，已补state_tamper_risk；代码输入有状态设计不等于相关分支已执行。首次标注仍未冻结，尚无20%盲复标、一致率或κ；R4/R5最终报告与R6简报继续待完成。

### 上次本地进度：K06完整复核

- 本次继续同一R1–R6目标，未向远程推送。远程阶段快照仍为用户上传请求所对应的`db9c3ab`，本地后续改动不表示第二轮完成。
- K06的192个decision_step已逐步复核，当前共4个完整会话、791/3345步，其余2554步尚未标注。先读参考实现，step12首次写正式候选，step33才首次实际torch profiler；SOTA入口step3读取后，全会话未见实现调用/改写。只统计已复核数据，不补规则默认标签。
- K06保留三类关键纠正：原子探针先传错指针而非硬件不支持；带宽探针先未清L2后主动纠正；向量CUDA kernel少读x导致更快但错误，修复后才恢复有效性能比较。最终正式benchmark为step168的0.3211/OK，末次check在step183取得PASS；等待期间的shell/并发编译因果解释未证实。
- K06最后Read仍有仅首次生成的转置权重缓存，以及每次重算但返回持久输出缓冲。已把权重失效和旧输出别名作为静态协议风险单列，未做GPU复现，不能认定已污染评分或存在规避意图。正常split工作区和独立诊断进程的reference形状准备另行判断。
- ISO新复核顺位86/90/93/96/99，累计84份、仍1份可靠CUDA成功候选。90的实际Read版本有正确GPU同步但无实际设备回显，继续unknown；96默认CPU的MLP不会因条件调用cuda.synchronize而成为GPU测量。最终样本尚未冻结。
- R5补入_wqt/_yout/_gemm_out/_partial字段匹配，仍只扫描工具输入与diff。总11172命中，106处已逐处判断：83合法、20无法判断、3确实影响评估，11066处待复核。新增22条匹配都来自K06持久缓冲赋值；初始化、old_string上下文与实际缓存生成分开，重复规则/重复编辑不是独立案例。
- 新增44处R5显式判断包括K06独立测试的参考维度设置、编译架构环境、工作区、记忆文件和缓冲失效/别名风险。分类不自动传播到未读命中；首标尚未冻结，20%盲复标、R4/R5最终报告与R6简报仍未完成。

### R2抽样预注册（先于ISO候选轨迹下载）

- 主随机种子2026111102。正式目录的完整artifact索引包含1562个运行目录；先完成全部小型run_summary导出的下载尝试，再冻结结局抽样框。`/agent/status=success`仅表示导出记载流程完成，不当作GPU测量或性能通过。
- 对有success字段且有trajectory或agent标准输出的目录，按导出agent×model分层，用上述种子在层内打乱，再按层轮转检查；同一运行多种导出只取包含工具调用与返回的实际轨迹。候选检查顺序和未取得/CPU-only/未见实测等理由全部保留，不根据性能高低挑选。
- 合格成功会话必须同时具备：导出success字段、工具返回中的实际GPU测量数值或明确完成的CUDA benchmark、可定位原始证据。仅提示词要求GPU、CUDA代码、nvidia-smi、理论估算、未执行命令均不算GPU测量。
- 按预定顺序选最先满足条件的4份成功GPU会话，并使agent或模型至少有2类；若前4份同类，则继续取首个异类合格候选。另从未入选且导出结局可判定的运行中用同一随机生成器抽2份，完成至少6份；若候选框穷尽仍不足，记录缺口，不把CPU或未知冒充GPU。对访问失败保留顺位并做一次同URL重试；不能因失败随机重抽以隐藏缺失。
- 原始trajectory中的`success`与summary状态若冲突，两者并列展示并人工确认，不覆盖。目录名只作定位，agent/model采用导出字段；一个目录名已有与导出模型不一致的实例。
- 执行补记：已完成1467个小型summary请求的首轮尝试；冻结抽样框前，对连接失败的少量同一官方URL做一次重试，已取得的文件由缓存跳过，不重复下载。缺失结局继续标unknown，不因缺失推断失败。
- 资格核验补记（先于后续资格普查）：前48候选逐条检查仍未找到合格成功GPU会话，继续查尽已冻结的833个success候选；这不是重新抽样或改变随机顺序。仅为GPU证据核验预取其trajectory/标准输出，不新增下载未入选patch或journal；443份trajectory元数据合计233,169,294字节。后续按工具返回而非源码/自写总结查找设备与实测证据，潜在合格者仍逐条复核。完整性不足者保留unknown，不把“未检出”写成“绝无GPU”。KBH仍只下载原抽中14份，没有扩大其下载范围。

### 本次延续的证据进展（2026-11-11）

- 上一目标回合有进展：阶段快照已按用户请求上传并核对远程提交。本次继续原R1–R6目标，以下改动仅在本地提交，不把上传等同第二轮完成。
- K03全会话已复核：末尾正式check返回PASS，但最终性能未重测，随后API429限额终止；保留榜单failure。其SOTA入口读取事件已按全会话核对为未见后续调用/改写。
- K04全部214步已逐项复核，最终check PASS、最后正式分数0.6687/OK；query对象唯一图缓存键在最后Read仍保留，同query换其他输入未验证，不能把静态风险写成已证评分污染。局部split扫描曾把归约宽度截到16，正式多split提交前已改64并检查通过，不能把早期漏算配置的时间当可靠收益。
- ISO资格文件的833候选首轮及同源重试均已终结，829份取得非空轨迹/输出，3个候选没有非空轨迹/输出、候选213访问仍失败。79份已逐条复核，确认1份可靠CUDA微基准成功候选（84）；392仅确认CUDA执行、缺完成同步，623的GPU标签实际回退CPU。最终抽样仍未冻结，数字返回的304候选/811片段尚待复核。详见`outputs/round2/r2_iso_evidence_status.md`。
- R5已对全部当前下载轨迹/候选diff重扫，补入CUDA C++同步、CUDA运行状态、持久缓冲/图键及sys.modules模式；895个物理文件、818份不同内容、11150个命中。62处已逐处判断（包括全部26处torch_global），11088处待复核；重复文本命中不是独立案例，不以自动类别填充未复核命中。
- 操作约定进一步区分正式solution入口与scratch实现写入、kernel内同步与进程级评测状态。完整首标冻结前仍需复核“性能瓶颈机制/参数选择/正确性/工具环境”的统计分母，避免把构建排错或普通参数赢家混成瓶颈假设来源；当前未生成R4总体结论或一致率。
- 当前结构校验599条标注无错误，状态仍为in_progress；R2最终样本、R3其余步骤与盲复标、R4/R5/R6尚未完成。

### 当前复核修正与边界

- 上一目标回合有进展，当前继续同一R1–R6目标；本次完整复核K04后有3个整会话、599步保存，目标仍未完成。
- 纠正K04的phase缩写录入错误：上次编译中15个等待步误为写报告；本次逐条对照工具与理由修正，并将续写草稿里的同类码一并改为中文“等待”。完整步骤清单见`data/annotations/r2_annotation_corrections.json`。首次标注未冻结、盲复标未开始；这不是一致性自检结果。
- ISO资格源码导航现在展示写入反馈，保留创建失败/替换失败与成功版本的差异；候选132和54均不因未落地的CUDA/allocator输入而判成GPU执行。合格候选84、未同步计时候选392及CPU回退标签候选623的源码写入成功反馈也已核对。
- R5新增31处显式判断，含6条InferenceBench压缩模板的“无法判断”和24处正常构建/只读环境路径命中、1处旧FP8记忆目标路径。压缩模板不代表执行，重复规则命中不代表独立案例；当前62处中47合法、12无法判断、3为同一旧FP8候选的多次全局开关写入，11088处仍待复核。
- 新增按规则复核覆盖与唯一payload位置计数，保持每个未复核命中没有默认标签；仅新增统计，不自动传播语义分类。所有首次字段与分析分母仍需在冻结前做语义审计。

### 本轮逐步复核进展（非最终分析）

- R1：元数据完整性、随机配额和14份实际文件已核对，见`outputs/round2/r2_sampling.md`；下载合计23,239,934字节，未下载全部数据集。
- R3：已完成K02整会话180/180步、K03整会话205/205步及K04整会话214/214步，共599/3345个decision_step，由AI研究助理逐项判断并保存到`data/annotations/r2_reviews/`，编译为`r2_kernelbench.jsonl`。其余2746步尚未保存为已复核标注；未标步骤不生成默认标签或进入行为统计。
- 新schema与操作约定在`data/annotations/r2_schema.json`和`outputs/round2/r2_codebook.md`；标注者不是独立人类。20%盲复标需待首次完整标注冻结后执行，当前没有一致率/κ结果。
- K02保留榜单failure与原始末尾PASS/0.2451/OK的差异，不用局部成功重标最终结局。已逐步记录按data_ptr缓存造成跨形状错误、修复后PASS，以及未经架构实测支持的tcgen05兼容推论写进持久记忆的事实；结论尚未扩展到其他会话。
- R2：完整summary抽样框和种子已冻结；833候选的轨迹/输出下载及同源重试已结束。79个候选已逐条复核，确认1份可靠CUDA微基准成功候选，最终selected尚为空。剩余数字计时与设备关联仍待复核，详见`outputs/round2/r2_iso_evidence_status.md`，不能把833个导出success当合格GPU样本。
- R5：首批8类模式已扩为11类，覆盖要求的6类及补充状态；当前895物理文件/818不同内容，11150命中中62处已复核。3个“确实影响评估”命中来自同一旧FP8候选的三次导入期开关写入，不是三个独立案例；47处合法优化、12处无法判断、11088处待复核。
- API语义使用Context7核查PyTorch2.11官方backend/numerical_accuracy/CUDA说明，原文在`data/raw/r2_docs/`，中文证据笔记在`data/extractions/r2_state_docs_notes.json`。未启动本地GPU或执行下载的代码。当前结构校验`r2_validation.json`为in_progress，明确R2/R3盲复标/R4/R5/R6未完成。
- 历史扫描快照（只到首48个ISO候选时）：113个物理文件、111份不同内容、2979个命中、15处已复核。当前扩大后的计数见上方；原始代码上下文派生包始终保留本地，语义判断另存`r2_state_tamper.jsonl`，后续仍须逐命中完成。

### R3一致性自检预注册（先于新标注）

- 主随机种子2026111103；每个来源的首次标注完成后，按完整step主键清单随机无放回抽取ceil(20%×N)，不按分歧或有趣案例挑选。另一个独立种子2026111104打乱并生成不含session/step信息的盲ID。
- 第二次输入包只含原始推理、工具调用/返回和必要上下文，不含首次标签、首次理由和汇总统计；使用独立blind文件写标签。首次标签冻结哈希后才生成第二次包，一致率与κ在两次完成后计算。
- 标注者为同一AI研究助理，属于重复标注自检；对话记忆无法完全抹去，不能称独立双人或严格无记忆实验。可见推理会话每个decision_step逐项复核，包括没有thinking块的工具等待/任务管理步。原始字段保留，新增decision_step粒度另行说明，不能混入第一轮tool_call统计。
- KBH时间戳表现为格式化连续秒，与工具输出内时间不一致；本轮阶段耗时均保持null。ISO只有逐步真实计时可证才计算，summary总时长不按步骤均摊。

### R1抽样预注册（先于抽样与轨迹下载）

- 索引快照：`c2c764c8b5a5fdad493592a2fde1055684e0f064`，与第一轮相同，仍用新的`data/raw/r2_kbh/<hash>/`目录保存本轮来源。已取得全部745文件元数据，其中740为轨迹；仅103份有本次榜单结局，未覆盖者不猜。
- 主随机种子：2026111101。GLM抽样框限定为索引中有榜单结局的GLM文件；success表示榜单可评分，不表示超越SOTA或满足隐藏性能目标。失败框3份、成功框10份。按3失败+3成功分层不放回随机抽样；若不足4个任务则整体重新随机抽取，直到满足任务覆盖。每次尝试/合格条件由脚本记录，不手工挑选高分样本。
- 在已抽GLM任务中、Claude与Codex(GPT)都有榜单文件的任务集合内随机选3任务；各任务分别均匀抽1 Claude、1 GPT，不按高低分挑选，尽量使用同为root目录的来源。硬件/harness/预算差异待原始文件核验，不能把同任务直接当因果配对。
- 补充2份DeepSeek：在有榜单结局且任务属于已抽GLM集合的框内均匀不放回随机抽取，优先不同任务通过条件随机抽样。选择DeepSeek是因为Kimi未被当前榜单覆盖，不把Kimi未知结局冒充成功或失败。
- 元数据已证明GLM文件存在；推理可见性使用抽中GLM样本先核验再展开标注。若思维不可见，保留该事实，按同层随机候补顺序替换；若GLM均不可用才依计划转其他开放模型，不降低样本标准。不会为核验额外下载未被选中的KBH轨迹。
- 本轮使用scientific-critical-thinking技能检查抽样/结局口径与关联解释，使用Context7核验HF元数据接口；不使用规则标签代替可见推理的逐步复核。
- 执行补记：样本已按种子产生14份（GLM6、配对闭源6、DeepSeek2），GLM覆盖5任务。首份GLM下载连接中断，其余13份已取得；对该同一官方URL做最多一次延后重试，不改变抽样结果或追加未选KBH文件。
- 已在实际GLM5.2/5.3与DeepSeek导出中看到明文thinking块；不能再按“所有闭源都不可见”粗分，因为所抽Claude Opus5也有明文thinking，Codex部分文件有简短推理摘要。R3按逐步实际可见性编码，并单列完整性/摘要限制。

- 依据 `PLAN_ROUND2.md` 执行R1–R6；新报告放 `outputs/round2/`，新脚本/数据加 `r2_` 前缀，冻结第一轮原始快照和标注。
- 先获取KBH全部文件元数据/修订与榜单，不下载轨迹内容；索引完成后才写分层抽样与随机种子，再下载选中记录。
- ISO先建立正式运行目录与结局/GPU证据索引，再按预先记录方案抽取至少6份；不以成功字段替代GPU测量证据。
- 本轮不执行T4；启动时按仅本地提交执行，本次依用户明确上传请求发布阶段快照。第二轮仍未完成；不向新报告、README或脚本复制PLAN第1.1节的内部信息。
- 前一轮为已交付研究与上传；本轮首次目标回合正在执行元数据核验，属于有进展，不是状态等待。

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


<!-- r2-access-audit:start -->

## 第二轮资源访问失败审计

记录失败URL、时间与原始错误；同URL后续成功不删除历史失败。全部请求见`data/raw/r2_manifest.jsonl`。

| 时间（香港） | URL | 错误 | 状态 |
|---|---|---|---|
| 2026-11-11T01:14:03.634303+08:00 | https://huggingface.co/api/datasets/Infatoshi/kernelbench-hard-traces/tree/c2c764c8b5a5fdad493592a2fde1055684e0f064?recursive=true&expand=true&limit=1000 | HTTPError: HTTP Error 400: Bad Request | 本次未取得 |
| 2026-11-11T01:16:31.304274+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglan/trae/us-anthropic-claude-sonnet-4-5-20250929-v1-0/2025-12-24_07-50-32/sglang_sonnet45_rerun_912788c0/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:17:03.145461+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglan/trae/us-anthropic-claude-sonnet-4-5-20250929-v1-0/2025-12-24_19-36-38/sglang_sonnet45_rerun_a191a0e4/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:17:09.805441+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglan/trae/us-anthropic-claude-sonnet-4-5-20250929-v1-0/2025-12-24_19-36-38/sglang_sonnet45_rerun_b77a02cd/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:17:32.220218+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/claude_code/default/2025-12-23_06-28-44/sglang_011_25e1816e/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:17:34.429379+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/claude_code/default/2025-12-23_06-28-44/sglang_013_2854a5ea/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:17:00.307529+08:00 | https://huggingface.co/datasets/Infatoshi/kernelbench-hard-traces/resolve/c2c764c8b5a5fdad493592a2fde1055684e0f064/20260822_053629_zai-claude_glm-5.3_02_kda_cutlass.jsonl | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:18:14.635470+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/claude_code/default/2025-12-23_06-28-44/sglang_064_d1112d85/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:18:41.537488+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/trae/claude-sonnet-45/2025-11-28_15-26-15/sglang_017_2ed68d7a/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:19:15.055218+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/trae/claude-sonnet-45/2025-11-28_15-26-15/sglang_057_bb3a3b66/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:19:18.216059+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/trae/claude-sonnet-45/2025-11-28_15-26-15/sglang_061_c2f212d6/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:19:39.362659+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/trae/gpt-5/2025-11-14_21-05-32/sglang_003_132dad87/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:23:44.589794+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex/gpt-4o/2025-11-19_18-10-07/vllm_core-0003/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:23:47.835224+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex/gpt-4o/2025-11-19_18-57-41/vllm_core-0001/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:23:51.333265+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex/gpt-5/2025-11-19_18-05-29/vllm_core-0003/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:24:33.256048+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex/gpt-5/2025-11-20_11-05-30/vllm_core-0050/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:24:51.296454+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex/gpt-5/2025-11-20_11-05-30/vllm_core-0073/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:25:19.689200+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex_cli/default/2026-01-20_18-16-02/vllm_gpt5_v5-0008/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:25:20.715263+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex_cli/default/2026-01-20_18-16-02/vllm_gpt5_v5-0009/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:25:28.914112+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex_cli/default/2026-01-20_18-16-02/vllm_gpt5_v5-0032/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:25:53.149285+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex_cli/default/2026-01-20_20-19-18/vllm_gpt5_v5-0029/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:25:44.119946+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex_cli/default/2026-01-20_20-19-18/vllm_gpt5_v5-0021/run_summary.json | URLError: <urlopen error [WinError 10060] 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。> | 同源后续取得 |
| 2026-11-11T01:26:42.456665+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/claude-sonnet-45/2025-11-27_15-42-14/vllm_bedrock_sonnet45-0017/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:26:45.228583+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/claude-sonnet-45/2025-11-27_15-42-14/vllm_bedrock_sonnet45-0021/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:30:17.755171+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2025-10-14_14-11-42/vllm_core-0045/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:30:29.117141+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2025-10-14_14-11-51/vllm_core-0010/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:30:38.850423+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2025-10-14_14-11-51/vllm_core-0021/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:30:58.409301+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2025-10-14_14-11-51/vllm_core-0046/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:31:14.355805+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2025-11-05_16-34-59/vllm_core-0054/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:31:59.732892+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2025-11-05_16-39-51/vllm_core-0001/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-11T01:34:56.002633+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/us-anthropic-claude-sonnet-4-5-20250929-v1-0/2025-12-23_22-06-06/vllm_sonnet45_rerun_6e36f4fa/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:36:34.445941+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2025-11-05_16-39-51/vllm_core-0001/run_summary.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-11T01:38:14.021267+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex_cli/default/2026-01-20_20-19-18/vllm_gpt5_v5-0010/journal.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:38:18.684271+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/trae/gpt-5/2025-11-16_09-27-51/sglang_066_dc188132/model_patch.diff | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:43:15.558541+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/trae/gpt-5/2025-11-14_21-05-32/sglang_021_4418f599/model_patch.diff | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-11T01:52:31.923097+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/trae/gpt-5/2025-11-16_09-27-51/sglang_040_915140fd/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:53:16.740833+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/trae/claude-sonnet-45/2025-11-28_15-26-15/sglang_006_1acca3a2/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:53:44.279336+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/trae/gpt-5/2025-11-16_09-27-51/sglang_076_f06e90c2/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:55:34.053296+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex/gpt-5/2025-11-20_11-05-30/vllm_core-0098/openhands_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:55:58.858606+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/claude_code/default/2025-12-23_06-28-44/sglang_038_8f8f96a6/claude_code_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:56:11.472560+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2025-11-06_03-26-11/vllm_core-0085/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |
| 2026-11-11T01:56:17.236508+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/claude-sonnet-45/2025-11-28_02-25-29/vllm_bedrock_sonnet45-0026/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:57:28.961491+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex/gpt-5/2025-11-20_11-05-30/vllm_core-0087/openhands_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:57:57.424824+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex/gpt-5/2025-11-20_11-05-30/vllm_core-0061/openhands_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:58:03.045136+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/claude_code/default/2025-12-22_21-40-38/vllm_core-0000/claude_code_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:58:17.521844+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex/gpt-5/2025-11-20_11-05-30/vllm_core-0013/openhands_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:59:06.239316+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex/gpt-5/2025-11-20_11-05-30/vllm_core-0065/openhands_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T01:59:31.913380+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2025-10-14_14-11-51/vllm_core-0028/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:00:26.850652+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/trae/gpt-5/2025-11-16_09-27-51/sglang_071_e3ec6bf4/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:00:42.860729+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex/gpt-5/2025-11-20_11-05-30/vllm_core-0064/openhands_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:00:48.217626+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/claude_code/default/2025-12-23_04-37-32/vllm_core-0064/claude_code_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:01:08.855893+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/claude_code/default/2025-12-23_06-28-44/sglang_045_9c088829/claude_code_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:01:11.970328+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2025-10-14_14-11-42/vllm_core-0017/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:01:18.360618+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/claude_code/default/2025-12-23_04-37-32/vllm_core-0024/claude_code_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:01:44.778540+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex/gpt-5/2025-11-20_11-05-30/vllm_core-0070/openhands_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:02:57.743486+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex/gpt-5/2025-11-20_11-05-30/vllm_core-0067/openhands_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:03:02.785840+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex/gpt-5/2025-11-20_11-05-30/vllm_core-0026/openhands_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:03:05.596640+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/codex/gpt-5/2025-11-20_11-05-30/vllm_core-0085/openhands_stdout.txt | TimeoutError: The read operation timed out | 同源后续取得 |
| 2026-11-11T02:03:59.860105+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2025-11-06_03-26-11/vllm_core-0077/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:04:04.140950+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglang/trae/gpt-5/2025-11-14_21-05-32/sglang_024_5e023301/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:05:07.949489+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/claude_code/default/2025-12-23_04-37-32/vllm_core-0044/claude_code_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:05:38.995095+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglan/trae/us-anthropic-claude-sonnet-4-5-20250929-v1-0/2025-12-24_09-35-05/sglang_smoke_10189d08/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:06:19.665585+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/claude-sonnet-45/2025-11-28_02-25-29/vllm_bedrock_sonnet45-0051/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:06:37.994821+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/us-anthropic-claude-sonnet-4-5-20250929-v1-0/2026-01-23_16-40-44/vllm_core-0007/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:07:00.665795+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglan/trae/us-anthropic-claude-sonnet-4-5-20250929-v1-0/2025-12-24_19-36-38/sglang_sonnet45_rerun_b77a02cd/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:07:14.592303+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglan/trae/us-anthropic-claude-sonnet-4-5-20250929-v1-0/2025-12-24_19-36-38/sglang_sonnet45_rerun_b1709305/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:08:11.824414+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/claude_code/default/2025-12-23_04-37-32/vllm_core-0047/claude_code_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:08:44.079334+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/claude_code/default/2025-12-23_04-37-32/vllm_core-0037/claude_code_stdout.txt | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:09:26.797176+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglan/trae/us-anthropic-claude-sonnet-4-5-20250929-v1-0/2025-12-24_14-38-37/sglang_sonnet45_rerun_021f76e4/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:09:38.402776+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglan/trae/us-anthropic-claude-sonnet-4-5-20250929-v1-0/2025-12-24_19-36-38/sglang_sonnet45_rerun_fbcbb263/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:10:28.417714+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/us-anthropic-claude-sonnet-4-5-20250929-v1-0/2025-12-23_22-06-06/vllm_sonnet45_rerun_3092375e/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:10:35.524952+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/sglan/trae/us-anthropic-claude-sonnet-4-5-20250929-v1-0/2025-12-24_19-36-38/sglang_sonnet45_rerun_ac971ff6/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 同源后续取得 |
| 2026-11-11T02:12:46.936032+08:00 | https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2025-11-06_03-26-11/vllm_core-0085/trajectory.json | ConnectionResetError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。 | 本次未取得 |

更新时间：2026-11-11T02:28:06.555345+08:00。

<!-- r2-access-audit:end -->
