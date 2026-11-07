from pathlib import Path
import sys
data = Path(sys.argv[1]).read_bytes()
for marker in (b'STR Missives private letter copy blocked:', b'STR Missives private quest update blocked:', b'Missives.esp'):
    assert marker in data, marker
print('PASS: Missives personal letter and quest isolation markers present in compiled client')
