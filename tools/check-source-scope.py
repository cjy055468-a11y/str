import json
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path

root = Path(sys.argv[1])
normalized_root = None
if '--missives-audit' in sys.argv:
    normalized_context = tempfile.TemporaryDirectory(prefix='str-missives-scope-')
    normalized_root = Path(normalized_context.name)
    files = ['Code/client/Games/Skyrim/TESObjectREFR.cpp', 'Code/client/Services/Generic/InventoryService.cpp',
             'Code/client/Services/Generic/ObjectService.cpp', 'Code/client/Services/Generic/QuestService.cpp']
    for file in files:
        target = normalized_root / file
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / file, target)
    patch = Path(__file__).resolve().parent.parent / 'fixes/missives1-delta.patch'
    subprocess.run(['git', 'apply', '--reverse', *['--include=' + f for f in files], str(patch)], cwd=normalized_root, check=True)

def current_path(file):
    if normalized_root is not None and (normalized_root / file).exists():
        return normalized_root / file
    return root / file
unchanged = [
    'Code/client/Games/Forms.cpp',
    'Code/client/Games/Skyrim/Actor.h',
    'Code/client/Services/Generic/CombatService.cpp',
    'Code/client/Services/Generic/ObjectService.cpp',
    'Code/client/Components/RemoteAnimationComponent.h',
    'Code/server/Services/ObjectService.cpp',
]
for file in unchanged:
    before = subprocess.check_output(['git', '-C', str(root), 'show', 'HEAD:' + file])
    assert before.replace(b'\r\n', b'\n') == current_path(file).read_bytes().replace(b'\r\n', b'\n'), file
file = 'Code/client/Games/Skyrim/Actor.cpp'
before = subprocess.check_output(['git', '-C', str(root), 'show', 'HEAD:' + file]).decode()
after = current_path(file).read_text()
regions = [
    ('bool TP_MAKE_THISCALL(HookDamageActor', 'TP_THIS_FUNCTION(TApplyActorEffect'),
    ('char TP_MAKE_THISCALL(HookActorProcess', 'TP_THIS_FUNCTION(TAddDeathItems'),
    ('char TP_MAKE_THISCALL(HookSetPosition', 'TP_THIS_FUNCTION(TForceState'),
    ('void Actor::StartCombatEx', 'bool Actor::RemoveSpell'),
    ('void TP_MAKE_THISCALL(HookAddInventoryItem, Actor', 'void* TP_MAKE_THISCALL(HookPickUpObject'),
]
for start, end in regions:
    original = before[before.index(start):before.index(end, before.index(start))]
    current = after[after.index(start):after.index(end, after.index(start))]
    if start.startswith('char TP_MAKE_THISCALL(HookActorProcess') and '--native-corpses' in sys.argv:
        exception = (Path(__file__).resolve().parent.parent / 'fixes/corpse1-native-process-block.txt').read_text()
        assert current.count(exception) == 1, 'Unexpected corpse process change'
        current = current.replace(exception, '')
    if start.startswith('char TP_MAKE_THISCALL(HookSetPosition') and '--native-corpses' in sys.argv:
        prefix = '    if (bIsRemote && !ScopedReferencesOverride::IsOverriden())\n'
        begin = current.index(prefix) + len(prefix)
        end_block = current.index('    // Don\'t interfere', begin)
        expected = (Path(__file__).resolve().parent.parent / 'fixes/corpse1-native-position-block.txt').read_text()
        assert current[begin:end_block] == expected, 'Unexpected corpse hook change'
        current = current[:begin] + '        return 1;\n\n' + current[end_block:]
    assert original.replace('\r\n', '\n') == current.replace('\r\n', '\n'), start
# The only new container/death changes defer epoch-matched updates into the
# existing pending spawn snapshot; require the rest of both handlers unchanged.
for file, function, original_start in [
    ('Code/client/Services/Generic/InventoryService.cpp', 'void InventoryService::OnNotifyInventoryChanges', '    if (acMessage.OwnershipEpoch != 0)'),
    ('Code/client/Services/Generic/ActorValueService.cpp', 'void ActorValueService::OnDeathStateChange', '    auto view = m_world.view<FormIdComponent, RemoteComponent>();'),
]:
    before = subprocess.check_output(['git', '-C', str(root), 'show', 'HEAD:' + file]).decode().replace('\r\n', '\n')
    after = current_path(file).read_text().replace('#include <Systems/PendingActorUpdates.h>\n', '')
    begin = after.index('    if (const auto entity = ', after.index(function))
    end = after.index(original_start, begin)
    after = after[:begin] + after[end:]
    if file.endswith('InventoryService.cpp'):
        start = 'void InventoryService::OnNotifyEquipmentChanges'
        end = 'void InventoryService::RunWeaponStateUpdates'
        # This actor-only handler is intentionally revised for owner armor
        # snapshots. Still require all other legacy inventory code unchanged.
        after = after[:after.index(start)] + before[before.index(start):before.index(end)] + after[after.index(end):]
    assert before == after, file + ': change outside authorized actor equipment/pending prefixes'
file = 'Code/server/Services/InventoryService.cpp'
before = subprocess.check_output(['git', '-C', str(root), 'show', 'HEAD:' + file]).decode()
after = current_path(file).read_text()
for start, end in [('void InventoryService::OnInventoryChanges', 'void InventoryService::OnEquipmentChanges')]:
    assert before[before.index(start):before.index(end)].replace('\r\n', '\n') == after[after.index(start):after.index(end)].replace('\r\n', '\n')
print(json.dumps({('unchanged_files_after_verified_missives_delta_reversal' if '--missives-audit' in sys.argv else 'unchanged_files'): unchanged, 'original_combat_regions': len(regions),
                  'original_server_inventory_handler': 'unchanged'}, indent=2))
