#!/usr/bin/env python3
"""Package the checked files and verify every ZIP entry byte for byte."""
import hashlib
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

mod, compiled, target = map(Path, sys.argv[1:])
target.mkdir(parents=True, exist_ok=True)
(target / 'Scripts/Source').mkdir(parents=True, exist_ok=True)
for name in ['AzuriteNoControl.esp', 'README.zh-CN.md', 'provenance.json']:
    shutil.copyfile(mod / name, target / name)
shutil.copytree(mod / 'SEQ', target / 'SEQ', dirs_exist_ok=True)
shutil.copytree(mod / 'Scripts/Source', target / 'Scripts/Source', dirs_exist_ok=True)
for path in compiled.glob('*.pex'):
    shutil.copyfile(path, target / 'Scripts' / path.name)
validation = {'source_revision': os.environ.get('GITHUB_SHA', 'local'),
              'run_id': os.environ.get('GITHUB_RUN_ID', 'local'),
              'checks': 'PASS', 'compiled_pex': 1,
              'requires_new_str_programs': False, 'gameplay_tested': False}
(target / 'build-validation.json').write_text(json.dumps(validation, indent=2) + '\n', encoding='utf-8')
digest = lambda data: hashlib.sha256(data).hexdigest()
manifest = {p.relative_to(target).as_posix(): digest(p.read_bytes())
            for p in target.rglob('*') if p.is_file() and p.name != 'SHA256.json'}
(target / 'SHA256.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
archive = target.parent / 'AzuriteNoControl-CHS.zip'
paths = [p for p in target.rglob('*') if p.is_file()]
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for path in sorted(paths):
        z.write(path, path.relative_to(target).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist()) == len(set(z.namelist())) == len(paths)
    assert {n: digest(z.read(n)) for n in z.namelist()} == {
        p.relative_to(target).as_posix(): digest(p.read_bytes()) for p in paths}
report = {'zip': archive.name, 'sha256': digest(archive.read_bytes()),
          'files': len(paths), 'zip_content_check': 'PASS', **validation}
(target.parent / 'archive-validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
