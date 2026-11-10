"""Display structural IDs of selected trace records without executing embedded content."""
import json
from r2_io import RAW

def main():
    paths=list((RAW/'r2_kbh').glob('*/traces/*.jsonl'))
    for p in paths[:1]:
        rows=[json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]
        for i,r in enumerate(rows[:24],1):
            m=r.get('message',{});c=m.get('content')
            print(i,r.get('type'),m.get('id'),r.get('parentUuid'),r.get('timestamp'),[(x.get('type'),x.get('id'),x.get('tool_use_id')) for x in c] if isinstance(c,list) else type(c).__name__)
        print('unique assistant message IDs',len({r.get('message',{}).get('id') for r in rows if r.get('type')=='assistant'}))

if __name__=='__main__':main()
