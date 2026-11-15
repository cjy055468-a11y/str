"""Read/write the subset of TES5 records used by the iNeed overlay."""
import struct
import zlib


def read_records(data, start=0, end=None):
    end = len(data) if end is None else end
    while start < end:
        sig, size = struct.unpack_from('<4sI', data, start)
        if sig == b'GRUP':
            assert size >= 24 and start + size <= end
            yield from read_records(data, start + 24, start + size)
            start += size
            continue
        assert start + 24 + size <= end
        flags, fid, revision, version, unknown = struct.unpack_from('<IIIHH', data, start + 8)
        payload = data[start + 24:start + 24 + size]
        if flags & 0x40000:
            expected = struct.unpack_from('<I', payload)[0]
            payload = zlib.decompress(payload[4:])
            assert len(payload) == expected
        subs, offset, extended = [], 0, None
        while offset < len(payload):
            kind, length = struct.unpack_from('<4sH', payload, offset)
            offset += 6
            if kind == b'XXXX':
                assert length == 4
                extended = struct.unpack_from('<I', payload, offset)[0]
                offset += 4
                continue
            if extended is not None:
                length, extended = extended, None
            assert offset + length <= len(payload)
            subs.append((kind, payload[offset:offset + length]))
            offset += length
        assert offset == len(payload) and extended is None
        yield dict(sig=sig, fid=fid, flags=flags, revision=revision,
                   version=version, unknown=unknown, subs=subs)
        start += 24 + size
    assert start == end


def editor_id(record):
    return next((v.rstrip(b'\0').decode('ascii') for k, v in record['subs'] if k == b'EDID'), '')


def pack_subs(subs):
    return b''.join(k + struct.pack('<H', len(v)) + v for k, v in subs)


def pack_record(record):
    payload = pack_subs(record['subs'])
    return struct.pack('<4sIIIIHH', record['sig'], len(payload), record['flags'] & ~0x40000,
                       record['fid'], record['revision'], record['version'], record['unknown']) + payload


def vmad(script, properties):
    def string(value):
        encoded = value.encode('ascii')
        return struct.pack('<H', len(encoded)) + encoded
    result = struct.pack('<HHH', 5, 2, 1) + string(script) + b'\0' + struct.pack('<H', len(properties))
    for name, typ, value in properties:
        result += string(name) + bytes((typ, 1)) + value
    return result


def remap_vmad_objects(data, old_index, new_index):
    result = bytearray(data)
    def string(offset):
        size = struct.unpack_from('<H', result, offset)[0]
        return offset + 2 + size
    version, format_, scripts = struct.unpack_from('<HHH', result)
    assert (version, format_, scripts) == (5, 2, 1)
    offset = string(6) + 1
    count = struct.unpack_from('<H', result, offset)[0]
    offset += 2
    for _ in range(count):
        offset = string(offset)
        typ, status = result[offset:offset + 2]
        offset += 2
        if typ == 1:
            fid = struct.unpack_from('<I', result, offset + 4)[0]
            if fid >> 24 == old_index:
                struct.pack_into('<I', result, offset + 4, (new_index << 24) | (fid & 0xFFFFFF))
            offset += 8
        elif typ in (3, 4):
            offset += 4
        elif typ == 5:
            offset += 1
        elif typ == 2:
            offset = string(offset)
        else:
            raise ValueError(f'Unexpected VMAD property type {typ}')
    assert offset == len(result)
    return bytes(result)
