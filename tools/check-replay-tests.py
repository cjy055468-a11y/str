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
    'Temporary actor identity survives discovery unload and ownership changes',
    'Recycled temporary form IDs and new connections cannot inherit actor identity',
    'Known temporary actor identity survives real assignment factory round trips',
    'Death received before 3D updates the pending spawn snapshot',
    'Loot received before 3D changes the pending corpse inventory',
    'Pending inventory guard leaves legacy drop events on their existing path',
    'Ownership handoff advances the pending snapshot before subsequent death and loot',
    'Drop rotation keeps fractional and negative radians through both message factories',
    'Drop proxies wait for attached geometry and make bounded wake attempts',
    'Reloaded drop geometry receives a new setup without repeated teleports',
    'Furniture recovery waits then exits only once per eligible episode',
    'Furniture recovery cancels when combat furniture or ownership eligibility ends',
    'A delayed furniture poll preserves the grace period after reevaluation',
    'Furniture recovery exit replaces a stale chair replay',
    'Drop setup waits for cell attachment even while the old geometry is present',
    'A registration ACK preserves a pickup reserved before its queue task runs',
    'Pickup-before-ACK and ACK-before-pickup retain the same registered identity',
    'A delayed pickup cannot retarget a recycled reference or a different drop nonce',
    'An unreserved drop remains pickable after its registration ACK',
    'Owner drop debit tolerates stale metadata and fragmented cached stacks',
    'Owner drop debit never invents a negative delta from an unavailable cache',
    'Equipment snapshots replace stale worn metadata without duplicating a cached item',
    'Equipment snapshots supply missing outfit entries and retain both worn hands',
    'An empty equipment snapshot clears worn flags without deleting owned inventory',
    'Pending equipment respects ownership epochs and never restores looted corpse armor',
    'Equipment notifications preserve the authoritative worn snapshot through the real factory',
    'Visible drop geometry without collision does not consume physics setup attempts',
}
root = ET.parse(Path(sys.argv[1])).getroot()
cases = root.findall('.//testcase')
assert cases, 'No tests executed'
assert not root.findall('.//failure'), 'Test assertion failure'
assert not root.findall('.//error'), 'Test execution error'
executed = {case.attrib.get('name') for case in cases if case.find('skipped') is None}
assert expected.issubset(executed), f'Missing required tests: {expected - executed}'
print(json.dumps({'test_cases': len(cases), 'executed_cases': len(executed),
                  'required_replay_cases': 5, 'required_drop_cases': 9, 'required_actor_cases': 7, 'required_coopfix3r2_cases': 12, 'required_regression_cases': 8,
                  'failures': 0, 'errors': 0}, indent=2))
