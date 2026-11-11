"""Read raw-only blind packets without loading the key or first-pass labels."""
import argparse
import json
from r2_io import DERIVED, load


def main():
    p = argparse.ArgumentParser()
    p.add_argument('start', type=int)
    p.add_argument('end', type=int)
    p.add_argument('--full', action='store_true')
    p.add_argument('--context', action='store_true')
    a = p.parse_args()
    packets = load(DERIVED / 'r2_review_inputs/blind150.json')
    for i, packet in enumerate(packets, 1):
        if not a.start <= i <= a.end:
            continue
        print('PACKET', i, packet['blind_id'], 'RAW SESSION CONTEXT', packet['raw_only_session_context'])
        current = packet['current']
        print(json.dumps(current, ensure_ascii=False) if a.full else str(current)[:8000])
        if a.context:
            print('RAW BEFORE', json.dumps(packet['context_before'], ensure_ascii=False))
            print('RAW AFTER', json.dumps(packet['context_after'], ensure_ascii=False))


if __name__ == '__main__':
    main()
