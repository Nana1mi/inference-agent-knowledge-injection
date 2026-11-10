"""Join every trace filename to official leaderboard status without opening traces."""
import json
import re
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import unquote
from r2_io import RAW,DERIVED,load,dump

class Rows(HTMLParser):
    def __init__(self):super().__init__();self.rows=[];self.cells=None;self.cell=None;self.hrefs=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='tr':self.cells=[];self.hrefs=[]
        elif tag in ('td','th') and self.cells is not None:self.cell=[]
        elif tag=='a' and self.cells is not None and a.get('href'):self.hrefs.append(a['href'])
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:
            self.cells.append(''.join(self.cell).strip());self.cell=None
        elif tag=='tr' and self.cells is not None:
            self.rows.append({'cells':self.cells,'hrefs':self.hrefs});self.cells=None

def identify(name):
    basename=name.rsplit('/',1)[-1]
    match=re.match(r'^(\d{8})_(\d{6})_(.+)_(\d{2}_[a-z0-9_]+)\.jsonl$',basename)
    if not match:return None
    date,clock,identity,task=match.groups()
    family=next((x for x in ('glm','kimi','deepseek','minimax','claude','gpt','grok','qwen') if re.search(r'(?:^|_)'+x,identity,re.I)), 'other')
    model_match=re.search(r'((?:glm|kimi|deepseek|MiniMax|claude|gpt|grok|qwen)[^/]*?)$',identity,re.I)
    model=model_match.group(1) if model_match else identity
    # Provider/harness prefixes may themselves contain a family name; use final actual model token.
    candidates=list(re.finditer(r'(glm-[^_]+|kimi-[^_]+|deepseek-v[^_]+|MiniMax-[^_]+|claude-(?:opus|sonnet|fable)[^_]*|gpt-[^_]+|grok-[^_]+|qwen[^_]*)',identity,re.I))
    if candidates:model=identity[candidates[-1].start():]
    return {'run_id':basename[:-6],'date':date,'time':clock,'identity':identity,'model_family':family,'model_from_filename':model,'task':task,'hardware_directory':name.rsplit('/',1)[0] if '/' in name else 'root_unspecified'}

def main():
    inventory=load(DERIVED/'r2_kbh_metadata_inventory.json');parser=Rows()
    parser.feed((RAW/'r2_kbh/r2_runs.html').read_text(encoding='utf-8'));board={}
    for row in parser.rows:
        links=[x for x in row['hrefs'] if 'kernelbench-hard-traces/blob/' in x and x.endswith('.jsonl')]
        if not links:continue
        filename=unquote(links[0].rsplit('/',1)[1]);cells=row['cells'];status=cells[0]
        outcome='success' if re.fullmatch(r'\d+(\.\d+)?',status) else 'failure' if status.upper() in ('FAIL','ERR','ERROR') else 'unknown'
        board[filename]={'outcome':outcome,'published_status':status,'cells':cells,'source_url':'https://kernelbench.com/runs','source_locator':'table row '+filename[:-6]}
    entries=[]
    for meta in inventory['files']:
        if meta.get('type')!='file':continue
        name=meta['path'];row={'file':name,'size':meta.get('size'),'blob_id':meta.get('oid'),'lfs':meta.get('lfs'),'kind':'trace' if name.endswith('.jsonl') else 'metadata_or_document','file_metadata':meta}
        identity=identify(name)
        if identity:row.update(identity)
        if name.endswith('.jsonl') and not identity:raise ValueError('Unparsed trace filename '+name)
        # Leaderboard links specify paths; do not transfer a root run status to an unrelated subdirectory.
        row['outcome']=(board.get(name) or {}).get('outcome','unknown');row['outcome_evidence']=board.get(name)
        entries.append(row)
    listed={x['file'] for x in entries};expected={x['rfilename'] for x in inventory['siblings']}
    if listed!=expected:raise ValueError(f'metadata sets differ: missing={expected-listed},extra={listed-expected}')
    result={'dataset':inventory['dataset'],'revision':inventory['revision'],'old_revision':'c2c764c8b5a5fdad493592a2fde1055684e0f064',
      'snapshot_updated':inventory['revision']!='c2c764c8b5a5fdad493592a2fde1055684e0f064','metadata_complete':True,
      'outcome_definition':'success=榜单可评分numeric peak fraction；failure=榜单FAIL/ERR；未被榜单覆盖不猜结局',
      'leaderboard_rows':len(board),'files':entries,'trace_count':sum(x['kind']=='trace' for x in entries),'file_count':len(entries)}
    dump(DERIVED/'r2_kbh_index.json',result);traces=[x for x in entries if x['kind']=='trace']
    print('files',len(entries),'traces',len(traces),'bytes',sum(x['size'] or 0 for x in entries),'board_rows',len(board))
    print('family',Counter(x['model_family'] for x in traces));print('outcome',Counter(x['outcome'] for x in traces))
    for family in ('glm','claude','gpt','kimi','deepseek'):
        rows=[x for x in traces if x['model_family']==family]
        print(family,Counter(x['model_from_filename'] for x in rows),Counter((x['task'],x['outcome']) for x in rows if x['outcome']!='unknown'))

if __name__=='__main__':main()
