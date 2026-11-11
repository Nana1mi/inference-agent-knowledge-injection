# ISO-Bench证据核验进度（阶段记录）

[实验] 当前确认1份有可靠CUDA完成计时的成功候选，尚未完成最终抽样。以下是本地读取导出文件的结果，不是本机GPU复现；完整索引见[运行索引](../../data/derived/r2_iso_index.json)，逐条理由与定位见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

## 覆盖与缺口

[实验] 正式目录冻结在`Lossfunk/ISO-Bench`的`0a6716bba4361f1ebe9366e1e2a33ffbb913dced`。完整artifact索引有1562个运行目录，实际取得1466份summary：833份导出success、632份error、1份max_steps；96个目录没有已取得summary。success只说明导出记载的agent流程状态，不代表GPU优化有效。来源字段和文件哈希在[索引](../../data/derived/r2_iso_index.json)，抽样框与种子在[selection](../../data/raw/r2_iso/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/selection.json)；[正式目录来源](https://github.com/Lossfunk/ISO-Bench/tree/0a6716bba4361f1ebe9366e1e2a33ffbb913dced/ISO-Bench/state/runs)。

[实验] 已按预先冻结的833个success候选顺序完成资格普查文件的下载尝试及同源重试：取得442份trajectory、248份仅含最终result的输出、139份其他文本输出；3个目录没有非空轨迹/标准输出，另1份trajectory两次访问后仍未取得（候选213）。仅有最终摘要的导出不能补写成逐步工具轨迹。计数见[导出盘点](../../data/derived/r2_iso_execution_inventory.json)，请求/失败见[manifest](../../data/raw/r2_manifest.jsonl)。

[实验] 目前400个候选已有逐条资格判断，确认合格1份；最终`selected`仍为空。不能把下载数量、关键词命中数或summary成功数当成合格样本数。数字计时导航涉及的304个候选现均有资格判断，但833个候选的普查尚余433份：62份trajectory、126份其他stdout、242份仅最终result、3份未取得；精确剩余顺位见[导出盘点的eligibility_review_coverage](../../data/derived/r2_iso_execution_inventory.json)。导航未检出数字或关键词不等于没有GPU测量。数字导航的811个返回片段只保留本地，覆盖统计只连接明确人工复核ID，不自动生成设备/资格标签。

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

[实验] 新增180/189/216/225/234/243/246/249/254/257/259/275/277/280/287/289/292/294共18份，未新增可靠成功GPU候选。180/277虽trajectory成功，实回CUDA不可用并跳过；246成功但warmup因triton.cdiv缺失失败。257也成功，本地Mamba数学函数产生mean秒值，但入口条件设备未打印，保留unknown，不按函数默认cpu推断实际设备。189只是CPU序列化，216仍是默认CPU rotary，新增VisionTransformer测量先配置失败、后捕获跳过；249的torch/NCCL engine是stub，只循环解析request_id字符串；275仅主机字符串树插入，287是逻辑prefix block/mark元数据。实际输入/Read、失败与成功反馈、返回和结局均见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 234/292文件哈希探针约.026–.028秒及mypy手动hook计数不代表GPU或CI任务实际性能。259的10–40%是新写摘要的EXPECTED数字，唯一测试导入失败，pip尾部输出仍metadata-generation-failed；254只做语法/导入验证，test_opt并未执行，280新增的benchmark文件也没有运行。导航未命中这些无空格秒单位或字段名中的ms，继续以完整工具序列补核，不能宣告GPU样本短缺已最终证成。

[实验] 本轮从非数字导航轨迹补核42份，仍未新增可靠成功GPU候选。21份仅一步启动错误且无工具调用（20份SSO令牌过期、1份配额耗尽）。108/114/168/171虽trajectory成功，基准分别在warmup、导入或CUDA初始化失败；114的管道sed成功不等于内部Python成功。176初次导入还落到另一worktree，修导入后未重跑。105实际CPU分配，120只计逻辑块元数据，138固定CPU且mock FlashInfer wrapper；117的fallback有时间返回但未打印实际设备，继续保留unknown。122只运行替换计时API的维护脚本，没有基准执行。全部实际Read、写入/错误反馈、返回与结局指针见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 105/117/120/138的无空格秒单位未进入原数字导航，304候选/811片段只是旧检索规则覆盖，不代表所有计时记录。工具导航和导出盘点已改为分别读取result/error：非空stdout不再遮住独立stderr，错误内容也保留正确字段指针。设备cue片段231→244，执行返回对象仍1837；错误中的NVIDIA驱动帮助文字也会触发正向cue，不能直接当GPU执行。完整工具序列检查与人工判断继续覆盖导航外候选。

[实验] 追加693/697/699/701/707/717/719/723/729/731/733/737/745/749/751/755/757/759/763/767/769/771/773/775/777/779/783/785/791/795/801/803/807/809/811共35份，未新增可靠成功GPU候选。699/771/811虽trajectory成功，分别明确CPU分配/输入转换、CPU memory pool和纯ServerArgs构造；701/745也成功但设备未输出，745还没有完成同步。749/767/769/773/801的部分条件设备未逐次确证，保留unknown。

[实验] 693初版把cumsum输出分配排除在循环外，约2x；final版把分配放回区间后四档.68–.71x退化，最终摘要却只引用较早数字。723真实metadata初始化因导入/401/配置验证失败，改为CPU cumsum/分配后六档.58–.90x均慢；737的12.8x实际来自另写python -c并固定CPU，不能按原CUDA脚本判设备。717单次extend不仅.89x更慢，还改变组顺序；697“峰值内存”脚本只打印预设tensor数量。795只测导入/签名，删部分sys.modules后第二次导入因重复schema注册失败，没有实际NCCL初始化测量。775的毫秒数是语法/源码检查，809是容器/虚拟指针打包，均不作GPU收益。全部实际输入/写入反馈、运行返回和结局定位见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 追加604/605/607/608/610/611/614/616/617/619/621/635/639/643/645/655/659/667/669/671/675/677/679/683/685/687/689共27份，未新增可靠成功GPU候选。616与667虽trajectory成功，前者测Python copy/list/dict及字符ord模拟，后者仅默认CPU RadixCache key/value与MockPool元数据。616的两个benchmark文件由agent新建，62.7x对应复制dict改共享引用，不是既有模型基准；667约.92→.75-.77秒也不证明GPU KV搬运。

[实验] 635六shape全部报0 active drivers，总时间0.000ms是累加器未更新；617经过依赖错误后同样在Triton驱动初始化失败，120秒timeout不当计时。604后期明确CPU，但早期条件设备未打印；655/685也未输出计时所用实际设备，三者保留unknown，685后续CUDA正确性测试跳过不回推早期。685还将rank-dispatch基准skip/return0，汇总不代表全功能；621先CPU协调模拟.87x退化，后来1.7x只剩Python条件循环。659“优化”combined约695ms比原473–492ms慢，两脚本工作量也不同；677 CPU narrow比slice慢，均不由优化摘要覆盖。完整输入/实际Read、反馈、返回及结局定位见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 本轮追加545/548/550/551/553/554/556/557/560/562/565/566/568/569/571/572/575/577/578/580/581及583/584/586/587/589/590/593/595/596/598/599/601共33份，未新增可靠成功GPU候选。556/572/580/584未输出实际设备，保持unknown；584的fused_available仅表示调用未异常，新增本地fallback的forward本来就调用reference，50/51 timeout实际是build_ext。566/578虽trajectory成功，分别只是NumPy准备与明确CPU的prepare_inputs；578输出行数还随版本改变，不当固定形状对照。

[实验] 557把mod.os.system替为空操作，所谓launch_server秒数仅命令构建；593旧路径重复创建/关闭aiohttp会话，新路径一个会话加pass循环，没有真实HTTP请求，492/461x不外推服务吞吐。554实回CUDA not available；586只用Python百万次加法模拟FlashAttention。589实回CPU，移除contiguous的4099.97x与zero-loop改索引的.38x均保留，595总时间反而110.905→119.554ms。596的TransferInfo/from_zmq只解析NumPy整数/指针字节，599虽列20000请求但遇容量就break，且目标模块导入失败；601只测默认CPU分配及bias构造。创建失败、实际Read/替换、返回与结局的精确指针均在[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)；设备导航新增显示返回中间的设备行，仍不自动生成判断。


[实验] 新增491/495/496/503/504/508/511/512/515/516/519/520/523/524/527/529/530/532/533/535/536/539/541/542共24份，仍未新增可靠成功GPU候选。495、504虽trajectory成功，实际均明确CPU，504三次logprob对照速度比约.58且更慢；541成功但只创建CUDA测试脚本，完整工具序列未执行它，50回传SIMD/整体加速数字是cat写入/回显的摘要，不是计时表。535拟创建被拒后Bash cat查到旧Python加法循环，不能用其约.0039秒证明allreduce CUDA改动；512/536未输出实际设备，分别还有限制为缺完成同步、speedup比值方向与常用定义相反，继续保留unknown。524的clone改alias以及分配类empty未填充等也不当等价GPU收益；523所谓prefill仅解已有token的文本。全部实际脚本、创建/替换反馈、运行返回和结局指针见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 本轮追加425/427/430/432/434/437/439/440/444/448/452及455/456/459/460/468/472/479/480/483/484/487/488共23份，未新增可靠成功GPU候选。成功状态的427/432/437/440/444/452分别测逻辑prefix block、LRU、默认CPU SDPA、明确CPU topk、CPU采样探针（数值导航命中实际timeout）、FakeTokenizer字符串；不按summary/任务名补GPU。434设备选择未输出且主机计时无完成同步，保留unknown；468虽成功写CUDA脚本，但执行先在导入失败，120秒timeout来自依赖检查。484前三次替换失败，按实际Read及最后成功插入后的Device cpu返回判断；488用假指针、NumPy和只累计calls的StubEngine，不是GPU/RDMA传输。具体写入反馈、实际Read/脚本和返回指针见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 追加顺位407/410/412/415/417/419/420/422共8份，仍未新增可靠成功GPU候选。407/417/422虽trajectory成功，实际分别为env查询/reload、Python prefix block元数据、明确device cpu的InputBatch构造。410/419实际回显cpu，419四shape收益有正有负；412用默认CPU的切片/empty-vs-zeros模拟，420是base64/BytesIO/PIL主机编码与Image.open路径，415用导入stub测block元数据。创建被拒时改查实际Read，不把拟写源码当既成执行；407虽追加配置实例化代码，数值返回未包含该项。全部创建/读取反馈、真实计时返回与结局指针见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 追加顺位395/397/399/400/402/404共6份，仍未新增可靠成功GPU候选。397和399虽trajectory成功，实际分别明确CUDA unavailable与Using device: cpu；397首次create失败，按实际Read定位旧脚本，empty不fill对zeros的49–208x不能当GPU收益。395实回CPU attention；400有CUDA分支及完成同步，但返回不报实际设备，保留unknown。402的num_gpu_blocks513是NeuronWorker整数/属性操作，已核实际方法源码；404是Python prefix block元数据、hash及computed标记，非设备缓存读写。写入反馈、实际Read、数值与结局指针见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)和[运行索引](../../data/derived/r2_iso_index.json)。


[实验] 追加顺位380/382/384/385/389/390共6份，仍未新增可靠成功GPU候选。380默认CPU张量加compile eager，wrapper最终None；382虽写有CUDA分支，实际两次均device=cpu。384首次create失败、重建后纯Python分支选择反而0.92x且MISMATCH；385有可选CUDA attention分支，实际三次均CPU-proxy并明确Kernel benchmark skipped，不能按生产MoE任务名归类。389计时LRUEvictor主机元数据，整体变快但add更慢；390 float8量化对照明确device=cpu并带CPU导入stub，10.00x/1.90x不当GPU收益。实际创建/Read/失败、执行返回及结局精确定位与哈希见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)及[运行索引](../../data/derived/r2_iso_index.json)。


[实验] 追加顺位369/370/372/374/377/379共6份，仍未新增可靠成功GPU候选。370/374是数字队列中的明确CPU测量，377虽trajectory成功但实测LRUEvictor主机字典/元数据，evict变快与update回退同时保留；379仅NumPy空数组与Python容器/字符串。沿相邻顺位导航发现369/372有CUDA脚本后补核：369只创建未执行，372最初create被拒、实际Read旧env脚本，后来两个新探针分别因msgspec导入及No CUDA GPUs are available失败。它们不在数字导航队列，代码含CUDA也不构成实际计时；仍按冻结候选顺位及精确工具反馈记录，见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。374 empty未fill与zeros/full不是同等初始化工作，不能把CPU分配差异等同整程序收益。

[实验] 追加顺位349/350/352/355/362/364/365/367仍未新增可靠成功GPU候选。352虽trajectory成功，实际Read为默认CPU张量/NumPy序列化；349/365回显CPU。350的0.046/1.267秒对应成功重建的async generator脚本，生产源码里的CUDA API不等于此脚本调用；367只测env查询/reload。355用人为CPU运算模拟remote get，364把导入失败后改为源码字符串检查和整数block演示，均不能当GPU模型测量。362的1898x向量判断收益与0.89x requantize回退分列，后者empty输入及重复原位改也限制外推。数字视图已补识别async def/time调用，仅改善源代码导航；逐条实际脚本、成功/失败反馈、数值及结局指针见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 追加顺位330/334/335/337/339/340/345/347仍未新增可靠成功GPU候选。337/340/345/347虽trajectory成功，实测分别为NeuronWorker配置整数、Python列表划分、逻辑PhysicalTokenBlock元数据、NumPy ngram。337方法名initialize_cache、345输出Free GPU blocks不构成设备分配证据，已核对实际方法源码。335约43ms含20次sleep(0.002)；334仅NCCL模块导入/元数据/地址解析，339只选backend与创建配置，均非实际GPU传输或解码。330明确回显CPU。340新路径更慢且checksum不同，不将其当等价加速。实际成功写入/Read、失败反馈、数值返回与结局定位见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 追加顺位310/312/315/317/320/322/324/329仍未新增可靠成功GPU候选。312虽trajectory成功，创建失败后实际Read是默认CPU张量切片/分配；310/315/324明确回显CPU；317是NumPy ngram，322为CPU序列化。320的GPU分支因缺依赖被SKIP，实际只测CPU；empty仅初始化首元素再求和，不具相同初始化工作。329实际源码仅管理PhysicalTokenBlock元数据，Device.GPU标签不意味着设备分配/执行。324的empty(no fill)也不自动证明整个程序数值等价。全部写入反馈、实际Read、数值及结局精确指针见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 追加顺位290/295/297/300/302/304/305/307仍未新增可靠成功GPU候选。297和307虽在trajectory记成功，实测分别为token列表/block元数据及默认CPU SDPA；295和305的实际脚本有条件CUDA分支和同步，但返回未说明实际设备，保留unknown。302拟创建失败后读到环境变量查询/hash脚本，新增配置路径又因import失败未完成；304的CPU tensor conversion收益与其他padding回退分别保留。300的CPU循环计时没有被当前数字导航抓到，直接核对原文的`agent_steps[38].tool_results[0].result`补入，说明导航不是完整性证明。精确写入反馈、实际脚本、数值返回和结局指针见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 追加顺位279/282/284/285的复核仍未新增可靠成功GPU候选。279与282的trajectory虽成功，279分配/采样探针明确回显CPU、其他验证默认CPU/Python列表；282拟创建被拒后Read到的是环境变量查询和模块reload主机计时。284的“CUDA graph batch info”只是优化对象名称，实测均on cpu；285最后实际脚本回显RotaryEmbedding.forward_native CPU及import失败/成功耗时。写入反馈、实际Read与数值定位见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[实验] 新增顺位66/262/264/265/267/269/270/272/274的逐条复核：270在trajectory成功，但两个数字返回均明确device=cpu；272成功但实测仍是block元数据。267最初create失败，实际Read的旧脚本默认CPU，后来调整CPU导入兼容性而非切到GPU。264实际回显CPU分配，265注释forward_cuda而代码明确device=cpu；269的7.50x/13.04x来自调度循环模拟，其生成器对照反而为0.99x/0.98x。66是DummyTokenizer，262是OrderedDict驱逐元数据，274是主机bytes编解码。完整写入反馈、Read与数值定位见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)，不将导入CUDA模块、算子名称或模拟收益记入GPU配额。

[实验] 新复核的252虽在trajectory记成功，step18只计时token列表与block分配/标记元数据；源码中的`num_gpu_blocks`是逻辑配额，不是GPU张量执行证据。231对DummyTokenizer和合成请求统计计时，237实际回显`device=cpu`；260创建成功后又替换为默认CPU张量模拟运算，不能按最早的FlashAttention计划归类。255读到了Triton attention源码，但数值来自另一个allocator脚本，缺具体设备输出，保留unknown。各例的工具输入、写入反馈、源码读取与数值返回精确指针见[资格复核](../../data/annotations/r2_iso_eligibility_reviews.json)。

[推断] 仍需按冻结顺位复核数字计时及其实际脚本，将设备选择、完成同步、测量对象与导出结局关联，才能确定最终样本和真实缺口。目前不能宣称正式目录绝无其他GPU会话，也不能用CPU或未同步提交计时降低标准凑够4份。第一轮两份API 400保留在原标注中，继续排除于本轮行为统计。
