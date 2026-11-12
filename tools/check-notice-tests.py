#!/usr/bin/env python3
import json,sys,xml.etree.ElementTree as ET
from pathlib import Path
r=ET.parse(Path(sys.argv[1])).getroot();cases=r.findall('.//testcase');assert not r.findall('.//failure') and not r.findall('.//error')
expected={'Notice reservations consume a public row only after commit','Failed local preparation releases a notice without changing another physical board','An old committed notice receipt never replaces a newer public generation','Late notice grants and unrelated denials cannot revive or cancel a transaction','Reconnect retains uncertain commit receipts and a server restart fences their tokens'}
actual={x.get('name') for x in cases if x.find('skipped') is None};assert expected<=actual,expected-actual
notice=[x for x in actual if 'notice' in x.lower() or 'physical board' in x.lower()];assert len(notice)>=18,len(notice)
print(json.dumps({'test_cases':len(cases),'notice_cases':len(notice),'failures':0,'errors':0},indent=2))
