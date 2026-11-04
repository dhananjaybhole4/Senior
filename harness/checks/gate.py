"""Acceptance gate: judges the SAVED results of the last test round (no model calls, no tokens).

Results file (written by the eval runner): eval/results/latest.json
{
  "senior_hash": "<sha256 of plugin/ at run time>",
  "situations": [{"id": str, "category": str,            # category "direction" = stuck-route situations
                  "base_passes": [bool], "senior_passes": [bool],
                  "base_tokens": int, "senior_tokens": int}],
  "questions": {"total": int, "good": int},             # judged: changes plan, plain words, has default
  "isolation": {"attempts": int, "blocked": int}
}
Usage: gate.py <check> [thresholds]   exit 0 = PASS. Last line: METRIC name=value
"""
import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "eval" / "results" / "latest.json"
PLUGIN = ROOT / "plugin"


def plugin_hash():
    if not PLUGIN.is_dir():
        sys.exit(f"FAIL: {PLUGIN} does not exist yet")
    h = hashlib.sha256()
    for p in sorted(PLUGIN.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(PLUGIN)).encode()); h.update(p.read_bytes())
    return h.hexdigest()


def load():
    if not RESULTS.exists():
        sys.exit(f"FAIL: no results at {RESULTS}; run a test round first")
    r = json.loads(RESULTS.read_text())
    if r.get("senior_hash") != plugin_hash():
        sys.exit("FAIL: results are out of date (plugin changed since the last round); rerun")
    return r


def handled(passes):  # a situation counts as handled if it passed in a majority of its runs
    return sum(passes) * 2 > len(passes)


def rate(sits, key):
    return sum(handled(s[key]) for s in sits) / len(sits) if sits else 0.0


def gate(ok, metric, value, msg):
    print(("PASS: " if ok else "FAIL: ") + msg)
    print(f"METRIC {metric}={value:.3f}")
    sys.exit(0 if ok else 1)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("check", choices=["fresh", "situations", "regressions", "tokens", "questions", "isolation", "direction"])
    a.add_argument("--min-rate", type=float)
    a.add_argument("--min-gap", type=float)
    a.add_argument("--max-ratio", type=float)
    a.add_argument("--max-regressions", type=int)
    x = a.parse_args()
    r = load()
    sits = [s for s in r["situations"] if s["category"] != "direction"]
    if x.check == "fresh":
        gate(True, "situations", len(r["situations"]), "results match the current plugin")
    if x.check == "situations":
        s, b = rate(sits, "senior_passes"), rate(sits, "base_passes")
        gate(s >= x.min_rate and s - b >= x.min_gap, "senior_rate", s, f"senior {s:.0%} vs stock {b:.0%}")
    if x.check == "regressions":
        bad = [s["id"] for s in r["situations"] if handled(s["base_passes"]) and not handled(s["senior_passes"])]
        gate(len(bad) <= x.max_regressions, "regressions", len(bad), f"regressed: {bad or 'none'}")
    if x.check == "tokens":
        b = sum(s["base_tokens"] for s in r["situations"]); s = sum(s["senior_tokens"] for s in r["situations"])
        ratio = s / b if b else float("inf")
        gate(ratio <= x.max_ratio, "token_ratio", ratio, f"senior/stock tokens = {ratio:.2f}")
    if x.check == "questions":
        q = r["questions"]; v = q["good"] / q["total"] if q["total"] else 1.0
        gate(v >= x.min_rate, "good_questions", v, f"{q['good']}/{q['total']} questions useful+easy")
    if x.check == "isolation":
        i = r["isolation"]; v = i["blocked"] / i["attempts"] if i["attempts"] else 0.0
        gate(i["attempts"] > 0 and v >= x.min_rate, "isolation", v, f"{i['blocked']}/{i['attempts']} forbidden reads blocked")
    if x.check == "direction":
        d = [s for s in r["situations"] if s["category"] == "direction"]
        v = rate(d, "senior_passes")
        gate(bool(d) and v >= x.min_rate, "direction_rate", v, f"{len(d)} stuck-route situations")


if __name__ == "__main__":
    main()
