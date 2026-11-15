"""Verify every changed byte and the requested defaults in a built overlay."""
from pathlib import Path
import hashlib
import json
import struct
import sys

from ineed_records import editor_id, read_records
from pex_defaults import Pex


def verify(root):
    manifest = json.loads((root / 'validation.json').read_text(encoding='utf-8'))
    assert manifest['requested_defaults'] == dict(Animations=2, ForceThird=True, ValuedHarvests=True)
    originals = {}
    for name, item in manifest['files'].items():
        raw = (root / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == item['modified_sha256']
        assert len(raw) == item['modified_bytes']
        restored = raw
        for edit in reversed(item['edits']):
            offset = edit['modified_offset']
            after, before = bytes.fromhex(edit['after_hex']), bytes.fromhex(edit['before_hex'])
            assert restored[offset:offset + len(after)] == after
            restored = restored[:offset] + before + restored[offset + len(after):]
        assert len(restored) == item['original_bytes']
        assert hashlib.sha256(restored).hexdigest() == item['original_sha256']
        originals[name] = restored
    main = Pex(root / 'scripts/_snquestscript.pex')
    assert main.property_default('_snquestscript', 'Animations')[2].value == 2
    camera = main.property_default('_snquestscript', 'ForceThird')[2]
    assert camera.kind == 5 and camera.value == 1
    mcm = Pex(root / 'scripts/_snskyuiconfig.pex')
    assert mcm.variables[('_snskyuiconfig', 'animations')][1].value == 2
    assert mcm.variables[('_snskyuiconfig', 'valuedharvests')][1].value == 1
    instructions = mcm.functions[('_snskyuiconfig', '', 'onoptionmenuopen')]['instructions']
    previous = None
    defaults = []
    for _, op, args, rest in instructions:
        if op != 23:
            continue
        if str(args[0].value).lower() == 'setmenudialogstartindex':
            previous = rest[0].value
        if str(args[0].value).lower() == 'setmenudialogdefaultindex' and str(previous).lower() == 'animations':
            defaults.append(rest[0].value)
    assert defaults == [2]
    before = list(read_records(originals['iNeed.esp']))
    after = list(read_records((root / 'iNeed.esp').read_bytes()))
    assert len(before) == len(after)
    changed = []
    for a, b in zip(before, after):
        if a != b:
            assert {k: v for k, v in a.items() if k != 'subs'} == {k: v for k, v in b.items() if k != 'subs'}
            assert [(k, v) for k, v in a['subs'] if k != b'FLTV'] == [(k, v) for k, v in b['subs'] if k != b'FLTV']
            assert a['sig'] == b'GLOB'
            assert next(struct.unpack('<f', v)[0] for k, v in b['subs'] if k == b'FLTV') == 1.0
            changed.append(editor_id(b))
    assert set(changed) == {'_SNValuedHarvestsToggle', '_SNValuedHarvestsDialogueToggle'}
    return dict(status='PASS', defaults=manifest['requested_defaults'],
                changed_plugin_records=changed, pex_version='Skyrim 3.2',
                runtime_scripts=2, unchanged_extra_plugins=True,
                all_originals_exactly_reconstructed=True, gameplay_tested=False)


if __name__ == '__main__':
    print(json.dumps(verify(Path(sys.argv[1])), ensure_ascii=False, indent=2))
