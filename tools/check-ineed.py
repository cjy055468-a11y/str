"""Validate overlay scope, original records, bindings, and compiled Skyrim PEX."""
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

from ineed_records import editor_id, pack_subs, read_records
from skyrim_pex import Pex

root, compiled = map(Path, sys.argv[1:3])
manifest = json.loads((root / 'provenance.json').read_text(encoding='utf-8'))
records = list(read_records((root / 'iNeed_STR_Compatibility.esp').read_bytes()))
header = records[0]
effects = [r for r in records[1:] if r['fid'] >> 24 == 5]
private = [r for r in records[1:] if r['fid'] >> 24 == 6]
masters = [v.decode().rstrip('\0') for k, v in header['subs'] if k == b'MAST']
assert masters == manifest['plugin_masters']
assert len(effects) == 2 and all(r['sig'] == b'MGEF' for r in effects)
assert {editor_id(r) for r in effects} == set(manifest['original_effects'])
assert len(records) == 16 and len(private) == 13
assert len({r['fid'] for r in records}) == len(records)
assert all(r['fid'] >> 24 in (5, 6) for r in records[1:])
assert {r['sig'] for r in private} == {b'MGEF', b'SPEL', b'QUST'}
assert struct.unpack('<fII', dict(header['subs'])[b'HEDR'])[1:] == (18, 0x826)
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

expected = {'_snneeds.pex', '_snstrlocalimod.pex', '_snstrlocalstumble.pex',
            '_snplayeralias.pex', '_snstrconsumerelay.pex', '_snstrconsumepulse.pex'}
paths = list(compiled.glob('*.pex'))
assert {p.name.lower() for p in paths} == expected
pex_objects = {p.stem.lower(): Pex(p) for p in paths}
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

# Validate all new VMAD property names/types against the actual compiled objects.
def vmad_properties(data):
    assert struct.unpack_from('<HHH', data) == (5, 2, 1)
    def string(offset):
        size = struct.unpack_from('<H', data, offset)[0]
        return data[offset + 2:offset + 2 + size].decode(), offset + 2 + size
    script, offset = string(6)
    offset += 1
    count = struct.unpack_from('<H', data, offset)[0]
    offset += 2
    props = {}
    for _ in range(count):
        name, offset = string(offset)
        typ, status = data[offset:offset + 2]
        offset += 2
        assert status == 1 and name.lower() not in props
        if typ == 1:
            unused, alias, value = struct.unpack_from('<HHI', data, offset)
            assert unused == 0 and alias == 0xFFFF
            offset += 8
        elif typ == 3:
            value = struct.unpack_from('<i', data, offset)[0]
            offset += 4
        else:
            raise AssertionError((script, name, typ))
        props[name.lower()] = (typ, value)
    assert offset == len(data)
    return script.lower(), props

by_id = {r['fid']: r for r in private}
for action, name in enumerate(('Reset', 'Eat', 'Drink', 'ChairEat', 'ChairDrink', 'Stop')):
    effect = by_id[0x06000820 + action]
    assert editor_id(effect) == '_SNSTRConsume' + name + 'Effect'
    parts = dict(effect['subs'])
    data = parts[b'DATA']
    assert len(data) == 152 and struct.unpack_from('<I', data)[0] == 0x0C008810
    assert all(struct.unpack_from('<i', data, o)[0] == -1 for o in (12, 16, 68, 88))
    assert struct.unpack_from('<I', data, 64)[0] == 1  # Script, not Slow Time
    assert struct.unpack_from('<II', data, 80) == (1, 0)  # fire-and-forget, self
    script, props = vmad_properties(parts[b'VMAD'])
    assert script == '_snstrconsumepulse' and props == {'action': (3, action)}
    assert pex_objects[script].properties[(script, 'action')][0].lower() == 'int'
    spell = by_id[0x06000810 + action]
    assert editor_id(spell) == '_SNSTRConsume' + name + 'Pulse'
    parts = dict(spell['subs'])
    assert struct.unpack('<IIIfIIffI', parts[b'SPIT']) == (0, 0x300001, 0, 0, 1, 0, 0, 0, 0)
    assert struct.unpack('<I', parts[b'EFID'])[0] == effect['fid']
    assert struct.unpack('<fII', parts[b'EFIT']) == (1.0, 0, 1)
quest = by_id[0x06000800]
assert editor_id(quest) == '_SNSTRConsumeRelay'
parts = dict(quest['subs'])
assert struct.unpack('<HBBII', parts[b'DNAM']) == (0, 0, 0, 0, 0)
assert set(parts) == {b'EDID', b'VMAD', b'DNAM', b'NEXT', b'ANAM'}
script, props = vmad_properties(parts[b'VMAD'])
assert script == '_snstrconsumerelay'
for action, name in enumerate(('Reset', 'Eat', 'Drink', 'ChairEat', 'ChairDrink', 'Stop')):
    assert props[(name + 'Pulse').lower()] == (1, 0x06000810 + action)
    assert pex_objects[script].properties[(script, (name + 'Pulse').lower())][0].lower() == 'spell'
assert props['idlestop_loose'] == (1, 0x0010D9EE) and len(props) == 7
assert {prop: val[0].lower() for (obj, prop), val in pex_objects['_snplayeralias'].properties.items()} == manifest['player_alias_properties']
for name, digest in manifest['retained_runtime_sha256'].items():
    assert hashlib.sha256((root / 'Scripts' / name).read_bytes()).hexdigest() == digest

assert not list(root.rglob('*.exe')) and not list(root.rglob('*.dll'))
source = (root / 'Scripts/Source/_SNNeeds.psc').read_text()
assert source.count('STRRecoverSleep(CompletedHours)') == 1
assert 'OnSleepStop(false)' not in source
assert 'Game.QueryStat("Hours Slept") - STRSleepStartHours' in source
assert not re.search(r'Set(GameHour|CurrentGameTime|TimeScale)|\.SetValue\(', source, re.I)
relay_source = (root / 'Scripts/Source/_SNSTRConsumeRelay.psc').read_text()
pulse_source = (root / 'Scripts/Source/_SNSTRConsumePulse.psc').read_text()
alias_source = (root / 'Scripts/Source/_SNPlayerAlias.psc').read_text()
preserved_alias = re.sub(r'(?ims)^(?:Function|Event)\s+(?:PlayConsumeIdles|OnInit|OnGetUp)\b.*?^End(?:Function|Event)[^\n]*', '', alias_source)
assert hashlib.sha256(preserved_alias.encode()).hexdigest() == manifest['player_alias_preserved_source_sha256']
assert 'SkyrimTogetherUtils.IsRemotePlayer(akTarget)' in pulse_source
assert 'akTarget == Game.GetPlayer()' in pulse_source
assert 'OnEffectFinish' not in re.sub(r';[^\n]*', '', pulse_source)
assert 'ForceFirstPerson' not in relay_source + pulse_source
assert 'ForceThirdPerson' not in relay_source + pulse_source
assert 'Epoch * 256 + Sequence' in relay_source and 'PreviousEpochs[slot]' in relay_source
assert 'token >= RemoteTokens[slot]' in relay_source
assert alias_source.count('Utility.Wait(7.0)') == 1 and alias_source.count('Utility.Wait(7.5)') == 1
assert all(x in alias_source for x in ('_SNQuest.NoAnimate', '_SNQuest.Animations', '_SNQuest.ForceThird'))
print(json.dumps({'result': 'PASS', 'record_overrides': 2, 'new_private_forms': 13,
                  'skyrim_pex_3_2': len(paths), 'vmad_matches_compiled_properties': True,
                  'previous_runtime_binaries_preserved': True,
                  'original_stats_and_effect_properties_preserved': True,
                  'native_binaries_changed': False,
                  'sleep_accounting': 'Hours Slept delta; interrupted sleep uses completed hours',
                  'gameplay_two_clients': 'NOT RUN'}, indent=2))
