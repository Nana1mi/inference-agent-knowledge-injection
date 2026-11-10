"""Collect unlabelled numeric tool returns for ISO eligibility review.

Numeric strings can be source echoes, host timings, or failed executions. This
queue does not classify devices, success, or measurement validity.
"""
import argparse
import re
from r2_io import ROOT, RAW, DERIVED, load, dump

MEASUREMENT = re.compile(r'(?i)(?:\b\d+(?:\.\d+)?\s*(?:ms|us|µs|seconds|TFLOPS|GB/s|token/s)\b|\b(?:baseline|optimized|latency|time|throughput|speedup|seconds_per_run|orig|opt)\b.{0,60}\d|\b\d+\.\d{3,}\b)')
EXECUTION = re.compile(r'(?<![/\w])(?:python(?:3)?\s|pytest\b|nvidia-smi\b|ncu\b|nsys\b|nvprof\b)', re.I)

def collect():
    rev = load(DERIVED/'r2_iso_index.json')['revision']
    plan = load(RAW/'r2_iso'/rev/'selection.json')
    reviewed = {r['order'] for r in load(ROOT/'data/annotations/r2_iso_eligibility_reviews.json')['reviews']}
    packets = []
    for candidate in plan['eligibility_check_order']:
        path = RAW/'r2_iso'/rev/'candidates'/candidate['run_path']/'trajectory.json'
        if not path.exists():
            continue
        for i, step in enumerate(load(path).get('agent_steps', [])):
            commands = [t.get('arguments', {}).get('command', '') for t in step.get('tool_calls') or []
                        if t.get('name', '').lower() in ('bash', 'shell', 'execute_bash', 'run')]
            if not any(EXECUTION.search(command) for command in commands):
                continue
            for j, result in enumerate(step.get('tool_results') or []):
                value = str(result.get('result') or result.get('error') or '')
                lines = [(k+1, line) for k, line in enumerate(value.splitlines()) if MEASUREMENT.search(line)]
                if lines:
                    packets.append({'order': candidate['order'], 'step': i+1, 'file': path.relative_to(ROOT).as_posix(),
                                    'locator': f'/agent_steps/{i}/tool_results/{j}/result', 'commands': commands,
                                    'numeric_lines': lines, 'result': value,
                                    'already_eligibility_reviewed': candidate['order'] in reviewed})
    dump(DERIVED/'r2_iso_measurement_inputs.json', {'scope': 'unlabelled numeric-result navigation; NOT proof of GPU measurement', 'packets': packets})
    print('numeric packets', len(packets), 'runs', len({p['order'] for p in packets}))
    return packets

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int)
    parser.add_argument('--end', type=int)
    args = parser.parse_args()
    for packet in collect():
        if args.start is None or not args.start <= packet['order'] <= (args.end or args.start):
            continue
        print('\nORDER', packet['order'], 'STEP', packet['step'], packet['locator'])
        print('COMMAND:', '\n'.join(packet['commands'])[:450])
        print('NUMERIC LINES:', str(packet['numeric_lines'])[:1800])
        print('RESULT END:', packet['result'][-500:])

if __name__ == '__main__':
    main()
