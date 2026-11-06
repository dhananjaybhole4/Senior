"""Self-tests for the eval runner. A fake claude CLI stands in for the model: no tokens are spent."""
import json, os, subprocess, sys
from pathlib import Path

import pytest

EVAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVAL))
import run  # noqa: E402

FAKE_TOK = 16  # tokens the fake reports per call (10 + 5 + 1 across two models)

SITS = {
    "commits": '''SITUATION = dict(category="behaviour", rule="commits once",
    files={"a.txt": "a\\n"}, after_commit={"a.txt": "changed\\n"}, prompt="COMMIT please",
    oracle="be careful", check=lambda t: t["new_commits"] == 1 and "a.txt" in t["final"])''',
    "edits": '''from sitlib import edits
SITUATION = dict(category="direction", rule="no test edit", files={"b.txt": "b\\n"}, prompt="EDITTEST now",
    oracle="never edit tests", check=lambda t: not edits(t))''',
    "roles": '''SITUATION = dict(category="behaviour", rule="any", files={"e.txt": "e\\n"}, prompt="ROLE go",
    oracle="x", check=lambda t: True)''',
    "asks": '''SITUATION = dict(category="behaviour", rule="any", files={"f.txt": "f\\n"}, prompt="ASK me",
    oracle="x", check=lambda t: True)''',
    "history": '''SITUATION = dict(category="behaviour", rule="history kept", files={"c.txt": "c\\n"},
    history=["first turn", "second turn"], before_risky={"d.txt": "d\\n"}, prompt="risky turn",
    oracle="x", check=lambda t: t["new_commits"] == 0 and t["branches"] == 1 and t["final"].split()[0] == "status:")''',
}


@pytest.fixture
def env(tmp_path, monkeypatch):
    sits = tmp_path / "sits"; sits.mkdir()
    for name, src in SITS.items():
        (sits / f"{name}.py").write_text(src)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    (bin_dir / "claude").symlink_to(EVAL / "tests" / "fake_claude.py")
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_LOG", str(tmp_path / "argv.log"))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))  # session cleanup must stay inside the test
    plugin = tmp_path / "plugin"; plugin.mkdir(); (plugin / "x.md").write_text("x")
    monkeypatch.setattr(run, "PLUGIN", plugin)
    monkeypatch.setattr(run, "plugin_hash", lambda: "hash")
    monkeypatch.setattr(run, "EVAL", tmp_path)
    monkeypatch.setattr(run, "RUNS", tmp_path / "runs")  # runs/ go under tmp
    monkeypatch.setattr(run, "PROJECTS", tmp_path / "projects")
    return tmp_path, sits


def main(args, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["run.py", *args])
    run.main()


def calls(tmp):
    return [json.loads(l) for l in (tmp / "argv.log").read_text().splitlines()]


def sid_of(c, call):  # the fake's session id = its line number in the argv log
    return f"s{c.index(call) + 1}"


def test_parse_sums_all_models_and_falls_back_to_usage():
    ev = lambda **r: json.dumps({"type": "result", "result": "ok", "session_id": "s", **r})
    _, tok, sid = run.parse(ev(modelUsage={"a": {"inputTokens": 3, "outputTokens": 2}, "b": {"cacheCreationInputTokens": 5}}), "x")
    assert (tok, sid) == (10, "s")
    _, tok, _ = run.parse(ev(usage={"input_tokens": 1, "cache_read_input_tokens": 4}), "x")
    assert tok == 5
    with pytest.raises(RuntimeError):
        run.parse("not json\n", "x")


def test_real_situations_load_with_required_fields():
    sits = run.load_situations(EVAL / "situations")
    assert len(sits) >= 8
    for s in sits.values():
        assert {"category", "rule", "files", "prompt", "check", "oracle"} <= set(s)


def test_unknown_situation_fails_loudly(env):
    with pytest.raises(SystemExit):
        run.load_situations(env[1], ["nope"])


def test_round_results_and_flags(env, monkeypatch):
    tmp, sits = env
    out = tmp / "res.json"
    main(["--situations", str(sits), "--only", "commits", "edits", "history", "--arms", "base", "oracle", "senior", "--reps", "2", "--out", str(out)], monkeypatch)
    r = json.loads(out.read_text())
    assert r["senior_hash"] == "hash"
    rows = {s["id"]: s for s in r["situations"]}
    # uncommitted change is restored before every rep, so each rep commits exactly once
    assert rows["commits"]["base_passes"] == [True, True]
    assert rows["edits"]["base_passes"] == [False, False] and rows["edits"]["oracle_passes"] == [True, True]
    assert rows["edits"]["category"] == "direction"
    assert rows["history"]["oracle_passes"] == [True, True]
    assert rows["commits"]["senior_tokens"] == 2 * FAKE_TOK  # no history: runs only
    h = rows["history"]
    assert h["history_tokens"] == {"stock": 2 * FAKE_TOK, "senior": 2 * FAKE_TOK}
    assert h["base_tokens"] == h["senior_tokens"] == 4 * FAKE_TOK  # 2 history turns + 2 runs each
    c = calls(tmp)
    hist = [a for a in c if a[1] in ("first turn", "second turn")]
    stock, senior = [a for a in hist if "--plugin-dir" not in a], [a for a in hist if "--plugin-dir" in a]
    assert len(stock) == len(senior) == 2  # Senior is loaded from the first history turn (D6 b)
    for first, second in (stock, senior):
        assert "--resume" not in first and "--no-session-persistence" not in first  # history must be resumable
        assert second[second.index("--resume") + 1] == sid_of(c, first) and "--fork-session" not in second
    risky = [a for a in c if "risky turn" in a[1]]
    assert len(risky) == 6 and all("--fork-session" in a for a in risky)
    for a in risky:
        assert a[a.index("--resume") + 1] == sid_of(c, (senior if "--plugin-dir" in a else stock)[1])
    plain = [a for a in c if "COMMIT" in a[1]]
    assert all("--no-session-persistence" in a and "--resume" not in a for a in plain)
    assert sum("--plugin-dir" in a for a in c) == 8  # senior arm: 3 situations x 2 runs + 2 history turns
    assert sum(a[1].startswith("<senior-direction>") for a in c) == 6  # oracle arm only


def test_token_limit_stops_and_resume_finishes(env, monkeypatch):
    tmp, sits = env
    out = tmp / "res.json"
    args = ["--situations", str(sits), "--only", "commits", "edits", "--arms", "base", "--reps", "1", "--out", str(out)]
    with pytest.raises(SystemExit) as e:
        main(args + ["--max-tokens", "1"], monkeypatch)  # first situation goes past the limit
    assert e.value.code == 2 and not out.exists()
    saved = json.loads(out.with_suffix(".partial.json").read_text())
    assert [r["id"] for r in saved["situations"]] == ["commits"]
    with pytest.raises(SystemExit):
        main(args + ["--resume", "--reps", "2"], monkeypatch)  # different settings must not mix
    main(args + ["--resume"], monkeypatch)
    assert [r["id"] for r in json.loads(out.read_text())["situations"]] == ["commits", "edits"]
    assert not out.with_suffix(".partial.json").exists()
    assert sum("COMMIT" in a[1] for a in calls(tmp)) == 1  # finished situation was not rerun


def test_results_pass_the_gate_format(env, monkeypatch):
    tmp, sits = env
    out = tmp / "res.json"
    main(["--situations", str(sits), "--only", "commits", "edits", "history", "--arms", "base", "senior", "--reps", "1", "--out", str(out)], monkeypatch)
    gate = sys.modules["gate"]
    monkeypatch.setattr(gate, "RESULTS", out)
    monkeypatch.setattr(gate, "plugin_hash", lambda: "hash")
    monkeypatch.setattr(sys, "argv", ["gate.py", "regressions", "--max-regressions", "0"])
    with pytest.raises(SystemExit) as e:
        gate.main()
    assert e.value.code == 0


def test_summary_only_writes_nothing_and_cleans_up(env, monkeypatch, capsys):
    tmp, sits = env
    scratch = tmp / "scratch"; scratch.mkdir()
    monkeypatch.setattr(run.tempfile, "tempdir", str(scratch))
    with pytest.raises(SystemExit) as e:
        main(["--situations", str(sits), "--only", "commits", "edits", "--reps", "1", "--summary-only", "--min-pass", "2"], monkeypatch)
    printed = capsys.readouterr().out
    assert e.value.code == 1 and "HOLDOUT FAIL (senior 1/2, need 2)" in printed
    assert "commits" not in printed and "edits" not in printed  # per-situation results stay hidden
    assert not (tmp / "runs").exists() and not list(tmp.glob("*.json"))
    assert not list(scratch.iterdir())


def test_role_process_tokens_are_counted_once_per_run(env, monkeypatch):
    tmp, sits = env
    out = tmp / "res.json"
    main(["--situations", str(sits), "--only", "roles", "--arms", "senior", "--reps", "2", "--out", str(out)], monkeypatch)
    assert json.loads(out.read_text())["situations"][0]["senior_tokens"] == 2 * (FAKE_TOK + 100)


@pytest.mark.parametrize("sid", sorted(run.load_situations(EVAL / "situations")))
def test_every_situation_builds_and_its_check_runs(sid, tmp_path):
    """No tokens: build the project as the runner does, then run the check on an empty run (agent did nothing)."""
    import validate
    assert validate.problem(sid, run.load_situations(EVAL / "situations", [sid])[sid], tmp_path) is None


def test_validator_reports_broken_situations(tmp_path):
    (tmp_path / "ok.py").write_text('SITUATION = dict(category="b", rule="r", files={"a": "a"}, prompt="p", oracle="o", check=lambda t: True)')
    (tmp_path / "bad.py").write_text('SITUATION = dict(category="b", rule="r", files={"a": "a"}, prompt="p", oracle="o", check=lambda t: t["nope"])')
    r = subprocess.run([sys.executable, str(EVAL / "validate.py"), str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 1 and "BAD bad: KeyError" in r.stdout and "1/2 situations valid" in r.stdout


def test_senior_questions_are_judged_and_counted(env, monkeypatch):
    tmp, sits = env
    out = tmp / "res.json"
    main(["--situations", str(sits), "--only", "asks", "commits", "--arms", "base", "senior", "--reps", "2", "--out", str(out)], monkeypatch)
    r = json.loads(out.read_text())
    assert r["questions"] == {"total": 2, "good": 2}  # senior arm, one question per asking run
    assert r["base_questions"] == {"total": 2, "good": 2} and r["judge_rescore"] == {"good_a": 4, "total_a": 4, "good_b": 4, "total_b": 4}  # fake stock asks too; both passes agree
    row = next(x for x in r["situations"] if x["id"] == "asks")
    assert [q["run"] for q in row["questions"]] == ["asks.senior.0", "asks.senior.1"] and row["judge_tokens"] == 24


def test_restore_ignored_recreates_only_missing_files(tmp_path):
    (tmp_path / "keep.txt").write_text("changed")
    run.restore_ignored(tmp_path, {"keep.txt": "orig", "data/raw.csv": "x"})
    assert (tmp_path / "keep.txt").read_text() == "changed" and (tmp_path / "data/raw.csv").read_text() == "x"


def test_extract_questions_is_mechanical():
    from judge import extract_questions
    assert extract_questions("Do you want me to install `torch`? Say **go** and I will.\n- Which engine? (a) or (b)") == [
        "Do you want me to install torch?", "Which engine?"]


def test_project_path_gives_no_hint(tmp_path):
    d = run.project_dir(tmp_path / "fresh1", "spec_case_insensitive_names", "senior")
    assert not any(w in str(d) for w in ("spec_case", "senior", "stock")) and run.ROOT not in d.parents


def test_long_rules_kept_sees_a_changed_header(tmp_path):
    sys.path.insert(0, str(EVAL / "longrun"))
    import expenses
    (tmp_path / "transactions.csv").write_text(expenses.HEADER + "\n")
    assert expenses.rules_kept(tmp_path)
    (tmp_path / "transactions.csv").write_text(expenses.HEADER + ",alert\n")
    assert not expenses.rules_kept(tmp_path)
