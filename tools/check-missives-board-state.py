#!/usr/bin/env python3
"""Execute production bridge bookkeeping with a stub VM; this is not an engine test."""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
args = parser.parse_args()
source = args.source.resolve()
with tempfile.TemporaryDirectory(prefix='missives-state-') as directory:
    root = Path(directory)
    (root / 'Misc').mkdir()
    (root / 'TiltedOnlinePCH.h').write_text('#include <cstdint>\n')
    (root / 'Misc/BSScript.h').write_text(r'''
#pragma once
#include <cstdint>
namespace BSScript {
struct Variable {
    enum Type { kEmpty, kInteger, kBoolean };
    Type type{kEmpty}; struct { int32_t i{}; } data;
    template<class T> void Set(T value) { data.i = static_cast<int32_t>(value); }
    void Clear() { type = kEmpty; }
};
struct StackFrame {
    uint32_t GetPageForFrame() { return 0; }
    Variable* GetStackFrameVariable(uint32_t, uint32_t) { return nullptr; }
};
struct NativeFunction;
struct IVirtualMachine { void BindNativeMethod(NativeFunction*) {} };
struct NativeFunction {
    NativeFunction(const char*, const char*, bool, uint32_t) {}
    virtual ~NativeFunction() = default;
    virtual bool MarshallAndDispatch(Variable*, IVirtualMachine*, uint32_t, Variable*, StackFrame*) { return false; }
    void SetCallableFromTasklets(bool) {}
    void* pFunction{}; Variable::Type returnType{};
    struct Param { Variable::Type type{}; };
    struct { Param data[2]; } parameters;
};
}
''')
    (root / 'test.cpp').write_text(r'''
#include <ModCompat/MissiveBoardBridge.h>
#include <cassert>
#include <iostream>
using namespace MissiveBoardBridge;
int main() {
    using O = Operation;
    constexpr uint32_t quest=100, board=200, other=201;
    SetConnection(true); SetReady(true); SetBoardReady(board,true); SetBoardAuthority(board,true);
    SetListing(quest,board,1,0); SetLocalPublisher(quest,board);
    assert(Call(O::LocalPublisher,quest,board)==1);
    SetListing(quest,board,1,3);
    assert(Call(O::Status,quest,board)==3); // cleanup must be observable
    assert(Call(O::CanGenerate,quest,board)==0);
    Call(O::AcknowledgeRemoval,quest,board);
    assert(Call(O::Status,quest,board)==-1);
    assert(Call(O::CanGenerate,quest,board)==1);
    SetListing(quest,board,2,0); SetLocalPublisher(quest,board);
    SetListing(quest,other,9,0);
    BeginSnapshot(board);
    assert(Call(O::BoardReady,board,0)==0);
    assert(Call(O::Status,quest,board)==3);
    assert(Call(O::Status,quest,other)==0); // physical-board scope
    SetListing(quest,board,2,0); EndSnapshot(board);
    assert(Call(O::LocalPublisher,quest,board)==1);
    BeginSnapshot(board); EndSnapshot(board); // absent from snapshot
    assert(Call(O::Status,quest,board)==3);
    SetListing(quest,board,3,0); // replacement before old cleanup acknowledgement
    Call(O::AcknowledgeRemoval,quest,board);
    assert(Call(O::Status,quest,board)==0);
    assert(Call(O::LocalPublisher,quest,board)==0);
    SetListing(quest,board,3,1);
    assert(Call(O::CanGenerate,quest,board)==0);
    Call(O::AcknowledgeRemoval,quest,board);
    assert(Call(O::Status,quest,board)==1);
    SetConnection(false);
    assert(Call(O::Status,quest,board)==-1);
    assert(Call(O::Connected,0,0)==0);
    std::cout << "PASS: production bridge removal/snapshot/publisher/board-isolation state regressions\n";
}
''')
    executable = root / 'test'
    subprocess.run(['g++','-std=c++20','-pthread','-I'+str(root),'-I'+str(source/'Code/client'),str(source/'Code/client/ModCompat/MissiveBoardBridge.cpp'),str(root/'test.cpp'),'-o',str(executable)],check=True)
    subprocess.run([str(executable)],check=True)
