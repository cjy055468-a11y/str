#!/usr/bin/env python3
"""Run the actual production ledger/client-state test bodies without Skyrim.

A minimal GameId/Buffer declaration replaces only the encoding dependency here;
the full production codec/factory roundtrip is additionally required on Windows.
"""
import argparse,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('source',type=Path);args=p.parse_args();src=args.source.resolve()
with tempfile.TemporaryDirectory(prefix='notice-pure-') as name:
 root=Path(name);(root/'catch2').mkdir();(root/'Structs').mkdir()
 (root/'catch2/catch.hpp').write_text(r'''
#pragma once
#include <cassert>
#include <cstdint>
#include <iostream>
#include <utility>
#include <vector>
using TestFn=void(*)();
inline std::vector<std::pair<const char*,TestFn>>& NoticeTests(){static std::vector<std::pair<const char*,TestFn>> tests;return tests;}
struct RegisterNoticeTest{RegisterNoticeTest(const char* name,TestFn fn){NoticeTests().push_back({name,fn});}};
#define JOIN0(a,b) a##b
#define JOIN(a,b) JOIN0(a,b)
#define TEST_CASE(name,tags) static void JOIN(test_,__LINE__)();static RegisterNoticeTest JOIN(reg_,__LINE__)(name,&JOIN(test_,__LINE__));static void JOIN(test_,__LINE__)()
#define REQUIRE(value) assert((value))
#define REQUIRE_FALSE(value) assert(!(value))
''')
 (root/'Structs/GameId.h').write_text(r'''
#pragma once
#include <cstdint>
namespace TiltedPhoques { struct Buffer { struct Writer; struct Reader; }; }
struct GameId {
 uint32_t ModId{},BaseId{};
 GameId()=default;GameId(uint32_t mod,uint32_t base):ModId(mod),BaseId(base){}
 bool operator==(const GameId& other)const{return ModId==other.ModId&&BaseId==other.BaseId;}
 bool operator!=(const GameId& other)const{return !(*this==other);}
 operator bool()const{return ModId||BaseId;}
 uint64_t LogFormat()const{return(uint64_t(ModId)<<32)|BaseId;}
};
''')
 ledger=(src/'Code/tests/notice_board.cpp').read_text();start=ledger.index('namespace\n{');stop=ledger.index('TEST_CASE("Notice wire protocol')
 (root/'ledger.cpp').write_text('#include <catch2/catch.hpp>\n#include <Game/Inventory/NoticeLedger.h>\n#include <atomic>\n#include <thread>\n'+ledger[start:stop])
 # Preserve the client test source verbatim; only rewrite the relative include
 # so it still points to the same production header after copying to temp.
 state=(src/'Code/tests/notice_client_state.cpp').read_text().replace('"../client/ModCompat/NoticeState.h"','<ModCompat/NoticeState.h>')
 (root/'state.cpp').write_text(state)
 (root/'main.cpp').write_text('#include <catch2/catch.hpp>\nint main(){for(const auto& [name,fn]:NoticeTests()){fn();std::cout<<"PASS: "<<name<<"\\n";}assert(NoticeTests().size()==17);}\n')
 command=['g++','-std=c++20','-Wall','-Wextra','-Werror','-pthread','-I'+str(root),'-I'+str(src/'Code/encoding'),'-I'+str(src/'Code/server'),'-I'+str(src/'Code/client'),str(root/'ledger.cpp'),str(root/'state.cpp'),str(root/'main.cpp'),'-o',str(root/'tests')]
 subprocess.run(command,check=True);subprocess.run([str(root/'tests')],check=True)
