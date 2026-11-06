import json
import runpy
import sys
from pathlib import Path

inspect = runpy.run_path(str(Path(__file__).with_name('check-pe.py')))['inspect']
files = [Path(p) for p in sys.argv[1:]]
assert {p.name for p in files} == {'SkyrimTogether.exe', 'EarlyLoad.dll', 'STServer.dll', 'SkyrimTogetherServer.exe'}
reports = [inspect(p, require_fix=True) for p in files]
data = next(p for p in files if p.name == 'SkyrimTogether.exe').read_bytes()
assert b'STR corpse death playback:' in data
for marker in (b'STR network NPC save policy:', b'STR network NPC save filter installed:', b'STR corpse speech cleanup:', b'STR corpse life-state guard:'):
    assert marker in data, marker
assert b'STR corpse action replay:' in data
assert b'STR Missives' not in data
assert b'STR corpse native motion:' not in data
assert b'STR network diagnostics v1 enabled' in next(p for p in files if p.name == 'STServer.dll').read_bytes()
print(json.dumps(reports, indent=2))
