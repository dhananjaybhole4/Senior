"""Tests for the plugin's scripts: .senior/ verify and the bwrap role launcher (fake claude, no tokens)."""
import json, os, shutil, subprocess, sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "plugin" / "scripts"


def sh(cwd, *args, env=None):
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd, capture_output=True, text=True, env=env)


@pytest.fixture
def proj(tmp_path):
    (tmp_path / ".senior" / "checks").mkdir(parents=True)
    (tmp_path / ".senior" / "checks" / "t.sh").write_text("exit 0\n")
    (tmp_path / ".senior" / "checks.toml").write_text('[[check]]\nname = "t"\ncmd = "sh .senior/checks/t.sh"\nwhy = "x"\n')
    return tmp_path


def test_verify_needs_harness(tmp_path):
    assert sh(tmp_path, SCRIPTS / "verify.py").returncode != 0


def test_verify_lock_pass_and_tamper(proj):
    r = sh(proj, SCRIPTS / "verify.py")
    assert r.returncode == 1 and "checks never locked" in r.stdout  # unapproved checks do not pass
    sh(proj, SCRIPTS / "verify.py", "lock")
    assert sh(proj, SCRIPTS / "verify.py").returncode == 0
    (proj / ".senior" / "checks" / "t.sh").write_text("exit 1\n")
    r = sh(proj, SCRIPTS / "verify.py")
    fails = [l.split()[1] for l in r.stdout.splitlines() if l.startswith("FAIL ")]
    assert r.returncode == 1 and fails == ["fingerprint", "t"] and "CHANGED" in r.stdout


FAKE = """#!/usr/bin/env python3
import json, os, pathlib, sys
root = pathlib.Path.cwd()
seen = sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())
wrote = []
for target in ("src/new.py", ".senior/checks/new.sh", ".senior/note.md"):
    try:
        (root / target).parent.mkdir(parents=True, exist_ok=True); (root / target).write_text("x"); wrote.append(target)
    except OSError:
        pass
print(json.dumps({"result": json.dumps({"seen": seen, "wrote": wrote}), "modelUsage": {"m": {"inputTokens": 7}}}))
"""


@pytest.mark.skipif(not shutil.which("bwrap"), reason="bubblewrap needed")
# writes into a hidden folder succeed inside the sandbox but are thrown away; `kept` = what reaches the disk
@pytest.mark.parametrize("role, sees_src, kept", [
    ("test-writer", False, [".senior/checks/new.sh", ".senior/note.md"]),
    ("builder", True, ["src/new.py", ".senior/note.md"]),
    ("reviewer", False, []),
])
def test_role_isolation(proj, tmp_path_factory, role, sees_src, kept):
    (proj / "src").mkdir(); (proj / "src" / "secret.py").write_text("SECRET = 1\n")
    bin_dir = tmp_path_factory.mktemp("bin")
    (bin_dir / "claude").write_text(FAKE); (bin_dir / "claude").chmod(0o755)
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}
    r = sh(proj, SCRIPTS / "role.py", role, "try to read and write everything", env=env)
    assert r.returncode == 0, r.stderr + r.stdout
    out = json.loads(r.stdout)
    assert ("src/secret.py" in out["seen"]) == sees_src
    assert ".senior/checks.toml" in out["seen"]
    on_disk = [t for t in ("src/new.py", ".senior/checks/new.sh", ".senior/note.md") if (proj / t).exists()]
    assert on_disk == kept
    assert (proj / "src" / "secret.py").read_text() == "SECRET = 1\n"  # hidden files are untouched
    assert json.loads((proj / ".senior" / "usage.jsonl").read_text()) == {"role": role, "tokens": 7}
