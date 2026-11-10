"""Recompute descriptive counts, with explicit units and annotation-method denominators."""
import json
from collections import Counter
from collect_sources import ROOT

def main():
    groups={}
    for path in sorted((ROOT/'data/annotations').glob('*.jsonl')):
        rows=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
        sessions=[]
        for sid in dict.fromkeys(r['session_id'] for r in rows):
            sr=[r for r in rows if r['session_id']==sid]
            first=next((r['step_id'] for r in sr if r.get('candidate_edit')),None)
            profiles=[r['step_id'] for r in sr if r['phase']=='profile']
            explicit=[r for r in sr if r['hypothesis_origin']=='explicit']
            sessions.append({'session_id':sid,'n':len(sr),'unit':sr[0]['unit'],
              'reviewed':sum(r['annotation_method']=='研究助理逐项复核' for r in sr),
              'phase':dict(Counter(r['phase'] for r in sr)),'tool':dict(Counter(r['tool'] for r in sr)),
              'layer':dict(Counter(r['layer'] for r in sr)),'first_candidate_edit':first,
              'first_profile':min(profiles) if profiles else None,
              'profile_before_first_edit':any(i<first for i in profiles) if first else None,
              'explicit_hypotheses':len(explicit),'explicit_unsupported':sum(r['evidence']=='无' for r in explicit),
              'unknown_hypothesis':sum(r['hypothesis_origin']=='missing' for r in sr),
              'turning_points':[r['step_id'] for r in sr if r['turning_point']]})
        groups[path.stem]={'total':len(rows),'unit':rows[0]['unit'],'sessions':sessions,
              'annotation_method':dict(Counter(r['annotation_method'] for r in rows)),
              **{key:dict(Counter(r[key] for r in rows)) for key in ('phase','tool','layer')}}
    out=ROOT/'data/derived/statistics.json'; out.write_text(json.dumps(groups,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(groups,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
