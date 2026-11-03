import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

expected = {
    'Exit-only replay requires a reset even when its action list is empty',
    'A seated NPC replay preserves its enter state',
    'Exit followed by a different furniture enter retains the new action',
    'A cache with no observed animations does not invent a reset or a pose',
    'EnTT initializes the original replay counter on creation and replacement',
}
root = ET.parse(Path(sys.argv[1])).getroot()
cases = root.findall('.//testcase')
assert cases, 'No tests executed'
assert not root.findall('.//failure'), 'Test assertion failure'
assert not root.findall('.//error'), 'Test execution error'
executed = {case.attrib.get('name') for case in cases if case.find('skipped') is None}
assert expected.issubset(executed), f'Missing required tests: {expected - executed}'
print(json.dumps({'test_cases': len(cases), 'executed_cases': len(executed),
                  'required_replay_cases': len(expected), 'failures': 0, 'errors': 0}, indent=2))
