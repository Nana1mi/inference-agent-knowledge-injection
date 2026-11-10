"""All-task feasibility matrix; reasoning is explicit, never a claim of executed compatibility."""
import json
from collect_sources import ROOT

SPECIAL={
 'regression_multimodal_prefill_ttft':('较有希望的移植候选','Qwen3.5-4B，单请求图像prefill；权重规模较小，但需核验sm86后端/图像峰值内存、原始慢路径能否保留。'),
 'regression_spec_decode_acceptance_drop':('有条件移植','Llama-3.1-8B + 独立EAGLE3，基座权重、drafter和KV必须同时容纳；还需替换或核验FP8 KV/attention后端，可能改变缺陷触发路径。'),
 'regression_mxfp4_moe_decode_throughput':('有条件移植','manifest列模型shards约12.8GiB，理论留有少量缓存空间；原任务是Hopper上的MXFP4 Triton路径，sm86兼容和工作负载峰值尚未测，不能只凭能放权重认定能跑。'),
 'optimize_llada2_mini_1xh100_sglang_open':('不适合原样运行','16.1B BF16仅权重粗估32.2GB，超过单3090；1.4B激活参数不等于只需存1.4B权重，另量化会改变任务。'),
 'optimize_qwen3_6_27b_1xh100_open':('不适合原样运行','27B BF16权重粗估54GB且有长上下文，超过单3090；量化后属于派生实验。'),
 'optimize_qwen3_8_27b_1xb200_dflash2_open':('不适合原样运行','27B主模型还叠加DFlash2；B200路径与sm86不等价，须另定义缩小任务。'),
 'regression_async_spec_decode_throughput':('不适合原样运行','120B MXFP4主模型加独立EAGLE3；单B200任务不等于可用单3090。'),
}

def main():
    rows=json.loads((ROOT/'data/derived/rsi_tasks.json').read_text(encoding='utf-8'))
    text='''# T5附表：逐任务硬件可行性核查

冻结仓库 `1a38072fbe284234c874356b86c9df666a5a79a3`。37行由 `scripts/build_rsi_appendix.py` 从全部 `task.toml` 生成；事实列 `[论文]`（官方仓库），判断列全部 `[推断]`。没有运行这些任务。单RTX3090按24GB作设计假设，不代表本机硬件。

“移植候选”不表示能按官方条件计分。更换GPU、模型、精度、并行或workload必须另报派生实验；团队若有对应数量H100/B200，可按原manifest进一步检查驱动、系统内存、存储、权重许可和离线构建缓存，再做nop/oracle试跑。

| 任务（链接到manifest） | 类别/引擎 | 原硬件 | 单3090判断 | 原因/团队硬件条件 |
|---|---|---|---|---|
'''
    for r in rows:
        count=r['gpus']; gpu='/'.join(r['gpu_types'] or [])
        if r['task'] in SPECIAL: verdict,reason=SPECIAL[r['task']]
        elif count and count>1:
            verdict='不适合原样运行'; reason=f'原任务固定{count}×{gpu}及其多卡/模型部署；单3090不能保持该并行和内存条件。团队需同等型号数量，替换须独立报告。'
        else:
            verdict='未验证，不列首批'; reason='固定Hopper/Blackwell部署或模型/低精度路径；未测sm86兼容及峰值内存，不能据单卡字样认定可运行。'
        text+=f"| [{r['task']}]({r['source']}) | {r['category']}/{r['engine']} | {count}×{gpu} | {verdict} | {reason} |\n"
    text+='\n注意：`support_kimi_linear_48b_4xh100_vllm`的目录名写4x，但manifest的environment.gpus是8，表格优先使用manifest。若不同文件冲突，应在团队试跑前解决，不能自行改成较小需求。\n'
    (ROOT/'outputs/T5_task_feasibility.md').write_text(text,encoding='utf-8')

if __name__=='__main__': main()
