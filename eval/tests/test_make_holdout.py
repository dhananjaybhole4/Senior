"""The exam writer must not see the visible situations and must print no contents (fake CLI, no tokens)."""
import os, shutil, subprocess, sys
from pathlib import Path

import pytest

EVAL = Path(__file__).resolve().parents[1]

FAKE = """#!/usr/bin/env python3
import json, pathlib, re, sys
prompt = sys.argv[sys.argv.index("-p") + 1]
out = pathlib.Path(re.search(r"into (\\S+)/ ", prompt).group(1))
dirs = ["eval/situations", ".git"] + (["plugin"] if "Existing visible" in prompt else [])  # fresh mode must hide rules too
seen = sum(len(list(pathlib.Path(d).rglob("*"))) for d in dirs)
for i in range(int(re.search(r"exactly (\\d+)", prompt).group(1))):
    (out / f"s{i}.py").write_text('SITUATION = dict(category="b", rule="SECRET-RULE", files={"a": "a"}, prompt="p", oracle="o", check=lambda t: True)')
print(json.dumps({"result": "done", "modelUsage": {"m": {"inputTokens": seen}}}))
"""


@pytest.mark.skipif(not shutil.which("bwrap"), reason="bubblewrap needed")
def test_exam_writer_is_blind_and_quiet(tmp_path):
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    (bin_dir / "claude").write_text(FAKE); (bin_dir / "claude").chmod(0o755)
    out = tmp_path / "exam"
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}
    r = subprocess.run([sys.executable, str(EVAL / "make_holdout.py"), "--out", str(out)], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "used 0 tokens" in r.stdout  # fake reports how many visible files it could see: none
    assert "10/10 situations valid" in r.stdout and "SECRET-RULE" not in r.stdout and "s0" not in r.stdout
    r2 = subprocess.run([sys.executable, str(EVAL / "make_holdout.py"), "--out", str(out)], capture_output=True, text=True, env=env)
    assert r2.returncode != 0  # never overwrite an existing exam


@pytest.mark.skipif(not shutil.which("bwrap"), reason="bubblewrap needed")
def test_fresh_writer_is_blind_to_rules_too(tmp_path):
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    (bin_dir / "claude").write_text(FAKE); (bin_dir / "claude").chmod(0o755)
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}
    r = subprocess.run([sys.executable, str(EVAL / "make_holdout.py"), "--fresh", "--out", str(tmp_path / "f")],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "used 0 tokens" in r.stdout and "15/15 situations valid" in r.stdout  # saw no situations, git or plugin
