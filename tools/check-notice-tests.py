#!/usr/bin/env python3
import json,re,sys,xml.etree.ElementTree as ET
from pathlib import Path
r=ET.parse(Path(sys.argv[1])).getroot();cases=r.findall('.//testcase');assert not r.findall('.//failure') and not r.findall('.//error')
source=Path(sys.argv[2]);expected=set()
for filename in ['notice_board.cpp','notice_client_state.cpp']:
 text=(source/'Code/tests'/filename).read_text(encoding='utf-8')
 expected.update(name for name,tags in re.findall(r'TEST_CASE\("([^"]+)",\s*"([^"]*)"\)',text) if '[noticeboard]' in tags)
assert len(expected)>=18,len(expected)
actual={x.get('name') for x in cases if x.find('skipped') is None};assert expected<=actual,expected-actual
print(json.dumps({'test_cases':len(cases),'notice_cases':len(expected),'failures':0,'errors':0},indent=2))
