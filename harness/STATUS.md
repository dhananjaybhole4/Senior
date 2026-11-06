# STATUS — 2026-11-06
**Phase:** M3 reset: focus moves from single moments to keeping a big project on course (owner insight). Hidden exam run 1: Senior 7/10, stock 6/10 (with folder leak).
**Done:** M1, M2, M3 fixes (rule 11, judge rubric + retry, merge_arms, runs/ move, heavy_download grader). Update 2026-11-06: Q26 self-test uses .venv python; Q27 rubric + rule 11 ratified; Q28 ≤1 more exam run on this seal, then reseal 10 new; Q29 fresh round ~15 × 2 per arm, cap 8M.
- make_holdout.py --fresh: 15 new visible situations → eval/situations_fresh/, writer blind to situations, git and plugin/ (Senior rules); unit test proves plugin/ hidden (fails when unhidden).
- Results (eval/results/latest.json): Senior 37/37, stock 30/37; slip 5/5; 0 regressions; direction 6/6 runs; question gap 50 pts; tokens 1.00x; isolation 15/15.
**Fresh round 1 (first run):** base 13/15, Senior 13/15, tokens 1.08x; set too easy (stock slips on 2). Findings: folder name = situation id leaks hints (both arms, all rounds); Senior proposes but doesn't build on stuck route; docs/SPEC read 1/2.
**Fresh round 2 (leak fixed, rules 11+12):** base 11/15, Senior 12/15, tokens 1.22x; slip set Senior 2/4 (need 80%); 1 regression (history_cents_split: Bash write denied in test env). Gains on spec_case/stuck_price are biased (they motivated the rules).
**Long explore, stock (1 run):** 6/8 hidden checks; broke partner's file format at turn 6 after promising to keep it at turn 0; 0 commits, 0 tests; 4.81M tokens (92% cache reads), cap hit before the last request. Premise supported (n=1).
**Long rerun (7 requests, graders fixed):** stock 6/8 (alert column breaks partner's file, 0 tests, 0 commits), Senior 8/8 (29 tests, 16 commits, kept format), tokens 2.13x (limit 1.3x); Senior's own feature offers cause scope creep.
**Next:** per-turn rule-break metric (free) → SPEC update (long-horizon goal, D1-D7, criteria; owner approval) → long-project test set built only from traps stock fails.
**Last verify 2026-11-06:** 7 FAIL "results out of date" (Senior rules changed; expected until next official round); unit tests 63 pass.
**Long explore, Senior (valid rerun):** 6/8, kept partner's format (stock broke it), 57 tests (stock 0), but 2.6x tokens per request, 0 commits, extra question turns; stopped at request 5/9 by cap.
**Long round 1 (6 req):** stock 7/8 4.56M; Senior 4/8 5.35M (grader hidden requirement + sim junior answer; harness skipped by the model). Runs paused. Across all long runs: stock added the alert column in 3/3, Senior refused it whenever it got there.
**Ledger test (2 runs/arm):** PASS: rule recorded 2/2; Senior broke partner's format 0/2 vs stock 2/2 (mid-run); guard checks 8,7 vs 7,7; tokens ~1.07x.
**Needs owner:** commit today's work? then SPEC update approval.
**Not verified:** Opus; macOS; fresh1 and all earlier scores (incl. exam run 1) carry the folder-name leak; writer may echo exam kinds (affects only the 1 remaining run on this seal); latest.json mixes 3 rounds, all on the current plugin.
**Holdout:** sealed 2026-11-05, runs 1 (2026-11-06: Senior 7/10, stock 6/10, tokens 1.22x)
