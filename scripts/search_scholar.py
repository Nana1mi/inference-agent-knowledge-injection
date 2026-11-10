"""Bounded secondary-index search, with query provenance and response-shape checks."""
import json
import time
from urllib.parse import urlencode
from collect_sources import RAW, fetch

QUERIES=['coding agent retrieval augmented memory ablation','agent skills context files coding']

def main():
    records=[]
    for i, query in enumerate(QUERIES):
        url='https://api.semanticscholar.org/graph/v1/paper/search?'+urlencode({'query':query,'fields':'title,year,externalIds,url','limit':10,'year':'2025-2026'})
        path=fetch(url,f'search/semantic_scholar_{i}.json','API metadata；全文许可另查')
        record={'query':query,'url':url,'limit':10,'date_range':'2025–2026','status':'not retrieved'}
        if path:
            data=json.loads(path.read_text(encoding='utf-8'))
            if 'data' not in data or not isinstance(data['data'],list): record['status']='invalid response shape'
            else:
                record.update(status='retrieved',returned=len(data['data']),provider_total=data.get('total'))
                for row in data['data']: print(row.get('title'),row.get('externalIds'))
        records.append(record); time.sleep(3.1)
    (RAW/'search/scholar_queries.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(records,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
