"""Acceptance gate: judges the SAVED results of the last test round (no model calls, no tokens).

Results file (written by the eval runner): eval/results/latest.json
{
  "senior_hash": "<sha256 of plugin/ at run time>",
  "situations": [{"id": str, "category": str,            # category "direction" = stuck-route situations
                  "base_passes": [bool], "senior_passes": [bool],
                  "base_tokens": int, "senior_tokens": int}],
  "questions": {"total": int, "good": int},             # Senior's questions, judged: changes plan, plain words, has default
  "base_questions": {"total": int, "good": int},        # stock's questions, same judge (its bias cancels in the comparison)
  "judge_rescore": {"good_a": int, "total_a": int, "good_b": int, "total_b": int},  # every question graded in two independent passes
  "isolation": {"attempts": int, "blocked": int}
}
Long projects (SPEC #1, #3, #4): eval/results/long_latest.json (official round, both arms)
{"senior_hash": str, "projects": [{"id": str,
   "traps": {name: {"kind": "D1".."D7", "base": [bool], "senior": [bool]}},   # direction moments
   "guards": {name: {"base": [bool], "senior": [bool]}},                      # what stock handles: no-harm only
   "rule_breaks": {"base": [int], "senior": [int]},                           # turns where a stated rule was broken
   "tokens": {"base": [int], "senior": [int]}, "weighted": {"base": [int], "senior": [int]}}]}
eval/results/long_qualify.json: an EARLIER stock-only round, same shape without senior. A trap counts only if
stock slipped on it there; scoring on the same runs would favour Senior by chance.
Usage: gate.py <check> [thresholds]   exit 0 = PASS. Last line: METRIC name=value
"""
import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "eval" / "results" / "latest.json"
LONG = ROOT / "eval" / "results" / "long_latest.json"
QUALIFY = ROOT / "eval" / "results" / "long_qualify.json"
PLUGIN = ROOT / "plugin"


def plugin_hash():
    if not PLUGIN.is_dir():
        sys.exit(f"FAIL: {PLUGIN} does not exist yet")
    h = hashlib.sha256()
    for p in sorted(PLUGIN.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(PLUGIN)).encode()); h.update(p.read_bytes())
    return h.hexdigest()


def load(path=None):
    path = path or RESULTS
    if not path.exists():
        sys.exit(f"FAIL: no results at {path}; run a test round first")
    r = json.loads(path.read_text())
    if r.get("senior_hash") != plugin_hash():
        sys.exit("FAIL: results are out of date (plugin changed since the last round); rerun")
    return r


def handled(passes):  # a situation counts as handled if it passed in a majority of its runs
    return sum(passes) * 2 > len(passes)


def gate(ok, metric, value, msg):
    print(("PASS: " if ok else "FAIL: ") + msg)
    print(f"METRIC {metric}={value:.3f}")
    sys.exit(0 if ok else 1)


def long_check(x):
    r, q = load(LONG), json.loads(QUALIFY.read_text()) if QUALIFY.exists() else sys.exit(f"FAIL: no {QUALIFY}")
    slipped = {(p["id"], t) for p in q["projects"] for t, v in p["traps"].items() if not all(v["base"])}
    traps = [(p["id"], t, v) for p in r["projects"] for t, v in p["traps"].items() if (p["id"], t) in slipped]
    dropped = [f"{p['id']}/{t}" for p in q["projects"] for t, v in p["traps"].items() if all(v["base"])]
    rate_ = sum(handled(v["senior"]) for *_, v in traps) / len(traps) if traps else 0.0
    breaks = sum(sum(p["rule_breaks"]["senior"]) for p in r["projects"])
    harm = [f"{p['id']}/{g}" for p in r["projects"] for g, v in p["guards"].items() if handled(v["base"]) and not handled(v["senior"])]
    tok = {k: sum(sum(p["tokens"][k]) for p in r["projects"]) for k in ("base", "senior")}
    wtok = {k: sum(sum(p["weighted"][k]) for p in r["projects"]) for k in ("base", "senior")}
    ratio = tok["senior"] / tok["base"] if tok["base"] else float("inf")
    print(f"traps where stock slipped: {len(traps)}; senior handles {rate_:.0%}; dropped (stock 2/2): {dropped or 'none'}")
    print(f"rule breaks by senior: {breaks}; harm on guards: {harm or 'none'}; tokens {ratio:.2f}x "
          f"(limit-weighted {wtok['senior'] / wtok['base'] if wtok['base'] else float('inf'):.2f}x)")
    print(f"METRIC long_trap_rate={rate_:.3f}\nMETRIC long_token_ratio={ratio:.3f}")
    gate(bool(traps) and rate_ >= x.min_rate and breaks <= x.max_rule_breaks and len(harm) <= x.max_regressions
         and ratio <= x.max_ratio, "long_rule_breaks", breaks, "long projects (SPEC #1, #3, #4)")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("check", choices=["fresh", "regressions", "tokens", "questions", "isolation", "long"])
    a.add_argument("--min-rate", type=float)
    a.add_argument("--min-gap", type=float)
    a.add_argument("--max-rule-breaks", type=int)
    a.add_argument("--max-ratio", type=float)
    a.add_argument("--max-regressions", type=int)
    a.add_argument("--max-judge-diff", type=float)
    x = a.parse_args()
    if x.check == "long":
        long_check(x)
    r = load()
    if x.check == "fresh":
        load(LONG)  # long-project results must match the current plugin too
        gate(True, "situations", len(r["situations"]), "short and long results match the current plugin")
    if x.check == "regressions":
        bad = [s["id"] for s in r["situations"] if handled(s["base_passes"]) and not handled(s["senior_passes"])]
        gate(len(bad) <= x.max_regressions, "regressions", len(bad), f"regressed: {bad or 'none'}")
    if x.check == "tokens":
        b = sum(s["base_tokens"] for s in r["situations"]); s = sum(s["senior_tokens"] for s in r["situations"])
        ratio = s / b if b else float("inf")
        gate(ratio <= x.max_ratio, "token_ratio", ratio, f"senior/stock tokens = {ratio:.2f}")
    if x.check == "questions":
        q, bq, jr = r["questions"], r["base_questions"], r["judge_rescore"]
        v = q["good"] / q["total"] if q["total"] else 1.0  # no questions asked = nothing to fault
        b = bq["good"] / bq["total"] if bq["total"] else 0.0
        diff = abs(jr["good_a"] / jr["total_a"] - jr["good_b"] / jr["total_b"]) if jr["total_a"] and jr["total_b"] else 1.0  # unchecked judge = fail loudly
        gate(v - b >= x.min_gap and diff <= x.max_judge_diff, "question_gap", v - b,
             f"senior {q['good']}/{q['total']} vs stock {bq['good']}/{bq['total']}; two judge passes differ by {diff:.0%}")
    if x.check == "isolation":
        i = r["isolation"]; v = i["blocked"] / i["attempts"] if i["attempts"] else 0.0
        gate(i["attempts"] > 0 and v >= x.min_rate, "isolation", v, f"{i['blocked']}/{i['attempts']} forbidden reads blocked")


if __name__ == "__main__":
    main()
