# STATUS — 2026-11-06
**Phase:** M3: visible checks PASS; hidden exam FAIL (Senior 7/10, need 8; stock 6/10) → fresh visible round in progress.
**Done:** M1, M2, M3 fixes (rule 11, judge rubric + retry, merge_arms, runs/ move, heavy_download grader). Update 2026-11-06: Q26 self-test uses .venv python; Q27 rubric + rule 11 ratified; Q28 ≤1 more exam run on this seal, then reseal 10 new; Q29 fresh round ~15 × 2 per arm, cap 8M.
- make_holdout.py --fresh: 15 new visible situations → eval/situations_fresh/, writer blind to situations, git and plugin/ (Senior rules); unit test proves plugin/ hidden (fails when unhidden).
- Results (eval/results/latest.json): Senior 37/37, stock 30/37; slip 5/5; 0 regressions; direction 6/6 runs; question gap 50 pts; tokens 1.00x; isolation 15/15.
**In progress:** fresh writer (Opus) generating 15 situations.
**Next:** validate + review each check → run both arms × 2 (cap 8M) → log first-run score in DECISIONS before any fix → general fixes only → one exam run (owner).
**Last verify 2026-11-06 (after owner relock):** PASS all, 0 fail.
**Needs owner:** Commit of today's work: asked, not answered.
**Not verified:** Opus; macOS; fresh situations not yet generated or reviewed; writer may echo exam kinds (affects only the 1 remaining run on this seal); latest.json mixes 3 rounds, all on the current plugin.
**Holdout:** sealed 2026-11-05, runs 1 (2026-11-06: Senior 7/10, stock 6/10, tokens 1.22x)
