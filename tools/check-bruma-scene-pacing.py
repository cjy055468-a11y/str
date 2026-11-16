"""Verify the client-only scheduling scope against the user's exact native baseline."""
from pathlib import Path
import hashlib
import json
import sys

source = Path(sys.argv[1])
repo = Path(__file__).resolve().parent.parent
base = json.loads((repo / 'fixes/notice-v2-source-manifest.json').read_text())
review = json.loads((repo / 'fixes/bruma-scene-pacing-v1-review.json').read_text())


def digest(data):
    return hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest()


assert digest((repo / 'fixes/notice-v2-v184.patch').read_bytes()) == review['base_patch_sha256']
assert digest((repo / 'fixes/bruma-scene-pacing-v1.patch').read_bytes()) == review['addon_patch_sha256']
for name, expected in base['files'].items():
    path = source / name
    if expected is None:
        assert not path.exists(), name
        continue
    data = path.read_bytes()
    if name in review['modified_client_sources']:
        assert expected == review['modified_client_sources'][name]['before_sha256'], name
        assert digest(data) == review['modified_client_sources'][name]['after_sha256'], name
        continue
    if name in review['inserted_only']:
        data = b''.join(line for line in data.splitlines(keepends=True) if b'SCENE_SYNC_DIAG' not in line)
    assert digest(data) == expected, name

for name, item in review['inserted_only'].items():
    data = (source / name).read_bytes()
    assert digest(data) == item['after_sha256'], name
    restored = b''.join(line for line in data.splitlines(keepends=True) if b'SCENE_SYNC_DIAG' not in line)
    assert digest(restored) == item['before_sha256'], name
for name, item in review['modified_client_sources'].items():
    assert name in {'Code/client/Services/Generic/TransportService.cpp', 'Code/client/Services/TransportService.h'}
    assert digest((source / name).read_bytes()) == item['after_sha256'], name
for name, expected in review['added_files'].items():
    assert name in {'Code/client/Diagnostics/SceneSyncTrace.h', 'Code/client/Services/SceneSyncInbox.h', 'Code/tests/scene_sync_inbox.cpp'}
    assert digest((source / name).read_bytes()) == expected, name

assert review['protocol_changes'] is False
assert review['server_changes'] is False
assert review['new_engine_hooks'] is False
assert review['previous_esms_used'] is False
print(json.dumps(dict(result='PASS', protocol='original notice-board-v2-r1',
                      client_dispatch_scheduling_changed=True,
                      original_actor_handlers_preserved_except_logging=True,
                      server_and_encoding_sources_unchanged=True,
                      new_engine_hooks=False, previous_esms_used=False,
                      gameplay_validation='requires two clients in Bruma city'), indent=2))
