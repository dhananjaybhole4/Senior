"""Run one role as a separate claude process that cannot see what it must not (bubblewrap, Linux/WSL).
python3 role.py <role> "<task>" [--allow "<tools>"]
  test-writer  sees only .senior/ (spec, boundaries) and writes tests there; never the code
  builder      sees everything; .senior/checks.toml and .senior/checks/ are read-only
  reviewer     sees only .senior/, read-only (goal, results, decisions)
Hidden folders appear empty; writes to read-only places fail. Tokens go to .senior/usage.jsonl."""
import argparse, json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path.cwd().resolve()
H = ROOT / ".senior"
ONLY_SENIOR = ["--tmpfs", str(ROOT), "--bind", str(H), str(H)]  # mounts apply in order: hide all, then re-show .senior
ROLES = {
    "test-writer": ONLY_SENIOR,
    "builder": ["--ro-bind", str(H / "checks.toml"), str(H / "checks.toml"), "--ro-bind", str(H / "checks"), str(H / "checks")],
    "reviewer": ["--tmpfs", str(ROOT), "--ro-bind", str(H), str(H)],
}
TOKEN_KEYS = ("inputTokens", "outputTokens", "cacheCreationInputTokens", "cacheReadInputTokens")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("role", choices=ROLES)
    a.add_argument("task")
    a.add_argument("--allow", default="Read Edit Write Glob Grep")
    x = a.parse_args()
    if not shutil.which("bwrap"):
        sys.exit("FAIL: bubblewrap (bwrap) is not installed; roles cannot be isolated")
    (H / "checks").mkdir(parents=True, exist_ok=True)
    (H / "checks.toml").touch()
    cmd = ["bwrap", "--dev-bind", "/", "/", *ROLES[x.role], "--chdir", str(ROOT), "--",
           "claude", "-p", x.task, "--output-format", "json", "--permission-mode", "acceptEdits",
           "--allowedTools", x.allow, "--no-session-persistence"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    try:
        r = json.loads(p.stdout)
    except json.JSONDecodeError:
        sys.exit(f"FAIL: {x.role} gave no result (exit {p.returncode}): {p.stderr.strip()[-500:]}")
    tok = sum(m.get(k, 0) for m in (r.get("modelUsage") or {}).values() for k in TOKEN_KEYS)
    with open(H / "usage.jsonl", "a") as f:
        f.write(json.dumps({"role": x.role, "tokens": tok}) + "\n")
    print(r.get("result", ""))
    sys.exit(1 if r.get("is_error") else 0)


if __name__ == "__main__":
    main()
