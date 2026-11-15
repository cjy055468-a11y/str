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
# Merge SKSE's actual additions, following its scripts/build.py workflow.
for path in (api / 'scripts/modified').glob('*.psc'):
    destination = output / path.name
    mode = 'a' if destination.exists() else 'w'
    with destination.open(mode) as file:
        file.write('\n' + path.read_text() + '\n')
