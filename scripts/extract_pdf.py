"""Reproduce the read-only Together PDF extraction and inspected page render."""
import json
import shutil
import subprocess
from collect_sources import ROOT, RAW

def main():
    pdf=RAW/'together/paper.pdf'
    commands=[['pdftotext','-layout',str(pdf),str(pdf.with_suffix('.txt'))],
              ['pdftoppm','-f','10','-l','10','-scale-to','1600','-png','-singlefile',str(pdf),str(ROOT/'data/derived/together_p10')]]
    results=[]
    for cmd in commands:
        if not shutil.which(cmd[0]):raise RuntimeError(f'{cmd[0]} missing; install Poppler or record unavailable')
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
        results.append({'command':cmd,'returncode':result.returncode,'stderr':result.stderr})
        result.check_returncode()
    (ROOT/'data/derived/pdf_extraction.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
