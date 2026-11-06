"""Re-grade the questions in saved results with the current judge: two independent passes per asking reply, both arms
(no agent re-runs, Haiku only). python3 eval/rejudge.py eval/results/<round>.json
Rewrites row questions / base_questions (pass A) + questions_b / base_questions_b (pass B) and the file's judge_rescore."""
import json, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run
from judge import judge

EVAL = Path(__file__).resolve().parent


def final_text(run_name):
    logs = sorted(run.RUNS.glob(f"*/{run_name}.log"), key=lambda f: f.stat().st_mtime)  # newest log wins (reruns)
    t, _, _ = run.parse(logs[-1].read_text(), run_name)
    return t["final"] or ""


def main():
    path = Path(sys.argv[1]); data = json.loads(path.read_text())
    sits = run.load_situations(EVAL / "situations")
    with tempfile.TemporaryDirectory() as tmp:
        for r in data["situations"]:
            r["judge_tokens"] = 0
            for arm, key in (("senior", "questions"), ("base", "base_questions")):
                r[key], r[key + "_b"] = [], []
                for i in range(len(r[f"{arm}_passes"])):
                    name = f"{r['id']}.{arm}.{i}"; text = final_text(name)
                    if "?" not in text:
                        continue
                    for field in (key, key + "_b"):
                        verdicts, tok = judge(sits[r["id"]]["prompt"], text, tmp)
                        r[field] += [{"run": name, **v} for v in verdicts]; r["judge_tokens"] += tok
    for key, field in (("questions", "questions"), ("base_questions", "base_questions")):
        qs = [q for r in data["situations"] for q in r[field]]
        data[key] = {"total": len(qs), "good": sum(q["good"] for q in qs)}
    data["judge_rescore"] = run.rescore_totals(data["situations"])
    path.write_text(json.dumps(data, indent=1))
    print(f"{path.name}: senior {data['questions']} stock {data['base_questions']} passes {data['judge_rescore']}")


if __name__ == "__main__":
    main()
