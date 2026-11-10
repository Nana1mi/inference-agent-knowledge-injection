"""Inspect and index the two official ISO-Bench trajectory exports."""
import json
from collect_sources import RAW, ROOT

def main():
    for file in sorted((RAW/'iso_current/traces').rglob('trajectory.json')):
        d=json.loads(file.read_text(encoding='utf-8'))
        print(file.parent.name,'model',d['model'],'steps',len(d['agent_steps']),'success',d['success'])
        for i,s in enumerate(d['agent_steps']):
            response=s.get('llm_response') or {}; calls=s.get('tool_calls') or []
            desc='; '.join(c.get('name','')+' '+str(c.get('arguments',{}))[:140] for c in calls)
            result='; '.join(str(r.get('result') or r.get('error'))[:170] for r in (s.get('tool_results') or []))
            print(f"{i+1:03d} {desc} | {result} | TEXT {str(response.get('content',''))[:250]} | ERROR {s.get('error')}")

if __name__=='__main__':main()
