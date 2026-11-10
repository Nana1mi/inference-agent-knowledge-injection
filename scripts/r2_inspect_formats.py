"""Inspect selected files' observable response structure before coding any behavior."""
import json
from collections import Counter
from r2_io import RAW,DERIVED,load,dump

def main():
    revision=load(DERIVED/'r2_kbh_index.json')['revision'];selection=load(RAW/'r2_kbh'/revision/'selection.json');out=[]
    for s in selection['selected']:
        path=RAW/'r2_kbh'/revision/'traces'/s['file']
        if not path.exists():continue
        rows=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
        types=Counter();thinking=[];text=[];assistant=0
        for line,r in enumerate(rows,1):
            if r.get('type')!='assistant':continue
            assistant+=1;content=r.get('message',{}).get('content',[])
            if isinstance(content,str):content=[{'type':'text','text':content}]
            for b in content:
                types[b.get('type')]+=1
                if b.get('type')=='thinking':thinking.append((line,b.get('thinking','')[:450]))
                elif b.get('type')=='text' and b.get('text'):text.append((line,b['text'][:300]))
        item={'file':s['file'],'family':s['model_family'],'model':s['model_from_filename'],'records':len(rows),'assistant_records':assistant,'block_types':dict(types),'thinking_examples':thinking[:1],'text_examples':text[:1]}
        out.append(item);print(json.dumps(item,ensure_ascii=False))
    dump(DERIVED/'r2_kbh_format_audit.json',out)

if __name__=='__main__':main()
