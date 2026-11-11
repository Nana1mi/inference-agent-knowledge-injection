"""Close the remaining ISO census using explicit export fields only.

Never inspect tool text, prompts, source code, or natural-language final reports.
Missing GPU fields stay unknown; this is not a performance reproduction.
"""
import hashlib
from collections import Counter
from r2_io import ROOT, RAW, DERIVED, ROUND, load, dump, now


GPU_POINTERS = [('gpu_measurement',), ('has_gpu_measurement',),
                ('evaluation', 'gpu_measurement'), ('metrics', 'gpu_measurement')]


def locate(obj, tokens):
    for token in tokens:
        if not isinstance(obj, dict) or token not in obj:
            return None
        obj = obj[token]
    return obj


def evidence(path, pointer, value):
    return {'file': path.relative_to(ROOT).as_posix(), 'pointer': pointer,
            'value': value, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    index = load(DERIVED / 'r2_iso_index.json')
    base = RAW / 'r2_iso' / index['revision']
    plan = load(base / 'selection.json')
    manual = load(ROOT / 'data/annotations/r2_iso_eligibility_reviews.json')['reviews']
    checked = {r['order'] for r in manual}
    assert len(checked) == 400, 'User stopped manual eligibility reviews at 400'
    runs = {r['run_path']: r for r in index['runs']}
    auto = []
    for c in plan['eligibility_check_order']:
        if c['order'] in checked:
            continue
        r = runs[c['run_path']]
        folder = base / 'candidates' / c['run_path']
        summary_path = ROOT / r['status_evidence']['file']
        success = r['success']
        success_source = evidence(summary_path, '/agent/status', r['export_status'])
        documents = [(summary_path, r['summary'])]
        trajectory = folder / 'trajectory.json'
        artifact = 'summary_only'
        if trajectory.exists():
            d = load(trajectory)
            documents.append((trajectory, d))
            artifact = 'trajectory_fields'
            if isinstance(d.get('success'), bool):
                success = d['success']
                success_source = evidence(trajectory, '/success', success)
        else:
            for path in sorted(folder.glob('*stdout*')):
                try:
                    d = load(path)
                except (ValueError, UnicodeDecodeError):
                    continue
                if not isinstance(d, dict) or d.get('type') != 'result':
                    continue
                documents.append((path, d))
                artifact = 'final_result_fields'
                if d.get('is_error') is True:
                    success = False
                    success_source = evidence(path, '/is_error', True)
                elif d.get('is_error') is False and d.get('subtype') == 'success':
                    success = True
                    success_source = evidence(path, '/is_error', False)
                    success_source['subtype_evidence'] = evidence(path, '/subtype', 'success')
                break
        gpu_fields = []
        for path, doc in documents:
            for tokens in GPU_POINTERS:
                value = locate(doc, tokens)
                if isinstance(value, bool):
                    gpu_fields.append(evidence(path, '/' + '/'.join(tokens), value))
        distinct = {e['value'] for e in gpu_fields}
        gpu = next(iter(distinct)) if len(distinct) == 1 else None
        auto.append({**c, 'success': success, 'success_evidence': success_source,
                     'summary_success': r['success'], 'success_conflict': success != r['success'],
                     'gpu_measurement': gpu, 'gpu_evidence': gpu_fields,
                     'gpu_field_conflict': len(distinct) > 1,
                     'eligible_success_gpu': success is True and gpu is True,
                     'artifact_scope': artifact,
                     'gpu_missing_reason': 'no explicit supported boolean GPU-measurement field' if not gpu_fields else None})
    assert len(auto) == 433 and not checked.intersection(r['order'] for r in auto)
    assert checked | {r['order'] for r in auto} == {c['order'] for c in plan['eligibility_check_order']}
    eligible = {r['order'] for r in manual if r['eligible_success_gpu']} | {
        r['order'] for r in auto if r['eligible_success_gpu']}
    selected = [{**c, 'session_id': f'I{i:02d}', 'selection_basis': 'all available confirmed successful GPU candidates'}
                for i, c in enumerate([c for c in plan['eligibility_check_order'] if c['order'] in eligible], 1)]
    plan['selected'] = selected
    plan['scope_amendment'] = {
        'authorized_on': '2026-11-11', 'manual_stop': 400, 'automatic_fields_only': 433,
        'selection_status': 'final_with_documented_shortfall',
        'old_quota_preserved_for_shortfall_reporting': True,
        'all_other_success_exports_used_for': 'metadata summary only; no inferred step behavior',
    }
    dump(base / 'selection.json', plan)
    combined = []
    by_manual = {r['order']: r for r in manual}
    by_auto = {r['order']: r for r in auto}
    for c in plan['eligibility_check_order']:
        r = runs[c['run_path']]
        if c['order'] in by_manual:
            review = by_manual[c['order']]
            success = r.get('trajectory_success')
            if not isinstance(success, bool):
                success = r['success']
            combined.append({**c, 'method': 'existing_manual', 'success': success,
                             'success_scope': 'trajectory flag when present; otherwise summary flag',
                             'gpu_measurement': review['gpu_measurement'],
                             'eligible_success_gpu': review['eligible_success_gpu']})
        else:
            q = by_auto[c['order']]
            combined.append({**c, 'method': 'automatic_fields_only', 'success': q['success'],
                             'success_scope': q['artifact_scope'],
                             'gpu_measurement': q['gpu_measurement'],
                             'eligible_success_gpu': q['eligible_success_gpu']})
    result = {
        'generated_at': now(), 'status': 'complete_under_scope_amendment',
        'scope': '400 prior manual decisions retained; 433 explicit-field decisions, no manual search',
        'supported_gpu_pointers': ['/' + '/'.join(p) for p in GPU_POINTERS],
        'success_meaning': 'exported agent workflow status, not optimization correctness or paper True Success',
        'counts': {'manual': 400, 'automatic': len(auto),
                   'automatic_success': dict(Counter(str(r['success']) for r in auto)),
                   'automatic_gpu': dict(Counter(str(r['gpu_measurement']) for r in auto)),
                   'automatic_success_conflicts': sum(r['success_conflict'] for r in auto),
                   'combined_success': dict(Counter(str(r['success']) for r in combined)),
                   'combined_gpu': dict(Counter(str(r['gpu_measurement']) for r in combined)),
                   'qualified_gpu_sessions': len(selected)},
        'shortfall': {'sessions_vs_original_6': max(0, 6 - len(selected)),
                      'successful_gpu_vs_original_4': max(0, 4 - len(selected)),
                      'agent_model_categories_vs_original_2': max(0, 2 - len({(r['agent'], r['model']) for r in selected}))},
        'selected': selected, 'automatic_rows': auto, 'combined_rows': combined,
        'limits': ['Missing structured GPU evidence is unknown, not no-GPU execution',
                   'Natural language and elapsed session duration are never measurement evidence',
                   'One qualified microbenchmark cannot establish model/scaffold preferences',
                   'Paper evaluation of patches is distinct from what appears in exported agent logs'],
    }
    dump(DERIVED / 'r2_iso_field_decisions.json', result)
    report = f'''# R2：ISO导出字段结案与样本缺口

2026-11-11｜按用户修订停止人工翻找，保留400份既有判断，余433份只读取结构字段。

[实验] 833个候选全部已处理，字段与逐文件SHA256见[自动判定表](../../data/derived/r2_iso_field_decisions.json)。自动处理433份：381份字段报告流程成功，52份trajectory.success=false，与summary成功字段冲突；433份均无受支持的显式GPU测量字段，因此GPU标为unknown，不能解释为全部未用GPU。未扫描工具正文、自然语言摘要或代码关键词补标签。

[实验] 合并既有判断后，480份保留成功流程字段、353份失败；这是不同层级导出字段的状态汇总，不是性能优化成功率。GPU证据状态为332份未测、500份unknown、1份已核可靠GPU完成计时。全部成功流程导出都用于上述元数据统计，逐步行为分析仍以冻结的KBH样本为主。

[实验] 所有可用的合格GPU会话均已选入[selection.json](../../data/raw/r2_iso/{index['revision']}/selection.json)：I01，原顺位84，TRAE/GPT-5。原最低6份会话仍缺5份，4份成功GPU会话缺3份，2类agent/model缺1类；按用户指示如实保留缺口。已有400份人工复核没有推翻、扩大或继续翻找。

[实验] I01只支持孤立采样函数的GPU微基准，不能据此估计ISO中的模型或scaffold行为分布。第一轮两份API400原标注继续保留在独立文件，不合并入本轮KBH行为统计。[原人工证据与I01定位](../../data/annotations/r2_iso_eligibility_reviews.json)，[首轮ISO标注](../../data/annotations/iso_bench.jsonl)。

[论文] ISO-Bench第5.1节表3报告：TRAE/GPT-5在vLLM的True Success为17.9%，定义同时要求命中正确瓶颈和取得可测性能提升；同一配置在SGLang为86.7%，并非全基准统一低成功率。第4.3节说明正式patch评测另外在H100上执行。[论文v1，第4.3、5.1节及表3](https://arxiv.org/html/2602.19594v1#S5.T3)。官方HTML快照保存在data/raw/r2_iso/paper_2602.19594v1.html，获取记录见r2_manifest.jsonl。

[推断] 本次可核的成功GPU会话不足，与论文在vLLM上观察到的低True Success在方向上相符；但导出可观测性、agent流程状态和论文正式patch评分的定义、环境、分母不同，不能把1/833作为论文成功率的复现，也不能把unknown都归失败。论文SGLang结果较高，同样不由本次日志缺口否定。

[实验] 复现：`python scripts/r2_finalize_iso_fields.py`。自动字段白名单、优先级、冲突及unknown原因均在脚本和逐行判定表中；没有执行任何上游代码或GPU实验。
'''
    (ROUND / 'R2_iso_summary.md').write_text(report, encoding='utf-8')
    print(result['counts'])
    print('Selected', selected, 'shortfall', result['shortfall'])


if __name__ == '__main__':
    main()
