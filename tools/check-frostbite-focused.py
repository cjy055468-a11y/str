"""Audit the requested changes against the exact uploaded Frostbite runtime."""
import argparse
import gzip
import hashlib
import json
import operator
import re
from pathlib import Path

from frostbite_build import calls, walk
from read_skyrim_pex import Reader

ROOT = Path('mods/frostbite-chs')
ALLOWED_FUNCTIONS = {'runverbosefeedback', 'updatedebuff', 'applyfixedpreset'}


def normalized(raw):
    return raw.replace(b'\r\n', b'\n')


def function_map(obj):
    return {(s['name'].lower(), f['name'].lower()): f for s in obj['states'] for f in s['functions']}


def without_offsets(value):
    if isinstance(value, list):
        return [without_offsets(x) for x in value]
    if isinstance(value, dict):
        return {k: without_offsets(v) for k, v in value.items() if k != 'offset'}
    return value


def run_debuff(function, body_temp, frost_resistance, base_health):
    """Execute the compiled non-latent arithmetic/branches with recorded native calls.

    This checks script decisions, not Skyrim's implementation of the native calls.
    """
    env = {'::bodytemp_var': body_temp}
    globals_ = {'regendebuff': 0.5, 'damagedebuff': 0.2, 'damagedelta': 5.0,
                'healthdebuff': 1, 'staminadebuff': 1, 'magickadebuff': 1}
    bases = {'Health': base_health, 'Stamina': 200.0, 'Magicka': 150.0}
    types = {n.lower(): t.lower() for n, t in function['locals']}
    damage, regen = [], set()

    def value(arg):
        if isinstance(arg, dict):
            if 'string' in arg:
                return arg['string']
            name = arg['id'].lower()
            return env.get(name, name)
        return arg

    def store(arg, result):
        env[arg['id'].lower()] = result

    arithmetic = {'FAdd': operator.add, 'IAdd': operator.add, 'FSub': operator.sub,
                  'ISub': operator.sub, 'FMul': operator.mul, 'IMul': operator.mul,
                  'FDiv': operator.truediv, 'IDiv': operator.floordiv,
                  'CmpEq': operator.eq, 'CmpLt': operator.lt, 'CmpLte': operator.le,
                  'CmpGt': operator.gt, 'CmpGte': operator.ge}
    code, pc, steps = function['code'], 0, 0
    while pc < len(code):
        steps += 1
        assert steps < 500
        instruction = code[pc]
        op, args = instruction['op'], instruction['args']
        if op in arithmetic:
            store(args[0], arithmetic[op](value(args[1]), value(args[2])))
        elif op == 'Assign':
            store(args[0], value(args[1]))
        elif op == 'Cast':
            cast = {'bool': bool, 'float': float, 'int': int}.get(types[args[0]['id'].lower()], lambda x: x)
            store(args[0], cast(value(args[1])))
        elif op == 'Not':
            store(args[0], not value(args[1]))
        elif op in ('Jmp', 'JmpT', 'JmpF'):
            take = op == 'Jmp' or (bool(value(args[0])) if op == 'JmpT' else not value(args[0]))
            if take:
                pc += args[-1]
                continue
        elif op == 'CallMethod':
            method = args[0]['id'].lower()
            receiver = value(args[1])
            params = [value(a) for a in args[3:]]
            result = None
            if method in ('getvalue', 'getvalueint'):
                result = globals_[receiver.removeprefix('::').removesuffix('_var')]
            elif method == 'getactorvalue':
                assert params == ['FrostResist']
                result = frost_resistance
            elif method == 'getbaseactorvalue':
                result = bases[params[0]]
            elif method == 'damageactorvalue':
                damage.append(tuple(params))
            elif method == 'addspell':
                regen.add(params[0])
            elif method == 'removespell':
                regen.discard(params[0])
            elif method == 'clearcolddebuffs':
                regen.clear()
            elif method == 'startflash':
                pass
            else:
                raise AssertionError(('Unhandled native call in audit', method))
            store(args[2], result)
        elif op == 'Return':
            break
        elif op != 'Nop':
            raise AssertionError(('Unhandled opcode in audit', op))
        pc += 1
    return damage, regen


def check(compiled=None):
    baseline = json.loads((ROOT/'input/no-screen-flash-baseline.json').read_text())
    assert baseline['archive_sha256'] == '3a19ca5382fd644c4338afdfb2e424e355ece81803e7827e4a380dd69a9fc44c'
    old_source = normalized(gzip.decompress((ROOT/'input/_JSW_FB_HandlerScript.before.psc.gz').read_bytes())).decode()
    new_source = normalized((ROOT/'Data/scripts/source/_JSW_FB_HandlerScript.psc').read_bytes()).decode()
    pattern = r'(?ims)^(?:\w+(?:\[\])?[ \t]+)?function[ \t]+(\w+)\([^\n]*\n.*?^endFunction\b[^\n]*'
    old_functions = {m.group(1).lower(): m.group() for m in re.finditer(pattern, old_source)}
    restored = re.sub(pattern, lambda m: old_functions[m.group(1).lower()]
                      if m.group(1).lower() in ALLOWED_FUNCTIONS else m.group(), new_source)
    assert restored == old_source, 'Changes outside the three requested function bodies'
    for name, digest in baseline['runtime_files'].items():
        if name in ('Frostbite.esl', 'scripts/source/_JSW_FB_HandlerScript.psc', 'scripts/_JSW_FB_HandlerScript.pex'):
            continue
        data = (ROOT/'Data'/name).read_bytes()
        if name.endswith('.psc'):
            data = normalized(data)
        assert hashlib.sha256(data).hexdigest() == digest, name

    _, before = walk((ROOT/'input/Frostbite.esl').read_bytes())
    _, after = walk((ROOT/'Data/Frostbite.esl').read_bytes())
    # Regenerate the previously shipped r2 plugin in memory for a focused diff.
    from frostbite_build import DEFAULTS, TEXT, walk as transform
    old_defaults = {k: v for k, v in DEFAULTS.items() if k != '_JSW_FB_HealthDebuff'}
    old_text = {k: v for k, v in TEXT.items() if not k.startswith('Decrease ')}
    def old_r2(kind, form, fields):
        edid = next((v.rstrip(b'\0').decode() for t, v in fields if t == 'EDID'), '')
        return [(t, __import__('struct').pack('<f', old_defaults[edid][1])
                 if kind == 'GLOB' and t == 'FLTV' and edid in old_defaults
                 else old_text[v.rstrip(b'\0').decode()].encode()+b'\0'
                 if kind in ('MGEF','SPEL','MESG') and t in ('FULL','DESC','ITXT')
                 and v.rstrip(b'\0').decode() in old_text else v) for t, v in fields]
    old_plugin, _ = transform((ROOT/'input/Frostbite.esl').read_bytes(), old_r2)
    _, before = walk(old_plugin)
    assert hashlib.sha256(old_plugin).hexdigest() == baseline['runtime_files']['Frostbite.esl']
    changed = []
    for a, b in zip(before, after):
        assert a[:3] == b[:3]
        assert len(a[3]) == len(b[3])
        for (tag, x), (tag2, y) in zip(a[3], b[3]):
            assert tag == tag2
            if x != y:
                assert (a[0] == 'MGEF' and tag == 'DNAM') or (a[1] == 0x04000813 and tag == 'FLTV')
                changed.append((a[0], f'{a[1]:08X}', tag))
        if b[0] in ('MGEF','SPEL'):
            for tag, raw in b[3]:
                if tag in ('FULL','DNAM','DESC') and raw.rstrip(b'\0'):
                    text = raw.rstrip(b'\0').decode()
                    assert re.search(r'[\u4e00-\u9fff]', text), text
                    assert not re.search(r'[A-Za-z]', re.sub(r'<[^>]+>', '', text)), text
    assert len(changed) == 4

    result = dict(status='PASS', original_plugin_retained=True, plugin_fields_changed=changed,
                  handler_functions_allowed=sorted(ALLOWED_FUNCTIONS), other_runtime_files_preserved=True,
                  compiled_checks=False, gameplay_tested=False)
    if compiled:
        obj = Reader((compiled/'_JSW_FB_HandlerScript.pex').read_bytes()).read()['objects'][0]
        original = Reader((ROOT/'input/_JSW_FB_HandlerScript.before.pex').read_bytes()).read()['objects'][0]
        original_functions, functions = function_map(original), function_map(obj)
        assert original_functions.keys() == functions.keys()
        for key in ('name','parent','flags','auto_state','variables','properties'):
            # Read-only property getters also contain instruction offsets; the
            # compiled file layout changes when the requested function shrinks.
            assert without_offsets(obj[key]) == without_offsets(original[key]), key
        modified = {name for name in functions if without_offsets(functions[name]) != without_offsets(original_functions[name])}
        assert modified == {('', n) for n in ALLOWED_FUNCTIONS}, modified
        for f in functions.values():
            for i, instruction in enumerate(f['code']):
                if instruction['op'] in ('Jmp','JmpT','JmpF'):
                    assert 0 <= i + instruction['args'][-1] <= len(f['code'])
        feedback = functions[('', 'runverbosefeedback')]
        assert {c['args'][1 if c['op']=='CallStatic' else 0]['id'].lower()
                for c in feedback['code'] if c['op'].startswith('Call')} == {'getvalueint','notification'}
        cases = 0
        for temperature in (0.51,0.5,0.20001,0.2,0.01,0.0):
            for resistance in (-50.0,0.0,50.0,100.0,150.0):
                for health in (100.0,1000.0):
                    damage, regen = run_debuff(functions[('', 'updatedebuff')], temperature, resistance, health)
                    assert [v for av, v in damage if av == 'Health'] == ([1.0] if temperature == 0 else [])
                    assert any('health' in spell for spell in regen) == (temperature <= 0.5)
                    for av, base in (('Stamina',200.0),('Magicka',150.0)):
                        expected = [max(0.0, base*0.05*(1-resistance/100))] if temperature <= 0.2 else []
                        assert [v for key, v in damage if key == av] == expected
                    cases += 1
        result.update(compiled_checks=True, unchanged_handler_functions=len(functions)-len(modified),
                      compiled_logic_boundary_cases=cases, screen_effect_calls_removed=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--compiled', type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.compiled), ensure_ascii=False, indent=2))
