import json
import runpy
import sys
from pathlib import Path
inspect = runpy.run_path(str(Path(__file__).with_name('check-pe.py')))['inspect']
files = [Path(p) for p in sys.argv[1:]]
assert {p.name for p in files} == {'STServer.dll', 'SkyrimTogetherServer.exe'}
result = [inspect(p, require_fix=True) for p in files]
data = next(p for p in files if p.name == 'STServer.dll').read_bytes()
for marker in (b'STR network diagnostics v1 enabled', b'STR network detail:', b'STR network app kick:', b'STR network SDK'):
    assert marker in data, marker
print(json.dumps(result, indent=2))
