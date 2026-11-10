"""Prespecified supplementary official-source retrieval; no mirror fallback."""
import time
from concurrent.futures import ThreadPoolExecutor
from collect_sources import fetch

IDS = ['2602.11988', '2607.27250', '2611.09802', '2605.25430', '2608.14036', '2510.04618']

if __name__ == '__main__':
    for ident in IDS:
        fetch(f'https://arxiv.org/abs/{ident}', f'papers/{ident}_abs.html', '参见页面 License')
        time.sleep(3.1)
        fetch(f'https://arxiv.org/html/{ident}', f'papers/{ident}.html', '参见页面 License')
        time.sleep(3.1)
    fetch('https://research.trychroma.com/context-rot', 'chroma/context_rot.html', '未核实；原站技术报告')
