import json
import runpy
import sys
from pathlib import Path

inspect = runpy.run_path(str(Path(__file__).with_name('check-pe.py')))['inspect']
files = [Path(path) for path in sys.argv[1:]]
assert {path.name for path in files} == {'SkyrimTogether.exe', 'EarlyLoad.dll', 'STServer.dll', 'SkyrimTogetherServer.exe'}
reports = [inspect(path) for path in files]
for path in files:
    data = path.read_bytes()
    if path.name != 'EarlyLoad.dll':
        assert b'v1.8.4-coopfix4j-corpse4-loot1\0' in data, f'{path.name}: missing corpse4j build tag'
client = next(path for path in files if path.name == 'SkyrimTogether.exe').read_bytes()
for marker in (b'STR corpse KillImpl invoked:', b'STR corpse native death item phase observed:'):
    assert marker in client, f'EXE lacks diagnostic marker {marker!r}'
print(json.dumps(reports, indent=2))
