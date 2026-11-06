import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

root = Path(sys.argv[1]).resolve()
repo = Path(__file__).resolve().parent.parent
delta = repo / 'fixes/corpse3-delta.patch'
expected = json.loads((repo / 'fixes/corpse3-scope.json').read_text())
paths = re.findall(r'^diff --git a/(.*?) b/', delta.read_text(), re.M)
assert paths == expected and len(paths) == 19
assert all(p.startswith('Code/client/') or p == 'Code/tests/corpse_speech_window.cpp' for p in paths)
assert not any('Missives' in p for p in paths)
env = os.environ.copy()
env['GIT_CEILING_DIRECTORIES'] = str(Path(tempfile.gettempdir()).resolve())
with tempfile.TemporaryDirectory(prefix='str-corpse3-scope-') as directory:
    normalized = Path(directory)
    for name in paths:
        target = normalized / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, target)
    subprocess.run(['git', 'apply', '--reverse', '--check', str(delta)], cwd=normalized, env=env, check=True)
    subprocess.run(['git', 'apply', '--reverse', str(delta)], cwd=normalized, env=env, check=True)
    # Check native combat, the old ActorProcess, the narrow SetPosition
    # exception and ordinary inventory/container paths against official source
    # after reversing exactly the reviewed corpse3 increment in a COPY.
    result = subprocess.run([sys.executable, str(repo / 'tools/check-source-scope.py'), str(root),
                             '--native-corpses', '--corpse-death-recovery',
                             '--normalized-source=' + str(normalized)], check=True, capture_output=True, text=True)
    baseline = json.loads(result.stdout)

actor = (root / 'Code/client/Games/Skyrim/Actor.cpp').read_text()
assert 'Actor::Create(pNpc, !acMessage.IsPlayer)' in (root / 'Code/client/Services/Generic/CharacterService.cpp').read_text()
assert actor.count('MarkNetworkNpcReplica();') == 1
assert 'NetworkActorSavePolicy::CanFilter(pActor)' in actor
extension = (root / 'Code/client/Games/ActorExtension.h').read_text()
assert 'mutable uint32_t onlineFlags{0};' in extension
assert 'std::atomic<' not in extension
assert 'actions.clear();' not in (root / 'Code/client/Systems/AnimationSystem.cpp').read_text()
assert not list((root / 'Code/client/ModCompat').glob('Missives*'))
print(json.dumps({'changed_files': paths, 'delta_sha256': hashlib.sha256(delta.read_bytes()).hexdigest(),
                  'legacy_scope_after_exact_increment_reversal': baseline,
                  'new_network_fields': False, 'native_actor_storage_added': False,
                  'corpse2_death_actions_and_graph_updates_retained': True,
                  'missives_excluded': True, 'native_game_test': 'not run'}, indent=2))
