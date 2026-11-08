#!/usr/bin/env python3
"""Extract only Missives posting aliases from the supplied Missives.esp."""
from __future__ import annotations

import argparse
import json
import struct
import zlib
from pathlib import Path


def records(data: bytes, start: int = 0, end: int | None = None):
    end = len(data) if end is None else end
    while start < end:
        signature = data[start : start + 4].decode("ascii")
        size = struct.unpack_from("<I", data, start + 4)[0]
        if signature == "GRUP":
            yield from records(data, start + 24, start + size)
            start += size
            continue
        flags, form_id = struct.unpack_from("<II", data, start + 8)
        payload = data[start + 24 : start + 24 + size]
        if flags & 0x40000:
            expected = struct.unpack_from("<I", payload)[0]
            payload = zlib.decompress(payload[4:])
            if len(payload) != expected:
                raise ValueError(f"bad compressed record {signature} {form_id:08X}")
        subs = []
        offset = 0
        extended = None
        while offset < len(payload):
            kind = payload[offset : offset + 4].decode("ascii")
            length = struct.unpack_from("<H", payload, offset + 4)[0]
            offset += 6
            if kind == "XXXX":
                extended = struct.unpack_from("<I", payload, offset)[0]
                offset += length
                continue
            if extended is not None:
                length, extended = extended, None
            sub = payload[offset : offset + length]
            if len(sub) != length:
                raise ValueError(f"truncated subrecord {kind} in {signature} {form_id:08X}")
            subs.append((kind, sub))
            offset += length
        if offset != len(payload):
            raise ValueError(f"bad subrecord boundaries in {signature} {form_id:08X}")
        yield signature, form_id, subs
        start += 24 + size


def parse_aliases(subs):
    found = []
    current = None
    for kind, payload in subs:
        if kind in ("ALLS", "ALST"):
            if current is not None:
                found.append(current)
            if len(payload) < 4:
                raise ValueError("short alias index")
            current = {"id": struct.unpack_from("<I", payload)[0]}
        elif current is not None and kind == "ALID":
            current["name"] = payload.rstrip(b"\0").decode("utf-8", errors="replace")
        elif current is not None and kind == "ALCO":
            if len(payload) >= 4:
                current["form"] = struct.unpack_from("<I", payload)[0]
    if current is not None:
        found.append(current)
    return found


def extract(path: Path):
    all_records = list(records(path.read_bytes()))
    header = next((subs for signature, _, subs in all_records if signature == "TES4"), None)
    if header is None:
        raise ValueError("plugin has no TES4 header")
    own_form_index = sum(kind == "MAST" for kind, _ in header)
    record_types = {form_id: signature for signature, form_id, _ in all_records}
    result = []
    for signature, form_id, subs in all_records:
        if signature != "QUST":
            continue
        if form_id >> 24 != own_form_index:
            continue
        aliases = parse_aliases(subs)
        by_name = {entry.get("name"): entry for entry in aliases}
        posting = by_name.get("Missive")
        board = by_name.get("MissiveBoard")
        if not posting or not board or "form" not in posting:
            continue
        if posting["form"] >> 24 != own_form_index:
            raise ValueError(f"posting alias in {form_id:08X} references an unsupported master form")
        if record_types.get(posting["form"]) != "BOOK":
            raise ValueError(f"posting alias in {form_id:08X} does not reference a BOOK form")
        result.append(
            {
                "quest": form_id & 0xFFFFFF,
                "book": posting["form"] & 0xFFFFFF,
                "posting_alias": posting["id"],
                "board_alias": board["id"],
            }
        )
    result.sort(key=lambda entry: entry["quest"])
    if len(result) != 264:
        raise ValueError(f"expected 264 Missives postings, extracted {len(result)}")
    if len({entry["quest"] for entry in result}) != len(result):
        raise ValueError("duplicate quest IDs")
    return result


def write_catalog(entries, path: Path):
    rows = [
        f"    {{{entry['quest']:#08x}u, {entry['book']:#08x}u, "
        f"{entry['posting_alias']}u, {entry['board_alias']}u}}"
        for entry in entries
    ]
    source = """#pragma once
#include <array>
#include <cstdint>

struct MissiveBoardEntry
{
    uint32_t Quest;
    uint32_t Book;
    uint16_t PostingAlias;
    uint16_t BoardAlias;
};

// Minimal local-form/alias index extracted from Missives.esp. This contains no
// task targets, objective aliases, globals or task state.
inline constexpr std::array<MissiveBoardEntry, %d> cMissiveBoardEntries{{
%s
}};
""" % (len(rows), ",\n".join(rows))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plugin", type=Path)
    parser.add_argument("catalog", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    entries = extract(args.plugin)
    write_catalog(entries, args.catalog)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"plugin": args.plugin.name, "entries": len(entries), "catalog": str(args.catalog)}))


if __name__ == "__main__":
    main()
