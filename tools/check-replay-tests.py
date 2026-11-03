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
    'Dropped instances retain distinct IDs and duplicate creation is idempotent',
    'Concurrent drop claims produce exactly one first winner',
    'Consumed drops stay absent from snapshots and creation retries',
    'Unacknowledged grants recover on reconnect without a second credit',
    'An already applied recovered grant does not add to the new actor again',
    'Disabled drops are recorded for deduplication but are never public or claimable',
    'Invalid drop counts and unknown IDs cannot produce grants',
    "An owned NPC can consume a drop without granting the same client's player a copy",
    'Dropped-item request and notification factories preserve IDs and stack metadata',
}
root = ET.parse(Path(sys.argv[1])).getroot()
cases = root.findall('.//testcase')
assert cases, 'No tests executed'
assert not root.findall('.//failure'), 'Test assertion failure'
assert not root.findall('.//error'), 'Test execution error'
executed = {case.attrib.get('name') for case in cases if case.find('skipped') is None}
assert expected.issubset(executed), f'Missing required tests: {expected - executed}'
print(json.dumps({'test_cases': len(cases), 'executed_cases': len(executed),
                  'required_replay_cases': 5, 'required_drop_cases': len(expected) - 5,
                  'failures': 0, 'errors': 0}, indent=2))
