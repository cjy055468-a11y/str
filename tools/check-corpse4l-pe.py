import json
import runpy
import sys
from pathlib import Path

inspect = runpy.run_path(str(Path(__file__).with_name("check-pe.py")))["inspect"]
files = [Path(path) for path in sys.argv[1:]]
assert {path.name for path in files} == {
    "SkyrimTogether.exe", "EarlyLoad.dll", "STServer.dll", "SkyrimTogetherServer.exe"
}
reports = [inspect(path) for path in files]
by_name = {path.name: path.read_bytes() for path in files}

marker = b"v1.8.4-coopfix4g-corpse4l-corpse-diagnostics\0"
for name in ("SkyrimTogether.exe", "STServer.dll"):
    assert marker in by_name[name], f"{name}: build marker missing"

client_markers = [
    b"STR corpse owner health tx:",
    b"STR corpse health rx:",
    b"STR corpse death rx:",
    b"STR corpse guest state:",
    b"STR corpse local KillImpl begin:",
    b"STR corpse ragdoll action rx:",
    b"STR corpse ragdoll action apply:",
    b"STR corpse guest native ActorProcess begin:",
    b"STR corpse guest native ActorProcess suppressed:",
    b"STR remote NPC Skyrim Activate hook:",
    b"STR remote NPC activate event:",
    b"STR remote NPC Skyrim TESActivateEvent rx:",
    b"STR remote NPC activate request tx:",
    b"STR remote NPC activate notify rx:",
    b"STR activate notify target unresolved:",
]
for expected in client_markers:
    assert expected in by_name["SkyrimTogether.exe"], expected

server_markers = [
    b"STR corpse server health relay:",
    b"STR corpse death request rx:",
    b"STR corpse death notify tx:",
    b"STR corpse ragdoll action request rx:",
    b"STR corpse ragdoll action relay:",
    b"STR NPC activate request rx:",
    b"STR NPC activate request relay:",
    b"STR activate request relay unclassified:",
]
for expected in server_markers:
    assert expected in by_name["STServer.dll"], expected

print(json.dumps(reports, indent=2))
