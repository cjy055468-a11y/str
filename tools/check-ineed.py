"""Validate overlay scope, original records, bindings, and compiled Skyrim PEX."""
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

from ineed_records import editor_id, pack_subs, read_records

root, compiled = map(Path, sys.argv[1:3])
manifest = json.loads((root / 'provenance.json').read_text(encoding='utf-8'))
records = list(read_records((root / 'iNeed_STR_Compatibility.esp').read_bytes()))
header, effects = records[0], records[1:]
masters = [v.decode().rstrip('\0') for k, v in header['subs'] if k == b'MAST']
assert masters == manifest['plugin_masters']
assert len(effects) == 2 and all(r['sig'] == b'MGEF' for r in effects)
assert {editor_id(r) for r in effects} == set(manifest['original_effects'])
for record in effects:
    original = manifest['original_effects'][editor_id(record)]
    assert record['fid'] == original['form_id']
    payload = pack_subs([(k, v) for k, v in record['subs'] if k != b'VMAD'])
    assert hashlib.sha256(payload).hexdigest() == original['non_vmad_sha256']
    vmad = next(v for k, v in record['subs'] if k == b'VMAD')
    name_size = struct.unpack_from('<H', vmad, 6)[0]
    name = vmad[8:8 + name_size].decode()
    assert name == original['replacement_script']
    assert (root / 'Scripts/Source' / (name + '.psc')).exists()

expected = {'_snneeds.pex', '_snstrlocalimod.pex', '_snstrlocalstumble.pex'}
paths = list(compiled.glob('*.pex'))
assert {p.name.lower() for p in paths} == expected
for path in paths:
    data = path.read_bytes()
    assert data[:8] == bytes.fromhex('fa57c0de03020001'), (path, data[:8].hex())
    assert len(data) > 100
    # Header strings are length-prefixed UTF-8; all later symbol indices refer here.
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
        strings.append(data[offset:offset + size].decode('utf-8'))
        offset += size
    lower = {s.lower() for s in strings}
    assert path.stem.lower() in lower
    if path.stem.lower() == '_snneeds':
        assert {'strrecoversleep', 'strlocalneeds', 'querystat', 'hours slept'} <= lower
        original_properties = manifest['needs_properties']
        assert set(p.lower() for p in original_properties) <= lower
    if path.stem.lower() == '_snstrlocalimod':
        assert {'getplayer', 'oneffectstart', 'oneffectfinish', 'staticfx', 'localeffect'} <= lower

assert not list(root.rglob('*.exe')) and not list(root.rglob('*.dll'))
source = (root / 'Scripts/Source/_SNNeeds.psc').read_text()
assert source.count('STRRecoverSleep(CompletedHours)') == 1
assert 'OnSleepStop(false)' not in source
assert 'Game.QueryStat("Hours Slept") - STRSleepStartHours' in source
assert not re.search(r'Set(GameHour|CurrentGameTime|TimeScale)|\.SetValue\(', source, re.I)
print(json.dumps({'result': 'PASS', 'record_overrides': 2, 'skyrim_pex_3_2': len(paths),
                  'original_stats_and_effect_properties_preserved': True,
                  'native_binaries_changed': False,
                  'sleep_accounting': 'Hours Slept delta; interrupted sleep uses completed hours',
                  'gameplay_two_clients': 'NOT RUN'}, indent=2))
