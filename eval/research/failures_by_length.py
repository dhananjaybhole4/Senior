"""Explore 3: do coding-agent failures show up (more) in long real sessions, and for vague (junior-like) users?

Joins the arXiv 2605.29442 failure labels to SWE-chat session metadata (persona). Prints tables only.
Usage: python eval/research/failures_by_length.py   (after eval/fetch_data.sh)
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow.parquet as pq

DATA = Path(__file__).resolve().parents[1] / "data"
SYMPTOMS = {"S1": "wrong diagnosis", "S2": "misread intent", "S3": "constraint violation",
            "S4": "overreach", "S5": "faulty code", "S6": "execution error", "S7": "false self-report"}
CAUSES = {"C1": "underspecified ask", "C2": "scope overreach", "C3": "premature action",
          "C4": "context loss", "C5": "default override", "C6": "ignored instruction"}
LENGTH_BINS = [(1, 5), (6, 20), (21, 60), (61, 10**9)]  # user turns per session


def bin_of(turns):
    return next(f"{lo}-{hi}" if hi < 10**9 else f"{lo}+" for lo, hi in LENGTH_BINS if lo <= turns <= hi)


def main():
    sessions = json.load(open(DATA / "misalignment/session_mapping.json"))
    episodes = json.load(open(DATA / "misalignment/annotated_misalignments.json"))
    persona = dict(zip(*pq.read_table(DATA / "swe-chat/sessions.parquet",
                                      columns=["session_id", "user_persona"]).to_pydict().values()))

    key = lambda r: (r["source"], str(r["repository_id"]), r["session_count_id"])
    meta = {key(s): s for s in sessions}
    eps_by_session = defaultdict(list)
    for e in episodes:
        eps_by_session[key(e)].append(e)
    unmatched = sum(k not in meta for k in eps_by_session)
    print(f"sessions {len(meta)}, episodes {len(episodes)}, episode-sessions missing from mapping {unmatched}")

    def table(title, group_of):
        turns, n_eps, n_sess, sym = Counter(), Counter(), Counter(), defaultdict(Counter)
        for k, s in meta.items():
            g = group_of(s)
            if g is None:
                continue
            n_sess[g] += 1
            turns[g] += s["user_turns"]
            for e in eps_by_session.get(k, []):
                n_eps[g] += 1
                sym[g].update(c for c in {**SYMPTOMS, **CAUSES} if e.get(c) not in (None, False))
        print(f"\n## {title}\n{'group':<22}{'sessions':>9}{'fail/100 msgs':>14}{'sess w/ fail':>13}  top labels (% of failures)")
        for g in sorted(n_sess, key=lambda g: (int(g.split("-")[0].rstrip("+")) if g[0].isdigit() else 0, g)):
            with_fail = sum(1 for k, s in meta.items() if group_of(s) == g and eps_by_session.get(k))
            top = ", ".join(f"{({**SYMPTOMS, **CAUSES})[c]} {100 * v / max(n_eps[g], 1):.0f}"
                            for c, v in sym[g].most_common(4))
            print(f"{g:<22}{n_sess[g]:>9}{100 * n_eps[g] / max(turns[g], 1):>14.1f}"
                  f"{100 * with_fail / n_sess[g]:>12.0f}%  {top}")

    cli = lambda s: s["session_type"] == "CLI" and s["user_turns"] > 0
    table("CLI sessions by length (user turns)", lambda s: bin_of(s["user_turns"]) if cli(s) else None)
    table("SWE-chat CLI sessions by persona",
          lambda s: persona.get(s["session_sha"]) if cli(s) and s["source"] == "swe" else None)
    table("Vague Requester by length",
          lambda s: bin_of(s["user_turns"]) if cli(s) and persona.get(s["session_sha"]) == "Vague Requester" else None)


if __name__ == "__main__":
    main()
