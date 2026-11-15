"""Change only user-requested defaults in the supplied iNeed 1.95 binaries.

All replacements carry their original bytes and locations for exact reversal.
No gameplay instructions are inserted or removed.
"""
from pathlib import Path
import hashlib
import json
import struct

from skyrim_pex import Pex


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

