"""Check the compiled vanilla room-rental overlay and its preserved interfaces."""
import json
from pathlib import Path
import re
import struct
import sys

root, compiled = map(Path, sys.argv[1:3])
source = (root / 'Scripts/Source/RentRoomScript.psc').read_text()
properties = re.findall(r'^(\w+) Property (\w+) Auto$', source, re.M)
assert properties == [('ObjectReference', 'Bed'), ('WIFunctionsScript', 'WI')]
assert 'Scriptname RentRoomScript extends Actor Conditional' in source
for statement in ('RegisterForSingleUpdateGameTime(pQuestScript.RentHours)',
                  'Game.GetPlayer().RemoveItem(pQuestScript.Gold, pQuestScript.RoomRentalCost.GetValueInt())',
                  'WI.ShowPlayerRoom(Self, Bed)', 'SetActorValue("Variable09", 1.0)',
                  'SetActorValue("Variable09", 0.0)', 'GetActorValue("Variable09") == 1.0'):
    assert source.count(statement) == 1, statement
assert 'GetFormFromFile' not in source  # No hard-coded inn or bed IDs.
assert not list(root.rglob('*.esp')) and not list(root.rglob('*.exe')) and not list(root.rglob('*.dll'))
paths = list(compiled.glob('*.pex'))
assert len(paths) == 1 and paths[0].stem.lower() == 'rentroomscript'
data = paths[0].read_bytes()
assert data[:8] == bytes.fromhex('fa57c0de03020001')
offset = 16
for _ in range(3):
    size = struct.unpack_from('>H', data, offset)[0]
    offset += 2 + size
count = struct.unpack_from('>H', data, offset)[0]
offset += 2
strings = []
for _ in range(count):
    size = struct.unpack_from('>H', data, offset)[0]
    offset += 2
    strings.append(data[offset:offset + size].decode())
    offset += size
symbols = {s.lower() for s in strings}
assert {'rentroomscript', 'bed', 'wi', 'variable09', 'strsyncsharedbed',
        'strrestoresharedbed', 'getactorowner', 'setactorowner',
        'onload', 'onunload', 'onupdategametime', 'ondeath'} <= symbols
print(json.dumps({'result': 'PASS', 'compiled_skyrim_pex_3_2': 1,
                  'original_vmad_properties': properties,
                  'original_price_duration_and_walk_to_preserved': True,
                  'shared_permission': 'all clients; synchronized Variable09; referenced Bed only',
                  'native_binaries_changed': False,
                  'gameplay_two_clients': 'NOT RUN'}, indent=2))
