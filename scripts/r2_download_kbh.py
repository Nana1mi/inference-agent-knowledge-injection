"""Only retrieve the filenames in the frozen selection.json; no dataset-wide download."""
from concurrent.futures import ThreadPoolExecutor
from r2_io import RAW,DERIVED,load,fetch

def main():
    revision=load(DERIVED/'r2_kbh_index.json')['revision'];selection=load(RAW/'r2_kbh'/revision/'selection.json')
    def get(row):
        name=row['file']
        return fetch(f'https://huggingface.co/datasets/Infatoshi/kernelbench-hard-traces/resolve/{revision}/{name}',
                     f'r2_kbh/{revision}/traces/{name}','MIT data card；上游库/模型另计')
    # First selected GLM is the explicit reasoning-visibility probe; still part of the final random sample.
    probe=get(selection['selected'][0])
    if not probe:print('Visibility probe not retrieved; retain failure and continue selected files')
    with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(get,selection['selected'][1:]))

if __name__=='__main__':main()
