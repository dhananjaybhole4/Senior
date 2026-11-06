"""Long-project round runner (fake claude, no tokens): gate format, qualify -> guards, resume, senior-only rerun."""
import json, os, sys
from pathlib import Path

import pytest

EVAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVAL / "longrun"))
sys.path.insert(0, str(EVAL.parent / "harness" / "checks"))
import run_long, gate

PROJECT = '''from pathlib import Path
FILES = {"a.txt": "a\\n"}
LATER_FILES = {1: {"b.txt": "b\\n"}}
NEW_SESSION_AT = 1
WORLD = "You are Kim."
SCRIPT = ["first", "second ROLE"]
TRAPS = {"kept": "D6", "easy": "D1"}
def rules_kept(d):
    return (Path(d) / "a.txt").read_text() == "a\\n"
def grade(d):
    return {"kept": (True, ""), "easy": (True, ""), "later file": ((Path(d) / "b.txt").exists(), "")}
'''


@pytest.fixture
def env(tmp_path, monkeypatch):
    projects = tmp_path / "projects"; projects.mkdir()
    (projects / "toy.py").write_text(PROJECT)
    monkeypatch.syspath_prepend(str(projects))
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    (bin_dir / "claude").symlink_to(EVAL / "tests" / "fake_claude.py")
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_LOG", str(tmp_path / "argv.log"))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    plugin = tmp_path / "plugin"; plugin.mkdir()
    r = run_long.run
    monkeypatch.setattr(r, "PLUGIN", plugin)
    monkeypatch.setattr(r, "plugin_hash", lambda: "hash1")
    monkeypatch.setattr(r, "RUNS", tmp_path / "runs")
    monkeypatch.setattr(r, "PROJECTS", tmp_path / "proj-runs")
    monkeypatch.setattr(run_long, "PROJECTS", projects)
    monkeypatch.setattr(run_long, "RUNS_OUT", tmp_path / "long_runs")
    monkeypatch.setattr(run_long, "QUALIFY", tmp_path / "q.json")
    monkeypatch.setattr(run_long, "LONG", tmp_path / "l.json")
    return tmp_path


def main(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["run_long.py", *args, "--cap", "100000", "--projects", "toy"])
    run_long.main()


def calls(tmp):
    return (tmp / "argv.log").read_text().splitlines() if (tmp / "argv.log").exists() else []


def test_latest_needs_an_earlier_qualify_round(env, monkeypatch):
    with pytest.raises(SystemExit, match="qualify round first"):
        main(monkeypatch, "latest")


def test_round_writes_gate_format_and_reuses_runs(env, monkeypatch):
    main(monkeypatch, "qualify")
    q = json.loads((env / "q.json").read_text())["projects"][0]
    assert set(q["traps"]) == {"kept", "easy"} and q["traps"]["kept"] == {"kind": "D6", "base": [True, True]}
    assert q["guards"] == {"later file": {"base": [True, True]}}  # LATER_FILES written before request 2
    assert q["rule_breaks"]["base"] == [0, 0] and all(t > 0 for t in q["weighted"]["base"])
    turns = json.loads((env / "long_runs" / "qualify_toy_base_r0.json").read_text())["turns"]
    assert [t["tokens"] for t in turns if "ROLE" not in t["junior"]] == [16] * (len(turns) - 1)  # per call, never the resumed session's running total
    asked = [json.loads(c) for c in calls(env)]
    asked = [c for c in asked if c[c.index("--model") + 1] == "sonnet"]
    assert all("--resume" not in c for c in asked if c[c.index("-p") + 1] == "second ROLE")  # fresh session there
    assert any("--resume" in c for c in asked if c[c.index("-p") + 1] not in ("first", "second ROLE"))  # follow-ups resume
    n = len(calls(env))
    main(monkeypatch, "qualify")
    assert len(calls(env)) == n  # finished runs reused: no new model calls

    # make "kept" a trap stock slipped on, so the official round must keep it as a trap
    data = json.loads((env / "q.json").read_text())
    data["projects"][0]["traps"]["kept"]["base"] = [False, True]
    (env / "q.json").write_text(json.dumps(data))
    main(monkeypatch, "latest")
    l = json.loads((env / "l.json").read_text())
    p = l["projects"][0]
    assert l["senior_hash"] == "hash1"
    assert set(p["traps"]) == {"kept"} and set(p["guards"]) == {"easy", "later file"}  # stock 2/2 -> guard
    assert set(p["tokens"]) == {"base", "senior"} and len(p["tokens"]["senior"]) == 2
    first = [json.loads(c) for c in calls(env)[n:] if "--plugin-dir" in c and "/senior:senior first" in c]
    assert len(first) == 2  # senior arm starts the plugin's command, once per run
    roles = json.loads((env / "long_runs" / "latest_toy_senior_r0.json").read_text())["turns"]
    assert any(t["tokens"] >= 100 for t in roles)  # role-process tokens counted on the turn that started them

    # plugin change: only senior reruns
    monkeypatch.setattr(run_long.run, "plugin_hash", lambda: "hash2")
    m = len(calls(env))
    main(monkeypatch, "latest")
    new = [json.loads(c) for c in calls(env)[m:]]
    assistant = [c for c in new if c[c.index("--model") + 1] == "sonnet"]  # the junior runs on haiku
    assert assistant and all("--plugin-dir" in c for c in assistant)
    sys.argv = ["gate.py", "long", "--min-rate", "0.8", "--max-rule-breaks", "0", "--max-regressions", "0", "--max-ratio", "9"]
    monkeypatch.setattr(gate, "LONG", env / "l.json"); monkeypatch.setattr(gate, "QUALIFY", env / "q.json")
    monkeypatch.setattr(gate, "plugin_hash", lambda: "hash2")
    with pytest.raises(SystemExit) as e:
        gate.main()
    assert e.value.code == 0  # the runner's output is what the gate reads


def test_error_turn_stops_the_run_and_saves_nothing(env, monkeypatch):
    monkeypatch.setattr(run_long, "failed", lambda out: "usage limit")
    with pytest.raises(RuntimeError, match="run invalid"):
        main(monkeypatch, "qualify")
    assert not list((env / "long_runs").glob("*.json"))
