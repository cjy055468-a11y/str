#!/usr/bin/env python3
"""Verify every install archive against the checked candidate, byte for byte."""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

candidate, archives = map(Path, sys.argv[1:])
digest = lambda data: hashlib.sha256(data).hexdigest()
specs = {
    'STR-NoticeBoard-v2-full-test.zip': (candidate, ''),
    'STR-NoticeBoard-v2-MO2.zip': (candidate / 'NoticeBoardCompatibility', ''),
    'STR-NoticeBoard-v2-programs.zip': (candidate / 'SkyrimTogetherReborn', 'SkyrimTogetherReborn/'),
}
report = []
for name, (root, prefix) in specs.items():
    expected = {prefix + p.relative_to(root).as_posix(): digest(p.read_bytes())
                for p in root.rglob('*') if p.is_file()}
    path = archives / name
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None, name
        members = [p.filename for p in archive.infolist() if not p.is_dir()]
        assert len(members) == len(set(members)), ('Duplicate ZIP entry', name)
        actual = {p: digest(archive.read(p)) for p in members}
        assert actual == expected, ('ZIP content mismatch', name, set(actual) ^ set(expected))
    report.append({'file': name, 'files': len(expected), 'sha256': digest(path.read_bytes())})
print(json.dumps({'archive_content_check': 'PASS', 'archives': report}, indent=2))
