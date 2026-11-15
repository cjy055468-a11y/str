"""Prepare compile-only declarations; none of these files enter the mod archive."""
from pathlib import Path
import shutil
import sys

api, output = map(Path, sys.argv[1:3])
repo = Path(__file__).resolve().parent.parent
output.mkdir(parents=True, exist_ok=True)
for directory in (api / 'scripts/vanilla', repo / 'tools/papyrus-interfaces', repo / 'tools/ineed-interfaces'):
    for path in directory.iterdir():
        if path.is_file():
            shutil.copyfile(path, output / path.name)
# iNeed's unchanged waterskin branch uses this SKSE method. Read its real declaration.
declaration = next(line for line in (api / 'scripts/modified/Actor.psc').read_text().splitlines()
                   if 'Function GetWornForm(' in line)
with (output / 'Actor.psc').open('a') as file:
    file.write('\n' + declaration + '\n')
