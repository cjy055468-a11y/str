import hashlib,json,os,re,subprocess,sys,tempfile,shutil
from pathlib import Path
root=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parent.parent
delta=repo/'fixes/corpse-board-r2-delta.patch'
paths=re.findall(r'^diff --git a/(.*?) b/',delta.read_text(),re.M)
assert paths==json.loads((repo/'fixes/corpse-board-r2-scope.json').read_text())
env=os.environ.copy();env['GIT_CEILING_DIRECTORIES']=str(Path(tempfile.gettempdir()).resolve())
# Independently restore the exact delivered corpse3 in a copy. This proves
# every unrelated file remains byte-for-byte the previously compiled source.
with tempfile.TemporaryDirectory(prefix='str-missives2-scope-') as temp:
 stage=Path(temp)
 for name in paths:
  target=stage/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/name,target)
 subprocess.run(['git','apply','--reverse','--check',str(delta)],cwd=stage,env=env,check=True)
 subprocess.run(['git','apply','--reverse',str(delta)],cwd=stage,env=env,check=True)
 # Rebuild the C7 baseline from the official pinned source using its full patch.
 with tempfile.TemporaryDirectory(prefix='str-c7-baseline-') as base:
  base=Path(base)
  import io,tarfile
  tracked=set(subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=root,text=True).splitlines())
  c7=repo/'fixes/coopfix4g-npc-loot-v184.patch'
  c7paths=set(re.findall(r'^diff --git a/(.*?) b/',c7.read_text(),re.M))
  wanted=(set(paths)|c7paths)&tracked
  archive=subprocess.check_output(['git','archive','HEAD',*sorted(wanted)],cwd=root)
  with tarfile.open(fileobj=io.BytesIO(archive)) as t:t.extractall(base,filter='data')
  subprocess.run(['git','apply',str(c7)],cwd=base,env=env,check=True)
  for name in set(paths)|c7paths:
   expected=base/name
   actual=stage/name if name in paths else root/name
   assert expected.exists()==actual.exists(),name
   if expected.exists():assert expected.read_bytes().replace(b'\r\n',b'\n')==actual.read_bytes().replace(b'\r\n',b'\n'),name
print(json.dumps({'native_changes_from_delivered_loot1':paths,'delta_sha256':hashlib.sha256(delta.read_bytes()).hexdigest(),'exact_loot1_recovery':True,'official_base':'54b3a858e228dc8807ed65bc3f9ac3c3f81b610d','game_test':'not run'},indent=2))
