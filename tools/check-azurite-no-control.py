#!/usr/bin/env python3
"""Check patch scope, alias bindings, startup sequence and compiled output."""
import argparse
import hashlib
import importlib.util
import json
import struct
import tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location('gen', Path(__file__).with_name('generate-azurite-no-control.py'))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)
p = argparse.ArgumentParser()
p.add_argument('mod', type=Path)
p.add_argument('--compiled', type=Path)
args = p.parse_args()
mod = args.mod
fixture = json.loads((mod / 'source-quest.json').read_text(encoding='utf-8'))
raw = (mod / gen.PATCH_NAME).read_bytes()
rows = list(gen.tes4.iter_records(raw))
assert [(kind, form) for kind, form, _ in rows] == [
    ('TES4', 0), ('QUST', gen.ORIGINAL_QUEST), ('QUST', gen.CLEANUP_QUEST)]
assert struct.unpack_from('<I', raw, 8)[0] == 0x200
header = rows[0][2]
assert struct.unpack('<fII', dict(header)['HEDR'])[1:] == (3, 0x801)
assert [v.rstrip(b'\0').decode() for t, v in header if t == 'MAST'] == fixture['masters'] + ['Azurite Weathers III.esp']
original = [(tag, bytes.fromhex(value)) for tag, value in fixture['subrecords']]
expected = [(tag, value) for tag, value in original
            if not (tag == 'ALSP' and value == struct.pack('<I', gen.CONTROL))]
assert rows[1][2] == expected, 'Original quest changed beyond the one control-power grant'
assert [int.from_bytes(v, 'little') for t, v in rows[1][2] if t == 'ALSP'] == [0x04000859]
assert dict(rows[1][2])['VMAD'] == dict(original)['VMAD'], 'Original season script binding changed'
cleanup = rows[2][2]
assert not any(t in ('ALSP', 'INDX') for t, _ in cleanup)
assert dict(cleanup)['DNAM'] == dict(original)['DNAM']
assert dict(cleanup)['ALUA'] == struct.pack('<I', 7)
assert dict(cleanup)['ALST'] == struct.pack('<I', 1)
vmad = dict(cleanup)['VMAD']
assert struct.unpack_from('<HHHBHHH', vmad) == (5, 2, 0, 2, 0, 0, 1)
assert struct.unpack_from('<HhIHHH', vmad, 13) == (0, 1, gen.CLEANUP_QUEST, 5, 2, 1)
offset = 27
def string():
    global offset
    n = struct.unpack_from('<H', vmad, offset)[0]
    offset += 2
    value = vmad[offset:offset+n].decode()
    offset += n
    return value
assert string() == gen.SCRIPT
assert struct.unpack_from('<BH', vmad, offset) == (0, 1)
offset += 3
assert string() == 'ControlPower'
assert vmad[offset:offset+2] == bytes([1, 1])
offset += 2
assert struct.unpack_from('<HhI', vmad, offset) == (0, -1, gen.CONTROL)
assert offset + 8 == len(vmad)
assert (mod / 'SEQ/AzuriteNoControl.seq').read_bytes() == struct.pack('<I', gen.CLEANUP_QUEST)
with tempfile.TemporaryDirectory() as folder:
    gen.generate(fixture, Path(folder))
    assert (Path(folder) / gen.PATCH_NAME).read_bytes() == raw, 'Patch is not reproducible'
provenance = json.loads((mod / 'provenance.json').read_text(encoding='utf-8'))
assert provenance['generated_sha256'] == hashlib.sha256(raw).hexdigest()
assert provenance['input_chinese_sha256'] == '422ac34f9510649f3d3a74bdad0435bcd42a0a1dfa3a3e7172077a6d717d219a'
compiled_count = 0
if args.compiled:
    paths = list(args.compiled.glob('*.pex'))
    assert len(paths) == 1 and paths[0].stem.lower() == gen.SCRIPT.lower()
    data = paths[0].read_bytes()
    assert data.startswith(bytes.fromhex('FA57C0DE')) and len(data) > 100
    for token in [b'OnPlayerLoadGame', b'RemoveSpell', b'ControlPower', b'HasSpell']:
        assert token in data, token
    compiled_count = 1
print(json.dumps({'patch_scope': 'PASS', 'reproducible': True,
                  'original_records_overridden': 1, 'weather_records_overridden': 0,
                  'new_cleanup_quests': 1, 'control_grants_removed': 1,
                  'season_trigger_retained': True, 'compiled_scripts': compiled_count,
                  'gameplay_tested': False}, indent=2))
