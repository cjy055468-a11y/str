import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

root = Path(sys.argv[1]).resolve()
repo = Path(__file__).resolve().parent.parent
scope = json.loads((repo / "fixes/corpse4k-scope.json").read_text())
baseline_patch = repo / "fixes/coopfix4g-corpse4-v184.patch"
delta_patch = repo / "fixes/corpse4k-delta.patch"
full_patch = repo / "fixes/coopfix4g-corpse4k-v184.patch"

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def patch_paths(path):
    return set(re.findall(r"^diff --git a/(.*?) b/", path.read_text(), re.M))

assert root.name == "source" or (root / ".git").exists(), "Expected the official source checkout"
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip() == scope["official_base"]
assert sha256(baseline_patch) == scope["baseline_patch_sha256"]
assert sha256(delta_patch) == scope["delta_patch_sha256"]
assert sha256(full_patch) == scope["full_patch_sha256"]

baseline_paths = patch_paths(baseline_patch)
delta_paths = patch_paths(delta_patch)
full_paths = patch_paths(full_patch)
assert sorted(delta_paths) == scope["delta_files"]
assert full_paths == baseline_paths | delta_paths, "Full candidate changed files outside the 4g baseline plus delta"

# Reconstruct the exact 4g source from the pinned official commit, then reverse
# the new delta in a copy of the candidate and compare every changed file.
with tempfile.TemporaryDirectory(prefix="str-corpse4k-delta-") as temp:
    stage = Path(temp) / "candidate-delta"
    stage.mkdir()
    for name in delta_paths:
        target = stage / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, target)
    subprocess.run(["git", "apply", "--reverse", "--check", str(delta_patch)], cwd=stage, check=True)
    subprocess.run(["git", "apply", "--reverse", str(delta_patch)], cwd=stage, check=True)

    baseline = Path(temp) / "baseline"
    baseline.mkdir()
    tracked = set(subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=root, text=True).splitlines())
    archive_paths = sorted((baseline_paths | delta_paths) & tracked)
    archive = subprocess.check_output(["git", "archive", "HEAD", *archive_paths], cwd=root)
    with tarfile.open(fileobj=io.BytesIO(archive)) as source_archive:
        source_archive.extractall(baseline, filter="data")
    subprocess.run(["git", "apply", str(baseline_patch)], cwd=baseline, check=True)

    for name in delta_paths:
        expected = baseline / name
        recovered = stage / name
        assert expected.exists() == recovered.exists(), name
        if expected.exists():
            assert expected.read_bytes().replace(b"\r\n", b"\n") == recovered.read_bytes().replace(b"\r\n", b"\n"), name

print(json.dumps({
    "baseline": scope["baseline"],
    "official_base": scope["official_base"],
    "baseline_files": len(baseline_paths),
    "delta_files": sorted(delta_paths),
    "full_candidate_scope_matches_baseline_plus_delta": True,
    "exact_baseline_recovery": True,
}, indent=2))
