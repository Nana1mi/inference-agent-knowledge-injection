"""Freeze the user-accepted first pass without changing any semantic labels."""
import hashlib
import subprocess
from r2_io import ROOT, DERIVED, load, dump, now


def main():
    target = ROOT / 'data/annotations/r2_frozen'
    sources = {
        'first_pass.jsonl': ROOT / 'data/annotations/r2_kernelbench.jsonl',
        'knowledge_sources.json': ROOT / 'data/annotations/r2_knowledge_source_reviews.json',
        'sessions.json': DERIVED / 'r2_sessions.json',
        'schema.json': ROOT / 'data/annotations/r2_schema.json',
    }
    target.mkdir(parents=True, exist_ok=True)
    manifest = target / 'manifest.json'
    prior = load(manifest) if manifest.exists() else None
    previous = {a['snapshot']: a for a in prior['artifacts']} if prior else {}
    artifacts = []
    for name, source in sources.items():
        original = source.read_bytes()
        data = original.replace(b'\r\n', b'\n')
        frozen = target / name
        if frozen.exists() and frozen.read_bytes().replace(b'\r\n', b'\n') != data:
            raise ValueError('Frozen first-pass source changed: ' + str(source))
        frozen.write_bytes(data)
        snapshot = frozen.relative_to(ROOT).as_posix()
        artifacts.append({'source': source.relative_to(ROOT).as_posix(),
                          'snapshot': snapshot, 'bytes': len(data),
                          'sha256': hashlib.sha256(data).hexdigest(),
                          'original_source_sha256': previous.get(snapshot, {}).get('original_source_sha256',
                              hashlib.sha256(original).hexdigest())})
    if prior and prior.get('hash_convention') == 'UTF-8, LF line endings' and prior['artifacts'] != artifacts:
        raise ValueError('Frozen manifest does not match accepted first pass')
    metadata = prior or {
            'frozen_at': now(), 'authorized_scope': 'User scope amendment 2026-11-11',
            'base_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'sessions': 14, 'steps': 3345, 'no_sample_expansion': True,
            'repeat_steps': 150, 'selection_seed': 2026111105, 'blind_seed': 2026111106,
            'limits': ['User-accepted first pass; not a claim of perfect semantic labels',
                       'Repeated annotations must not overwrite these snapshots'],
        }
    metadata.update(artifacts=artifacts, hash_convention='UTF-8, LF line endings')
    dump(manifest, metadata)
    dump(DERIVED / 'r2_scope_update.json', {
        'version': 2, 'authorized_on': '2026-11-11',
        'authority': 'PLAN_ROUND2.md section 4 and explicit user scope amendment',
        'kbh': {'sessions': 14, 'frozen_steps': 3345, 'repeat_steps': 150,
                'manifest': manifest.relative_to(ROOT).as_posix()},
        'iso': {'manual_review_stopped_at': 400, 'automatic_remainder': 433,
                'missing_gpu_field': 'unknown', 'sample_shortfall_allowed': True},
        'r5': {'unit': 'canonical session x scan rule', 'priority_cap': 150,
               'remainder_random_sample': 50, 'priority_seed': 2026111107,
               'random_seed': 2026111108},
        'milestones': {'R4_draft': '2026-11-11', 'R5': '2026-11-12',
                       'R6': '2026-11-13', 'self_audit': '2026-11-14'},
        'remote_push': False, 'gpu_execution': False,
    })
    print('Frozen 14 sessions / 3345 steps; separate repeat target 150')


if __name__ == '__main__':
    main()
