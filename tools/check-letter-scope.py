import hashlib, json, subprocess, sys
from pathlib import Path

root = Path(sys.argv[1])
repo = Path(__file__).resolve().parent.parent
manifest = json.loads((repo / 'fixes/missives-letters-source-manifest.json').read_text())
modified = subprocess.check_output(['git', '-C', str(root), 'diff', '--name-only', 'HEAD']).decode().splitlines()
new = subprocess.check_output(['git', '-C', str(root), 'ls-files', '--others', '--exclude-standard']).decode().splitlines()
assert set(modified + new) == set(manifest), 'Unexpected changes outside reviewed source manifest'
for name, expected in manifest.items():
    assert hashlib.sha256((root / name).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == expected, name
print(json.dumps({'verified_files': len(manifest), 'manifest_matches': True, 'line_endings_normalized': True, 'new_engine_hooks': 0, 'new_engine_layouts': 0}, indent=2))
