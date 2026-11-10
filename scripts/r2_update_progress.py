"""Replace only a delimited Round 2 access audit; preserve all first-round prose."""
import json
from r2_io import ROOT,RAW,now

START='<!-- r2-access-audit:start -->';END='<!-- r2-access-audit:end -->'

def main():
    records=[json.loads(l) for l in (RAW/'r2_manifest.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    ok={r['path'] for r in records if r['status']==200};fail=[r for r in records if r['status']=='failed']
    block=START+'\n\n## 第二轮资源访问失败审计\n\n'
    block+='记录失败URL、时间与原始错误；同URL后续成功不删除历史失败。全部请求见`data/raw/r2_manifest.jsonl`。\n\n'
    block+='| 时间（香港） | URL | 错误 | 状态 |\n|---|---|---|---|\n'
    for r in fail:
        msg=r['error'].replace('|','/').replace('\n',' ')
        block+=f"| {r['accessed_at']} | {r['url']} | {msg} | {'同源后续取得' if r['path'] in ok else '本次未取得'} |\n"
    block+='\n更新时间：'+now()+'。\n\n'+END
    p=ROOT/'outputs/PROGRESS.md';body=p.read_text(encoding='utf-8')
    if START in body:
        a=body.index(START);b=body.index(END,a)+len(END);body=body[:a]+block+body[b:]
    else:body+='\n\n'+block+'\n'
    p.write_text(body,encoding='utf-8')
    print('round2 access failures',len(fail),'recovered paths',sum(r['path'] in ok for r in fail))

if __name__=='__main__':main()
