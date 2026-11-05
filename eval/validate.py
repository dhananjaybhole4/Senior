"""Check a folder of situations without any model call: each loads, its project builds, its check runs.
python3 eval/validate.py <dir>   prints only counts (safe for the sealed holdout)."""
import sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run

REQUIRED = {"category", "rule", "files", "prompt", "check", "oracle"}


def problem(sid, sit, tmp):
    """None if the situation is usable, else a short reason."""
    missing = REQUIRED - set(sit)
    if missing:
        return f"missing {sorted(missing)}"
    d = Path(tmp) / sid
    run.setup(d, sit)
    run.write(d, sit.get("before_risky", {}))
    run.git(d, "add", "-A"); run.git(d, "commit", "-qm", run.SAVEPOINT, "--allow-empty"); run.git(d, "branch", run.SAVEPOINT)
    run.write(d, sit.get("after_commit", {}))
    t = {"tools": [], "final": "", "new_commits": 0, "branches": 1, "repo": d}
    if not isinstance(sit["check"](t), bool):
        return "check must return a bool"
    return None


def main():
    sits = run.load_situations(sys.argv[1])
    with tempfile.TemporaryDirectory() as tmp:
        bad = {}
        for sid, sit in sits.items():
            try:
                why = problem(sid, sit, tmp)
            except Exception as e:  # report every broken situation, not just the first
                why = f"{type(e).__name__}: {e}"
            if why:
                bad[sid] = why
    for sid, why in bad.items():
        print(f"BAD {sid}: {why}")
    print(f"{len(sits) - len(bad)}/{len(sits)} situations valid")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
