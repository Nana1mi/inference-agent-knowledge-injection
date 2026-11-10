"""Extract every task manifest and create a task-level hardware feasibility appendix."""
import json
import tomllib
from collections import Counter
from collect_sources import RAW, ROOT

def main():
    rows=[]
    for p in sorted((RAW/'rsi/files/tasks').glob('*/task.toml')):
        d=tomllib.loads(p.read_text(encoding='utf-8')); m=d.get('metadata',{}).get('inference_bench',{}); env=d.get('environment',{})
        rows.append({'task':p.parent.name,'description':d['task']['description'], 'category':m.get('category'),
                     'engine':m.get('engine'), 'gpus':env.get('gpus'), 'gpu_types':env.get('gpu_types'),
                     'model':m.get('model'), 'agent_timeout_sec':d.get('agent',{}).get('timeout_sec'),
                     'correctness':m.get('correctness'), 'source':f"https://github.com/apple-aiml-research/ml-rsi-inference-bench/blob/1a38072fbe284234c874356b86c9df666a5a79a3/tasks/{p.parent.name}/task.toml"})
    (ROOT/'data/derived/rsi_tasks.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    print('tasks',len(rows),'categories',Counter(r['category'] for r in rows),'engine',Counter(r['engine'] for r in rows))
    for r in rows: print(r['task'],r['gpus'],r['gpu_types'],json.dumps(r['model'],ensure_ascii=False)[:250])

if __name__=='__main__': main()
