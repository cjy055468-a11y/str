"""Generate, statically verify and package the user-requested Frostbite rebuild."""
import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import zipfile
import zlib
from pathlib import Path

from read_skyrim_pex import Reader

ORIGINAL_ESL_SHA = '56b271b9566fda1c25ee1bcf145a98549c72bffcbd254a931c842260761be040'
ORIGINAL_ZIP_SHA = '08d056b05e7af161b640fd915148b4536efd43e4cdb0295d282eb5507f372f62'
SWF_SHA = '971f18e31ce99f44a346d2e759efba9368369218683256276b6ac613db27faa9'
COOLING = {'_JSW_FB_CoolDelta': (0.005, 0.0075),
           '_JSW_FB_ColdDelta': (0.01, 0.015),
           '_JSW_FB_FreezingDelta': (0.025, 0.0375)}
TEXT = {
    'Damage Stamina Regen': '抑制耐力恢复', 'Damage Magicka Regen': '抑制魔法恢复',
    'Damage Health Regen': '抑制生命恢复', 'Cold': '寒冷',
    'This clothing is unrecognized by Frostbite. How much protection does it have against the cold?': 'Frostbite 尚未记录这件衣物。它能提供多少保暖效果？',
    'Unknown Clothing': '未识别的衣物', 'No Protection': '几乎不保暖',
    'Some Protection': '提供一定保暖', 'Excellent Protection': '保暖效果极佳', 'Cancel': '取消',
    'This food is unrecognized by Frostbite. Does it have warming properties?': 'Frostbite 尚未记录这种食物。食用后能够暖身吗？',
    'Unknown Food': '未识别的食物', 'Yes': '可以暖身', 'No': '不能暖身',
}
SCRIPT_PARENTS = {'_JSW_FB_ConfigScript': 'SKI_ConfigBase',
                  '_JSW_FB_HandlerScript': 'ReferenceAlias',
                  '_JSW_FB_MeterWidget': '_JSW_FB_Widget', '_JSW_FB_Widget': 'SKI_WidgetBase'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parts(payload):
    result, i, extended = [], 0, None
    while i < len(payload):
        tag, n = struct.unpack_from('<4sH', payload, i)
        i += 6
        if tag == b'XXXX':
            assert n == 4
            extended = struct.unpack_from('<I', payload, i)[0]
            i += 4
            continue
        if extended is not None:
            n, extended = extended, None
        value = payload[i:i+n]
        assert len(value) == n
        i += n
        result.append((tag.decode('ascii'), value))
    assert i == len(payload) and extended is None
    return result


def encode_parts(values):
    result = bytearray()
    for tag, value in values:
        if len(value) > 65535:
            result += b'XXXX'+struct.pack('<HI', 4, len(value))
            result += tag.encode()+bytes(2)+value
        else:
            result += tag.encode()+struct.pack('<H', len(value))+value
    return bytes(result)


def walk(raw, transform=None):
    """Preserve record/group headers and all unmodified record bytes."""
    i, output, rows = 0, bytearray(), []
    while i < len(raw):
        header = bytearray(raw[i:i+24])
        assert len(header) == 24
        kind = header[:4].decode('ascii')
        size, flags, form = struct.unpack_from('<III', header, 4)
        total = size if kind == 'GRUP' else size+24
        assert total >= 24 and i+total <= len(raw)
        body = raw[i+24:i+total]
        if kind == 'GRUP':
            body, nested = walk(body, transform)
            rows += nested
            struct.pack_into('<I', header, 4, len(body)+24)
        else:
            payload = body
            if flags & 0x40000:
                length = struct.unpack_from('<I', payload)[0]
                payload = zlib.decompress(payload[4:])
                assert len(payload) == length
            values = parts(payload)
            rows.append((kind, form, flags, values))
            changed = transform(kind, form, values) if transform else values
            if changed != values:
                body = encode_parts(changed)
                if flags & 0x40000:
                    body = struct.pack('<I', len(body))+zlib.compress(body, 9)
                struct.pack_into('<I', header, 4, len(body))
        output += header+body
        i += total
    assert i == len(raw)
    return bytes(output), rows


def generate(root):
    source = (root/'input/Frostbite.esl').read_bytes()
    assert sha(source) == ORIGINAL_ESL_SHA
    changes = []
    def change(kind, form, values):
        edid = next((v.rstrip(b'\0').decode() for t, v in values if t == 'EDID'), '')
        changed = []
        for tag, value in values:
            updated = value
            if kind == 'GLOB' and edid in COOLING and tag == 'FLTV':
                before, after = COOLING[edid]
                assert value == struct.pack('<f', before)
                updated = struct.pack('<f', after)
            elif kind in ('MGEF','SPEL','MESG') and tag in ('FULL','DESC','ITXT'):
                original = value.rstrip(b'\0').decode('utf-8')
                if original in TEXT:
                    updated = TEXT[original].encode('utf-8')+b'\0'
            if updated != value:
                changes.append({'record': kind, 'form': f'{form:08X}', 'editor_id': edid,
                                'field': tag, 'before': value.hex(), 'after': updated.hex()})
            changed.append((tag, updated))
        return changed
    generated, _ = walk(source, change)
    (root/'Data/Frostbite.esl').write_bytes(generated)
    (root/'plugin-changes.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2)+'\n')
    assert len(changes) == 20
    print(json.dumps({'plugin_sha256': sha(generated), 'translated_fields': 17, 'cooling_defaults': 3}))


def calls(function, method):
    result = []
    for code in function['code']:
        if code['op'] not in ('CallMethod','CallStatic','CallParent'):
            continue
        slot = 1 if code['op'] == 'CallStatic' else 0
        value = code['args'][slot]
        if isinstance(value, dict) and value.get('id','').lower() == method.lower():
            result.append(code)
    return result


def check(root, compiled=None):
    original = (root/'input/Frostbite.esl').read_bytes()
    actual = (root/'Data/Frostbite.esl').read_bytes()
    assert sha(original) == ORIGINAL_ESL_SHA
    _, old = walk(original)
    _, new = walk(actual)
    assert len(old) == len(new)
    text_fields = cooling_fields = 0
    quest = None
    for before, after in zip(old, new):
        assert before[:3] == after[:3]  # types, IDs, flags
        kind, form, flags, a = before
        b = after[3]
        assert len(a) == len(b)
        edid = next((v.rstrip(b'\0').decode() for t, v in a if t == 'EDID'), '')
        for (ta, va), (tb, vb) in zip(a, b):
            assert ta == tb
            if va == vb:
                continue
            if ta == 'FLTV' and edid in COOLING:
                x, y = COOLING[edid]
                assert va == struct.pack('<f', x) and vb == struct.pack('<f', y)
                cooling_fields += 1
            else:
                assert kind in ('MGEF','SPEL','MESG') and ta in ('FULL','DESC','ITXT')
                assert vb == TEXT[va.rstrip(b'\0').decode()].encode('utf-8')+b'\0'
                text_fields += 1
        if kind == 'QUST':
            assert not any(t == 'INDX' for t, v in b)
            assert next(v for t, v in a if t == 'VMAD') == next(v for t, v in b if t == 'VMAD')
            assert ('ALFR', struct.pack('<I', 0x14)) in b
            quest = f'{form:08X}'
    assert (text_fields, cooling_fields) == (17,3)
    assert sha((root/'Data/Interface/exported/widgets/Frostbite/meter.swf').read_bytes()) == SWF_SHA
    config = (root/'Data/scripts/source/_JSW_FB_ConfigScript.psc').read_text(encoding='utf-8-sig')
    handler = (root/'Data/scripts/source/_JSW_FB_HandlerScript.psc').read_text(encoding='utf-8-sig')
    assert 'Actor Property PlayerRef  Auto' in config and 'Actor Property PlayerRef  Auto' in handler
    assert 'Property Widget ' in config and 'Property Enabled ' in config
    for source in (config, handler):
        declarations = re.findall(r'(?im)^\s*\w+(?:\[\])?\s+property\s+(\S+)', source)
        assert all(name.isascii() for name in declarations)
    assert handler.count('damage = damage * (1.0 - (frostResist / 100.0))') == 3
    assert 'int function GetVersion()\n\treturn 2' in config
    assert 'if (version >= 2)' in config and 'Pages[0] = "设置"' in config
    assert 'Frostbite/Logo.dds' not in config
    assert '_coolingDefaultsUpdated = true' in handler
    assert handler.count('\tUpgradeCoolingDefaults()') == 2
    assert '\t\tClearColdDebuffs()\n\t\tStopWarmingAnimation()\n\tendIf' in handler
    assert handler.count('SendModEvent("FrostbiteNearHeatSource")') == 1
    assert 'Game.GetPlayer' not in handler  # preserve the bound local alias
    assert handler.count('UnregisterForAllControls()') == 1
    for value in ('0.0075', '0.015', '0.0375'):
        assert f'SetSliderDialogDefaultValue({value})' in config
    pex = []
    if compiled:
        paths = sorted(compiled.glob('*.pex'))
        assert {p.stem.lower() for p in paths} == {n.lower() for n in SCRIPT_PARENTS}
        objects = {}
        for path in paths:
            data = Reader(path.read_bytes()).read()
            assert data['game'] == 1 and len(data['objects']) == 1
            obj = data['objects'][0]
            expected = next(n for n in SCRIPT_PARENTS if n.lower() == obj['name'].lower())
            assert obj['parent'].lower() == SCRIPT_PARENTS[expected].lower()
            assert all(p['name'].isascii() for p in obj['properties'])
            objects[expected] = obj
            pex.append({'file': path.name, 'sha256': sha(path.read_bytes()), 'version': data['version']})
        config_obj = objects['_JSW_FB_ConfigScript']
        handler_obj = objects['_JSW_FB_HandlerScript']
        assert {'widget','enabled','playerref'} <= {p['name'].lower() for p in config_obj['properties']}
        funcs = {(s['name'].lower(), f['name'].lower()): f for s in handler_obj['states'] for f in s['functions']}
        f = funcs[('', 'updatedebuff')]
        divs = [c for c in f['code'] if c['op'] == 'FDiv' and
                isinstance(c['args'][1], dict) and c['args'][1].get('id','').lower() == 'frostresist']
        assert len(divs) == 3
        for div in divs:
            assert div['args'][2] == 100.0
            i = f['code'].index(div)
            reduced = f['code'][i+1]
            assert reduced['op'] == 'FSub' and reduced['args'][1] == 1.0 and reduced['args'][2] == div['args'][0]
            multiplied = f['code'][i+2]
            assert multiplied['op'] == 'FMul' and reduced['args'][0] in multiplied['args'][1:]
        assert len(calls(f, 'DamageActorValue')) == 3
        for name in ('oninit','onplayerloadgame'):
            assert len(calls(funcs[('',name)], 'UpgradeCoolingDefaults')) == 1
        assert len(calls(funcs[('', 'clearcolddebuffs')], 'HasSpell')) == 3
        assert len(calls(funcs[('', 'clearcolddebuffs')], 'RemoveSpell')) == 3
        assert len(calls(funcs[('', 'onupdate')], 'ClearColdDebuffs')) == 1
        assert len(calls(funcs[('', 'oncontrolDown'.lower())], 'StopWarmingAnimation')) == 1
        assert len(calls(funcs[('', 'stopwarminganimation')], 'UnregisterForAllControls')) == 1
        cf = {(s['name'].lower(), f['name'].lower()): f for s in config_obj['states'] for f in s['functions']}
        assert any(c['op'] == 'Return' and c['args'] == [2] for c in cf[('', 'getversion')]['code'])
        for name in ('ongamereload','onconfigopen'):
            assert calls(cf[('',name)], 'RepairLocalBindings')
        for state in ('enabled_toggle','enabled_warming_toggle'):
            assert calls(cf[(state,'onselectst')], 'SendModEvent')
        for state, value in (('cool_delta_slider',0.0075),('cold_delta_slider',0.015),('freezing_delta_slider',0.0375)):
            call = calls(cf[(state,'onslideropenst')], 'SetSliderDialogDefaultValue')
            assert len(call) == 1 and abs(call[0]['args'][-1]-value) < 1e-7
            assert calls(cf[(state,'ondefaultst')], 'SetValue')
        literal_strings = [a['string'] for s in handler_obj['states'] for f in s['functions']
                           for c in f['code'] for a in c['args'] if isinstance(a,dict) and 'string' in a]
        assert {'FrostResist','Health','Magicka','Stamina'} <= set(literal_strings)
        assert any('这里很温暖' in v for v in literal_strings)
    result = {'status': 'PASS', 'plugin_sha256': sha(actual), 'records_preserved': len(old),
              'record_ids_flags_and_vmad_preserved': True, 'local_player_alias_preserved': True,
              'translated_plugin_fields': text_fields, 'cooling_default_fields': cooling_fields,
              'background_quest': quest, 'stage_less_quest': True,
              'compiled_scripts': len(pex), 'pex': pex, 'gameplay_tested': False}
    (root/'build-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False))
    return result


def imports(skse, skyui, dest, interfaces):
    dest.mkdir(parents=True, exist_ok=True)
    for path in (skse/'scripts/vanilla').glob('*'):
        if path.is_file():
            shutil.copy2(path, dest/path.name)
    for path in (skse/'scripts/modified').glob('*.psc'):
        target = dest/path.name
        if target.exists():
            target.write_text(target.read_text(encoding='utf-8-sig')+'\n'+path.read_text(encoding='utf-8-sig'), encoding='utf-8')
        else:
            shutil.copy2(path, target)
    for path in interfaces.glob('*.psc'):
        shutil.copy2(path, dest/path.name)
    # These are imports only. Never recompile or distribute SkyUI's base scripts.
    for folder in ('Source','Headers'):
        for path in (skyui/f'dist/Data/Scripts/{folder}').glob('*.psc'):
            shutil.copy2(path, dest/path.name)
    print(json.dumps({'import_files': len(list(dest.glob('*'))), 'runtime_dependency_scripts_to_ship': 0}))


def package(root, compiled, out):
    validation = check(root, compiled)
    assert validation['compiled_scripts'] == 4
    candidate = out/'candidate'
    candidate.mkdir(parents=True, exist_ok=True)
    for path in (root/'Data').rglob('*'):
        if path.is_file():
            target = candidate/path.relative_to(root/'Data')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    for path in compiled.glob('*.pex'):
        name = next(n for n in SCRIPT_PARENTS if n.lower() == path.stem.lower())
        shutil.copy2(path, candidate/'scripts'/(name+'.pex'))
    shutil.copy2(root/'README_ZH.md', candidate/'README_ZH.md')
    shutil.copy2(root/'build-validation.json', candidate/'build-validation.json')
    provenance = {'mod': 'Frostbite 2.2.5 CHS r1', 'original_archive_sha256': ORIGINAL_ZIP_SHA,
                  'original_esl_sha256': ORIGINAL_ESL_SHA, 'source_commit': os.getenv('GITHUB_SHA','local'),
                  'run_id': os.getenv('GITHUB_RUN_ID'), 'compiler': 'Caprica v0.3.0, --game=skyrim --allow-unknown-events=1',
                  'skse_api_revision': '25b72352adb6543fa6d0bd3795780672b2e238e0',
                  'skyui_revision': '835428728e2305865e220fdfc99d791434955eb1',
                  'gameplay_tested': False, 'str_native_files_modified': False}
    (candidate/'provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+'\n')
    hashes = {p.relative_to(candidate).as_posix(): sha(p.read_bytes()) for p in sorted(candidate.rglob('*')) if p.is_file()}
    (candidate/'SHA256.json').write_text(json.dumps(hashes, ensure_ascii=False, indent=2)+'\n')
    archive = out/'Frostbite-2.2.5-CHS-Cold1.5-Fix-r1.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(candidate.rglob('*')):
            if path.is_file():
                z.write(path, path.relative_to(candidate).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(hashes)|{'SHA256.json'}
        for name, digest in hashes.items():
            assert sha(z.read(name)) == digest
        assert set(n for n in z.namelist() if n.lower().endswith('.pex')) == {'scripts/'+n+'.pex' for n in SCRIPT_PARENTS}
        assert 'Frostbite.esl' in z.namelist()
        assert not any('papyrus-imports' in n or n.startswith('input/') or n.endswith('.esp') for n in z.namelist())
    result = {'zip_content_check': 'PASS', 'zip': archive.name, 'sha256': sha(archive.read_bytes()),
              'files': len(hashes)+1, 'compiled_scripts': 4, 'gameplay_tested': False}
    (out/'archive-validation.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=('generate','check','imports','package'))
    p.add_argument('--root', type=Path, default=Path('mods/frostbite-chs'))
    p.add_argument('--compiled', type=Path)
    p.add_argument('--out', type=Path)
    p.add_argument('--skse', type=Path)
    p.add_argument('--skyui', type=Path)
    p.add_argument('--interfaces', type=Path, default=Path('tools/papyrus-interfaces'))
    args = p.parse_args()
    if args.command == 'generate':
        generate(args.root)
    elif args.command == 'check':
        check(args.root, args.compiled)
    elif args.command == 'imports':
        imports(args.skse, args.skyui, args.out, args.interfaces)
    else:
        package(args.root, args.compiled, args.out)


if __name__ == '__main__':
    main()
