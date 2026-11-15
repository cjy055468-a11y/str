"""Change only user-requested defaults in the supplied iNeed 1.95 binaries.

All replacements carry their original bytes and locations for exact reversal.
No gameplay instructions are inserted or removed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct

from pex_defaults import Pex


def sha(data):
    return hashlib.sha256(data).hexdigest()


def normalize_function(function):
    return dict(return_type=function['return_type'], flags=function['flags'],
                parameters=function['parameters'], locals=function['locals'],
                instructions=[(op, [(a.kind, a.value) for a in args], [(a.kind, a.value) for a in rest])
                              for _, op, args, rest in function['instructions']])


def apply_edits(raw, edits):
    edits = sorted(edits, key=lambda x: x['original_offset'])
    end = 0
    shift = 0
    for edit in edits:
        offset = edit['original_offset']
        before, after = bytes.fromhex(edit['before_hex']), bytes.fromhex(edit['after_hex'])
        assert offset >= end and raw[offset:offset + len(before)] == before
        edit['modified_offset'] = offset + shift
        end = offset + len(before)
        shift += len(after) - len(before)
    result = raw
    for edit in reversed(edits):
        offset = edit['original_offset']
        result = result[:offset] + bytes.fromhex(edit['after_hex']) + result[offset + len(bytes.fromhex(edit['before_hex'])):]
    restored = result
    for edit in reversed(edits):
        offset = edit['modified_offset']
        after = bytes.fromhex(edit['after_hex'])
        assert restored[offset:offset + len(after)] == after
        restored = restored[:offset] + bytes.fromhex(edit['before_hex']) + restored[offset + len(after):]
    assert restored == raw
    return result, dict(original_sha256=sha(raw), modified_sha256=sha(result),
                        original_bytes=len(raw), modified_bytes=len(result), edits=edits,
                        exact_original_reconstruction=True)


def edit_at(raw, offset, length, after, reason):
    return dict(original_offset=offset, before_hex=raw[offset:offset + length].hex(),
                after_hex=after.hex(), reason=reason)


def default_edit(pex, name, kind, value):
    assert len(pex.objects) == 1
    object_ = pex.objects[0][0]
    type_, old = pex.variables[(object_.lower(), name.lower())]
    assert old.kind == 0 and old.value is None
    after = bytes((kind,)) + struct.pack('>i' if kind == 3 else '>B', value)
    return edit_at(pex.data, old.offset - 1, 1, after, f'{name}: default {value}'), len(after) - 1


def update_size(pex, delta):
    offset, size = pex.object_sizes[pex.objects[0][0].lower()]
    return edit_at(pex.data, offset, 4, struct.pack('>I', size + delta), 'Update PEX object size after typed initializers')


def harvest_edits(data):
    results = []
    expected = {0x05042EB8: '_SNValuedHarvestsToggle', 0x05049AA0: '_SNValuedHarvestsDialogueToggle'}

    def walk(start, end):
        while start < end:
            sig, size = struct.unpack_from('<4sI', data, start)
            if sig == b'GRUP':
                walk(start + 24, start + size)
                start += size
                continue
            flags, fid = struct.unpack_from('<II', data, start + 8)
            if fid in expected:
                assert sig == b'GLOB' and not flags & 0x40000
                pos, field, name = start + 24, None, None
                while pos < start + 24 + size:
                    key, length = struct.unpack_from('<4sH', data, pos)
                    pos += 6
                    if key == b'EDID':
                        name = data[pos:pos + length].rstrip(b'\0').decode()
                    if key == b'FLTV':
                        assert length == 4 and struct.unpack_from('<f', data, pos)[0] == 0.0
                        field = pos
                    pos += length
                assert field is not None and name == expected[fid]
                results.append(edit_at(data, field, 4, struct.pack('<f', 1.0), f'{name}: default enabled'))
            start += 24 + size
        assert start == end

    walk(0, len(data))
    assert len(results) == 2
    return results


def build(original, bsa_scripts, output):
    output.mkdir(parents=True, exist_ok=True)
    (output / 'scripts').mkdir(exist_ok=True)
    report = dict(mod='iNeed Continued 1.95 MCM defaults', scope='New game / initial defaults; MCM remains editable',
                  requested_defaults=dict(Animations=2, ForceThird=True, ValuedHarvests=True), files={})

    main_path = original / 'scripts/_snquestscript.pex'
    main = Pex(main_path)
    type_, backing, camera = main.property_default('_SNQuestScript', 'ForceThird')
    assert type_.lower() == 'bool' and camera.kind == 5 and camera.value == 1
    type_, backing, old = main.property_default('_SNQuestScript', 'Animations')
    assert type_.lower() == 'int'
    initializer, delta = default_edit(main, backing, 3, 2)
    raw, details = apply_edits(main.data, [initializer, update_size(main, delta)])
    out = output / 'scripts/_snquestscript.pex'
    out.write_bytes(raw)
    patched = Pex(out)
    assert patched.property_default('_SNQuestScript', 'Animations')[2].value == 2
    assert patched.property_default('_SNQuestScript', 'ForceThird')[2].value == 1
    assert {k: normalize_function(v) for k, v in patched.functions.items()} == {
        k: normalize_function(v) for k, v in main.functions.items()}
    details['all_function_bodies_unchanged'] = True
    details['ForceThird_original_and_patched'] = True
    report['files']['scripts/_snquestscript.pex'] = details

    mcm = Pex(bsa_scripts / '_snskyuiconfig.pex')
    animation, delta1 = default_edit(mcm, 'Animations', 3, 2)
    harvests, delta2 = default_edit(mcm, 'ValuedHarvests', 5, 1)
    key = ('_snskyuiconfig', '', 'onoptionmenuopen')
    instructions = mcm.functions[key]['instructions']
    previous_start = None
    matches = []
    for pos, op, args, variadic in instructions:
        if op != 23:
            continue
        method = str(args[0].value).lower()
        if method == 'setmenudialogstartindex':
            previous_start = variadic[0].value
        elif method == 'setmenudialogdefaultindex' and str(previous_start).lower() == 'animations':
            assert len(variadic) == 1 and variadic[0].kind == 3 and variadic[0].value == 0
            matches.append(edit_at(mcm.data, variadic[0].offset, 4, struct.pack('>i', 2),
                                   'Animations MCM reset-default index: 0 -> 2'))
    assert len(matches) == 1
    raw, details = apply_edits(mcm.data, [animation, harvests, update_size(mcm, delta1 + delta2)] + matches)
    out = output / 'scripts/_snskyuiconfig.pex'
    out.write_bytes(raw)
    patched = Pex(out)
    assert patched.variables[('_snskyuiconfig', 'animations')][1].value == 2
    assert patched.variables[('_snskyuiconfig', 'valuedharvests')][1].value == 1
    # The only changed instruction operand is that one menu-default literal.
    differences = []
    for function in mcm.functions:
        before, after = normalize_function(mcm.functions[function]), normalize_function(patched.functions[function])
        if before != after:
            differences.append(function)
            b, a = before.pop('instructions'), after.pop('instructions')
            assert before == after and len(b) == len(a)
            changed = [(x, y) for x, y in zip(b, a) if x != y]
            assert len(changed) == 1
            x, y = changed[0]
            assert x[0] == y[0] == 23 and x[1] == y[1] and x[2] == [(3, 0)] and y[2] == [(3, 2)]
    assert differences == [key]
    details['changed_instruction_operands'] = 1
    details['other_function_bodies_unchanged'] = True
    report['files']['scripts/_snskyuiconfig.pex'] = details

    plugin = (original / 'iNeed.esp').read_bytes()
    raw, details = apply_edits(plugin, harvest_edits(plugin))
    assert len(raw) == len(plugin)
    (output / 'iNeed.esp').write_bytes(raw)
    report['files']['iNeed.esp'] = details
    (output / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('original', type=Path)
    parser.add_argument('bsa_scripts', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = build(args.original, args.bsa_scripts, args.output)
    print(json.dumps({'result': 'PASS', 'defaults': result['requested_defaults'],
                      'files': {name: dict(bytes_before=value['original_bytes'], bytes_after=value['modified_bytes'],
                                           reconstruction=value['exact_original_reconstruction'])
                                for name, value in result['files'].items()}}, indent=2))
