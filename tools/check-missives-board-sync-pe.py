#!/usr/bin/env python3
import json
import runpy
import sys
from pathlib import Path

inspect = runpy.run_path(str(Path(__file__).with_name("check-pe.py")))["inspect"]
files = [Path(path) for path in sys.argv[1:]]
assert {path.name for path in files} == {"SkyrimTogether.exe", "EarlyLoad.dll", "STServer.dll", "SkyrimTogetherServer.exe"}
reports = [inspect(path) for path in files]
for path in files:
    if path.name != "EarlyLoad.dll":
        data = path.read_bytes()
        assert b"coopfix4g-corpse5-state1s-loot2-missives-board-r6\0" in data, f"wrong build marker: {path.name}"
client = next(path for path in files if path.name == "SkyrimTogether.exe").read_bytes()
server = next(path for path in files if path.name == "STServer.dll").read_bytes()
for marker in [
    b"STR Missives board server handshake complete",
    b"STR Missives board listing synchronized:",
    b"STR Missives posting copy suppressed:",
]:
    assert marker in client, marker
assert b"STR Missives board posting claimed on board:" in server
print(json.dumps(reports, indent=2))
