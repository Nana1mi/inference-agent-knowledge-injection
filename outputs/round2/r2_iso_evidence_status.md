# ISO-Bench证据核验进度（阶段记录）

[实验] 当前确认1份有可靠CUDA完成计时的成功候选，尚未完成最终抽样。以下是本地读取导出文件的结果，不是本机GPU复现；完整索引见[运行索引](../../data/derived/r2_iso_index.json)，逐条理由与定位见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

## 覆盖与缺口

[实验] 正式目录冻结在`Lossfunk/ISO-Bench`的`0a6716bba4361f1ebe9366e1e2a33ffbb913dced`。完整artifact索引有1562个运行目录，实际取得1466份summary：833份导出success、632份error、1份max_steps；96个目录没有已取得summary。success只说明导出记载的agent流程状态，不代表GPU优化有效。来源字段和文件哈希在[索引](../../data/derived/r2_iso_index.json)，抽样框与种子在[selection](../../data/raw/r2_iso/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/selection.json)；[正式目录来源](https://github.com/Lossfunk/ISO-Bench/tree/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs)。

[实验] 已按预先冻结的833个success候选顺序完成资格普查文件的下载尝试及同源重试：取得442份trajectory、248份仅含最终result的输出、139份其他文本输出；3个目录没有非空轨迹/标准输出，另1份trajectory两次访问后仍未取得（候选213）。仅有最终摘要的导出不能补写成逐步工具轨迹。计数见[导出盘点](../../data/derived/r2_iso_execution_inventory.json)，请求/失败见[manifest](../../data/raw/r2_manifest.jsonl)。

[实验] 目前164个候选已有逐条资格判断，确认合格1份；最终`selected`仍为空。不能把下载数量、关键词命中数或summary成功数当成合格样本数。关键词导航之外，新增数字计时导航得到304个候选、811个返回片段，尚未逐一复核；未检出关键词不等于没有GPU测量。该导航由`scripts/r2_iso_measurement_queue.py`生成，原文片段只保留本地。

## 已复核的三个关键区别

| 冻结顺位 | 观察与定位 | 当前处理 |
|---|---|---|
| 84，TRAE / GPT-5 | summary和trajectory均记成功；step17脚本仅在CUDA可用时运行并打印GPU分支，对CUDA张量计时且每轮同步。step18返回两组GPU秒数。 | 计入可靠GPU微基准候选；只测孤立采样函数，使用导入stub，不外推为完整引擎的端到端收益。 |
| 392，TRAE / GPT-5 | step12脚本实际选择CUDA，step15返回设备与两组秒数；两个计时循环均仅用主机时钟，没有区间末同步或CUDA事件。step14只修改正确性判断。 | 确认CUDA执行，但不把主机提交秒数当可靠设备完成测量；不用于补齐可靠GPU测量配额。 |
| 623，TRAE / Sonnet 4.5 | step34明确CUDA不可用；step46脚本将设备回退到CPU，却保留固定的“GPU”行标签；step47打印相应数值。trajectory本身记失败，与summary成功冲突。 | 保留CPU/标签和状态冲突，不计成功GPU测量。 |

[实验] 三例的原始导出分别为[候选84](https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2026-01-23_21-19-19/vllm_core-0005/trajectory.json)、[候选392](https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/gpt-5/2026-01-23_21-19-19/vllm_core-0006/trajectory.json)、[候选623](https://raw.githubusercontent.com/Lossfunk/ISO-Bench/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs/vllm/trae/claude-sonnet-45/2025-11-28_02-25-29/vllm_bedrock_sonnet45-0051/trajectory.json)。上述step从1开始，JSON指针的agent_steps索引从0开始；全部精确指针和SHA256保存在资格复核及运行索引。

[论文] PyTorch官方CUDA说明指出设备执行通常异步，未经同步的主机时间可能不准确；文档展示CUDA事件及等待完成的计时方式。这里用它解释计时语义，不声称已核实每份ISO环境的PyTorch版本：[CUDA说明的Asynchronous execution](https://github.com/pytorch/pytorch/blob/v2.11.0/docs/source/notes/cuda.rst)。冻结原文与中文笔记见[API证据笔记](../../data/extractions/r2_state_docs_notes.json)。

[实验] 本次额外检查了源码写入反馈：候选132的创建因文件已存在失败，候选54的创建/部分替换也失败。这些输入代码不能当作实际测试脚本；其原始秒数没有充分设备证据，继续保留unknown。检查程序`scripts/r2_iso_numeric_view.py`同时展示输入定位及对应工具的成功/错误返回；缺失反馈不推定成功。

[实验] 候选90说明还需检查实际Read内容：step8读取的脚本与最初创建输入不同，实际版本按CUDA可用性选设备，并在GPU分支正确同步，但step9/14/16的秒数没有输出实际设备，继续保留unknown。候选96的step48 Read显示输入和回退MLP均默认CPU，条件调用CUDA同步不能改变计算设备；step49/50的毫秒数不计GPU样本。精确指针与文件哈希见[逐条资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)及[运行索引](../../data/derived/r2_iso_index.json)。

[实验] 新检查的候选还包括模拟测量：147的配置读取成本由`time.sleep`人为添加，158用等待模拟顺序/批量warmup请求，165以虚拟地址与Dummy传输引擎代替真实KV传输。这些代码创建反馈均成功，也有真实主机计时，但不是实际GPU模型或传输测量。146的CUDA-graph插件名称同样不够：已执行脚本只测默认CPU张量和对象初始化，返回还显示缺少`libcuda.so.1`。全部判断保留精确工具输入、写入反馈、数值返回和结局定位，见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

## 接下来的核验

[实验] 追加顺位330/334/335/337/339/340/345/347仍未新增可靠成功GPU候选。337/340/345/347虽trajectory成功，实测分别为NeuronWorker配置整数、Python列表划分、逻辑PhysicalTokenBlock元数据、NumPy ngram。337方法名initialize_cache、345输出Free GPU blocks不构成设备分配证据，已核对实际方法源码。335约43ms含20次sleep(0.002)；334仅NCCL模块导入/元数据/地址解析，339只选backend与创建配置，均非实际GPU传输或解码。330明确回显CPU。340新路径更慢且checksum不同，不将其当等价加速。实际成功写入/Read、失败反馈、数值返回与结局定位见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 追加顺位310/312/315/317/320/322/324/329仍未新增可靠成功GPU候选。312虽trajectory成功，创建失败后实际Read是默认CPU张量切片/分配；310/315/324明确回显CPU；317是NumPy ngram，322为CPU序列化。320的GPU分支因缺依赖被SKIP，实际只测CPU；empty仅初始化首元素再求和，不具相同初始化工作。329实际源码仅管理PhysicalTokenBlock元数据，Device.GPU标签不意味着设备分配/执行。324的empty(no fill)也不自动证明整个程序数值等价。全部写入反馈、实际Read、数值及结局精确指针见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 追加顺位290/295/297/300/302/304/305/307仍未新增可靠成功GPU候选。297和307虽在trajectory记成功，实测分别为token列表/block元数据及默认CPU SDPA；295和305的实际脚本有条件CUDA分支和同步，但返回未说明实际设备，保留unknown。302拟创建失败后读到环境变量查询/hash脚本，新增配置路径又因import失败未完成；304的CPU tensor conversion收益与其他padding回退分别保留。300的CPU循环计时没有被当前数字导航抓到，直接核对原文的`agent_steps[38].tool_results[0].result`补入，说明导航不是完整性证明。精确写入反馈、实际脚本、数值返回和结局指针见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 追加顺位279/282/284/285的复核仍未新增可靠成功GPU候选。279与282的trajectory虽成功，279分配/采样探针明确回显CPU、其他验证默认CPU/Python列表；282拟创建被拒后Read到的是环境变量查询和模块reload主机计时。284的“CUDA graph batch info”只是优化对象名称，实测均on cpu；285最后实际脚本回显RotaryEmbedding.forward_native CPU及import失败/成功耗时。写入反馈、实际Read与数值定位见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 新增顺位66/262/264/265/267/269/270/272/274的逐条复核：270在trajectory成功，但两个数字返回均明确device=cpu；272成功但实测仍是block元数据。267最初create失败，实际Read的旧脚本默认CPU，后来调整CPU导入兼容性而非切到GPU。264实际回显CPU分配，265注释forward_cuda而代码明确device=cpu；269的7.50x/13.04x来自调度循环模拟，其生成器对照反而为0.99x/0.98x。66是DummyTokenizer，262是OrderedDict驱逐元数据，274是主机bytes编解码。完整写入反馈、Read与数值定位见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)，不将导入CUDA模块、算子名称或模拟收益记入GPU配额。

[实验] 新复核的252虽在trajectory记成功，step18只计时token列表与block分配/标记元数据；源码中的`num_gpu_blocks`是逻辑配额，不是GPU张量执行证据。231对DummyTokenizer和合成请求统计计时，237实际回显`device=cpu`；260创建成功后又替换为默认CPU张量模拟运算，不能按最早的FlashAttention计划归类。255读到了Triton attention源码，但数值来自另一个allocator脚本，缺具体设备输出，保留unknown。各例的工具输入、写入反馈、源码读取与数值返回精确指针见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[推断] 仍需按冻结顺位复核数字计时及其实际脚本，将设备选择、完成同步、测量对象与导出结局关联，才能确定最终样本和真实缺口。目前不能宣称正式目录绝无其他GPU会话，也不能用CPU或未同步提交计时降低标准凑够4份。第一轮两份API 400保留在原标注中，继续排除于本轮行为统计。
