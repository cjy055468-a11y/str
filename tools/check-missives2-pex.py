from pathlib import Path
import hashlib,json,struct,sys
source,out=map(Path,sys.argv[1:])
expected={p.stem.lower() for p in source.glob('*.psc')}
actual={p.stem.lower():p for p in out.glob('*.pex')}
assert len(expected)==18
assert set(actual)==expected,(set(actual)-expected,expected-set(actual))
result=[]
for name,p in sorted(actual.items()):
 data=p.read_bytes()
 assert data[:4]==bytes.fromhex('fa57c0de'),p.name
 assert data[4:6]==bytes([3,2]),(p.name,'not Skyrim PEX 3.2',data[:8].hex())
 assert struct.unpack_from('>H',data,6)[0]==1,(p.name,'not Skyrim game id')
 assert len(data)>100,p.name
 result.append({'file':p.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
print(json.dumps({'compiled_scripts':len(result),'skyrim_pex_version':'3.2','files':result},indent=2))
