"""Build two iNeed MGEF overrides; never edit the source ESP in place."""
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

header = dict(sig=b'TES4', fid=0, flags=0, revision=0, version=44, unknown=0,
              subs=[(b'HEDR', struct.pack('<fII', 1.7, len(overrides) + 1, 0x800)),
                    (b'CNAM', b'iNeed STR compatibility\0'),
                    (b'SNAM', b'Local drunk visuals/physics; sleep script overlay.\0')])
for master in masters + [b'iNeed.esp\0']:
    header['subs'] += [(b'MAST', master), (b'DATA', b'\0' * 8)]
body = b''.join(map(pack_record, overrides))
group = struct.pack('<4sI4sIHHI', b'GRUP', len(body) + 24, b'MGEF', 0, 0, 0, 0) + body
output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(pack_record(header) + group)
assert len(list(read_records(output.read_bytes()))) == 3
print(json.dumps({'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                  'plugin_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                  'overrides': [editor_id(r) for r in overrides],
                  'unchanged_gameplay_data': True}, indent=2))
