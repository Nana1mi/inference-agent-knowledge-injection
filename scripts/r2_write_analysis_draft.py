"""Render the two-question R4 draft from frozen counts and pinned case evidence."""
from r2_io import ROOT, DERIVED, ROUND, load


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '| ' + ' | '.join('---' for _ in headers) + ' |'] +
                     ['| ' + ' | '.join(str(x).replace('|', '/') for x in row) + ' |' for row in rows])


def dist(counts, n):
    return '；'.join(f'{k} {v}（{v/n:.1%}）' for k, v in sorted(counts.items(), key=lambda p: (-p[1], p[0]))) if n else '无'


def main():
    data = load(DERIVED / 'r2_analysis.json')
    ss = data['by_session']
    byid = {s['session_id']: s for s in ss}
    model_rows = data['by_exact_model']
    observed_prior = sum(s['successful_profile_before_code_edit'] for s in ss)
    content = [
        '# R4：优化偏好与环境知识使用（初稿）',
        '2026-11-11｜按用户修订冻结14份KBH会话、3345个decision_step；150步分层盲复标及κ尚待完成。',
        '当前最清楚的观察：参考实现全部在前3步被读取；SOTA入口读过13份、其中10份未见采用；首次代码修改前仅1份出现成功profile。以下都是这些已选样本中的行为描述。',
        '[实验] 数据来自[冻结首标及哈希清单](../../data/annotations/r2_frozen/manifest.json)，以[统计JSON](../../data/derived/r2_analysis.json)和`scripts/r2_analyze_frozen.py`重建；全文由`scripts/r2_write_analysis_draft.py`生成。模型、任务、榜单结局与原始URL逐会话保存于统计JSON。抽样框和已知结局分层见[R1报告](r2_sampling.md)。',
        '## 问题A：agent的优化偏好是什么？',
        '[实验] 每个decision_step只有一个主要阶段、工具用途与层次标签；百分比分母是对应模型的步骤数，不是工具调用次数、实际用时或独立实验数。等待也占步骤。工具“其他”包含shell、编辑和任务管理，不可据此称模型不使用工具。',
    ]
    for field, title in [('phase', '按模型的阶段分布'), ('tool', '按模型的工具用途分布'), ('layer', '按模型的层次分布')]:
        content += ['### ' + title, table(['模型（文件名）', '会话 / 步骤', '完整类别：次数（占本模型步骤）'], [
            [m, ','.join(s['sessions']) + ' / ' + str(s['steps']), dist(s[field], s['steps'])]
            for m, s in model_rows.items()])]
    content += [
        '[实验] GLM-5.3的修改与测量各占29.2%和31.7%；GPT-5.6-sol这三份会话的测量占40.3%、等待占24.8%，profile阶段仅7步（1.1%）。Claude-opus-5只有一个TopK会话，探索代码167/561步；Claude-opus-4-8的两份会话则等待151/388步。这些差异同时受任务、运行预算、导出方式和环境影响，不能当作跨任务模型排名。',
        '[推断] 本样本更支持“从实现与验证反复推进，再用profile解决具体疑问”的工作序列，而非普遍先profile再动代码。层次标签受题目指定的算子或子图限制，不能解释为agent自由选择优化对象的总体偏好。',
        '### 首次修改前是否做过profile',
        '[实验] “代码修改”沿用首标phase=修改代码，包括辅助探针；正式候选另用candidate_edit字段。成功profile沿用phase=profile且outcome=成功；只发起后失败的profile不算取得结果，也不由此认证硬件采样质量。',
        table(['会话 / 模型', '首代码修改', '首正式候选', '首profile尝试 / 成功', '成功profile早于代码 / 正式候选'], [
            [s['session_id'] + ' / ' + s['model'], s['first_code_edit'], s['first_formal_candidate_edit'],
             str(s['first_profile_attempt']) + ' / ' + str(s['first_successful_profile_step']),
             ('是' if s['successful_profile_before_code_edit'] else '否') + ' / ' + ('是' if s['successful_profile_before_formal_candidate_edit'] else '否')]
            for s in ss]),
        f'[实验] {observed_prior}/14份在首次代码修改前有成功profile；同一份也是首次正式候选前的唯一一例（K13，DeepSeek TopK，第20步profile、第24步辅助修改、第85步正式候选）。其余13份只能说此前未观察到成功profile，不能说全过程从未profile。None表示未观察到该事件。',
        '### 假设来源',
        '[实验] 下表只以hypothesis非null的步骤为分母；无假设步骤不并入“不可判定”稀释分布。显式和操作暗示的假设都保留，名义来源是本步可追溯的主要来源，非模型内部知识的真实起源。',
        table(['模型', '有假设步骤 / 全步骤', '显式 / 暗示', '来源：次数（占有假设步骤）'], [
            [m, str(s['hypothesis_steps']) + ' / ' + str(s['steps']),
             str(s['hypothesis_origin'].get('explicit', 0)) + ' / ' + str(s['hypothesis_origin'].get('inferred', 0)),
             dist(s['hypothesis_source_nonnull_hypotheses'], s['hypothesis_steps'])] for m, s in model_rows.items()]),
        '[实验] 有假设的1564步中，798步归读源码、639步归模型先验、113步归profile数据、14步归参考实现或SOTA。读取参考/SOTA的事件多于14次：来源标签要求该步机制有可定位的依赖关系，不把早期读过知识自动归给所有后续修改。',
        '### 同任务对照：逐对列出',
    ]
    for task, members in data['paired_tasks'].items():
        content += ['**' + task + '**', table(['会话 / 模型 / 榜单结局', '步骤', '测量 / 修改 / profile', '首代码 / 正式候选', '假设来源（次数）'], [
            [s['session_id'] + ' / ' + s['model'] + ' / ' + s['published_outcome'], s['steps'],
             '/'.join(str(s['phase'].get(k, 0)) for k in ['测量', '修改代码', 'profile']),
             str(s['first_code_edit']) + ' / ' + str(s['first_formal_candidate_edit']),
             '；'.join(f'{k} {v}' for k, v in s['hypothesis_source_nonnull_hypotheses'].items())] for s in members])]
    content += [
        '[实验] KDA：GLM K01与Claude K07、GPT K08分别对照，首次代码修改为22对15、22对21步；仅K01后来出现成功profile（第52步），三份榜单都失败。TopK：GLM K05与Claude K09、GPT K10分别为首代码19对29、19对9步；正式候选则26对49、26对9步，三份都在首次修改之后才取得成功profile，榜单都成功。',
        '[实验] MoE：GLM K02/K03分别对照Claude K11与GPT K12，首代码修改为12/40对10/9步；K03和K11后来有成功profile，K02/K12未观察到。四份榜单都失败。两个GLM会话的版本与轨迹不同，保留两行，不平均成一个GLM分数；跨任务也不计算混合平均。',
        '## 问题B：知识放在环境里时，agent怎么用？',
        '[实验] 14/14读取参考实现，首次发生在第1–3步；13/14读取SOTA入口，K10未见读取。下表列出读取前已有的阶段，帮助区分一开始核接口与经历优化后再求助。最早读取库源码、技能及其他网页片段的时间也完整保存在统计JSON。',
        table(['会话', '首参考实现步', '读参考前的阶段', '首SOTA步', '知识类别事件数 / 榜单结局'], [
            [s['session_id'], s['first_knowledge_access']['参考实现']['step'],
             '；'.join(f'{k}×{v}' for k, v in s['first_knowledge_access']['参考实现']['before_phase_counts'].items()) or '无前置步骤',
             s['first_knowledge_access'].get('SOTA入口', {}).get('step', '未见'),
             str(s['source_events']) + ' / ' + s['published_outcome']] for s in ss]),
        '[实验] 合计84个读取步骤、85个“决策步×来源类别”事件；同类多个文件同一步只算一次。K12第2步同时读参考与SOTA，前者适配、后者未见采用，因此分成两个来源事件。以下分母为来源事件，不与步骤标签混算。',
        table(['来源类别', '事件数', '照搬', '改写适配', '读了但未见用', '明确反驳'], [
            [kind, q['events']] + [q['use'].get(k, 0) for k in ['照搬', '改写适配', '读了但没用', '读了并明确反驳']]
            for kind, q in data['knowledge']['by_kind'].items()]),
        '[实验] SOTA的3次适配全部出现在TopK任务（K05/K09/K13），用途是独立torch.topk诊断基线，且参考实现与SOTA本来就是同一算子；不能据此认定采用了3种新性能算法。两次照搬均在K14，复制的是输入构造helper和常量，不是性能kernel。',
        table(['榜单结局', '会话数', '事件数', '照搬', '改写适配', '未见使用', '明确反驳'], [
            [outcome, len(q['sessions']), q['events']] + [q['use'].get(k, 0) for k in ['照搬', '改写适配', '读了但没用', '读了并明确反驳']]
            for outcome, q in data['knowledge']['by_published_outcome'].items()]),
        '[实验] 成功的7份有27/37个适配事件，失败的7份也有34/48个。一个会话可以贡献很多事件，不能把事件当独立样本做成功率检验。这里同时观察到知识适配与成功、适配与失败，不估计知识注入的因果收益。',
        '### 三个原文片段',
    ]
    cases = [
        ('K05', 'SOTA用于诊断基线，没有移入正式候选',
         '第7步读取SOTA：原始L18是工具请求，L19回传torch.topk包装。第19–20步的L50–L53另建并运行scratch基线，返回五种形状的top-k计时。后续正式候选另写，故“改写适配”在此是诊断用途，不能当作新算法注入。', 'L18–L19；L50–L53'),
        ('K11', '读取后排除一条具体架构路径',
         '第87–89步，L296请求读取例程92的CMake/架构配置，L297显示Sm100等声明；L298指出当前设备是Sm120。L299–L300继续查builder，随后L301拒绝这一grouped bf16路径并在L302–L303写入经验。片段支持拒绝这个builder，不能扩大成整个CUTLASS不可用。榜单最终失败不反推这次判断的收益。', 'L296–L303'),
        ('K14', '照搬的是兼容接口与输入构造',
         '第101–103步，L417说明要对齐用户要求的接口，L418–L422读取reference的路由、输入helper和常量；L425写入solution.py保留相应功能语句。性能实现仍是自写kernel，两个“照搬”事件不等于复制oracle forward来通过性能评测。', 'L417–L425'),
    ]
    for sid, title, explanation, locator in cases:
        s = byid[sid]
        content += ['**' + sid + '：' + title + '**',
                    '[实验] ' + explanation + ' 原始定位：[' + sid + '导出](' + s['source_url'] + ') ' + locator +
                    '；本地源文件：`' + s['raw_file'] + '`。来源事件及输入哈希见统计JSON的knowledge.event_provenance。']
    content += [
        '### 初稿的解释边界',
        '[推断] 这些样本中，参考实现主要先用于理解数学与接口；SOTA被读到并不意味着随后采用；知识还会用于建立比较基线、排除不适配路径和补齐接口。这三个用途值得分别设计检索提示与记录字段，不能只统计“读过知识库”。',
        '[实验] 样本是在有榜单结局的框内分层抽取，含任务配对而非随机分配知识条件。模型版本、硬件、时间预算、推理可见性不同；所有阶段耗时保持null。首标已按用户要求冻结，本文为初稿，150步分层重复标注完成后补充一致率/κ及其对解释可靠性的限制，不根据最终结局回改首标。',
    ]
    ROUND.mkdir(parents=True, exist_ok=True)
    (ROUND / 'R4_analysis.md').write_text('\n\n'.join(content) + '\n', encoding='utf-8')
    print('Wrote R4 two-question draft from frozen statistics')


if __name__ == '__main__':
    main()
