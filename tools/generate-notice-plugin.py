#!/usr/bin/env python3
"""Build independent public notice BOOKs and a native catalog from Missives.esp.

The source plugin supplies quest IDs and appearance only. The new plugin contains
no QUST, alias instances, objective targets, rewards, or overrides of vanilla forms.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import struct
import zlib
from pathlib import Path


def iter_records(data: bytes, start: int = 0, end: int | None = None):
    limit = len(data) if end is None else end
    offset = start
    while offset < limit:
        if offset + 24 > limit:
            raise ValueError('Truncated TES4 record header')
        kind = data[offset:offset+4].decode('ascii')
        size, flags, form = struct.unpack_from('<III', data, offset+4)
        if kind == 'GRUP':
            if size < 24 or offset + size > limit:
                raise ValueError('Invalid TES4 group size')
            yield from iter_records(data, offset+24, offset+size)
            offset += size
            continue
        stop = offset + 24 + size
        if stop > limit:
            raise ValueError('Record exceeds its parent group')
        payload = data[offset+24:stop]
        if flags & 0x40000:
            expected = struct.unpack_from('<I',payload)[0]
            payload = zlib.decompress(payload[4:])
            if len(payload) != expected:
                raise ValueError('Compressed record size mismatch')
        parts = []
        cursor = 0
        extended = None
        while cursor < len(payload):
            if cursor+6 > len(payload):
                raise ValueError('Truncated subrecord header')
            tag, length = struct.unpack_from('<4sH',payload,cursor)
            cursor += 6
            if tag == b'XXXX':
                if length != 4:
                    raise ValueError('Invalid extended length')
                extended = struct.unpack_from('<I',payload,cursor)[0]
                cursor += 4
                continue
            if extended is not None:
                length, extended = extended, None
            value = payload[cursor:cursor+length]
            if len(value) != length:
                raise ValueError('Truncated subrecord body')
            parts.append((tag.decode('ascii'), value))
            cursor += length
        yield kind, form, parts
        offset = stop


def aliases(parts):
    result = []
    alias = None
    for tag, value in parts:
        if tag in ('ALST','ALLS'):
            alias = {'id':struct.unpack_from('<I',value)[0]}
            result.append(alias)
        elif alias is not None and tag == 'ALID':
            alias['name'] = value.rstrip(b'\0').decode('utf-8')
        elif alias is not None and tag == 'ALCO':
            alias['form'] = struct.unpack_from('<I',value)[0]
    return result


def zstring(text: str) -> bytes:
    return text.encode('utf-8') + b'\0'


def subrecord(tag: str, value: bytes) -> bytes:
    if len(value) > 65535:
        return b'XXXX'+struct.pack('<HI',4,len(value))+tag.encode()+b'\0\0'+value
    return tag.encode()+struct.pack('<H',len(value))+value


def record(kind: str, form: int, parts) -> bytes:
    payload = b''.join(subrecord(tag,value) for tag,value in parts)
    return struct.pack('<4sIIIIHH',kind.encode(),len(payload),0,form,0,44,0)+payload


def papyrus_string(text: str) -> bytes:
    raw = text.encode('utf-8')
    return struct.pack('<H',len(raw))+raw


def slip_script(quest: int, posting_alias: int, board_alias: int) -> bytes:
    # VMAD v5, object format 2, one script, four fixed properties.
    result = struct.pack('<HHH',5,2,1)+papyrus_string('STRNoticeSlip')+bytes([0])+struct.pack('<H',4)
    result += papyrus_string('Mission')+bytes([1,1])+struct.pack('<HhI',0,-1,quest)
    result += papyrus_string('PostingAlias')+bytes([3,1])+struct.pack('<i',posting_alias)
    result += papyrus_string('BoardAlias')+bytes([3,1])+struct.pack('<i',board_alias)
    result += papyrus_string('BoardBase')+bytes([1,1])+struct.pack('<HhI',0,-1,0x020012CB)
    return result


def category(editor_id: str) -> str:
    key = editor_id.removeprefix('_M_Missive')
    titles = {
        'KillAnimal':'清理野兽','KillBandit':'剿灭强盗','KillForsworn':'剿灭弃誓者',
        'KillGiant':'讨伐巨人','KillDragon':'屠龙','CourierLetter':'递送信件',
        'CourierWeapon':'递送武器','CourierPotion':'递送药水','RetrieveRuins':'寻回古物',
        'RetrieveHideout':'取回被盗传家宝','RetrieveWilderness':'寻回传家宝',
        'TrackFugitive':'追捕逃犯','TrackVampire':'追猎吸血鬼','TrackThief':'追捕窃贼',
        'GatherInn':'为旅店采购',
    }
    if key in titles:
        return titles[key]
    for prefix, title in [('GatherIngr','收集炼金材料'),('GatherOre','收集矿石'),('GatherSoulGem','收集灵魂石')]:
        if key.startswith(prefix):
            level = key[len(prefix):]
            suffix = {'Low':'普通','Med':'进阶','High':'高阶','VeryHigh':'珍稀'}.get(level,'')
            return title + ('（'+suffix+'）' if suffix else '')
    raise ValueError('Unknown notice category: '+editor_id)


def build(source: Path, output: Path, header: Path):
    raw = source.read_bytes()
    rows = list(iter_records(raw))
    header_parts = next(parts for kind,_,parts in rows if kind == 'TES4')
    masters = [value.rstrip(b'\0').decode() for tag,value in header_parts if tag == 'MAST']
    if masters != ['Skyrim.esm','Update.esm']:
        raise ValueError('The reviewed source Missives.esp must use Skyrim.esm and Update.esm masters')
    own_index = len(masters)
    by_form = {form:(kind,parts) for kind,form,parts in rows}
    catalog = []
    for kind,form,parts in rows:
        if kind != 'QUST' or form >> 24 != own_index:
            continue
        by_name = {a.get('name'):a for a in aliases(parts)}
        posting, board = by_name.get('Missive'),by_name.get('MissiveBoard')
        if not posting or not board or 'form' not in posting:
            continue
        book = posting['form']
        if book not in by_form or by_form[book][0] != 'BOOK':
            raise ValueError('Posting alias is not a book')
        catalog.append({'quest':form&0xffffff,'book':book&0xffffff,
                        'posting_alias':posting['id'],'board_alias':board['id']})
    catalog.sort(key=lambda item:item['quest'])
    if len(catalog) != 264 or len({item['quest'] for item in catalog}) != 264:
        raise ValueError('Expected exactly 264 distinct task templates')
    books = []
    for index,item in enumerate(catalog):
        item['proxy'] = 0x800+index
        _, original = by_form[(own_index<<24)|item['book']]
        values = dict(original)
        editor_id = values['EDID'].rstrip(b'\0').decode()
        title = '悬赏公文：'+category(editor_id)
        parts = [('EDID',zstring('STRNoticeSlip_'+f"{item['quest']:06X}")),
                 ('VMAD',slip_script((own_index<<24)|item['quest'],item['posting_alias'],item['board_alias']))]
        # Keep inert visual/audio/book metadata. No source VMAD or dynamic text.
        for tag in ('OBND',):
            if tag in values:parts.append((tag,values[tag]))
        parts.append(('FULL',zstring(title)))
        for tag,value in original:
            if tag in ('MODL','MODT','MODS','MODC'):
                parts.append((tag,value))
        description = '<font face="$HandwrittenFont"><font size="32">'+title+'</font>\n\n此委托正在招募承接者。\n取下这张告示以接受委托；接受后可查看具体目标与报酬。</font>'
        parts.append(('DESC',zstring(description)))
        for tag in ('YNAM','ZNAM','KSIZ','KWDA','DATA','INAM','CNAM'):
            if tag == 'DATA':
                parts.append(('DATA',bytes.fromhex('00000000ffffffff0000000000000000')))
            elif tag in values:
                parts.append((tag,values[tag]))
        books.append(record('BOOK',0x03000000|item['proxy'],parts))
    # HEDR counts both non-header records and GRUP headers.
    plugin_header = [('HEDR',struct.pack('<fII',1.7,len(books)+1,0x800+len(books))),
                     ('CNAM',zstring('STR Notice Board Compatibility')),
                     ('SNAM',zstring('Independent public notices. Tasks remain local.'))]
    for master in masters+['Missives.esp']:
        plugin_header += [('MAST',zstring(master)),('DATA',bytes(8))]
    body = b''.join(books)
    group = struct.pack('<4sI4siIHH',b'GRUP',24+len(body),b'BOOK',0,0,0,0)+body
    output.mkdir(parents=True,exist_ok=True)
    esp = record('TES4',0,plugin_header)+group
    (output/'STRNoticeBoard.esp').write_bytes(esp)
    (output/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n',encoding='utf-8')
    provenance = {'source_plugin':'Missives.esp','source_sha256':hashlib.sha256(raw).hexdigest(),
                  'generated_plugin':'STRNoticeBoard.esp','generated_sha256':hashlib.sha256(esp).hexdigest(),
                  'quest_templates':len(catalog),'records_created':len(books),'record_types':['BOOK'],
                  'master_plugins':masters+['Missives.esp'],'task_target_data_copied':False}
    (output/'catalog-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    cpp = '#pragma once\n#include <array>\n#include <cstdint>\n\nstruct NoticeTemplate\n{\n    uint32_t Quest;\n    uint32_t Book;\n    uint16_t PostingAlias;\n    uint16_t BoardAlias;\n    uint32_t Proxy;\n};\n\ninline constexpr std::array<NoticeTemplate, 264> kNoticeTemplates{{\n'
    cpp += ',\n'.join(f"    {{0x{e['quest']:06X}u, 0x{e['book']:06X}u, {e['posting_alias']}u, {e['board_alias']}u, 0x{e['proxy']:06X}u}}" for e in catalog)
    cpp += '\n}};\n'
    header.parent.mkdir(parents=True,exist_ok=True)
    header.write_text(cpp)
    # Reparse generated records rather than trusting writer lengths.
    generated = list(iter_records(esp))
    assert sum(kind=='BOOK' for kind,_,_ in generated)==264
    assert all(kind in ('TES4','BOOK') for kind,_,_ in generated)
    assert not any(b'<Alias=' in value for _,_,parts in generated for _,value in parts)
    print(json.dumps(provenance,indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plugin',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--header',type=Path,required=True)
    args=parser.parse_args()
    build(args.plugin,args.output,args.header)

if __name__=='__main__':main()
