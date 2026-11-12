#!/usr/bin/env python3
"""Verify a freshly applied v2 source, plugin, scripts and private task boundary."""
import argparse, hashlib, importlib.util, json, re, struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--mod',type=Path,default=Path('mods/notice-board'));args=p.parse_args()
source=args.source.resolve();mod=args.mod.resolve();scripts=mod/'Scripts/Source'
def need(value,message):
 if not value:raise SystemExit(message)
module_spec=importlib.util.spec_from_file_location('generator',Path(__file__).with_name('generate-notice-plugin.py'))
generator=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(generator)
rows=list(generator.iter_records((mod/'STRNoticeBoard.esp').read_bytes()))
need(all(kind in ('TES4','BOOK') for kind,_,_ in rows),'New ESP must contain only new BOOKs')
masters=[v.rstrip(b'\0').decode() for tag,v in rows[0][2] if tag=='MAST']
need(masters==['Skyrim.esm','Update.esm','Missives.esp'],'Wrong proxy ESP masters')
catalog=json.loads((mod/'catalog.json').read_text(encoding="utf-8"));need(len(catalog)==264,'Wrong notice catalog size')
need((source/'Code/client/ModCompat/NoticeCatalog.h').read_bytes()==(mod/'NoticeCatalog.h').read_bytes(),'Native/proxy catalogs differ')
books={fid:dict(parts) for kind,fid,parts in rows if kind=='BOOK'};need(len(books)==264,'Proxy count differs')
def read_string(data,offset):
 n=struct.unpack_from('<H',data,offset)[0];offset+=2;return data[offset:offset+n].decode(),offset+n
for item in catalog:
 fid=0x03000000|item['proxy'];need(fid in books,'Missing independent proxy BOOK')
 values=books[fid];need(b'<Alias=' not in values['FULL']+values['DESC'],'Unresolved dynamic task text in public notice')
 vmad=values['VMAD'];version,fmt,count=struct.unpack_from('<HHH',vmad);need((version,fmt,count)==(5,2,1),'Bad script binding header')
 name,offset=read_string(vmad,6);need(name=='STRNoticeSlip','Wrong proxy script');offset+=1;n=struct.unpack_from('<H',vmad,offset)[0];offset+=2;props={}
 for _ in range(n):
  name,offset=read_string(vmad,offset);kind,status=vmad[offset:offset+2];offset+=2
  if kind==1:props[name]=struct.unpack_from('<I',vmad,offset+4)[0];offset+=8
  elif kind==3:props[name]=struct.unpack_from('<i',vmad,offset)[0];offset+=4
  else:raise SystemExit('Unexpected proxy property type')
 need(offset==len(vmad),'Proxy property payload trailing data')
 need(props=={'Mission':0x02000000|item['quest'],'PostingAlias':item['posting_alias'],'BoardAlias':item['board_alias'],'BoardBase':0x020012CB},'Proxy VMAD property mismatch')
 need(values['DATA']==bytes.fromhex('00000000ffffffff0000000000000000'),'Proxy must not teach skills/spells or award gold')
psc=(scripts/'STRNoticeBridge.psc').read_text(encoding="utf-8");cpp=(source/'Code/client/ModCompat/NoticeBridge.cpp').read_text(encoding="utf-8")
prototypes={name:(len([a for a in args.split(',') if a.strip()]),result.lower()) for result,name,args in re.findall(r'^(?:(Bool|Int)\s+)?Function\s+(\w+)\(([^)]*)\)\s+Global\s+Native',psc,re.M)}
bindings={name:(int(count),{'Boolean':'bool','Integer':'int','Empty':''}[kind]) for name,count,kind in re.findall(r'\{"(\w+)",O::\w+,(\d+),V::k(Boolean|Integer|Empty)\}',cpp)}
need(prototypes==bindings,'Papyrus/native signature mismatch')
need(len(prototypes)==19,'Expected 19 fresh native functions')
controller=(scripts/'_M_ActivatorScript.psc').read_text(encoding="utf-8");slip=(scripts/'STRNoticeSlip.psc').read_text(encoding="utf-8")
online=controller[controller.index('Function RenderList'):controller.index('Function UpdateOfflineBoard')]
need('mission.Start(' not in online and 'GetAlias(' not in online,'Public rendering must not start/fill task aliases')
need('MissiveBoard.AddItem(proxy, 1, True)' in online and 'IsOriginalBookProtected(questId)' in online,'Public slip rendering or shared-book preparation protection missing')
need('Utility.WaitMenuMode(1.0)' in controller and 'Utility.WaitMenuMode(1.0)' in slip,'Container menu must not suspend public refresh or claim processing')
need('ElseIf noticeStatus == 4' in slip and 'If noticeStatus == 2' in slip,'Reservation/commit gates missing')
delivery=slip[slip.index('Function DeliverTask()'):slip.index('Function AbortClaim')]
need(delivery.index('MarkLocalTask(')<delivery.index('AddItem(')<delivery.index('SetStage(20)'),'Receipt must precede personal marking, letter delivery and acceptance')
need('Mission.SetStage(20)' not in slip[:slip.index('Function DeliverTask()')],'Task acceptance before commit')
for filename in ['_M_AliasMissiveScript.psc','_M_AliasMissiveDeliverScript.psc']:
 need('IsLocalTask(mission.GetFormID())' in (scripts/filename).read_text(encoding="utf-8"),'Original alias autoaccept isolation missing')
old=[f for f in (source/'Code').rglob('*') if f.is_file() and ('MissiveBoard' in f.name or 'MissivesBoard' in f.name or f.name=='missives.cpp')]
need(not old,'Old board implementation remains: '+str(old))
for filename in ['Code/client/Services/Generic/QuestService.cpp','Code/client/Services/Generic/InventoryService.cpp','Code/client/Services/Generic/ObjectService.cpp','Code/client/Games/Skyrim/TESObjectREFR.cpp','Code/client/Games/Skyrim/Actor.cpp']:
 need('NoticeIsolation' in (source/filename).read_text(encoding="utf-8"),'Missing isolation integration '+filename)
need('STRNoticeBoard.esp' in (source/'Code/client/ModCompat/NoticeIsolation.h').read_text(encoding="utf-8"),'Proxy slips not excluded from generic inventory synchronization')
for filename in ['Code/client/World.cpp','Code/server/World.cpp']:
 need('emplace<NoticeBoardService>' in (source/filename).read_text(encoding="utf-8"),'Fresh service not registered')
need('RegisterNoticeBridge(*apThis)' in (source/'Code/client/Games/Misc/BSScript.cpp').read_text(encoding="utf-8"),'Fresh native bridge not registered')
for filename,name in [('Code/encoding/Messages/ClientMessageFactory.h','RequestNoticeBoard'),('Code/encoding/Messages/ServerMessageFactory.h','NotifyNoticeBoard')]:
 need(name in (source/filename).read_text(encoding="utf-8"),'Fresh message factory not registered')
wire=(source/'Code/encoding/Structs/PublicNotice.h').read_text(encoding="utf-8")
need(set(re.findall(r'^\s*(?:uint64_t|GameId)\s+(\w+)\{',wire,re.M))=={'Id','Board','Quest'},'Task-instance data leaked into public notice wire model')
for filename in ['RequestNoticeBoard.h','NotifyNoticeBoard.h']:
 text=(source/'Code/encoding/Messages'/filename).read_text(encoding="utf-8")
 need('PublicNotice Notice' in text and 'uint64_t Token' in text and 'uint64_t ServerSession' in text,'Missing transaction/session fencing')
preserved=json.loads((Path(__file__).resolve().parent.parent/'fixes/notice-base-preserved.json').read_text(encoding="utf-8"))
for filename,expected in preserved['unchanged_base_files'].items():
 need(hashlib.sha256((source/filename).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==expected,'Previous non-board base changed: '+filename)
report={'new_book_records':264,'new_native_bindings':len(prototypes),'task_instance_fields_on_wire':0,'display_starts_shadow_quests':False,'old_board_implementation':'absent','previous_base_files_preserved':len(preserved['unchanged_base_files']),'plugin_sha256':hashlib.sha256((mod/'STRNoticeBoard.esp').read_bytes()).hexdigest(),'static_integration':'PASS','gameplay_two_client':'NOT_RUN'}
print(json.dumps(report,indent=2))
