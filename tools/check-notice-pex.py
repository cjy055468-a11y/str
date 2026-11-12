#!/usr/bin/env python3
import json,sys
from pathlib import Path
source=Path(sys.argv[1]);compiled=Path(sys.argv[2]);expected={p.stem.lower()+'.pex' for p in source.glob('*.psc')};paths=list(compiled.rglob('*.pex'));actual={p.name.lower() for p in paths}
assert expected==actual and len(actual)==5,(expected,actual)
for p in paths:assert len(p.read_bytes())>16 and p.read_bytes().startswith(bytes.fromhex('FA57C0DE')),p.name
print(json.dumps({'compiled_pex':len(paths),'source_count':len(expected),'magic_verified':True},indent=2))
