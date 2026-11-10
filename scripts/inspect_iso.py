"""Index the official ISO-Bench release tree for transcript availability."""
import json
from collections import Counter
from collect_sources import RAW

def main():
    d=json.loads((RAW/'iso_current/tree.json').read_text(encoding='utf-8'))
    print('sha',d.get('sha'),'files',len(d.get('tree',[])),'truncated',d.get('truncated'))
    blobs=[x for x in d.get('tree',[]) if x['type']=='blob']
    print('top directories',Counter(x['path'].split('/')[0] for x in blobs).most_common(18))
    candidates=[x for x in blobs if any(s in x['path'].lower() for s in ('trajectory','transcript','trace','agent.log'))]
    print('candidate paths',len(candidates))
    for x in candidates[:35]:print(x['path'],x.get('size'))
    print('root documentation',[(x['path'],x.get('size')) for x in blobs if '/' not in x['path']][:15])
    (RAW/'iso_current/candidate_paths.json').write_text(json.dumps({'sha':d.get('sha'),'truncated':d.get('truncated'),'paths':candidates},ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
