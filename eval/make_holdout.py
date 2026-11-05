"""Owner runs this in their own terminal: a separate model writes 10 hidden-exam situations.
It works in a bubblewrap sandbox where the visible situations, the pilot, results and git history are
hidden, so the exam is written independently. Only counts are printed, never contents.
python3 eval/make_holdout.py [--model opus] [--out DIR]     then seal the staging folder (owner-only)"""
import argparse, json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "harness" / "_holdout_staging"
HIDDEN = ["eval/situations", "eval/pilot", "eval/results", "eval/runs", ".git"]  # what the exam writer must not see
COUNT = 10
TIMEOUT_S = 3600
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
- Validate with: python3 eval/validate.py {out}   and fix until it prints {count}/{count} situations valid.
Reply only "done" when finished."""


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--model", default="opus")
    a.add_argument("--out", default=str(STAGING))
    x = a.parse_args()
    out = Path(x.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if list(out.glob("*.py")):
        sys.exit(f"{out} already has situations; seal or empty it first")
    if not shutil.which("bwrap"):
        sys.exit("bubblewrap (bwrap) is needed to hide the visible situations")
    hide = [arg for h in HIDDEN if (ROOT / h).exists() for arg in ("--tmpfs", str(ROOT / h))]
    cmd = ["bwrap", "--dev-bind", "/", "/", *hide, "--chdir", str(ROOT), "--",
           "claude", "-p", PROMPT.format(count=COUNT, out=out), "--model", x.model,
           "--setting-sources", "project,local", "--strict-mcp-config", "--no-session-persistence",
           "--tools", "Read Write Edit Glob Grep Bash", "--permission-mode", "acceptEdits",
           "--allowedTools", f"Read Write Edit Glob Grep Bash(python3 eval/validate.py *)", "--output-format", "json"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    try:
        usage = json.loads(p.stdout).get("modelUsage") or {}
        print(f"exam writer used {sum(v for m in usage.values() for k, v in m.items() if k.endswith('Tokens'))} tokens")
    except json.JSONDecodeError:
        sys.exit(f"exam writer failed (exit {p.returncode}); nothing printed to keep the exam hidden")
    v = subprocess.run([sys.executable, str(ROOT / "eval" / "validate.py"), str(out)], capture_output=True, text=True)
    print(v.stdout.strip().splitlines()[-1])  # count line only; BAD lines would reveal ids
    if v.returncode or len(list(out.glob("*.py"))) != COUNT:
        sys.exit(f"expected {COUNT} valid situations; empty {out} and rerun")


if __name__ == "__main__":
    main()
