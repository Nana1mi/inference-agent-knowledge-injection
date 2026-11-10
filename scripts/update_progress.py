"""Reconcile all historical access failures with current snapshots in the progress report."""
import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from collect_sources import ROOT, RAW

def main():
    manifest=[json.loads(l) for l in (RAW/'manifest.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    succeeded={r['path'] for r in manifest if r['status']==200}
    failures=[r for r in manifest if r['status']=='failed']
    block='## 阻塞项\n\n'
    block+='原始访问失败均逐条保留下表；同一路径后来取得的标为已恢复，其余保持未取得。不使用镜像或缓存绕过限制。全部成功请求/哈希见 `data/raw/manifest.jsonl`。\n\n'
    block+='| 时间（香港） | URL | 错误 | 当前状态 |\n|---|---|---|---|\n'
    for r in failures:
        error=r['error'].replace('|','/').replace('\n',' ')
        block+=f"| {r['accessed_at']} | {r['url']} | {error} | {'同一路径后来已取得' if r['path'] in succeeded else '本次未取得'} |\n"
    block+='\n其他证据缺口：KernelSeek官方artifact未定位；SEIS论文矩阵原始日志与对应harness未取得；完整公开源未取得的原因见T1。Semantic Scholar限流不解释为没有文献。GitHub连接器的部分大树请求等待后取消，未将取消解释为资源不存在；ISO原始递归树明确truncated=true。\n\n'
    tail='''## 未完成项与交付边界

- T4可选实测未运行，评分器未实现/运行；已交设计、环境记录、协议和知识卡，原因是指定3090环境不可用。
- 原始轨迹无法取得的来源不能满足逐会话标注；已对实际可取得来源抽取两条序列，并明确压缩episode的限制。不伪造数据补齐来源。
- KernelBench结构性标注主要是规则初标，尚无独立第二标注者；不能将初标统计当作普遍agent特性。
- Apple全部37份task.toml已解析，但网络中断的嵌套说明/源码未声称全部读完；未进行框架安装、nop/oracle、硬件兼容或GPU复现。
- 底座、团队硬件/模型/provider、主指标待讨论；本轮没有替团队拍板。

## 复现与终验

离线终验已运行，结果见 `data/derived/validation.json`：标注字段/类型与原始定位、工具返回配对、快照SHA256、37题计数、统计分母及本地链接。该检查不验证科学真伪或GPU正确性。采集失败不影响已保存样本的离线重建。脚本语法编译通过；Together PDF按PDF技能提取并目视核对p10，关键数字页码已建ledger。
'''
    path=ROOT/'outputs/PROGRESS.md';text=path.read_text(encoding='utf-8')
    text=text[:text.index('## 阻塞项')]+block+tail
    text+='\n最后汇总时间：'+datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat()+'。\n'
    path.write_text(text,encoding='utf-8')
    print('historical_failures',len(failures),'recovered_paths',sum(r['path'] in succeeded for r in failures),'success_responses',sum(r['status']==200 for r in manifest))

if __name__=='__main__':main()
