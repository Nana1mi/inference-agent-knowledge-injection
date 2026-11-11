"""Round 2 official-source acquisition with frozen paths and independent provenance."""
import hashlib
import json
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
DERIVED = ROOT / 'data/derived'
ROUND = ROOT / 'outputs/round2'

def now():
    return datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat()

def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Match the repository's *.json eol=lf rule so committed hashes reproduce.
    path.write_bytes(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))

def fetch(url, relative, note='官方公开来源；许可依上游，不自动再分发', timeout=45, revalidate_existing=False):
    target = RAW / relative
    if target.exists() and not revalidate_existing:
        return target
    record = {'url':url, 'path':target.relative_to(ROOT).as_posix(), 'accessed_at':now(), 'license_note':note}
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'InferenceKnowledgeResearch-Round2/1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data=response.read()
            record.update(status=response.status, final_url=response.url,
                          content_type=response.headers.get('Content-Type',''),
                          next_link=response.headers.get('Link'),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=data:
            target.with_name(target.name+'.changed').write_bytes(data)
            raise ValueError('Official URL changed: preserved existing snapshot; new response saved as .changed')
        target.write_bytes(data)
        print('OK',relative,len(data),flush=True)
    except Exception as exc:
        record.update(status='failed',error=f'{type(exc).__name__}: {exc}')
        print('FAIL',url,record['error'],flush=True);target=None
    RAW.mkdir(parents=True,exist_ok=True)
    with (RAW/'r2_manifest.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(record,ensure_ascii=False)+'\n')
    return target

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))
