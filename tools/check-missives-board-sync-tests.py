#!/usr/bin/env python3
"""Require the board-local claim and wire-model regressions in the TPTests XML."""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

expected = {
    "Missives board has one public listing and an atomic board-local claimant",
    "Concurrent claims on one Missives board row elect exactly one player",
    "The same Missives quest can be listed independently on different boards",
    "A newly elected board authority can retire an expired public line",
    "Missives board protocol serializes only the public line identifiers",
}
root = ET.parse(Path(sys.argv[1])).getroot()
cases = root.findall(".//testcase")
assert not root.findall(".//failure"), "test assertion failure"
assert not root.findall(".//error"), "test execution error"
executed = {case.attrib.get("name") for case in cases if case.find("skipped") is None}
assert expected <= executed, f"Missing Missives board tests: {sorted(expected-executed)}"
print(json.dumps({"test_cases": len(cases), "missives_board_cases": len(expected), "failures": 0, "errors": 0}, indent=2))
