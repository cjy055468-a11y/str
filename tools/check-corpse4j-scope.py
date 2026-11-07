import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

source = Path(sys.argv[1]).resolve()
repo = Path(__file__).resolve().parent.parent
candidate_patch = repo / 'fixes/corpse4j-death-init.delta.patch'
base_patch = repo / 'fixes/coopfix4i-corpse4-v184.patch'
paths = re.findall(r'^diff --git a/(.*?) b/', candidate_patch.read_text(), re.M)
expected_paths = json.loads((repo / 'fixes/corpse4j-scope.json').read_text())
assert paths == expected_paths, f'Unexpected candidate scope: {paths}'

env = os.environ.copy()
env['GIT_CEILING_DIRECTORIES'] = str(Path(tempfile.gettempdir()).resolve())

# Reverse the new delta from staged copies of only its files.
with tempfile.TemporaryDirectory(prefix='str-corpse4j-reverse-') as temp:
    staged = Path(temp)
    for name in paths:
        target = staged / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    subprocess.run(['git', 'apply', '--reverse', '--check', str(candidate_patch)], cwd=staged, env=env, check=True)
    subprocess.run(['git', 'apply', '--reverse', str(candidate_patch)], cwd=staged, env=env, check=True)

    # Independently recreate the exact 4i baseline from the pinned official tree.
    base_paths = set(re.findall(r'^diff --git a/(.*?) b/', base_patch.read_text(), re.M))
    tracked = set(subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', 'HEAD'], cwd=source, text=True).splitlines())
    wanted = (set(paths) | base_paths) & tracked
    with tempfile.TemporaryDirectory(prefix='str-corpse4i-baseline-') as base_temp:
        baseline = Path(base_temp)
        archive = subprocess.check_output(['git', 'archive', 'HEAD', *sorted(wanted)], cwd=source)
        with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
            bundle.extractall(baseline, filter='data')
        subprocess.run(['git', 'apply', str(base_patch)], cwd=baseline, env=env, check=True)
        for name in paths:
            expected = baseline / name
            actual = staged / name
            assert expected.exists() == actual.exists(), f'Unexpected file creation/removal: {name}'
            if expected.exists():
                assert expected.read_bytes().replace(b'\r\n', b'\n') == actual.read_bytes().replace(b'\r\n', b'\n'), f'Candidate exceeded delta: {name}'

print(json.dumps({
    'candidate_files': paths,
    'candidate_delta_sha256': hashlib.sha256(candidate_patch.read_bytes()).hexdigest(),
    'exact_corpse4i_recovery': True,
    'official_base': '54b3a858e228dc8807ed65bc3f9ac3c3f81b610d',
    'game_test': 'not run'
}, indent=2))
