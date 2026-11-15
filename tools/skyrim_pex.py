"""Validate Skyrim PEX 3.2 objects, properties, functions and bytecode boundaries."""
from dataclasses import dataclass
from pathlib import Path
import struct


@dataclass
class Value:
    kind: int
    value: object
    offset: int


class Pex:
    ARG_COUNTS = [0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2,
                  3, 3, 3, 3, 3, 1, 2, 2, 3, 2, 3, 1, 3, 3, 3,
                  2, 2, 3, 3, 4, 4]

    def __init__(self, path):
        self.path = Path(path)
        self.data = self.path.read_bytes()
        self.offset = 0
        assert self.data[:8] == bytes.fromhex('fa57c0de03020001'), self.path
        self.offset = 16
        self.headers = [self.text() for _ in range(3)]
        self.strings = [self.text() for _ in range(self.read('H'))]
        if self.read('B'):
            self.read('Q')
            for _ in range(self.read('H')):
                self.read('HHHB')
                lines = self.read('H')
                self.offset += 2 * lines
        for _ in range(self.read('H')):
            self.read('HB')
        self.variables = {}
        self.properties = {}
        self.functions = {}
        self.objects = []
        self.object_sizes = {}
        for _ in range(self.read('H')):
            name = self.symbol()
            size_offset = self.offset
            size = self.read('I')
            self.object_sizes[name.lower()] = (size_offset, size)
            parent = self.symbol()
            self.symbol()
            self.read('I')
            self.symbol()
            self.objects.append((name, parent))
            for _ in range(self.read('H')):
                var = self.symbol()
                type_ = self.symbol()
                self.read('I')
                self.variables[(name.lower(), var.lower())] = (type_, self.value())
            for _ in range(self.read('H')):
                prop = self.symbol()
                type_ = self.symbol()
                self.symbol()
                self.read('I')
                flags = self.read('B')
                if flags & 4:
                    self.properties[(name.lower(), prop.lower())] = (type_, self.symbol())
                else:
                    if flags & 1:
                        self.function(name, '@property', prop + '.get', False)
                    if flags & 2:
                        self.function(name, '@property', prop + '.set', False)
            for _ in range(self.read('H')):
                state = self.symbol()
                for _ in range(self.read('H')):
                    self.function(name, state)
        assert self.offset == len(self.data), (self.path, self.offset, len(self.data))

    def read(self, fmt):
        length = struct.calcsize('>' + fmt)
        assert self.offset + length <= len(self.data)
        vals = struct.unpack_from('>' + fmt, self.data, self.offset)
        self.offset += length
        return vals[0] if len(vals) == 1 else vals

    def text(self):
        length = self.read('H')
        assert self.offset + length <= len(self.data)
        value = self.data[self.offset:self.offset + length].decode('utf-8')
        self.offset += length
        return value

    def symbol(self):
        index = self.read('H')
        assert index < len(self.strings)
        return self.strings[index]

    def value(self):
        kind = self.read('B')
        offset = self.offset
        if kind == 0:
            val = None
        elif kind in (1, 2):
            val = self.symbol()
        elif kind == 3:
            val = self.read('i')
        elif kind == 4:
            val = self.read('f')
        elif kind == 5:
            val = self.read('B')
            assert val in (0, 1)
        else:
            raise ValueError(('Unknown Skyrim PEX value', kind, offset))
        return Value(kind, val, offset)

    def function(self, object_, state, name=None, named=True):
        if named:
            name = self.symbol()
        return_type, documentation = self.symbol(), self.symbol()
        self.read('I')
        flags = self.read('B')
        params = [(self.symbol(), self.symbol()) for _ in range(self.read('H'))]
        locals_ = [(self.symbol(), self.symbol()) for _ in range(self.read('H'))]
        count = self.read('H')
        instructions = []
        for _ in range(count):
            pos = self.offset
            opcode = self.read('B')
            assert 0 <= opcode < len(self.ARG_COUNTS)
            args = [self.value() for _ in range(self.ARG_COUNTS[opcode])]
            variadic = []
            if opcode in (23, 24, 25):
                size = self.value()
                assert size.kind == 3 and 0 <= size.value <= 128
                variadic = [self.value() for _ in range(size.value)]
            instructions.append((pos, opcode, args, variadic))
        for index, (_, opcode, args, _) in enumerate(instructions):
            if opcode in (20, 21, 22):
                target = args[-1]
                assert target.kind == 3 and 0 <= index + target.value <= count
        self.functions[(object_.lower(), state.lower(), name.lower())] = dict(
            return_type=return_type, flags=flags, parameters=params,
            locals=locals_, instructions=instructions)

    def property_default(self, object_, prop):
        type_, backing = self.properties[(object_.lower(), prop.lower())]
        type2, value = self.variables[(object_.lower(), backing.lower())]
        assert type_.lower() == type2.lower()
        return type_, backing, value
