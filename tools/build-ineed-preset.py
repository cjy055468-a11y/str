"""Apply only preset initializers to the supplied Chinese loose main PEX."""
from pathlib import Path
import hashlib
import json
import sys

from ineed_preset_bytes import apply_edits, default_edit, harvest_edits, normalize_function, update_size
from skyrim_pex import Pex

original, output = map(Path, sys.argv[1:3])
output.mkdir(parents=True, exist_ok=True)
(output / 'Scripts').mkdir(exist_ok=True)
main = Pex(original / 'scripts/_snquestscript.pex')
assert hashlib.sha256(main.data).hexdigest() == '059d3dda1832e7b411a4edc5df64060c4657d4093ee186ce159bf29497e80ce3'
edits, delta = [], 0
for name, kind, value in (('Animations', 3, 2), ('FoodSpoilage', 5, 1)):
    _, backing, _ = main.property_default('_snquestscript', name)
    edit, added = default_edit(main, backing, kind, value)
    edits.append(edit)
    delta += added
for name in ('ForceThird', 'DisplayPercent', 'EnableMod'):
    value = main.property_default('_snquestscript', name)[2]
    assert value.kind == 5 and value.value == 1
raw, details = apply_edits(main.data, edits + [update_size(main, delta)])
target = output / 'Scripts/_SNQuestScript.pex'
target.write_bytes(raw)
patched = Pex(target)
assert {k: normalize_function(v) for k, v in main.functions.items()} == {
    k: normalize_function(v) for k, v in patched.functions.items()}
details['all_function_bodies_unchanged'] = True
plugin = (original / 'iNeed.esp').read_bytes()
assert hashlib.sha256(plugin).hexdigest() == 'ada5d1b2118a1dff121ef8f728d870b485d2fb3c910ac00a6481e786725d0fb7'
raw, plugin_details = apply_edits(plugin, harvest_edits(plugin))
(output / 'iNeed.esp').write_bytes(raw)
report = dict(version='0.3-preset-nomcm',
              requested_defaults=dict(Animations=2, ForceThird=True, ValuedHarvests=True,
                                      FoodSpoilage=True, DisplayPercent=True),
              mcm='hidden: original quest and hotkey callbacks retained',
              files={'Scripts/_SNQuestScript.pex': details, 'iNeed.esp': plugin_details},
              original_main_localization_and_functions_preserved=True,
              preset_gameplay_tested=False)
(output / 'preset-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(result='PASS', defaults=report['requested_defaults'],
                      original_main_function_bodies_unchanged=True,
                      modified_plugin_globals_only=2), indent=2))
