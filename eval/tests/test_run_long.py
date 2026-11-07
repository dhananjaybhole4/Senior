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
    monkeypatch.setattr(run_long, "PY38", Path(sys.executable))
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
    assert set(q["traps"]) == {"kept", "easy", "runs on Python 3.8"} and q["traps"]["kept"] == {"kind": "D6", "base": [True, True]}
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
    base_calls = [c for c in map(json.loads, calls(env)[n:]) if c[c.index("--model") + 1] == "sonnet" and "--plugin-dir" not in c]
    assert not base_calls  # stock runs of the qualify round reused
    l = json.loads((env / "l.json").read_text())
    p = l["projects"][0]
    assert l["senior_hash"] == "hash1"
    assert set(p["traps"]) == {"kept"} and set(p["guards"]) == {"easy", "later file", "runs on Python 3.8"}  # stock 2/2 -> guard
    assert set(p["tokens"]) == {"base", "senior"} and len(p["tokens"]["senior"]) == 2
    first = [json.loads(c) for c in calls(env)[n:] if "--plugin-dir" in c and '"first"' in c]
    assert len(first) == 2  # senior arm loads the plugin; the junior's first message is sent unchanged (hooks act alone)
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


def test_grader_change_regrades_saved_runs_without_model_calls(env, monkeypatch):
    main(monkeypatch, "qualify")
    n = len(calls(env))
    (env / "projects" / "toy.py").write_text(PROJECT.replace('"easy": (True, "")', '"easy": (False, "")'))
    monkeypatch.delitem(sys.modules, "toy")
    main(monkeypatch, "qualify")
    assert len(calls(env)) == n  # no new model calls
    q = json.loads((env / "q.json").read_text())["projects"][0]
    assert q["traps"]["easy"]["base"] == [False, False]
    (env / "projects" / "toy.py").write_text(PROJECT.replace('SCRIPT = ["first",', 'SCRIPT = ["changed",'))
    monkeypatch.delitem(sys.modules, "toy")
    main(monkeypatch, "qualify")
    assert len(calls(env)) > n  # what the model sees changed: real reruns


def test_senior_only_on_another_model_leaves_the_official_round_alone(env, monkeypatch):
    main(monkeypatch, "qualify")
    main(monkeypatch, "latest")
    before = {f.name: f.read_text() for f in [env / "l.json", *(env / "long_runs").iterdir()]}
    n = len(calls(env))
    main(monkeypatch, "latest", "--senior-only", "--model", "opus")
    new = [json.loads(c) for c in calls(env)[n:]]
    assistant = [c for c in new if c[c.index("--model") + 1] != "haiku"]
    assert assistant and all(c[c.index("--model") + 1] == "opus" and "--plugin-dir" in c for c in assistant)  # no stock reruns
    assert {f.name: f.read_text() for f in [env / "l.json", *(env / "long_runs").iterdir()] if f.name in before} == before
    p = json.loads((env / "l_opus.json").read_text())["projects"][0]
    assert set(p["tokens"]) == {"senior"} and len(p["tokens"]["senior"]) == 2
    m = len(calls(env))
    main(monkeypatch, "latest", "--senior-only", "--model", "opus")
    assert len(calls(env)) == m  # its own runs are reused


def test_exam_prints_counts_only_and_leaves_nothing(env, monkeypatch, capsys, tmp_path):
    import tempfile, exam
    sealed = tmp_path / "sealed"; sealed.mkdir()
    (sealed / "quiz.py").write_text(PROJECT.replace('"kept": (True, "")', '"kept": ((Path(d) / ".git" / "plugin-seen").exists(), "")'))  # stock slips on "kept", senior handles it
    monkeypatch.delitem(sys.modules, "quiz", raising=False)
    before = set(Path(tempfile.gettempdir()).glob("proj-*"))
    monkeypatch.setattr(sys, "argv", ["exam.py", str(sealed), "--cap", "100000", "--min-rate", "0.8", "--min-projects", "1"])
    with pytest.raises(SystemExit) as e:
        exam.main()
    out = capsys.readouterr()
    assert e.value.code == 0, out
    assert out.out.splitlines() == ["exam: 1/1 projects hold; traps stock slipped on 1, Senior handled 1; guards harmed 0; "
                                    "grader errors 0, runs stopped early 0",
                                    "METRIC exam_projects_held=1"]
    assert "quiz" not in out.out + out.err and "kept" not in out.out + out.err  # no exam names reach verify's output
    assert set(Path(tempfile.gettempdir()).glob("proj-*")) == before  # runs, logs, projects, results all deleted
    assert not any((env / n).exists() for n in ("runs", "long_runs", "q.json", "l.json", "proj-runs"))
    monkeypatch.setattr(sys, "argv", ["exam.py", str(sealed), "--cap", "100000", "--min-rate", "0.8", "--min-projects", "2"])
    with pytest.raises(SystemExit) as e:
        exam.main()
    assert e.value.code == 1  # 1 of 1 project holds, 2 needed


def test_exam_failure_names_nothing(env, monkeypatch, capsys, tmp_path):
    import exam
    sealed = tmp_path / "sealed"; sealed.mkdir()
    (sealed / "quiz.py").write_text(PROJECT)
    def boom(name, *a):
        raise RuntimeError(f"qualify_{name}_base_r0 turn 1 failed: usage limit")
    monkeypatch.setattr(run_long, "run_one", boom)
    monkeypatch.setattr(sys, "argv", ["exam.py", str(sealed), "--cap", "100000", "--min-rate", "0.8", "--min-projects", "1"])
    with pytest.raises(SystemExit) as e:
        exam.main()
    out = capsys.readouterr()
    assert "RuntimeError" in str(e.value.code) and "quiz" not in str(e.value.code) + out.out + out.err


def test_exam_graders_never_wait_on_the_owners_terminal(env, monkeypatch, capsys, tmp_path):
    """verify runs the exam from the owner's terminal: a built program asking for input must not hang grading."""
    import exam
    sealed = tmp_path / "sealed"; sealed.mkdir()
    (sealed / "quiz.py").write_text(PROJECT.replace('"kept": (True, "")', '"kept": ((Path(d) / ".git" / "plugin-seen").exists(), "")').replace('"easy": (True, ""),', '"easy": (__import__("subprocess").run([__import__("sys").executable, "-c", "input()"], timeout=5).returncode == 1, ""),'))
    r, w = os.pipe()  # a stdin that never ends, like an idle terminal
    saved = os.dup(0); os.dup2(r, 0)
    try:
        monkeypatch.setattr(sys, "argv", ["exam.py", str(sealed), "--cap", "100000", "--min-rate", "0.8", "--min-projects", "1"])
        with pytest.raises(SystemExit) as e:
            exam.main()
    finally:
        os.dup2(saved, 0); os.close(saved); os.close(r); os.close(w)
    assert e.value.code == 0, capsys.readouterr()


def exam_run(monkeypatch, capsys, sealed, code):
    import exam
    monkeypatch.delitem(sys.modules, "quiz", raising=False)  # each test seals its own version of the project
    monkeypatch.setattr(sys, "argv", ["exam.py", str(sealed), "--cap", "100000", "--min-rate", "0.8", "--min-projects", "1"])
    with pytest.raises(SystemExit) as e:
        exam.main()
    out = capsys.readouterr()
    assert e.value.code == code, (e.value.code, out)
    return str(e.value.code) + out.out + out.err


def test_exam_survives_crashing_graders_and_hung_calls(env, monkeypatch, capsys, tmp_path):
    sealed = tmp_path / "sealed"; sealed.mkdir()
    (sealed / "quiz.py").write_text(PROJECT.replace('SCRIPT = ["first", "second ROLE"]', 'SCRIPT = ["first", "second ROLE", "HANG"]')
                                    .replace("def grade(d):\n", "def grade(d):\n    if (Path(d) / '.senior').exists(): raise ValueError('bad state')\n")
                                    .replace('return (Path(d) / "a.txt")', 'assert not (Path(d) / ".senior").exists()\n    return (Path(d) / "a.txt")'))
    # crashes only on a state the model builds (fake ROLE writes .senior/), so the preflight on starting files passes
    monkeypatch.setattr(run_long.run, "TIMEOUT_S", 2)
    out = exam_run(monkeypatch, capsys, sealed, 1)  # graders failed -> traps failed -> project does not hold
    assert "exam: 0/1 projects hold" in out and "runs stopped early 4" in out  # all 4 runs (2 stock, 2 senior) hit HANG and "grader errors" in out
    assert "grader errors 0" not in out and "quiz" not in out and "bad state" not in out


def test_exam_preflight_stops_before_any_model_call(env, monkeypatch, capsys, tmp_path):
    sealed = tmp_path / "sealed"; sealed.mkdir()
    (sealed / "quiz.py").write_text(PROJECT.replace("SCRIPT = ", "SCRIPTS = "))  # broken: no SCRIPT
    out = exam_run(monkeypatch, capsys, sealed, "FAIL before any model call (0 tokens used): exam project 1 of 1 is broken (AttributeError)")
    assert not calls(env) and "quiz" not in out


def test_graded_program_that_waits_or_hangs_fails_instead_of_stopping(tmp_path):
    import _common
    (tmp_path / "ask.py").write_text("input()\n")
    (tmp_path / "loop.py").write_text("while True: pass\n")
    assert _common.py(tmp_path, "ask.py")[0] == 1  # no input: EOFError, not a wait on the terminal
    assert _common.py(tmp_path, "loop.py", timeout=1) == (-1, "timed out after 1s")


def test_exam_project_without_a_slipped_trap_does_not_hold(env, monkeypatch, capsys, tmp_path):
    sealed = tmp_path / "sealed"; sealed.mkdir()
    (sealed / "quiz.py").write_text(PROJECT)  # stock passes every trap: nothing for Senior to show (owner, Q1 b)
    assert "exam: 0/1 projects hold; traps stock slipped on 0" in exam_run(monkeypatch, capsys, sealed, 1)
