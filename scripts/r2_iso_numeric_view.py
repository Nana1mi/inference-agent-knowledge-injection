"""Show unlabelled numeric returns alongside device-related source excerpts.

This is navigation for manual review. A source mention is not a device label;
use the full trajectory when call paths or measurement validity are unclear.
"""
import argparse
import re
from r2_io import ROOT, RAW, DERIVED, load

CUE = re.compile(r'device|cuda|gpu|cpu|synchronize|elapsed_time|sys\.modules|^\s*def\s', re.I | re.M)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('orders', type=int, nargs='+')
    parser.add_argument('--full-source', action='store_true')
    args = parser.parse_args()
    rev = load(DERIVED/'r2_iso_index.json')['revision']
    plan = load(RAW/'r2_iso'/rev/'selection.json')
    packets = load(DERIVED/'r2_iso_measurement_inputs.json')['packets']
    for candidate in plan['eligibility_check_order']:
        if candidate['order'] not in args.orders:
            continue
        path = RAW/'r2_iso'/rev/'candidates'/candidate['run_path']/'trajectory.json'
        if not path.exists():
            print('ORDER', candidate['order'], 'trajectory missing')
            continue
        data = load(path)
        print('\nORDER', candidate['order'], candidate['run_path'], 'trajectory.success', data.get('success'))
        for i, step in enumerate(data.get('agent_steps', [])):
            for j, call in enumerate(step.get('tool_calls') or []):
                payload = call.get('arguments') or {}
                target = str(payload.get('path') or payload.get('file_path') or '')
                for field in ('file_text', 'new_str', 'new_string', 'content', 'command'):
                    value = payload.get(field)
                    if not isinstance(value, str) or not value:
                        continue
                    if '.bench_scratch' not in target and '.bench_scratch' not in value:
                        continue
                    if not ('\n' in value and (args.full_source or CUE.search(value))):
                        continue
                    lines = list(enumerate(value.splitlines(), 1))
                    selected = lines if args.full_source else [(k, line) for k, line in lines if CUE.search(line)]
                    if not selected:
                        continue
                    print('SOURCE', f'/agent_steps/{i}/tool_calls/{j}/arguments/{field}', 'target', target)
                    results = step.get('tool_results') or []
                    print('WRITE/COMMAND FEEDBACK', [
                        {'success': result.get('success'), 'error': str(result.get('error') or '')[:260],
                         'result_begin': str(result.get('result') or '')[:200]}
                        for result in results if result.get('call_id') == call.get('call_id')])
                    print('\n'.join(f'{k}: {line}' for k, line in selected))
        for packet in packets:
            if packet['order'] == candidate['order']:
                print('RETURN', packet['locator'], 'NUMERIC', str(packet['numeric_lines'])[:800])
                print('RESULT BEGIN', packet['result'][:260], 'END', packet['result'][-160:])

if __name__ == '__main__':
    main()
