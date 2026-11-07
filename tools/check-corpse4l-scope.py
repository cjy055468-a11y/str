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
scope = json.loads((repo / "fixes/corpse4l-scope.json").read_text())
baseline_patch = repo / "fixes/coopfix4g-corpse4k-v184.patch"
baseline_delta = repo / "fixes/corpse4k-delta.patch"
delta_patch = repo / "fixes/corpse4l-delta.patch"
full_patch = repo / "fixes/coopfix4g-corpse4l-v184.patch"


def sha256(data):
    if isinstance(data, Path):
        data = data.read_bytes()
    return hashlib.sha256(data).hexdigest()


def patch_paths(path):
    return set(re.findall(r"^diff --git a/(.*?) b/", path.read_text(), re.M))


assert root.name == "source" or (root / ".git").exists(), "Expected the official source checkout"
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip() == scope["official_base"]
assert sha256(baseline_patch) == scope["baseline_patch_sha256"]
assert sha256(baseline_delta) == scope["baseline_delta_sha256"]
assert sha256(delta_patch) == scope["delta_patch_sha256"]
assert sha256(full_patch) == scope["full_patch_sha256"]

baseline_paths = patch_paths(baseline_patch)
delta_paths = patch_paths(delta_patch)
full_paths = patch_paths(full_patch)
assert sorted(delta_paths) == scope["delta_files"]
assert full_paths == baseline_paths | delta_paths, "Full candidate changed files outside the 4g baseline plus diagnostic delta"

tracked_changes = set(subprocess.check_output(["git", "diff", "--name-only", "HEAD"], cwd=root, text=True).splitlines())
untracked_changes = set(subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=root, text=True).splitlines())
assert tracked_changes | untracked_changes == full_paths, "Applied source tree has missing or out-of-scope files"

# Reconstruct both the exact 4g baseline and full diagnostic candidate from the
# pinned official release, then compare all changed files byte-for-byte.
with tempfile.TemporaryDirectory(prefix="str-corpse4l-check-") as temp:
    temp = Path(temp)
    tracked = set(subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=root, text=True).splitlines())
    archive_paths = sorted((full_paths | baseline_paths) & tracked)
    archive = subprocess.check_output(["git", "archive", "HEAD", *archive_paths], cwd=root)

    official = temp / "official"
    official.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive)) as source_archive:
        source_archive.extractall(official, filter="data")

    reconstructed_full = temp / "full"
    shutil.copytree(official, reconstructed_full)
    subprocess.run(["git", "apply", "--check", str(full_patch)], cwd=reconstructed_full, check=True)
    subprocess.run(["git", "apply", str(full_patch)], cwd=reconstructed_full, check=True)
    for name in full_paths:
        actual = root / name
        expected = reconstructed_full / name
        assert actual.exists() == expected.exists(), name
        if expected.exists():
            assert actual.read_bytes() == expected.read_bytes(), name

    reconstructed_baseline = temp / "baseline"
    shutil.copytree(official, reconstructed_baseline)
    subprocess.run(["git", "apply", "--check", str(baseline_patch)], cwd=reconstructed_baseline, check=True)
    subprocess.run(["git", "apply", str(baseline_patch)], cwd=reconstructed_baseline, check=True)

    reversed_delta = temp / "reversed-delta"
    reversed_delta.mkdir()
    for name in delta_paths:
        target = reversed_delta / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, target)
    subprocess.run(["git", "apply", "--reverse", "--check", str(delta_patch)], cwd=reversed_delta, check=True)
    subprocess.run(["git", "apply", "--reverse", str(delta_patch)], cwd=reversed_delta, check=True)
    for name in delta_paths:
        assert (reconstructed_baseline / name).read_bytes() == (reversed_delta / name).read_bytes(), name

print(json.dumps({
    "baseline": scope["baseline"],
    "official_base": scope["official_base"],
    "baseline_files": len(baseline_paths),
    "diagnostic_delta_files": sorted(delta_paths),
    "full_candidate_scope_matches_baseline_plus_delta": True,
    "applied_full_patch_matches_source": True,
    "reverse_delta_recovers_exact_4g_baseline": True,
}, indent=2))
