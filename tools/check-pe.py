"""Check real Windows artifacts; never accepts an original EXE as a fixed build."""
import argparse
import hashlib
import json
import struct
from pathlib import Path


def inspect(path, require_fix=False):
    data = path.read_bytes()
    if data[:2] != b"MZ":
        raise ValueError(f"{path.name}: missing DOS header")
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\0\0":
        raise ValueError(f"{path.name}: missing PE header")
    machine = struct.unpack_from("<H", data, pe + 4)[0]
    magic = struct.unpack_from("<H", data, pe + 24)[0]
    characteristics = struct.unpack_from("<H", data, pe + 22)[0]
    if machine != 0x8664 or magic != 0x20B:
        raise ValueError(f"{path.name}: expected x64 PE32+")
    is_dll = bool(characteristics & 0x2000)
    if is_dll != (path.suffix.lower() == ".dll"):
        raise ValueError(f"{path.name}: DLL characteristic mismatch")
    if path.name == "SkyrimTogether.exe":
        build_markers = (b"v1.8.4-coopfix4g", b"v1.8.4-coopfix4h-corpse4-loot1", b"v1.8.4-coopfix4i-corpse4-loot1", b"v1.8.4-coopfix4j-corpse4-loot1", b"v1.8.4-coopfix4j-r1-corpse4-loot1")
        if not any(marker in data for marker in build_markers):
            raise ValueError(f"{path.name}: missing a recognized Skyrim Together build marker")
        for marker in (b"1.6.1170.0", b"EarlyLoad.dll", b"libcef.dll"):
            if marker not in data:
                raise ValueError(f"{path.name}: missing expected marker {marker!r}")
        if require_fix and (b"STR replay audit v2:" not in data or b"STR drop grant applied:" not in data or b"STR NPC reattach request:" not in data or b"STR corpse pending death:" not in data or b"STR player pickpocket blocked:" not in data or b"STR furniture recovery exit:" not in data or b"STR drop proxy physics:" not in data or b"STR drop save filter installed:" not in data or b"STR drop owner placement:" not in data):
            raise ValueError("EXE lacks the combined replay/dropfix markers")
    if require_fix and path.name in ("STServer.dll", "SkyrimTogetherServer.exe"):
        server_build_markers = (b"master@v1.8.4-coopfix4g\0", b"master@v1.8.4-coopfix4h-corpse4-loot1\0", b"master@v1.8.4-coopfix4i-corpse4-loot1\0", b"master@v1.8.4-coopfix4j-corpse4-loot1\0", b"master@v1.8.4-coopfix4j-r1-corpse4-loot1\0")
        if not any(marker in data for marker in server_build_markers):
            raise ValueError(f"{path.name}: matching protocol build tag is missing")
    return {"file": path.name, "bytes": len(data), "machine": "AMD64",
            "format": "PE32+", "dll": is_dll,
            "sha256": hashlib.sha256(data).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", type=Path, nargs="+")
    parser.add_argument("--require-fix", action="store_true")
    args = parser.parse_args()
    print(json.dumps([inspect(p, args.require_fix) for p in args.files], indent=2))


if __name__ == "__main__":
    main()
