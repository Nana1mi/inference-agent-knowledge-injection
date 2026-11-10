"""Archive the official PyTorch backend semantics used in state review."""
from r2_io import fetch

def main():
    for file in ['backends.md','notes/numerical_accuracy.rst','notes/cuda.rst']:
        fetch('https://raw.githubusercontent.com/pytorch/pytorch/v2.11.0/docs/source/'+file,'r2_docs/pytorch_v2.11.0/'+file)

if __name__=='__main__':main()
