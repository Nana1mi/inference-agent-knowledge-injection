"""Show unlabelled decision steps for the research assistant's per-step review.

Code blocks and verbose payloads can be expanded using --full. No semantic labels
are generated. The compact view preserves beginning/end and evidence-related prose.
"""
import argparse
import json
import re
from r2_io import ROOT,DERIVED,load

def compact(text,limit):
    if len(text)<=limit:return text
    prose=re.sub(r'```.*?```','[code block retained in original]',text,flags=re.S)
    if len(prose)<=limit:return prose
    paragraphs=prose.split('\n\n')
    chosen=[p for p in paragraphs[1:-1] if re.search(r'bottleneck|profil|measur|eviden|reference|sota|correct|fail|faster|slower|bandwidth|memory.bound|compute.bound|hypothes|cache|global|backend|should|instead',p,re.I)]
    beginning=min(500,max(100,limit//3));ending=min(350,max(80,limit//4))
    middle='\n'.join(chosen)[:max(0,limit-beginning-ending)]
    return prose[:beginning]+'\n[...unlabelled excerpt... ]\n'+middle+'\n[...]\n'+prose[-ending:]

def main():
    p=argparse.ArgumentParser();p.add_argument('session');p.add_argument('start',type=int);p.add_argument('end',type=int);p.add_argument('--full',action='store_true');p.add_argument('--reason-limit',type=int,default=1700);p.add_argument('--payload-limit',type=int,default=850);args=p.parse_args()
    rows=[json.loads(l) for l in (DERIVED/'r2_review_inputs'/f'{args.session}.jsonl').read_text(encoding='utf-8').splitlines()]
    for row in rows:
        if not args.start<=row['step_id']<=args.end:continue
        print(f"\nSTEP {row['step_id']} L{row['source_lines'][0]}–{row['source_lines'][-1]}")
        thinking='\n'.join(t['text'] for t in row['thoughts']);text='\n'.join(t['text'] for t in row['texts'])
        print('THINKING:',thinking if args.full else compact(thinking,args.reason_limit))
        if text:print('TEXT:',text if args.full else compact(text,600))
        for call in row['calls']:
            inp=call['input'] or {};summary={k:v for k,v in inp.items() if k not in ('content','old_string','new_string','patch','code')}
            payload=json.dumps(summary,ensure_ascii=False)
            print('TOOL',call['name'],payload if args.full else compact(payload,args.payload_limit))
            for field in ('old_string','new_string','content','patch','code'):
                if field in inp:print(field+':',inp[field] if args.full else compact(str(inp[field]),args.payload_limit))
            result=call.get('result') or {};value=result.get('content','');value=value if isinstance(value,str) else json.dumps(value,ensure_ascii=False)
            print('RESULT L'+str(result.get('line')),value if args.full else compact(value,args.payload_limit))
        for context in row.get('context_messages',[]):
            value=context['content']
            print('FOLLOWING USER CONTEXT L'+str(context['line']),
                  value if args.full else compact(value,args.payload_limit))

if __name__=='__main__':main()
