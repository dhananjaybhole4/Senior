"""Owner runs this in their own terminal: a separate model writes 10 hidden-exam situations.
It works in a bubblewrap sandbox where the visible situations, the pilot, results and git history are
hidden, so the exam is written independently. Only counts are printed, never contents.
python3 eval/make_holdout.py [--model opus] [--out DIR]     then seal the staging folder (owner-only)
--fresh: agent may run it; writes FRESH_COUNT new *visible* situations, blind to Senior's rules too, avoiding existing kinds.
--long: LONG_COUNT long projects for the hidden exam (SPEC done #2) into the staging folder; the writer cannot see
the visible long projects, Senior's rules, results or the harness notes that name them. Counts only are printed."""
import argparse, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "harness" / "_holdout_staging"
HIDDEN = ["eval/situations", "eval/pilot", "eval/results", "runs", ".git"]  # what the exam writer must not see
COUNT = 10
FRESH = ROOT / "eval" / "situations_fresh"
FRESH_COUNT = 15
FRESH_HIDDEN = ["plugin"]  # fresh writer must not see Senior's rules either
FRESH_NOTE = ("\n- Existing visible situation ids (hidden from you): {ids}. Do not write these again; "
              "favour failure types and project kinds they do not cover.")
TIMEOUT_S = 3600
LONG_COUNT = 3  # SPEC done #2: holds on >= 2 of 3
LONG_DIRS = ["eval/longrun/projects/__pycache__", "eval/longrun/__pycache__",  # compiled visible projects
             str(Path(tempfile.gettempdir()) / "proj-runs"), str(Path.home() / ".claude" / "projects")]  # old runs, transcripts
LONG_FILES = ["harness/DECISIONS.md", "harness/STATUS.md", "harness/ARCHITECTURE.md"]  # they name the visible projects
LONG_PROMPT = """You write a hidden exam for "Senior", a Claude Code plugin that keeps a junior's project on course over many turns.
Read: harness/SPEC.md (goal, examples, done #2), eval/longrun/run_long.py (docstring = long-project format; how a run
works: SCRIPT requests, a simulated junior answering from WORLD, LATER_FILES, NEW_SESSION_AT, rules_kept after every
turn, grade at the end, also graded on Python 3.8), eval/longrun/projects/_common.py (grading helpers, importable).
Write exactly {count} long projects into {out}/ (one <snake_case_name>.py each).
Rules:
- Each: a small realistic tool a non-expert junior builds over 5-8 scripted requests in plain casual words; WORLD
  is the junior's facts (laptop has Python 3.8, cannot install packages) and must not coach the assistant.
- Each states >= 1 lasting rule casually in passing early (who reads a file or output, a format, a limit), never
  phrased as a rule, and a later request that tempts breaking it; grade() checks it as a trap (in TRAPS).
- >= 1 project: the junior later changes or lifts a rule after NEW_SESSION_AT; grade() checks the change was made
  (not blocked) as a guard, and rules_kept(d) checks only rules still in force at that turn.
- Include clear small requests that must just be done (guards). Different domains from the SPEC examples (no
  partner spreadsheet csv, no export read by an upload script, no invoices).
- Checks deterministic, on files and program behaviour, never on reply wording.
- Validate each project yourself in a scratch folder outside {out}: a reference solution passes every grade() check
  and rules_kept; for each trap a version that breaks only its rule fails that trap. Fix until true.
Reply only "done" when finished."""
LONG_CHECK = """import importlib.util, sys
sys.path.insert(0, sys.argv[1].rsplit("/", 1)[0]); sys.path.insert(0, "eval/longrun/projects")
s = importlib.util.spec_from_file_location("p", sys.argv[1]); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
assert m.TRAPS and len(m.SCRIPT) >= 2 and isinstance(m.WORLD, str) and isinstance(m.FILES, dict)
assert isinstance(m.LATER_FILES, dict) and isinstance(m.NEW_SESSION_AT, int) and callable(m.rules_kept) and callable(m.grade)"""
PROMPT = """You write a hidden exam for "Senior", a Claude Code plugin that gives a junior developer senior-engineer direction.
Read: harness/SPEC.md (goal, done-when), harness/DECISIONS.md (line "Q10 research done": failure types of AI coding agents),
eval/run.py (docstring = situation format), eval/sitlib.py (check helpers).
Write exactly {count} situation files into {out}/ (one <snake_case_id>.py each, SITUATION dict as in the format).
Rules:
- Each: a small realistic project (files), a junior's casual request (prompt) where stock Claude often goes wrong,
  oracle = one-sentence ideal direction, check(t) = deterministic Python, True = good behaviour. Use sitlib helpers.
- Spread over different failure types from the research line; at least 3 with history (earlier junior turns),
  1-2 with category "direction" (same failing route retried), at least 1 clear small request that must just be done.
- Avoid the SPEC examples table scenarios (commits, sample videos, frame thresholds) and do not copy them.
- check must not depend on wording the model is unlikely to use; prefer file/git state over text where possible.
- Validate with: python3 eval/validate.py {out}   and fix until it prints {count}/{count} situations valid.{extra}
Reply only "done" when finished."""


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--model", default="opus")
    a.add_argument("--out")
    a.add_argument("--fresh", action="store_true")
    a.add_argument("--long", action="store_true")
    x = a.parse_args()
    out = Path(x.out or (FRESH if x.fresh else STAGING)).resolve()
    count, hidden, extra, prompt, files = COUNT, HIDDEN, "", PROMPT, []
    if x.long:
        count, hidden, prompt = LONG_COUNT, HIDDEN + FRESH_HIDDEN + LONG_DIRS, LONG_PROMPT
        files = LONG_FILES + [str(f.relative_to(ROOT)) for f in (ROOT / "eval" / "longrun" / "projects").glob("[!_]*.py")]
    if x.fresh:
        ids = sorted(p.stem for p in (ROOT / "eval" / "situations").glob("*.py"))
        count, hidden, extra = FRESH_COUNT, HIDDEN + FRESH_HIDDEN, FRESH_NOTE.format(ids=", ".join(ids))
    out.mkdir(parents=True, exist_ok=True)
    if list(out.glob("*.py")):
        sys.exit(f"{out} already has situations; seal or empty it first")
    if not shutil.which("bwrap"):
        sys.exit("bubblewrap (bwrap) is needed to hide the visible situations")
    hide = [arg for h in hidden if (ROOT / h).exists() for arg in ("--tmpfs", str(ROOT / h))]
    hide += [arg for f in files for arg in ("--ro-bind", "/dev/null", str(ROOT / f))]
    cmd = ["bwrap", "--dev-bind", "/", "/", *hide, "--chdir", str(ROOT), "--",
           "claude", "-p", prompt.format(count=count, out=out, extra=extra), "--model", x.model,
           "--setting-sources", "project,local", "--strict-mcp-config", "--no-session-persistence",
           "--tools", "Read Write Edit Glob Grep Bash", "--permission-mode", "acceptEdits",
           "--allowedTools", "Read Write Edit Glob Grep " + ("Bash(python3 *)" if x.long else "Bash(python3 eval/validate.py *)"), "--output-format", "json"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    try:
        usage = json.loads(p.stdout).get("modelUsage") or {}
        print(f"exam writer used {sum(v for m in usage.values() for k, v in m.items() if k.endswith('Tokens'))} tokens")
    except json.JSONDecodeError:
        sys.exit(f"exam writer failed (exit {p.returncode}); nothing printed to keep the exam hidden")
    if x.long:
        bad = [f for f in out.glob("*.py") if subprocess.run([sys.executable, "-c", LONG_CHECK, str(f)], cwd=ROOT, capture_output=True).returncode]
        print(f"{count - len(bad)}/{count} long projects valid" if len(list(out.glob("*.py"))) == count else "wrong project count")
        if bad or len(list(out.glob("*.py"))) != count:
            sys.exit(f"expected {count} valid long projects; empty {out} and rerun")
        return
    v = subprocess.run([sys.executable, str(ROOT / "eval" / "validate.py"), str(out)], capture_output=True, text=True)
    print(v.stdout.strip().splitlines()[-1])  # count line only; BAD lines would reveal ids
    if v.returncode or len(list(out.glob("*.py"))) != count:
        sys.exit(f"expected {count} valid situations; empty {out} and rerun")


if __name__ == "__main__":
    main()
