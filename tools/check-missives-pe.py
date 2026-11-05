import json
import runpy
import sys
from pathlib import Path

inspect = runpy.run_path(str(Path(__file__).with_name('check-pe.py')))['inspect']
files = [Path(p) for p in sys.argv[1:]]
assert {p.name for p in files} == {'SkyrimTogether.exe', 'EarlyLoad.dll', 'STServer.dll', 'SkyrimTogetherServer.exe'}
reports = [inspect(p, require_fix=True) for p in files]
assert b'STR corpse native motion:' in next(p for p in files if p.name == 'SkyrimTogether.exe').read_bytes()
assert b'STR network diagnostics v1 enabled' in next(p for p in files if p.name == 'STServer.dll').read_bytes()
data = next(p for p in files if p.name == 'SkyrimTogether.exe').read_bytes()
for marker in (b'STR Missives posting copy suppressed:', b'STR Missives remote quest stage ignored:', b'STR Missives board audit:', b'STR Missives local posting:'):
    assert marker in data, marker
print(json.dumps(reports, indent=2))
