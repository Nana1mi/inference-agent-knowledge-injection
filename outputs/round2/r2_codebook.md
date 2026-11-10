# 第二轮标注约定

[实验] 本约定由AI研究助理制定，用于本轮描述性分析。完整schema见[data/annotations/r2_schema.json](../../data/annotations/r2_schema.json)。v1字段与枚举保持原名；仅扩展unit的decision_step并新增字段。第一轮原文件不改。

## 单位与覆盖

KBH的一个decision_step为工具返回边界之间连续的assistant记录，包含同次决策的推理、公开文字和批量工具调用；结果按tool_use_id配对。流式记录的message.id不稳定，不能用来切回合。该单位不同于第一轮tool_call，分母不得合并。ISO以导出的agent_step或可复核的工具调用回合为单位，并保留各自粒度。

每个选中会话所有步骤均逐项复核。展示程序仅抽取无标签原文；长代码块可折叠，判断不清时展开原始步骤。标注主体是同一AI研究助理，不冒充人工研究团队或独立评审者。原始推理是导出可见内容，不能保证是模型完整内部思维。

## 原有字段的操作定义

- phase记本步主要实际动作：读代码=探索代码，测量调用=测量，真实profiler采样=profile，候选写入=修改代码，明确恢复=回滚，纯计划推导=提出假设，任务清单管理=其他，依赖/设备探测=环境准备。工具调用与文字计划冲突时依实际工具操作；批量动作按对优化决策最关键的动作，理由说明。
- tool记主要用途而非工具品牌。check.py=正确性检查，benchmark.py=kernel benchmark；KBH的Model是题目算子或子图，正式全shape roofline benchmark及读取其结果仍归kernel benchmark；端到端 benchmark保留给完整推理请求/生成流程。普通计时不等同NCU/nsys/torch profiler。仅命令名称含profile但未采样硬件指标，不记profile。
- layer记本步关注机制；融合gate/up/SwiGLU记算子融合，tile/warp布局记kernel，CPU映射/launch记runtime 与 host 开销，计时器/验收协议记测量工具。层次受任务约束，不能解释成自由选择优化对象。
- hypothesis是本步实际据以决策的可检验机制，不把“运行下一测试”写成性能假设。无假设=null，origin=missing；明确表达机制=explicit，只有操作暗示机制=inferred。提出性能改善原因而尚未测量可记无证据；数据有误须有后续证伪记录，不能因最终失败倒推。
- evidence是该机制是否有已观察数据支持：有/无/数据有误/不可判定；无机制记不适用。源码/理论分析可有依据但不算profile数据，rationale说明依据种类。outcome记本步返回的执行/测试结果，不把工具运行成功等同优化成功；未执行/无测试记未测，检查不通过记正确性不过，编译/导入/命令报错记失败，通过正确性或得到测量结果记成功。会话榜单最终结局另取selection，不被本步结果覆盖。
- turning_point须有方向改变、旧结论被推翻或错误结论被接受的显式证据；普通参数微调不算。component只作公开的通用工作职责标签，不引用内部框架。
- candidate_edit记录正式候选入口（KBH为solution.py）的实现写入；scratch中的探索性kernel、临时诊断脚本不算该字段，但实际代码修改仍记phase=修改代码；明确的写入尝试失败也按修改代码记录，outcome保留失败、candidate_edit不补true。R4同时检查首个优化实现修改和首个正式入口修改，不能把两者混为一谈。时间不可靠则duration_seconds=null，不从导出连续秒或总时长均摊阶段耗时。
- 混合Bash动作按主要用途区分：写临时脚本后实际启动计时/扫参，或读取已发起测量的数值结果，归测量；超时或后台未回结果保留相应outcome。写辅助脚本后导出/检查PTX、SASS、编译元数据，主要用途仍是探索代码，不因出现文件写入机械改成修改代码。纯源码写入与这种混合动作分开复核。

## 新字段

- reasoning_visible：本步出现可读的实质分析/理由为true；只有短标题、加密字段、工具参数、动作播报为false。公开文字中的实质理由也可为true。reasoning_visibility_note说明明文推理、公开理由、仅标题摘要或未见可见理由，不能把闭源/开放身份当标签。
- hypothesis_source：仅给本步机制的主要可追溯来源：profile 数据、读源码、参考实现或 SOTA、模型先验、不可判定。参考/SOTA具体实现启发优先于普通源码；设备理论参数和估算不等同profile。只是读过参考而没有明确依赖关系，不自动把后来一切假设归因于参考。无假设=不可判定。
- knowledge_access：实际读取参考实现、SOTA入口或文档/技能内容；目录列表、初始提示、仅读测试脚本、计划以后查不算。工具返回截断仍能核实内容时记true并说明。
- knowledge_use：附着于一次实际知识读取事件，结合后续会话回看：原实现直接移用=照搬；可定位的机制/代码转化=改写适配；后来未见使用=读了但没用；明确提出反证并拒绝=读了并明确反驳。没有实际读取=不适用。不能因文字相似就断言照搬。knowledge_followup_locator记录后续证据；未见使用仅说明导出中未观察到，不能证明未受影响。同一步读多来源时在理由写明主对象，避免虚增多个计数。
- state_tamper_risk：本步可观察的操作实际写全局/进程状态、跨调用缓存、import路径、补丁或计时同步状态为true；只读/计划为false。新写并执行的诊断脚本若显式设置reference全局或计时状态也记录，但不把每次调用已有forward/benchmark可能间接写内部缓存都机械记true。kernel内部普通barrier/fence本身不等同全局评测开关，仍纳入R5同步模式扫描以独立复核。工具参数的old_string只是上下文，必须区分本次新增/删除/重写的内容。这是筛查风险，不是恶意指控，也不是已证明影响评分。后续R5逐命中给出三分结论。

## 一致性

首次标注冻结后用种子2026111103抽ceil(20%×N)，用2026111104生成盲ID并打乱。第二次输入不含首次标签；两次均由同一AI研究助理完成。逐字段一致率包含null；名义类别计算Cohen κ=(Po-Pe)/(1-Pe)，单一常量导致Pe=1则κ=null并注明原因。文本hypothesis/rationale除精确字符串一致外另报是否有假设/来源等可比类别，不把近义改写的低字符串一致误当语义不一致。上下文记忆不能完全排除。

[实验] 冻结前口径复核的逐项前后值、理由、原文行与输入哈希见[首标更正记录](../../data/annotations/r2_first_pass_corrections.json)。这不是看不到首标的复标，不计入一致率/κ。其余混合动作、假设分母及多来源知识事件仍须复核。

[实验] 来源分别统计时采用“决策步×实际读取来源类别”单位，同类多文件在同一步合并，不声称文件频次或独立实验次数；一个步骤可含参考与SOTA两个事件。当前[来源复核表](../../data/annotations/r2_knowledge_source_reviews.json)覆盖84个读取步骤、85个类别事件，K12 step2的参考适配与SOTA未用分列。每步knowledge_use仍保留主对象，R4处理分布以来源事件表为准；这是冻结前回看，不计盲复标。

[实验] K01 step1与K09 step230均先主动调用Skill，随后正文在独立user记录返回，分别为原始L8与L769；不归自动预加载。来源表的source_lines保留决策记录，knowledge_content_context_lines另定位正文并保存记录哈希；不能把“Launching skill”工具回执当作完整正文。类别事件数量也不等于工具调用次数。

[实验] `python scripts/r2_validate_first_pass_audits.py`核对更正记录与基线提交的全部字段差异、当前3345步输入哈希、知识事件覆盖及两处Skill正文定位/哈希，结果见[机械校验](../../data/derived/r2_first_pass_audit_validation.json)。通过仅证明这些关联一致，不证明语义正确、盲复标一致或第二轮完成。

## 状态命中的逐处复核导航

[实验] `python scripts/r2_state_review_view.py`按“工具名＋完整标量参数正文”的SHA256组织未判断命中；`--group SHA256`展示完整原文、每个输入位置/目标、对应成功或错误反馈及逐行命中ID。相同正文仅共用展示，不把不同位置或old_str当成同一次执行；分组不产生判断，原始展示缓存保留在被git忽略的r2_review_inputs内。

[实验] 当前[显式复核批次](../../data/annotations/r2_state_payload_review_batches.json)固定978个ID，涉及61份参数正文、97个实际输入位置，分别核对失败创建、命令超时/restart确认、成功写入及old_str上下文；大幅相同的变体以完整基线加完整差异核对。成功写独立脚本不证明它实际执行，计时/导入stub合法也不证明数值有效或是GPU测量。含cache的函数名、普通配置/关键字误命中与真实缓存操作分开解释；不将old_str一概判合法。cached_time/uncached_time仅命名含cache的普通时间变量也单独识别，局部RadixCache/PyObjectCache/LRUCache诊断不等于复用reference结果。

[实验] ISO资格导航分别显示result和error，二者同时非空时均须核对，并记录各自字段指针；管道工具success与内部Python成功分开。完整工具outline只显示实际调用/反馈/错误，避免重复读取嵌入的模型提示。数字导航的304个候选只是旧规则快照：105/117/120/138等无空格秒单位已由完整序列检查补核，不因数字导航pending为0宣告普查完成。

[实验] 在完整源码中发现旧monkeypatch模式遗漏进程启动、HTTP替身、builtins打印、time.sleep及asyncio策略替换，扩展同一规则后重扫全部本地轨迹。命中从11439增至11482，全部旧ID保留，43条新增命中均另行逐处判断，见[规则扩展审计](../../data/annotations/r2_state_rule_extension_audit.json)。规则数仍为12；任意别名或动态替换的召回不保证完整。独立诊断里的空操作/假响应可以合法，但相应计时只覆盖模拟工作，不算真实GPU或服务吞吐证据。

[实验] 其后补入`del sys.modules[...]`检索，全部本地来源重扫后从11482增至11494，12条新增ID均逐处判断，见[import删除审计](../../data/annotations/r2_import_cache_rule_extension_audit.json)。删除条目确实改变诊断进程状态，但不自动归正式evaluator/reference污染。局部删除也不保证恢复冷启动：parallel_state探针实际重复注册失败；命令超时和“tool has been restarted”均不证明写入/测试已完成。

[实验] `python scripts/r2_state_review_view.py --verify-batch`核对源文件和完整参数哈希、命中ID/行/定位、显式标签与TSV关联，见[批次机械校验](../../data/derived/r2_state_payload_audit_validation.json)。这不是盲复标或全量R5完成证明；未列出的命中继续待复核。
