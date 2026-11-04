import json
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
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
    assert before.replace(b'\r\n', b'\n') == (root / file).read_bytes().replace(b'\r\n', b'\n'), file
file = 'Code/client/Games/Skyrim/Actor.cpp'
before = subprocess.check_output(['git', '-C', str(root), 'show', 'HEAD:' + file]).decode()
after = (root / file).read_text()
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
    assert original.replace('\r\n', '\n') == current.replace('\r\n', '\n'), start
# The only new container/death changes defer epoch-matched updates into the
# existing pending spawn snapshot; require the rest of both handlers unchanged.
for file, function, original_start in [
    ('Code/client/Services/Generic/InventoryService.cpp', 'void InventoryService::OnNotifyInventoryChanges', '    if (acMessage.OwnershipEpoch != 0)'),
    ('Code/client/Services/Generic/ActorValueService.cpp', 'void ActorValueService::OnDeathStateChange', '    auto view = m_world.view<FormIdComponent, RemoteComponent>();'),
]:
    before = subprocess.check_output(['git', '-C', str(root), 'show', 'HEAD:' + file]).decode().replace('\r\n', '\n')
    after = (root / file).read_text().replace('#include <Systems/PendingActorUpdates.h>\n', '')
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
after = (root / file).read_text()
for start, end in [('void InventoryService::OnInventoryChanges', 'void InventoryService::OnEquipmentChanges')]:
    assert before[before.index(start):before.index(end)].replace('\r\n', '\n') == after[after.index(start):after.index(end)].replace('\r\n', '\n')
print(json.dumps({'unchanged_files': unchanged, 'original_combat_regions': len(regions),
                  'original_server_inventory_handler': 'unchanged'}, indent=2))
