import json, subprocess, sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "merge_arms.py"


def row(sid, arm, passes, good):
    q = [{"run": f"{sid}.{arm}.0", "q": "x?", "good": good}]
    r = {"id": sid, "category": "c", "rule": "r", "judge_tokens": 1,
         "history_tokens": {"senior": 5} if arm == "senior" else {"stock": 7},
         "questions": [], "questions_b": [], "base_questions": [], "base_questions_b": []}
    prefix = "" if arm == "senior" else "base_"
    r.update({f"{arm}_passes": passes, f"{arm}_tokens": 10, f"{prefix}questions": q, f"{prefix}questions_b": q})
    return r


def write(p, arms, rows, **extra):
    p.write_text(json.dumps({"senior_hash": "h", "model": "sonnet", "reps": 1, "arms": arms, "situations": rows, **extra}))
    return p


def merge(tmp, s, b):
    out = tmp / "out.json"
    p = subprocess.run([sys.executable, "-B", str(SCRIPT), str(s), str(b), str(out)], capture_output=True, text=True)
    return p, out


def test_merge_takes_stock_from_old_round(tmp_path):
    s = write(tmp_path / "s.json", ["senior"], [row("a", "senior", [True], True)])
    b = write(tmp_path / "b.json", ["base", "senior"], [{**row("a", "base", [False], False), "senior_passes": [False]}],
              isolation={"attempts": 1, "blocked": 1})
    p, out = merge(tmp_path, s, b)
    assert p.returncode == 0, p.stderr
    r = json.loads(out.read_text())
    x = r["situations"][0]
    assert r["arms"] == ["base", "senior"] and x["senior_passes"] == [True] and x["base_passes"] == [False]
    assert x["history_tokens"] == {"senior": 5, "stock": 7}
    assert r["questions"] == {"total": 1, "good": 1} and r["base_questions"] == {"total": 1, "good": 0}
    assert r["isolation"]["blocked"] == 1


def test_merge_refuses_different_situations(tmp_path):
    s = write(tmp_path / "s.json", ["senior"], [row("a", "senior", [True], True)])
    b = write(tmp_path / "b.json", ["base", "senior"], [row("z", "base", [True], True)])
    p, _ = merge(tmp_path, s, b)
    assert p.returncode != 0 and "different situations" in p.stderr
