"""Build preserved drunk overrides and private consume relay forms."""
import copy
import hashlib
import json
from pathlib import Path
import struct
import sys

from ineed_records import editor_id, pack_record, pack_subs, read_records, vmad

source, output = map(Path, sys.argv[1:3])
records = list(read_records(source.read_bytes()))
header = records[0]
masters = [v for k, v in header['subs'] if k == b'MAST']
assert masters == [x.encode() + b'\0' for x in
                   ('Skyrim.esm', 'Update.esm', 'Dawnguard.esm', 'HearthFires.esm', 'Dragonborn.esm')]
byname = {editor_id(r): r for r in records}
overrides = []
for name in ('_SNDrunkFX', '_SNDrunkStumbleScript'):
    record = copy.deepcopy(byname[name])
    assert record['sig'] == b'MGEF' and record['fid'] >> 24 == len(masters)
    if name == '_SNDrunkFX':
        original = next(v for k, v in record['subs'] if k == b'VMAD')
        script = b'magicImodScript'
        replacement = b'_SNSTRLocalImod'
        assert original[8:8 + len(script)] == script
        # Preserve all original image-space properties and their form IDs.
        patched = original[:6] + struct.pack('<H', len(replacement)) + replacement + original[8 + len(script):]
    else:
        patched = vmad('_SNSTRLocalStumble', [])
    record['subs'] = [(k, patched if k == b'VMAD' else v) for k, v in record['subs']]
    assert [(k, v) for k, v in record['subs'] if k != b'VMAD'] == [
        (k, v) for k, v in byname[name]['subs'] if k != b'VMAD']
    overrides.append(record)

def record(kind, local_id, name, subs):
    return dict(sig=kind, fid=0x06000000 | local_id, flags=0, revision=0,
                version=44, unknown=0, subs=[(b'EDID', name.encode() + b'\0')] + subs)


def object_property(name, form_id):
    return name, 1, struct.pack('<HHI', 0, 0xFFFF, form_id)


actions = ('Reset', 'Eat', 'Drink', 'ChairEat', 'ChairDrink', 'Stop')
new_effects, spells = [], []
for action, name in enumerate(actions):
    # TES5 MGEF DATA layout checked against xEdit wbDefinitionsTES5.pas.
    data = bytearray(152)
    struct.pack_into('<I', data, 0, 0x0C008810)  # hidden, painless, no hit/area/visuals
    for offset in (12, 16, 68, 88):
        struct.pack_into('<i', data, offset, -1)  # no skill/resistance/actor values
    struct.pack_into('<I', data, 64, 1)  # Script archetype, never Slow Time
    struct.pack_into('<I', data, 80, 1)  # fire and forget
    struct.pack_into('<I', data, 140, 2)  # silent
    effect_id = 0x06000820 + action
    spell_id = 0x06000810 + action
    new_effects.append(record(b'MGEF', 0x820 + action, '_SNSTRConsume' + name + 'Effect', [
        (b'VMAD', vmad('_SNSTRConsumePulse', [('Action', 3, struct.pack('<i', action))])),
        (b'DATA', bytes(data)), (b'DNAM', b'\0')]))
    # Manual zero-cost self cast, ignore resistance and absorb/reflect. No cast art.
    spit = struct.pack('<IIIfIIffI', 0, 0x300001, 0, 0.0, 1, 0, 0.0, 0.0, 0)
    spells.append(record(b'SPEL', 0x810 + action, '_SNSTRConsume' + name + 'Pulse', [
        (b'OBND', b'\0' * 12), (b'FULL', b'\0'), (b'DESC', b'\0'), (b'SPIT', spit),
        (b'EFID', struct.pack('<I', effect_id)), (b'EFIT', struct.pack('<fII', 1.0, 0, 1))]))

# This is the exact vanilla IdleStop_Loose binding on the uploaded _SNQuest.
idle_stop = 0x0010D9EE
assert bytes.fromhex('0000ffffeed91000') in next(
    v for k, v in byname['_SNQuest']['subs'] if k == b'VMAD')
properties = [object_property(name + 'Pulse', 0x06000810 + action)
              for action, name in enumerate(actions)]
properties.append(object_property('IdleStop_Loose', idle_stop))
quest = record(b'QUST', 0x800, '_SNSTRConsumeRelay', [
    (b'VMAD', vmad('_SNSTRConsumeRelay', properties)),
    # No stages, aliases, dialogue, journal or autostart: GetRelay explicitly starts it.
    (b'DNAM', struct.pack('<HBBII', 0, 0, 0, 0, 0)), (b'NEXT', b''), (b'ANAM', struct.pack('<I', 0))])
groups = [(b'MGEF', overrides + new_effects), (b'SPEL', spells), (b'QUST', [quest])]
record_count = sum(len(items) for _, items in groups)
header = dict(sig=b'TES4', fid=0, flags=0, revision=0, version=44, unknown=0,
              subs=[(b'HEDR', struct.pack('<fII', 1.7, record_count + len(groups), 0x826)),
                    (b'CNAM', b'iNeed STR compatibility\0'),
                    (b'SNAM', b'Local drunk effects, sleep accounting, consume animation relay.\0')])
for master in masters + [b'iNeed.esp\0']:
    header['subs'] += [(b'MAST', master), (b'DATA', b'\0' * 8)]
body = b''
for label, items in groups:
    payload = b''.join(map(pack_record, items))
    body += struct.pack('<4sI4sIHHI', b'GRUP', len(payload) + 24, label, 0, 0, 0, 0) + payload
output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(pack_record(header) + body)
assert len(list(read_records(output.read_bytes()))) == 1 + record_count
print(json.dumps({'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                  'plugin_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                  'overrides': [editor_id(r) for r in overrides],
                  'new_private_records': record_count - len(overrides),
                  'unchanged_gameplay_data': True}, indent=2))
