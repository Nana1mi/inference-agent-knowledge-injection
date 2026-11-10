"""Join explicit per-hit judgments; no automatic propagation to new occurrences."""
import csv
import hashlib
import json
from collections import Counter
from r2_io import ROOT,DERIVED,load,dump

def main():
    scan=load(DERIVED/'r2_state_tamper_hits.json');hits={h['hit_id']:h for h in scan['hits']};seen=set()
    for fields in csv.reader((ROOT/'data/annotations/r2_state_tamper_reviews.tsv').read_text(encoding='utf-8').splitlines(),delimiter='\t'):
        if not fields or fields[0].startswith('#'):continue
        if len(fields)!=3:raise ValueError('expected hit_id/classification/rationale')
        key,category,reason=fields
        if key in seen:raise ValueError('duplicate hit review '+key)
        seen.add(key)
        if key not in hits:raise ValueError('review no longer matches scan '+key)
        if category not in ['确实影响评估','合法优化','无法判断']:raise ValueError(category)
        h=hits[key];h['review']=category;h['review_rationale']=reason
        h['reviewer']='AI研究助理逐处复核';h['reviewed_line_sha256']=hashlib.sha256(h['line'].encode()).hexdigest()
    scan['review_status']='complete' if len(seen)==len(hits) else 'partial'
    scan['review_counts']=dict(Counter(h['review'] or '待复核' for h in hits.values()))
    dump(DERIVED/'r2_state_tamper_reviewed.json',scan)
    exported=[{k:v for k,v in h.items() if k not in ('line','context_before','context_after')} for h in hits.values() if h['review'] is not None]
    (ROOT/'data/annotations/r2_state_tamper.jsonl').write_text(''.join(json.dumps(h,ensure_ascii=False)+'\n' for h in exported),encoding='utf-8')
    rule_coverage=[]
    for rule in scan['rules']:
        subset=[h for h in hits.values() if h['rule']==rule]
        rule_coverage.append({'rule':rule,'required_hits':len(subset),
                              'reviewed_hits':sum(h['review'] is not None for h in subset),
                              'counts':dict(Counter(h['review'] or '待复核' for h in subset))})
    position=lambda h:(h['raw_file'],h['source_locator'],h['payload_line'])
    dump(DERIVED/'r2_state_review_coverage.json',{'review_status':scan['review_status'],'counts':scan['review_counts'],
         'required_hits':len(hits),'reviewed_hits':len(seen),'physical_files':len(scan['coverage']),
         'unique_payload_positions':len({position(h) for h in hits.values()}),
         'positions_with_any_manual_judgement':len({position(h) for h in hits.values() if h['review'] is not None}),
         'rule_coverage':rule_coverage,
         'unit_note':'one hit per file/payload/line/rule; multiple rules may match one position; no new occurrence receives a default verdict'})
    print('state review',len(seen),'/',len(hits),scan['review_counts'])

if __name__=='__main__':main()
