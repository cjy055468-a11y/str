#!/usr/bin/env python3
import json,runpy,sys
from pathlib import Path
inspect=runpy.run_path(str(Path(__file__).with_name('check-pe.py')))['inspect']
files=[Path(x) for x in sys.argv[1:]]
assert {p.name for p in files}=={'SkyrimTogether.exe','EarlyLoad.dll','STServer.dll','SkyrimTogetherServer.exe'}
for p in files:
 if p.name!='EarlyLoad.dll':assert b'coopfix4g-corpse5-state1s-loot2-notice-board-v2-r1\0' in p.read_bytes(),p.name
client=next(p for p in files if p.name=='SkyrimTogether.exe').read_bytes();server=next(p for p in files if p.name=='STServer.dll').read_bytes()
for marker in (b'STR fresh notice compatibility:',b'STR notice session ready',b'GetNoticeState',b'IsOriginalBookProtected'):assert marker in client,marker
assert b'STR notice committed:' in server
print(json.dumps([inspect(p) for p in files],indent=2))
