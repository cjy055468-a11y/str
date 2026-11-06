import json,runpy,sys
from pathlib import Path
inspect=runpy.run_path(str(Path(__file__).with_name('check-pe.py')))['inspect']
files=[Path(p) for p in sys.argv[1:]]
assert {p.name for p in files}=={'SkyrimTogether.exe','EarlyLoad.dll','STServer.dll','SkyrimTogetherServer.exe'}
reports=[inspect(p) for p in files]
for p in files:
 if p.name!='EarlyLoad.dll': assert b'v1.8.4-coopfix4g-missives2r1\0' in p.read_bytes(),p.name
client=next(p for p in files if p.name=='SkyrimTogether.exe').read_bytes()
for marker in [b'STR Missives',b'STR corpse life-state guard:',b'STR corpse native process eligibility:',b'STR corpse speech cleanup:',b'STR drop grant applied:',b'STR furniture recovery exit:']:
 assert marker in client,marker
print(json.dumps(reports,indent=2))
