"""Read-only T4 feasibility probe. Does not run an agent or GPU workload, or read credentials."""
import json
import shutil
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo
from collect_sources import ROOT

def main():
    commands=[['nvidia-smi','--query-gpu=name,memory.total,driver_version','--format=csv'],['opencode','--version']]
    results=[]
    for cmd in commands:
        if not shutil.which(cmd[0]): results.append({'command':cmd,'error':'not on PATH'}); continue
        try:
            p=subprocess.run(cmd,encoding='utf-8',errors='replace',capture_output=True,timeout=45)
            results.append({'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
        except Exception as e: results.append({'command':cmd,'error':str(e)})
    target=ROOT/'data/derived/environment.json'
    target.write_text(json.dumps({'checked_at':datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat(),'gpu_workload_started':False,'commands':results},ensure_ascii=False,indent=2),encoding='utf-8')
    print(target.read_text(encoding='utf-8'))

if __name__=='__main__': main()
