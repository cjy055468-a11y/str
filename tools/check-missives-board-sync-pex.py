#!/usr/bin/env python3
"""Require a compiler output PEX for every script shipped by the new mod."""
import json
import sys
from pathlib import Path

source = Path(sys.argv[1])
compiled = Path(sys.argv[2])
expected = {path.stem + ".pex" for path in source.glob("*.psc")}
actual_paths = list(compiled.rglob("*.pex"))
actual = {path.name for path in actual_paths}
assert expected == actual, f"PEX mismatch: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}"
for path in actual_paths:
    data = path.read_bytes()
    assert len(data) > 16, f"empty/truncated PEX: {path.name}"
    assert data.startswith(b"Pex\0"), f"invalid Papyrus bytecode: {path.name}"
assert "STRMissivesBoardBridge.pex" in actual
print(json.dumps({"pex_count": len(actual), "source_count": len(expected), "all_bytecode_valid": True}, indent=2))
