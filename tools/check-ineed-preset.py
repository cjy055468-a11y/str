"""Validate the merged preset and ensure the user-tested relay is unchanged."""
from pathlib import Path
import hashlib
import json
import re
import struct
import sys

from ineed_records import editor_id, read_records
from ineed_preset_bytes import normalize_function
from skyrim_pex import Pex

root = Path(sys.argv[1])
report = json.loads((root / 'preset-validation.json').read_text(encoding='utf-8'))
manifest = json.loads((root / 'provenance.json').read_text(encoding='utf-8'))
expected = dict(Animations=2, ForceThird=True, ValuedHarvests=True,
                FoodSpoilage=True, DisplayPercent=True)
assert report['requested_defaults'] == expected
assert hashlib.sha256((root / 'iNeed_STR_Compatibility.esp').read_bytes()).hexdigest() == manifest['retained_compat_plugin_sha256']
assert len(manifest['retained_runtime_sha256']) == 6
for name, digest in manifest['retained_runtime_sha256'].items():
    assert hashlib.sha256((root / 'Scripts' / name).read_bytes()).hexdigest() == digest

originals = {}
for name, item in report['files'].items():
    data = (root / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == item['modified_sha256']
    assert len(data) == item['modified_bytes']
    for edit in reversed(item['edits']):
        pos = edit['modified_offset']
        before, after = bytes.fromhex(edit['before_hex']), bytes.fromhex(edit['after_hex'])
        assert data[pos:pos + len(after)] == after
        data = data[:pos] + before + data[pos + len(after):]
    assert len(data) == item['original_bytes']
    assert hashlib.sha256(data).hexdigest() == item['original_sha256']
    originals[name] = data

main = Pex(root / 'Scripts/_SNQuestScript.pex')
for name, value in expected.items():
    if name == 'ValuedHarvests':
        continue  # This toggle is stored in globals, not a main-script property.
    default = main.property_default('_snquestscript', name)[2]
    assert default.value == value and default.kind == (3 if name == 'Animations' else 5)
# Reconstruct the original main to validate every existing function and string.
main_original_path = root.parent / '.ineed-main-verification.pex'
try:
    main_original_path.write_bytes(originals['Scripts/_SNQuestScript.pex'])
    original_main = Pex(main_original_path)
    assert main.strings == original_main.strings
    assert {k: normalize_function(v) for k, v in main.functions.items()} == {
        k: normalize_function(v) for k, v in original_main.functions.items()}
finally:
    main_original_path.unlink(missing_ok=True)

before = list(read_records(originals['iNeed.esp']))
after = list(read_records((root / 'iNeed.esp').read_bytes()))
assert len(before) == len(after)
changed = []
for a, b in zip(before, after):
    if a == b:
        continue
    assert {k: v for k, v in a.items() if k != 'subs'} == {k: v for k, v in b.items() if k != 'subs'}
    assert a['sig'] == b'GLOB'
    assert [(k, v) for k, v in a['subs'] if k != b'FLTV'] == [(k, v) for k, v in b['subs'] if k != b'FLTV']
    assert next(struct.unpack('<f', v)[0] for k, v in a['subs'] if k == b'FLTV') == 0
    assert next(struct.unpack('<f', v)[0] for k, v in b['subs'] if k == b'FLTV') == 1
    changed.append(editor_id(b))
assert set(changed) == {'_SNValuedHarvestsToggle', '_SNValuedHarvestsDialogueToggle'}

config = Pex(root / 'Scripts/_SNSkyUIConfig.pex')
assert [(a.lower(), b.lower()) for a, b in config.objects] == [('_snskyuiconfig', 'ski_configbase')]
assert {name for (obj, name) in config.properties} == {'_snquest', '_snfoodspoilagequest', 'followerneedstype'}
for name, value in (('animations', 2), ('displaypercent', 1), ('valuedharvests', 1)):
    assert config.variables[('_snskyuiconfig', name)][1].value == value
assert config.variables[('_snskyuiconfig', 'forcethird')][1].value in (None, 0)

def calls(name):
    body = config.functions[('_snskyuiconfig', '', name)]
    return [(str(args[0].value).lower(), args, rest) for _, op, args, rest in body['instructions'] if op in (23, 24)]

ready_calls = calls('onconfigmanagerready')
assert 'unregistermod' in [name for name, _, _ in ready_calls]
assert 'registermod' not in [name for name, _, _ in ready_calls]
assert any(name == 'unregisterformodevent' and rest[0].value == 'SKICP_configManagerReady' for name, _, rest in ready_calls)
assert 'strapplypreset' in [name for name, _, _ in calls('onconfiginit')]
assert 'start' in [name for name, _, _ in calls('strapplypreset')]
assert 'stop' not in [name for name, _, _ in calls('strapplypreset')]
assert 'applysettings' not in [name for name, _, _ in calls('strapplypreset')]
assert all(not name.startswith('setgame') for name, _, _ in calls('strapplypreset'))
assert ('_snskyuiconfig', '', 'onconfigmanagerreset') in config.functions
for preserved_callback in ('onkeydown', 'onanimationevent', 'onupdate', 'applysettings', 'onconfigclose'):
    assert ('_snskyuiconfig', '', preserved_callback) in config.functions
source = (root / 'Scripts/Source/_SNSkyUIConfig.psc').read_text()
blocks = {match[1].lower(): match[0] for match in re.finditer(
    r'(?ims)^(?:\w+[ \t]+)?(?:Function|Event)[ \t]+(\w+)\([^\n]*\).*?^End(?:Function|Event)[^\n]*', source)}
for name, digest in manifest['config_preserved_source_functions'].items():
    assert hashlib.sha256(blocks[name].encode()).hexdigest() == digest, name
assert 'manager.UnregisterMod(Self)' in source and 'manager.RegisterMod(' not in source
assert 'DisplayPercentList[1] = "$Numbers"' in source
assert '_SNQuest.FoodSpoilage = True' in source and '_SNQuest.DisplayPercent = True' in source
assert '_SNFoodSpoilageQuest.Start()' in source
assert not any(p.suffix.lower() in ('.dll', '.exe') for p in root.rglob('*') if p.is_file())
assert not any(p.name.lower().startswith('ski_') for p in (root / 'Scripts').glob('*.pex'))
print(json.dumps(dict(result='PASS', defaults=expected, mcm='hidden by per-mod registration override',
                      spoilage_quest_auto_start=True, numeric_spoilage='original Numbers / remaining freshness percent',
                      main_localization_and_all_function_bodies_preserved=True,
                      validated_animation_relay_and_previous_fixes_byte_identical=True,
                      changed_original_plugin_records=changed, runtime_scripts=8,
                      animation_gameplay='User confirmed A consumes and B can see it',
                      new_preset_and_hidden_mcm_gameplay='NOT RUN'), ensure_ascii=False, indent=2))
