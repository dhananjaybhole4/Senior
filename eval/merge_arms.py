"""Combine a Senior-only round with the stock (base) rows of an earlier round (owner Q22: stock does not use the plugin,
so a plugin change needs only the Senior arm rerun). Both files must cover the same situations and reps.
python3 eval/merge_arms.py <senior_only.json> <stock_source.json> <out.json>"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import rescore_totals

BASE_KEYS = ("base_passes", "base_tokens", "base_questions", "base_questions_b")


def main():
    senior, stock, out = (Path(p) for p in sys.argv[1:4])
    s, b = json.loads(senior.read_text()), json.loads(stock.read_text())
    if s["arms"] != ["senior"] or "base" not in b["arms"]:
        sys.exit(f"need a Senior-only round ({s['arms']}) and a round with stock ({b['arms']})")
    if (s["model"], s["reps"]) != (b["model"], b["reps"]):
        sys.exit(f"model/reps differ: {s['model']}/{s['reps']} vs {b['model']}/{b['reps']}")
    base_rows = {r["id"]: r for r in b["situations"]}
    if set(base_rows) != {r["id"] for r in s["situations"]}:
        sys.exit("the two rounds cover different situations")
    for r in s["situations"]:
        old = base_rows[r["id"]]
        r.update({k: old[k] for k in BASE_KEYS})
        r["history_tokens"]["stock"] = old["history_tokens"]["stock"]
    rows = s["situations"]
    final = {**s, "arms": ["base", "senior"], "situations": rows}
    for key in ("questions", "base_questions"):
        qs = [q for r in rows for q in r[key]]
        final[key] = {"total": len(qs), "good": sum(q["good"] for q in qs)}
    final["judge_rescore"] = rescore_totals(rows)
    final["stock_from"] = stock.name
    for key in ("isolation",):  # results that do not come from situation runs
        if key in b:
            final[key] = b[key]
    out.write_text(json.dumps(final, indent=1))
    print(f"saved {out}: senior {final['questions']} stock {final['base_questions']} passes {final['judge_rescore']}")


if __name__ == "__main__":
    main()
