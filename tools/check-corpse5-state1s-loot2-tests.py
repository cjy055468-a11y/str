import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

expected = {
    "Equivalent NPC inventory snapshots ignore entry order and split stacks",
    'Corpse refresh waits one second and fires only once per authoritative death',
    'Unready corpses retain the deadline without consuming the attempt',
    'An authoritative resurrection cancels the old corpse refresh deadline',
    'Recycled corpse handles and ownership epochs cannot inherit an old timer',
    'Invalid corpse identities and backwards clocks cannot trigger a refresh',

    'Remote NPC pose cannot fabricate native death before KillImpl',
    'Remote dying NPC keeps its native transition instead of replaying a fake completion',
    'Native corpse completion and actual resurrection supersede stale pose life bits',
    'Native death processing excludes living unconscious and essential down states',

    'Resolved NPC equipment replaces template counts instead of duplicating armor and weapons',
    'NPC snapshot preserves legitimate spare equipment stacks and different enchantments',
    'NPC ordinary signed inventory deltas still combine with every template row',
    'An exhausted resolved NPC item cannot regain the default outfit count',
    'Resolved NPC snapshots preserve quest equipment and both equipped hands',
    'Corrected NPC counts survive the actual assignment and spawn message factories',

    'Missives encodes the valid zero network entity without confusing it with absence',
    'Missives actor zero and revision three survive the actual request factory',

    'Missives publishes one canonical instance and preserves its claim tombstone',
    'Concurrent Missives claims elect exactly one personal recipient',
    'Missives progress is claimant-only ordered and survives authority handoff',
    'Missives reservations and retired instances cannot generate a second personal mission',
    'Missives real factories retain canonical aliases globals and personal grants',
    'Missives protocol rejects oversized and nonfinite alias context',
    'Personal quest metadata and far quest actors survive the real wire format',
    'Different Missives boards elect independent generators without sharing quest ownership',

    'A stale live action preserves only a confirmed corpse life field',
    'Dying actors retain their normal transition into a completed death',
    'An accepted resurrection or unknown death state does not retain corpse bits',
    'Corpse speech allows a final line before a bounded death deadline',
    'Repeated late speech cannot extend an expired corpse deadline',
    'A revived actor regains speech and a later death receives a new grace period',
    'A recycled reference handle cannot inherit a corpse speech mute',
    'Corpse speech timing handles a clock rollback without unsigned expiry',
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
    'A drop outfit refresh round trips without requesting another native equip action',
    'Only a drop creator can update placement without changing stack identity',
    'Placement updates cannot revive consumed drops or accept nonfinite coordinates',
    'Drop placement messages and snapshots retain placement through real factories',
    'Drop placement waits for stable samples and rate limits later movement',
    'An unsent placement remains pending until publication is confirmed',
    'Unattached native drops cannot invent an authoritative placement',
}
root = ET.parse(Path(sys.argv[1])).getroot()
cases = root.findall('.//testcase')
assert len(cases)>=109, 'Expected all 103 baseline, 5 refresh, and 1 inventory guard test'
assert not root.findall('.//failure'), 'Test assertion failure'
assert not root.findall('.//error'), 'Test execution error'
executed = {case.attrib.get('name') for case in cases if case.find('skipped') is None}
assert expected.issubset(executed), f'Missing required tests: {expected - executed}'
print(json.dumps({'test_cases': len(cases), 'executed_cases': len(executed),
                  'required_replay_cases': 5, 'required_drop_cases': 9, 'required_actor_cases': 7, 'required_coopfix3r2_cases': 12, 'required_regression_cases': 9, 'required_placement_cases': 6, 'required_corpse_timing_cases': 5, 'required_corpse_life_field_cases': 3,
                  'failures': 0, 'errors': 0}, indent=2))
