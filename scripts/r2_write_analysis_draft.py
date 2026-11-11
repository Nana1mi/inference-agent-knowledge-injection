"""Render R4 using frozen counts and a separate manual evidence review."""
from collections import Counter
import hashlib
from r2_io import ROOT, DERIVED, ROUND, load, dump

LEVELS = ['照抄代码', '借用思路', '作为对照基线', '读了未用']
GROUPS = ['GLM', '闭源模型', 'DeepSeek']


def table(headers, rows):
    def cell(x):
        return str(x).replace('|', '/').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '| ' + ' | '.join('---' for _ in headers) + ' |'] +
                     ['| ' + ' | '.join(map(cell, row)) + ' |' for row in rows])


def dist(counts, n):
    return '；'.join(f'{k} {v}（{v/n:.1%}）' for k, v in sorted(counts.items(), key=lambda p: (-p[1], p[0]))) if n else '无'


def loc(pins):
    return '；'.join('s' + str(p['step']) + ' L' + ','.join(map(str, p['source_lines'])) +
                     (' → 返回L' + ','.join(map(str, p['tool_result_lines'])) if p['tool_result_lines'] else '') for p in pins)


def yn(value):
    return '是' if value else '否'


def main():
    data = load(DERIVED / 'r2_analysis.json')
    path = ROOT / 'data/annotations/r2_r4_evidence_reviews.json'
    review = load(path)
    byid = {s['session_id']: s for s in data['by_session']}
    sessions = review['sessions']
    revised = {s['session_id']: s for s in sessions}
    models = data['by_exact_model']
    events = review['knowledge_events']
    included = [e for e in events if e['included']]
    sota = {e['session_id']: e for e in included if e['consultation_kind'] == 'SOTA入口'}
    docs = [e for e in included if e['consultation_kind'] == '文档']
    pairs = review['closed_model_pairs']

    def subset(ids, kind=None):
        return [e for e in included if e['session_id'] in ids and (not kind or e['consultation_kind'] == kind)]

    def levels(evs):
        counts = Counter(e['adoption_level'] for e in evs)
        return [counts[k] for k in LEVELS] + [counts[None]]

    def compact_knowledge(sid):
        e = sota.get(sid)
        ds = subset([sid], '文档')
        return ('s' + str(e['step_id']) + ' ' + e['adoption_level'] if e else '未见SOTA读取') + \
               f'；文档{len(ds)} / 借用{sum(x["adoption_level"] == "借用思路" for x in ds)} / 未分级{sum(x["adoption_level"] is None for x in ds)}'

    def document_evidence(e):
        text = e['evidence_note']
        if e.get('idea_evidence'):
            a = e['idea_evidence']
            text += ' 可见' + ('推理' if a['origin'] == 'thought' else '代码注释') + '原文：' + a['excerpt'][:180]
        return text + ' 定位：' + loc(e['followup_evidence'])

    aggregate = {'version': 1, 'review_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                 'frozen_manifest_sha256': review['frozen_manifest_sha256'],
                 'legacy_category_events': len(events),
                 'reference_background_events': sum(e['source_kind'] == '参考实现' for e in events),
                 'consultation_events': len(included), 'sota_events': len(sota), 'document_events': len(docs),
                 'excluded_implementation_or_snippet_events': sum(not e['included'] and e['source_kind'] != '参考实现' for e in events),
                 'adoption_levels': LEVELS, 'by_group': {}, 'by_exact_model': {}, 'pairs': pairs}
    for grouping, groups in [('by_group', GROUPS), ('by_exact_model', list(models))]:
        for group in groups:
            members = [s for s in sessions if s['model_group' if grouping == 'by_group' else 'model'] == group]
            ids = [s['session_id'] for s in members]
            aggregate[grouping][group] = {'sessions': ids, 'n': len(ids),
                'profile_attempt_before_first_modification': sum(s['attempt_before_first_code_write'] for s in members),
                'profile_support_before_first_performance_edit': sum(s['profile_support_before_first_performance_edit'] for s in members),
                'sota': {'events': len(subset(ids, 'SOTA入口')), 'levels_then_ungraded': levels(subset(ids, 'SOTA入口'))},
                'documents': {'events': len(subset(ids, '文档')), 'levels_then_ungraded': levels(subset(ids, '文档'))}}
    dump(DERIVED / 'r2_r4_analysis.json', aggregate)
    c = [
        '# R4：优化偏好与环境知识使用（修订初稿）',
        '2026-11-11｜14份KBH会话、3345步首标保持冻结；150步盲复标及κ尚待完成。按用户最新定义新增证据复核层，不回写首标。',
        '背景说明：14份都在第1–3步读取参考实现，这是读取题目定义，不计知识查阅。修订后可见：13份读取SOTA，其中3份只作对照基线，10份未见采用；首次修改前实际尝试profile为1/14，首次性能改动前有profile支撑为3/14。两个profile指标回答不同问题，下面按模型与同任务逐对展开。',
        '数据与重建：[冻结首标清单](../../data/annotations/r2_frozen/manifest.json)、[冻结分布统计](../../data/derived/r2_analysis.json)、[手工证据复核](../../data/annotations/r2_r4_evidence_reviews.json)、[修订统计](../../data/derived/r2_r4_analysis.json)。运行`scripts/r2_analyze_frozen.py`及`scripts/r2_write_analysis_draft.py`重建；后者读取已复核判断，不自动推测采用或性能动机。原始URL、文件、行号和输入哈希逐项保存在JSON。',
        '## 问题A：agent的优化偏好是什么？',
        '每个decision_step只有一个主要阶段、工具用途与层次标签。百分比分母是该模型的步骤数，不是工具调用数、独立实验数或实际用时。等待占步骤；阶段耗时保持null。题目已指定优化对象，层次分布只描述题目允许的范围。',
    ]
    for field, title in [('phase', '按模型的阶段分布'), ('tool', '按模型的工具用途分布'), ('layer', '按模型的层次分布')]:
        c += ['### ' + title, table(['模型', '会话 / 步骤', '类别：次数（占该模型步骤）'], [
            [m, ','.join(s['sessions']) + ' / ' + str(s['steps']), dist(s[field], s['steps'])] for m, s in models.items()])]
    c += [
        'GLM-5.3的修改与测量各占29.2%和31.7%；GPT-5.6-sol三份会话测量占40.3%、等待占24.8%，profile阶段7步（1.1%）。Claude-opus-5仅一个TopK样本；Claude-opus-4-8两份样本等待151/388步。任务、预算、硬件和导出可见性共同影响分布，不能解释成模型排名。',
        '### 观察3：profile尝试与性能决策支撑',
        '**(a) 首次修改前是否实际尝试profile。** 首修改计可执行文件的首次创建/改写，包括独立数学/计时探针；排除计划、笔记、下载和纯环境准备脚本。不能只取冻结phase=修改代码首步：K03有s17的shell基线脚本，K11有s8的dense探针，K14有s7的校准脚本，早于旧标签首步。旧值另存于证据JSON。实际运行ncu/nsys/torch.profiler即为尝试；安装检查、计划、普通benchmark、CUDA events、clock64和静态PTX检查不算。',
        '**(b) 首次以性能为目的修改前，是否有profile数据支撑。** 纳入正式候选和目标算子的scratch替代算法原型；排除明确“先得到正确基线”、数学/编译/接口修复，以及仅创建计时/校准/配置扫描脚本。首版有独立性能目的则计入。需要此前真实返回profile结果，并有可见推理/注释将结果用于决策；一般计时支持的优化仍记“无profile支撑”。动机判读依据逐份列明，不能从最终成绩倒推。',
        table(['模型组', '会话数', '(a) 修改前尝试', '(b) 首性能改动前有profile支撑'], [[g, q['n'], f'{q["profile_attempt_before_first_modification"]}/{q["n"]}', f'{q["profile_support_before_first_performance_edit"]}/{q["n"]}'] for g, q in aggregate['by_group'].items()]),
        table(['具体模型', '会话', '(a)', '(b)'], [[m, ','.join(q['sessions']), f'{q["profile_attempt_before_first_modification"]}/{q["n"]}', f'{q["profile_support_before_first_performance_edit"]}/{q["n"]}'] for m, q in aggregate['by_exact_model'].items()]),
        table(['会话 / 模型', '首修改 / 首性能修改', '(a) / (b)', '基线排除及性能动机'], [[s['session_id'] + ' / ' + s['model'], str(s['first_code_write_step']) + ' / ' + str(s['first_performance_edit_step']), yn(s['attempt_before_first_code_write']) + ' / ' + yn(s['profile_support_before_first_performance_edit']), s['performance_edit_rationale'] + ' 定位：' + loc(s['performance_edit_evidence'])] for s in sessions]),
        '没有自动排除所有首版。K01有输出折叠和coalesced加载，K05有单launch目的，K08有不落state的持久递推，K11有共享激活，K12有免host同步；首版已见具体性能目的。K02/K03/K04/K06/K07/K09/K14则有明确正确基线阶段。K13的s24只是floor探针，首次目标TopK性能原型为s32，不能拿晚至s85的正式文件作为首次性能实现。',
        table(['会话 / 模型', '实际首尝试步 / 首次可见数据步', '结果与失败原因'], [[s['session_id'] + ' / ' + s['model'], str(s['first_profile_attempt_step']) + ' / ' + str(byid[s['session_id']]['first_successful_profile_step']), s['attempt_result_note'] + (' 定位：' + loc(s['attempt_evidence']) if s['attempt_evidence'] else '')] for s in sessions]),
        '首次修改前只有K13尝试且成功；其余13份在这个窗口内未尝试，不填成“profile失败”。表中另列后续首试失败：属性名错误、可执行路径不存在、Python编码异常、导入路径错误、计数器权限不足。K07调用后缺少可见结果，原因无法判定；K10的后台返回/CPU tracing警告不能当GPU profiling失败。None表示未观察到。',
        table(['有支撑会话', '此前数据 → 性能决策'], [[s['session_id'], s['support_note'] + ' 定位：' + loc([p for p in s['performance_edit_evidence'] if p['step'] in s['support_steps']]) + '；改动s' + str(s['first_performance_edit_step'])] for s in sessions if s['profile_support_before_first_performance_edit']]),
        'GLM从(a)0/6变为(b)2/6（K03、K04）；闭源两项均0/6；DeepSeek两项均1/2（K13）。这是会话计数，不做跨任务性能均值。K04没有闭源同任务样本；配对内变化只出现在MoE的K03。',
        '口径敏感性：K03的s19 dense GEMM和s25 TMA dense原型用于组件/codegen校准，主表不算目标MoE性能实现；若把组件性能原型也算入首次性能修改，则K03首步改为s19、(b)改为否，GLM为1/6、整体2/14。K02的s50实际写的是完整grouped GEMM＋SwiGLU替代原型，不能仅依其推理中“single expert”的计划文字排除。主表3/14需要连同这一操作定义使用。',
        '### 假设来源',
        '仅以hypothesis非null步骤为分母。保留冻结字段原名：“读源码”“参考实现或SOTA”是旧假设来源类别，不充当本次“知识查阅”次数。不可见推理和操作暗示均限制来源归因。',
        table(['模型', '有假设 / 总步数', '显式 / 暗示', '来源：次数（占有假设步骤）'], [[m, f'{s["hypothesis_steps"]} / {s["steps"]}', str(s['hypothesis_origin'].get('explicit', 0)) + ' / ' + str(s['hypothesis_origin'].get('inferred', 0)), dist(s['hypothesis_source_nonnull_hypotheses'], s['hypothesis_steps'])] for m, s in models.items()]),
        '有假设1564步中，798归读源码、639归模型先验、113归profile、14归旧“参考实现或SOTA”。这些是步骤来源标签，不是知识采用事件或独立样本。',
        '### profile与阶段：同任务逐对比较',
        table(['任务：GLM ↔ 闭源', '步骤；测量/修改/profile', '(a) 尝试前置', '(b) 首性能步 / profile支撑'], [[task + '：' + left + ' ↔ ' + right, ' ↔ '.join(str(byid[s]['steps']) + '；' + '/'.join(str(byid[s]['phase'].get(k, 0)) for k in ['测量', '修改代码', 'profile']) for s in [left, right]), yn(revised[left]['attempt_before_first_code_write']) + ' ↔ ' + yn(revised[right]['attempt_before_first_code_write']), ' ↔ '.join('s' + str(revised[s]['first_performance_edit_step']) + ' / ' + yn(revised[s]['profile_support_before_first_performance_edit']) for s in [left, right])] for task, left, right in pairs]),
        'KDA两对与TopK两对的(b)均为否↔否。MoE保留两个GLM版本：K02对K11/K12仍是否↔否；K03对K11/K12为是↔否。KDA和这四份MoE榜单均失败，TopK三份均成功，结局不反向认证机制。DeepSeek K13/TopK与K14/MoE只作补充，未替换原闭源配对。',
        '## 问题B：知识放在环境里时，agent怎么用？',
        '### 原观察1改为背景：参考实现是题目定义',
        '知识查阅只计SOTA入口和实际返回的文档：README、教程、API签名/文档注释、主动查询的技能规范。API文档可位于源码文件，但纯实现正文、目录、搜索片段和零散版权/尾注不计。混合返回只计确实返回的文档内容。参考实现的输入、数学和接口核对全部排除，冻结原标签保持不变。',
        table(['模型组', '会话', '读取题目参考 / 首次步', '计入知识查阅？'], [[g, ','.join(q['sessions']), f'{q["n"]}/{q["n"]}；' + ','.join(s + ':s' + str(byid[s]['first_knowledge_access']['参考实现']['step']) for s in q['sessions']), '否'] for g, q in aggregate['by_group'].items()]),
        table(['任务：逐对', '参考首次步 GLM ↔ 闭源'], [[task + '：' + left + ' ↔ ' + right, str(byid[left]['first_knowledge_access']['参考实现']['step']) + ' ↔ ' + str(byid[right]['first_knowledge_access']['参考实现']['step'])] for task, left, right in pairs]),
        '### 观察2：四级采用与证据缺口',
        table(['会话 / 模型', '首SOTA读取步', '读取之前的阶段', '首文档步'], [[s['session_id'] + ' / ' + s['model'], s['first_knowledge_access'].get('SOTA入口', {}).get('step', '未见'), '；'.join(f'{k}×{v}' for k, v in s['first_knowledge_access'].get('SOTA入口', {}).get('before_phase_counts', {}).items()) or '无可列前置阶段', min((e['step_id'] for e in docs if e['session_id'] == s['session_id']), default='未见')] for s in data['by_session']]),
        '四级：**照抄代码 / 借用思路 / 作为对照基线 / 读了未用**。照抄须有可核验代码搬运；借用须在可见推理或代码注释找到具体方法及后续实施。只有调用名/结构相似而缺这种证据的，保留“证据不足、未分级”，不另造第五级，也不强行填“读了未用”。读了未用表示未见可辨识采用，仍可能帮助排除方案。类别不等同收益或合法性。',
        f'旧85个来源事件拆为：参考{aggregate["reference_background_events"]}次（背景）、纯实现/片段{aggregate["excluded_implementation_or_snippet_events"]}次（排除）、知识查阅{len(included)}次＝SOTA {len(sota)}＋文档{len(docs)}。同一步同类多文件合并，不是文件数、唯一知识量或独立实验数。文档{sum(e["adoption_level"] is not None for e in docs)}/{len(docs)}次足以分级，其余保留证据缺口。',
        table(['模型组 / 来源', '事件数', *LEVELS, '证据不足未分级'], [[g + ' / ' + kind, len(subset(q['sessions'], kind)), *levels(subset(q['sessions'], kind))] for g, q in aggregate['by_group'].items() for kind in ['SOTA入口', '文档']]),
        table(['具体模型 / 来源', '事件数', *LEVELS, '未分级'], [[m + ' / ' + kind, len(subset(q['sessions'], kind)), *levels(subset(q['sessions'], kind))] for m, q in aggregate['by_exact_model'].items() for kind in ['SOTA入口', '文档']]),
        'SOTA：GLM读取6/6，1份作基线、5份未见采用；闭源读取5/6，1份作基线、4份未见采用，K10未见读取；DeepSeek读取2/2，1份作基线、1份未见采用。3份基线均为TopK的K05/K09/K13，不能记为借用新的性能算法。本定义下未确认“照抄代码”事件；旧K14的两次helper复制来自题目参考，已排除。',
        table(['任务：逐对', 'GLM：SOTA；文档/借用/未分级', '闭源：SOTA；文档/借用/未分级'], [[task + '：' + left + ' ↔ ' + right, compact_knowledge(left), compact_knowledge(right)] for task, left, right in pairs]),
        '### 十份SOTA未采用：逐份原因',
        '区分已证客观障碍与agent明确表态。“可能不支持SM120”是兼容性警告，不是已运行失败，不自动构成拒绝动机。无迹可循指现有导出不足判定原因。',
        table(['会话 / 模型', '读取步', '原因类别', '依据与限制', '原始定位'], [[e['session_id'] + ' / ' + e['model'], e['step_id'], e['nonadoption_reason_category'], e['evidence_note'], loc(e['followup_evidence'])] for e in sota.values() if e['adoption_level'] == '读了未用']),
        '合计：客观硬件/接口障碍2份（K04缺依赖、K06数值接口不等价），明确拒绝vendor调用1份（K14），无迹可循7份。前两份不能进一步称为agent自述的放弃动机；禁止直接调用vendor不等于禁止借鉴算法。',
        '### 文档采用的可见证据',
        table(['会话 / 模型；读取步', '文档', '采用 / 证据状态', '推理或代码注释及后续定位'], [[e['session_id'] + ' / ' + e['model'] + '；s' + str(e['step_id']), e['document'], e['adoption_level'] or '证据不足、未分级', document_evidence(e)] for e in docs]),
        'K08深度文档的base-2 gate→ex2对应s21注释；K09规范的5次基线/2σ对应s232–234推理；K12 join/split对应s35注释。GPT部分会话只导出推理标题，因此“未分级”差异也反映可见性，不能当采用能力差异。',
        '### 与榜单结局的关系',
    ]
    outcome_rows = []
    for g in GROUPS:
        for outcome in ['success', 'failure']:
            ids = [s['session_id'] for s in sessions if s['model_group'] == g and s['published_outcome'] == outcome]
            if ids:
                outcome_rows.append([g + ' / ' + outcome, len(ids), len(subset(ids)), *levels(subset(ids))])
    c += [table(['模型组 / 榜单结局', '会话数', '知识事件数', *LEVELS, '未分级'], outcome_rows),
          '成功与失败会话都出现文档借用。SOTA基线3份均在TopK成功会话，但这是按任务与结果分层抽取，没有知识随机分配。事件在会话内聚集，不能把38个事件当独立样本估计知识注入收益。',
          '### 三个原文定位片段']
    cases = [
        ('K05', '对照基线', 's7 L18请求、L19返回torch.topk包装；s19–20 L50–53另写并运行scratch/base.py，返回各shape计时。归对照基线，不归性能算法借用。'),
        ('K08', '文档借用', 's18 L47请求deep-dive及实现、L48返回含base-2指数优化的文档；s21 L53–54新增候选，注释说明保持base-2 gate以映射ex2。只计文档片段，未调用FlashKDA扩展。'),
        ('K03', '正确基线后才有profile支撑的性能改动', 's37/40建立正确Triton基线；s54 L170请求NCU、L173返回13.20ms及16.64% achieved occupancy，s55/56 L174–181解释限制，s58 L185–186开始CUDA替代原型。故(a)否、(b)是。'),
    ]
    for sid, title, explanation in cases:
        c += ['**' + sid + '：' + title + '**', explanation + ' [' + sid + '原始导出](' + byid[sid]['source_url'] + ')；本地源文件：`' + byid[sid]['raw_file'] + '`。']
    c += ['### 初稿边界', '这些样本支持分别记录查阅、可见采用、基线用途、拒绝/客观障碍和性能决策证据，不支持知识注入的因果效果或模型总体排名。配对非随机实验；版本、硬件、预算、可见性仍有混杂。150步同一标注者重复标注尚未完成，κ不伪填；本次R4证据复核不能替代盲复标。']
    ROUND.mkdir(parents=True, exist_ok=True)
    (ROUND / 'R4_analysis.md').write_bytes(('\n\n'.join(c) + '\n').encode('utf-8'))
    print('Wrote revised R4 and r2_r4_analysis.json from frozen counts + manual evidence review')


if __name__ == '__main__':
    main()
