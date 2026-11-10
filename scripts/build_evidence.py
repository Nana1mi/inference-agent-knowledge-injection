"""Write the extraction ledger and exact PDF page locators from archived source text."""
import json
from collect_sources import ROOT, RAW

PAPERS=[
 ('SEIS','2610.04646v1','§3.3、§5.1、§6、附录C/D/F/H','code/report inheritance; correctness gaps','architecture/observational; no isolated report effect'),
 ('KernelSeek','2611.03517v1','§2.5、§5.3、§6、附录D/E','0.50x vs 1.13x reported task comparison','one run per arm; human/front-end/prior-work confounds'),
 ('InferenceBench','2607.20468','§5、附录F/G/Table19','169/180=93.9% in main paper pool','do not mix with current website denominator'),
 ('ISO-Bench','2602.19594','§5、附录A/D','up to 87.2% bottleneck targeting,17.9% true success (project summary)','descriptive; not a knowledge-injection ablation'),
 ('VibeServe','2605.06068','§3.3、§4.3、附录B','no-skill 1100 tok/s ~35 rounds vs full ~10k at60 rounds/25h','unequal reached rounds/time; single setup'),
 ('MetaInfer v1','2607.12875v1','§3.2–3.3、§4.2–4.4','contract knowledge base, source-reference comparisons','do not conflate with v3'),
 ('MetaInfer v3','2607.12875v3','§3–5、§6','execution-adaptation route search','not numerical validation of v1 knowledge-only claim'),
 ('KernelEvolve','2512.23236','§3.2.3–3.2.4、§5','MTIA-specific retrieval and compilation/correctness qualitative claim','no isolated matched-budget quantitative KB ablation located'),
 ('FlashInfer-Bench','2601.00227','§3.1/3.3/3.5、§4.5','trace schema and kernel substitution','trace is workload/solution/evaluation, not agent transcript'),
 ('Glia','2510.27176','§3.3、§4、§5.6、附录A.1','research-process and component ablation','no isolated external-knowledge effect extracted'),
 ('ADRS','2510.06189','§4.2、§6.1–6.4、§7.2.1、附录A/B','search/evaluator design and ablations','no isolated domain-knowledge effect extracted'),
 ('Evaluating AGENTS.md','2602.11988','摘要、§4–5/Tables3/6','inference cost over20%; task success not generally improved','use current downloaded version; file provenance matters'),
 ('Two-Agent Context Ablation','2607.27250','§3、§4','291 completed runs,288 evaluated correctness cells','selective corpus may differ from always-on; agent-specific task selection'),
 ('Stale Instructions','2611.09802','摘要、Results/Tables','22 tasks,732 trajectories; about2 extra calls in test-command case','not all cases show detectable difference'),
 ('CODESKILL','2605.25430','§4/Table2','37.88,39.53,40.35 average pass rate across lifecycle variants','trained manager; no implication that arbitrary cards share the effect'),
 ('Demystifying Skills','2608.14036','§3–4/Table1/Fig3','6.06pp matched skill vs workflow; pool5to100 precision29.6%to3.3%','retrieval precision not equivalent to success'),
 ('ACE','2510.04618','§4.6/Table3、A.5、Table2','incremental-update/reflection ablations; unreliable feedback may degrade','adjacent domain; not serving-engine intervention'),
 ('Scientific Agent Skills','2609.00065','元数据/摘要','method tooling attribution only; current v2 metadata','not included as effect evidence'),
]

def main():
    rows=[]
    for name,ident,locator,claim,limits in PAPERS:
        stem=ident if (RAW/'papers'/f'{ident}.txt').exists() else ident.removesuffix('v1')
        rows.append({'source_id':name,'url':f'https://arxiv.org/html/{ident}','locator':locator,'claim_type':'论文',
                     'extraction':claim,'limitations':limits,'local_source':f'data/raw/papers/{stem}.txt'})
    text=(RAW/'together/paper.txt').read_text(encoding='utf-8')
    searches=[('knowledge_effect','25–31','§4.4/Fig5'),('kb_contents','Expert-curated knowledge base.','C.2.1'),
              ('expert_ensemble','6.2×','C.2.1'),('wait_time','57.0','C.3/Table6'),('gpu_reset','GPU resets.','C.3 NVIDIA')]
    pdf_pages={}
    for sid,needle,locator in searches:
        pages=[i for i,page in enumerate(text.split('\f'),1) if needle in page]
        pdf_pages[sid]=pages
        rows.append({'source_id':'Together/'+sid,'url':'https://www.together.ai/together-compiler-paper',
                     'locator':locator+'; PDF pages '+','.join(map(str,pages)), 'claim_type':'论文', 'extraction':needle,
                     'local_source':'data/raw/together/paper.txt','limitations':'author report; not independently rerun'})
    rows.append({'source_id':'Apple RSI','url':'https://github.com/apple-aiml-research/ml-rsi-inference-bench/tree/1a38072fbe284234c874356b86c9df666a5a79a3',
                 'locator':'README + tasks/*/task.toml + tests/test.sh + third_party/pier/README.md','claim_type':'论文',
                 'extraction':'37 tasks;10 support,20 optimization,7 regression;20vLLM/17SGLang','local_source':'data/derived/rsi_tasks.json',
                 'limitations':'static inspection only; some nested docs inaccessible'})
    out=ROOT/'data/extractions';out.mkdir(exist_ok=True)
    (out/'evidence.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'together_pages.json').write_text(json.dumps(pdf_pages,indent=2),encoding='utf-8')
    print(json.dumps(pdf_pages,indent=2))

if __name__=='__main__':main()
