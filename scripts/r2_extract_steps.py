"""Extract maximal consecutive assistant blocks before a tool-result boundary.

Structural extraction only: no phase, evidence, knowledge-use or risk labels are
inferred here. Every semantic label is supplied by an explicit review file.
"""
import json
from collections import Counter
from r2_io import RAW,DERIVED,load,dump

def main():
    rev=load(DERIVED/'r2_kbh_index.json')['revision'];selection=load(RAW/'r2_kbh'/rev/'selection.json');sessions=[]
    outdir=DERIVED/'r2_review_inputs';outdir.mkdir(exist_ok=True)
    for number,s in enumerate(selection['selected'],1):
        path=RAW/'r2_kbh'/rev/'traces'/s['file']
        if not path.exists():continue
        rows=[json.loads(l) for l in path.read_text(encoding='utf-8').splitlines() if l.strip()]
        results={}
        for line,r in enumerate(rows,1):
            c=r.get('message',{}).get('content',[])
            if not isinstance(c,list):continue
            for b in c:
                if b.get('type')=='tool_result':results[b.get('tool_use_id')]={'line':line,'content':b.get('content'),'is_error':b.get('is_error')}
        groups=[];pending=[]
        def close():
            if not pending:return
            thoughts=[];texts=[];calls=[];lines=[]
            for ln,row in pending:
                lines.append(ln);c=row.get('message',{}).get('content',[])
                if isinstance(c,str):c=[{'type':'text','text':c}]
                for b in c:
                    if b.get('type')=='thinking':thoughts.append({'line':ln,'text':b.get('thinking','')})
                    elif b.get('type')=='text':texts.append({'line':ln,'text':b.get('text','')})
                    elif b.get('type')=='tool_use':calls.append({'line':ln,'id':b.get('id'),'name':b.get('name'),'input':b.get('input'), 'result':results.get(b.get('id'))})
            groups.append({'step_id':len(groups)+1,'source_lines':lines,'thoughts':thoughts,'texts':texts,'calls':calls,
                           'source_timestamp':pending[0][1].get('timestamp')})
            pending.clear()
        for line,r in enumerate(rows,1):
            if r.get('type')=='assistant':pending.append((line,r))
            elif r.get('type')=='user':
                close()
                content=r.get('message',{}).get('content')
                if isinstance(content,str) and content.startswith('Base directory for this skill:'):
                    if not groups or not any(c['name']=='Skill' for c in groups[-1]['calls']):
                        raise ValueError(f'unattached skill context {path}:{line}')
                    groups[-1].setdefault('context_messages',[]).append(
                        {'line':line,'role':'user','content':content})
        close()
        sid=f'K{number:02d}';filename=outdir/(sid+'.jsonl')
        filename.write_text(''.join(json.dumps(g,ensure_ascii=False)+'\n' for g in groups),encoding='utf-8')
        sessions.append({'session_id':sid,'selection':s,'raw_file':path.relative_to(RAW.parents[1]).as_posix(),
                         'step_file':filename.relative_to(RAW.parents[1]).as_posix(),'steps':len(groups),
                         'visible_thinking_steps':sum(any(t['text'].strip() for t in g['thoughts']) for g in groups),
                         'tool_calls':sum(len(g['calls']) for g in groups),'reasoning_characters':sum(len(t['text']) for g in groups for t in g['thoughts'])})
    dump(DERIVED/'r2_sessions.json',sessions)
    for s in sessions:print(s['session_id'],s['selection']['model_from_filename'],s['selection']['task'],s['steps'],'steps',s['visible_thinking_steps'],'with thinking',s['reasoning_characters'],'thinking chars')

if __name__=='__main__':main()
