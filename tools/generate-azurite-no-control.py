#!/usr/bin/env python3
"""Build a narrowly scoped control-power removal patch from the supplied ESP."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

spec = importlib.util.spec_from_file_location('tes4', Path(__file__).with_name('generate-notice-plugin.py'))
tes4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tes4)

CONTROL = 0x0400084F
ORIGINAL_QUEST = 0x04000850
CLEANUP_QUEST = 0x05000800
PATCH_NAME = 'AzuriteNoControl.esp'
SCRIPT = 'AZW_RemoveControl'


def script_binding():
    # Quest VMAD v5/format2: no quest scripts/fragments, one player alias.
    data = struct.pack('<HHH', 5, 2, 0) + struct.pack('<BHHH', 2, 0, 0, 1)
    data += struct.pack('<HhIHHH', 0, 1, CLEANUP_QUEST, 5, 2, 1)
    data += tes4.papyrus_string(SCRIPT) + struct.pack('<BH', 0, 1)
    data += tes4.papyrus_string('ControlPower') + bytes([1, 1])
    return data + struct.pack('<HhI', 0, -1, CONTROL)


def generate(fixture, output):
    expected_masters = ['Skyrim.esm', 'Update.esm', 'Dawnguard.esm', 'Dragonborn.esm']
    assert fixture['masters'] == expected_masters
    assert fixture['quest_form_id'] == ORIGINAL_QUEST
    original = [(tag, bytes.fromhex(value)) for tag, value in fixture['subrecords']]
    override = []
    alias = None
    removed = 0
    for tag, value in original:
        if tag == 'ALST':
            alias = struct.unpack('<I', value)[0]
        if tag == 'ALSP' and alias == 1 and value == struct.pack('<I', CONTROL):
            removed += 1
            continue
        override.append((tag, value))
    assert removed == 1
    assert not any(tag == 'INDX' for tag, _ in original)
    cleanup = []
    for tag, value in original:
        if tag == 'EDID':
            value = b'AZW_NoControlCleanupQuest\0'
        elif tag == 'VMAD':
            value = script_binding()
        elif tag == 'ALID':
            value = b'Player\0'
        elif tag == 'ALSP':
            continue
        cleanup.append((tag, value))
    # Two QUST records plus one GRUP; next own object after 0x800 is 0x801.
    header = [('HEDR', struct.pack('<fII', 1.7, 3, 0x801)),
              ('CNAM', b'Azurite control removal patch\0'),
              ('SNAM', b'Remove only the control power; retain original weather and seasonal trigger.\0')]
    for name in expected_masters + ['Azurite Weathers III.esp']:
        header += [('MAST', name.encode() + b'\0'), ('DATA', bytes(8))]
    body = tes4.record('QUST', ORIGINAL_QUEST, override) + tes4.record('QUST', CLEANUP_QUEST, cleanup)
    group = struct.pack('<4sI4siIHH', b'GRUP', 24 + len(body), b'QUST', 0, 0, 0, 0) + body
    raw_header = bytearray(tes4.record('TES4', 0, header))
    struct.pack_into('<I', raw_header, 8, 0x200)  # ESL flagged ESP
    plugin = bytes(raw_header) + group
    output.mkdir(parents=True, exist_ok=True)
    (output / PATCH_NAME).write_bytes(plugin)
    (output / 'SEQ').mkdir(exist_ok=True)
    (output / 'SEQ/AzuriteNoControl.seq').write_bytes(struct.pack('<I', CLEANUP_QUEST))
    provenance = {'input_filename': 'Azurite Weathers III.esp',
                  'input_chinese_sha256': fixture['source_sha256'],
                  'generated_plugin': PATCH_NAME,
                  'generated_sha256': hashlib.sha256(plugin).hexdigest(),
                  'control_spell_local_id': '00084F',
                  'modified_original_quest_local_id': '000850',
                  'original_alias_spell_removed': 1,
                  'original_seasonal_trigger_retained': True,
                  'weather_records_overridden': 0,
                  'new_cleanup_quests': 1,
                  'requires_skse': False,
                  'gameplay_tested': False}
    (output / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    return provenance


def main():
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--source', type=Path)
    source.add_argument('--fixture', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    fixture_path = args.output / 'source-quest.json'
    if args.source:
        raw = args.source.read_bytes()
        rows = list(tes4.iter_records(raw))
        masters = [v.rstrip(b'\0').decode() for t, v in rows[0][2] if t == 'MAST']
        quest = next(parts for kind, form, parts in rows if kind == 'QUST' and form == ORIGINAL_QUEST)
        fixture = {'source_sha256': hashlib.sha256(raw).hexdigest(), 'masters': masters,
                   'quest_form_id': ORIGINAL_QUEST, 'subrecords': [(tag, value.hex()) for tag, value in quest]}
        args.output.mkdir(parents=True, exist_ok=True)
        fixture_path.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')
    else:
        fixture = json.loads(args.fixture.read_text(encoding='utf-8'))
    print(json.dumps(generate(fixture, args.output), indent=2))


if __name__ == '__main__':
    main()
