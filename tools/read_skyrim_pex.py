"""Read-only Skyrim PEX audit reader using the published PEX field/opcode layout."""
import argparse
import json
import struct
from pathlib import Path

OPS = 'Nop IAdd FAdd ISub FSub IMul FMul IDiv FDiv IMod Not INeg FNeg Assign Cast CmpEq CmpLt CmpLte CmpGt CmpGte Jmp JmpT JmpF CallMethod CallParent CallStatic Return StrCat PropGet PropSet ArrayCreate ArrayLength ArrayGetElement ArraySetElement ArrayFindElement ArrayRFindElement'.split()
COUNTS = [0] + [3]*9 + [2]*5 + [3]*5 + [1,2,2,3,2,3,1,3,3,3,2,2,3,3,4,4]


class Reader:
    def __init__(self, raw):
        assert raw[:4] == bytes.fromhex('FA57C0DE')
        self.raw = raw
        self.i = 4
        self.strings = []

    def u(self, fmt):
        values = struct.unpack_from('>'+fmt, self.raw, self.i)
        self.i += struct.calcsize('>'+fmt)
        return values[0] if len(values) == 1 else list(values)

    def string(self):
        n = self.u('H')
        value = self.raw[self.i:self.i+n].decode('utf-8')
        self.i += n
        return value

    def ref(self):
        return self.strings[self.u('H')]

    def value(self):
        tag = self.u('B')
        if tag == 0:
            return None
        if tag in (1,2):
            return {'id' if tag == 1 else 'string': self.ref()}
        if tag == 3:
            return self.u('i')
        if tag == 4:
            return self.u('f')
        if tag == 5:
            return bool(self.u('B'))
        raise ValueError(('value tag',tag,self.i))

    def instruction(self):
        offset = self.i
        op = self.u('B')
        assert op < len(OPS), (op, offset)
        args = [self.value() for _ in range(COUNTS[op])]
        if op in (23,24,25):
            n = self.value()
            assert isinstance(n, int) and n >= 0
            args += [self.value() for _ in range(n)]
        return {'offset':offset, 'op': OPS[op], 'args': args}

    def function(self, property_name=None):
        name = self.ref() if property_name is None else property_name
        return_type = self.ref()
        doc = self.ref()
        flags = self.u('I')
        native_flags = self.u('B')
        params = [(self.ref(), self.ref()) for _ in range(self.u('H'))]
        locals_ = [(self.ref(), self.ref()) for _ in range(self.u('H'))]
        code = [self.instruction() for _ in range(self.u('H'))]
        return {'name':name,'return_type':return_type,'flags':flags,'native_flags':native_flags,
                'parameters':params,'locals':locals_,'code':code}

    def object(self):
        name = self.ref()
        size = self.u('I')
        parent = self.ref()
        doc = self.ref()
        flags = self.u('I')
        auto_state = self.ref()
        variables = []
        for _ in range(self.u('H')):
            variables.append({'name':self.ref(),'type':self.ref(),'flags':self.u('I'),'value':self.value()})
        properties = []
        for _ in range(self.u('H')):
            prop = {'name':self.ref(),'type':self.ref(),'doc':self.ref(),'flags':self.u('I')}
            f = self.u('B')
            if f & 4:
                prop['auto_var'] = self.ref()
            else:
                if f & 1:
                    prop['read'] = self.function(prop['name']+'@get')
                if f & 2:
                    prop['write'] = self.function(prop['name']+'@set')
            properties.append(prop)
        states = []
        for _ in range(self.u('H')):
            state = self.ref()
            states.append({'name':state,'functions':[self.function() for _ in range(self.u('H'))]})
        return {'name':name,'parent':parent,'flags':flags,'auto_state':auto_state,
                'variables':variables,'properties':properties,'states':states}

    def read(self):
        major, minor, game = self.u('BBH')
        assert major == 3 and game == 1 and minor in (1,2)
        compiled = self.u('Q')
        source, user, machine = self.string(), self.string(), self.string()
        self.strings = [self.string() for _ in range(self.u('H'))]
        if self.u('B'):
            self.u('Q')
            for _ in range(self.u('H')):
                self.u('HHHB')
                for _ in range(self.u('H')):
                    self.u('H')
        for _ in range(self.u('H')):
            self.u('HB')
        objects = [self.object() for _ in range(self.u('H'))]
        assert self.i == len(self.raw), (self.i, len(self.raw))
        return {'version':[major,minor],'game':game,'source':source,'strings':self.strings,'objects':objects}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('file', type=Path)
    p.add_argument('--function')
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    data = Reader(args.file.read_bytes()).read()
    if args.output:
        args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'file':args.file.name,'source':data['source'],'game':data['game'],
                      'objects':[(o['name'],o['parent']) for o in data['objects']]},ensure_ascii=False))
    if args.function:
        for obj in data['objects']:
            for state in obj['states']:
                for function in state['functions']:
                    if function['name'].lower() == args.function.lower():
                        print(json.dumps(function,ensure_ascii=False,indent=2))
