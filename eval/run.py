"""Test round: run each situation in fresh git repos under several arms, check behaviour, save results.

Arms: base = stock Claude · oracle = hand-written direction in the message · senior = plugin loaded.
Situation file (eval/situations/<id>.py) defines SITUATION = dict(category, rule, files, prompt, check,
  oracle?, history? = earlier junior turns, before_risky? = files committed after the history,
  after_commit? = files left uncommitted when the risky turn starts).
check(t) gets t = {tools, final, new_commits, branches, repo} for the risky turn (helpers: eval/sitlib.py).

python3 eval/run.py [--situations DIR] [--only ID ...] [--arms base senior] [--reps 3] [--model sonnet]
                    [--out eval/results/latest.json] [--max-tokens N] [--resume] [--summary-only --min-pass N]
Progress is saved to <out>.partial.json after every situation; stopping (Ctrl+C, kill, --max-tokens) keeps it.
--resume: continue a stopped round with the same settings, skipping situations already done.
--max-tokens: stop after the situation that takes the round past N tokens (all arms + history).
--summary-only: work in a temp dir that is deleted, write no results, print totals only.
"""
import argparse, importlib.util, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

EVAL = Path(__file__).resolve().parent
ROOT = EVAL.parent
sys.path.insert(0, str(EVAL))
sys.path.insert(0, str(ROOT / "harness" / "checks"))
from gate import PLUGIN, handled, plugin_hash  # one definition of "handled" and of the plugin hash
from sitlib import SAVEPOINT
from judge import judge

MAX_TURNS, TIMEOUT_S = 12, 600
BUILTIN_TOOLS = "Read Edit Write Glob Grep Bash"  # fewer tool definitions = smaller prompt, no subagent spawns
ALLOWED = "Read Edit Write Glob Grep Bash(git *) Bash(ls *) Bash(cat *) Bash(python -m pytest*) Bash(python3 -m pytest*)"
TOKEN_KEYS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
MODEL_USAGE_KEYS = ("inputTokens", "outputTokens", "cacheCreationInputTokens", "cacheReadInputTokens")


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, check=True).stdout


def write(d, files):
    for p, c in files.items():
        f = Path(d) / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(c)


def setup(d, sit):
    Path(d).mkdir(parents=True)
    write(d, sit["files"])
    git(d, "init", "-q", "-b", "main"); git(d, "config", "user.name", "junior"); git(d, "config", "user.email", "j@example.com")
    git(d, "add", "-A"); git(d, "commit", "-qm", "initial")


def load_situations(folder, only=None):
    sits = {}
    for f in sorted(Path(folder).glob("*.py")):
        spec = importlib.util.spec_from_file_location(f"situation_{f.stem}", f)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        sits[f.stem] = mod.SITUATION
    if only:
        missing = set(only) - set(sits)
        if missing:
            sys.exit(f"unknown situations: {sorted(missing)}")
        sits = {k: v for k, v in sits.items() if k in only}
    if not sits:
        sys.exit(f"no situations in {folder}")
    return sits


def parse(stdout, where):
    """stream-json -> ({tools, final}, total tokens over all models, session_id)."""
    tools, result = [], None
    for line in stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            tools += [{"name": c["name"], "input": c.get("input", {})} for c in ev["message"]["content"] if c.get("type") == "tool_use"]
        if ev.get("type") == "result":
            result = ev
    if result is None:
        raise RuntimeError(f"{where}: no result event; see its .log")
    # modelUsage covers every model the session used (e.g. a small helper model); usage only the main one
    if result.get("modelUsage"):
        tok = sum(m.get(k, 0) for m in result["modelUsage"].values() for k in MODEL_USAGE_KEYS)
    else:
        tok = sum(result.get("usage", {}).get(k, 0) for k in TOKEN_KEYS)
    return {"tools": tools, "final": result.get("result")}, tok, result.get("session_id")


def claude(d, msg, model, arm=None, resume=None, fork=False):
    cmd = ["claude", "-p", msg, "--model", model, "--setting-sources", "project,local", "--strict-mcp-config",
           "--tools", BUILTIN_TOOLS, "--max-turns", str(MAX_TURNS), "--permission-mode", "acceptEdits",
           "--allowedTools", ALLOWED, "--output-format", "stream-json", "--verbose"]
    if resume:
        cmd += ["--resume", resume] + (["--fork-session"] if fork else [])
    elif fork:  # a risky turn with no history: nothing to resume, nothing to keep
        cmd += ["--no-session-persistence"]
    if arm == "senior":
        cmd += ["--plugin-dir", str(PLUGIN)]
    p = subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    return p.stdout + "\n#STDERR\n" + p.stderr


def message(sit, arm):
    if arm == "oracle":
        return f"<senior-direction>{sit['oracle']}</senior-direction>\n\n{sit['prompt']}"
    return sit["prompt"]


def role_usage(d):  # tokens of role processes started by the plugin (scripts/role.py appends here)
    f = Path(d) / ".senior" / "usage.jsonl"
    return [json.loads(l)["tokens"] for l in f.read_text().splitlines()] if f.exists() else []


def observe(d, out, where, roles_before):
    t, tok, _ = parse(out, where)
    tok += sum(role_usage(d)[roles_before:])
    t["new_commits"] = int(git(d, "rev-list", "--count", "HEAD")) - int(git(d, "rev-list", "--count", SAVEPOINT))
    t["branches"] = len([b for b in git(d, "branch", "--format=%(refname:short)").split() if b != SAVEPOINT])
    t["repo"] = Path(d)
    return t, tok


def session_dir(d):  # where claude stores sessions for cwd d (only history runs persist sessions)
    return Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(Path(d).resolve()))


def build_history(d, sit, model, work, log, arm):
    """Fresh repo + earlier junior turns (plugin loaded for the senior arm) + save point. Returns (session, tokens)."""
    shutil.rmtree(d, ignore_errors=True); shutil.rmtree(session_dir(d), ignore_errors=True)  # leftovers of a stopped run
    setup(d, sit)
    session, tok = None, 0
    for i, turn in enumerate(sit.get("history", [])):
        out = claude(d, turn, model, arm, resume=session)
        (work / f"{log}.hist{i}.log").write_text(out)
        _, t, session = parse(out, f"{log}.hist{i}")
        tok += t
    write(d, sit.get("before_risky", {}))
    git(d, "add", "-A"); git(d, "commit", "-qm", SAVEPOINT, "--allow-empty")
    git(d, "branch", SAVEPOINT)
    return session, tok


def group_of(arm):
    return "senior" if arm == "senior" else "stock"


def run_situation(sid, sit, arms, reps, model, work, quiet=False):
    """Returns ({arm: [(passed, tokens)]}, {group: history tokens}). History is built once per group
    (stock: base + oracle, senior: plugin loaded) and forked for every run of that group."""
    res, hist, questions, judge_tok = {}, {}, [], 0
    for arm in arms:
        d = work / sid / group_of(arm)
        if group_of(arm) not in hist:
            hist[group_of(arm)] = build_history(d, sit, model, work, f"{sid}.{group_of(arm)}", arm if arm == "senior" else None)
        session = hist[group_of(arm)][0]
        res[arm] = []
        for rep in range(reps):
            git(d, "checkout", "-qf", "main"); git(d, "reset", "-q", "--hard", SAVEPOINT); git(d, "clean", "-qfdx")
            for b in git(d, "branch", "--format=%(refname:short)").split():
                if b not in ("main", SAVEPOINT):
                    git(d, "branch", "-qD", b)
            write(d, sit.get("after_commit", {}))
            roles_before = len(role_usage(d))
            out = claude(d, message(sit, arm), model, arm, resume=session, fork=True)
            name = f"{sid}.{arm}.{rep}"
            (work / f"{name}.log").write_text(out)
            t, tok = observe(d, out, name, roles_before)
            res[arm].append((bool(sit["check"](t)), tok))
            if arm == "senior" and "?" in (t["final"] or ""):  # SPEC #6 grades Senior's questions only
                verdicts, jt = judge(sit["prompt"], t["final"], d)
                questions += [{"run": name, **v} for v in verdicts]; judge_tok += jt
            if not quiet:
                print(f"  {name}: {'pass' if res[arm][-1][0] else 'FAIL'} {tok} tok", flush=True)
    for group in hist:
        shutil.rmtree(session_dir(work / sid / group), ignore_errors=True)  # test sessions would pollute log mining
    return res, {g: tok for g, (_, tok) in hist.items()}, questions, judge_tok


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--situations", default=str(EVAL / "situations"))
    a.add_argument("--only", nargs="+")
    a.add_argument("--arms", nargs="+", default=["base", "senior"], choices=["base", "oracle", "senior"])
    a.add_argument("--reps", type=int, default=3)
    a.add_argument("--model", default="sonnet")
    a.add_argument("--out", default=str(EVAL / "results" / "latest.json"))
    a.add_argument("--summary-only", action="store_true")
    a.add_argument("--min-pass", type=int)
    a.add_argument("--max-tokens", type=int)
    a.add_argument("--resume", action="store_true")
    x = a.parse_args()
    if "senior" in x.arms and not PLUGIN.is_dir():
        sys.exit(f"arm 'senior' needs {PLUGIN}")
    sits = load_situations(x.situations, x.only)
    senior_hash = plugin_hash() if PLUGIN.is_dir() else None
    work = Path(tempfile.mkdtemp(prefix="senior-eval-")) if x.summary_only else EVAL / "runs" / Path(x.out).stem
    out = Path(x.out); partial = out.with_suffix(".partial.json")
    header = {"senior_hash": senior_hash, "model": x.model, "reps": x.reps, "arms": x.arms}
    rows = []
    if x.resume:
        if not partial.exists():
            sys.exit(f"nothing to resume: {partial} does not exist")
        saved = json.loads(partial.read_text())
        if {k: saved.get(k) for k in header} != header:
            sys.exit(f"cannot resume: settings or plugin differ from the stopped round ({partial})")
        rows = saved["situations"]
    elif not x.summary_only:
        shutil.rmtree(work, ignore_errors=True); partial.unlink(missing_ok=True)
    if not x.summary_only:
        work.mkdir(parents=True, exist_ok=True); out.parent.mkdir(parents=True, exist_ok=True)
    done = {r["id"] for r in rows}
    used = 0
    try:
        for sid, sit in sits.items():
            if sid in done:
                continue
            if x.max_tokens is not None and used >= x.max_tokens:
                print(f"STOPPED: token limit {x.max_tokens} reached ({used} used); continue with --resume")
                sys.exit(2)
            if not x.summary_only:
                print(sid, flush=True)
            res, hist, questions, judge_tok = run_situation(sid, sit, x.arms, x.reps, x.model, work, x.summary_only)
            # an arm's tokens = its risky-turn runs + its group's history (all processes counted, SPEC #5)
            row = {"id": sid, "category": sit["category"], "rule": sit["rule"], "history_tokens": hist,
                   "judge_tokens": judge_tok, "questions": questions}
            for arm, runs in res.items():
                row[f"{arm}_passes"] = [p for p, _ in runs]
                row[f"{arm}_tokens"] = sum(t for _, t in runs) + hist[group_of(arm)]
            rows.append(row)
            used += sum(hist.values()) + judge_tok + sum(t for runs in res.values() for _, t in runs)
            if not x.summary_only:
                partial.write_text(json.dumps({**header, "situations": rows}, indent=1))
    finally:
        if x.summary_only:
            shutil.rmtree(work, ignore_errors=True)
    summary = {arm: sum(handled(r[f"{arm}_passes"]) for r in rows) for arm in x.arms}
    tokens = {arm: sum(r[f"{arm}_tokens"] for r in rows) for arm in x.arms}
    for arm in x.arms:
        print(f"{arm}: {summary[arm]}/{len(rows)} handled, {tokens[arm]} tokens")
    if not x.summary_only:
        final = {**header, "situations": rows}
        if "senior" in x.arms:  # gate input for SPEC #6; per-question verdicts stay in each row
            qs = [q for r in rows for q in r["questions"]]
            final["questions"] = {"total": len(qs), "good": sum(q["good"] for q in qs)}
        out.write_text(json.dumps(final, indent=1))
        partial.unlink()
        print(f"saved {out}; logs in {work}")
    if x.min_pass is not None:
        target = "senior" if "senior" in x.arms else x.arms[-1]
        ok = summary[target] >= x.min_pass
        print(f"HOLDOUT {'PASS' if ok else 'FAIL'} ({target} {summary[target]}/{len(rows)}, need {x.min_pass})")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
