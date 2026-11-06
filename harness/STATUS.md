# STATUS — 2026-11-06
**Phase:** M3: official round + isolation done. Gate: 2 FAIL (questions judge drift, direction).
**Done:** M1, M2. M3 rule 11 "stuck → change route". Official round (eval/results/latest.json, 37 × 2): stock 30/37, Senior 34/37; where stock slips (5 situations) Senior 4/5 = 80%; 0 regressions; tokens 0.93x. Questions: Senior 30/37 good vs stock 20/60 (gap 48 pts), but the two judge passes differ by 6% (limit 5). Isolation (eval/isolation.py): 15/15 forbidden reads/writes blocked (5 sandbox-only + 10 real role agents, 0.86M tokens); agents did try and hit the wall (1 builder run was stopped by a permission prompt first).
**Verify 2026-11-06:** PASS fresh, situations, regressions, tokens, isolation, self-test (.venv on PATH), fingerprint, size 3097/3500, hardcode, docs. FAIL questions (judge drift 6%), direction 1/3.
**Findings:**
- Direction failures (stuck_regex_html, stuck_threshold_tuning, 1/2 each): in both failed runs the runner refused a command; Senior then asked to run it instead of switching route.
- Slip score 4/5 is fragile: one situation = 20 pts. More situations where stock slips are needed.
- Gate hashes everything in plugin/, incl. Python cache files: any import of plugin scripts makes all results stale (fixed in isolation.py with -B).
**Needs owner:** nothing.
**Next:** direction (why a refused command stops the route change; fix in Senior's rules, general); judge drift (stricter rubric or third pass); more situations where stock slips; then holdout (owner).
**Not verified:** rule 11 outside the stuck set (over-triggering); Opus; macOS. Always use .venv.
**Holdout:** sealed 2026-11-05, runs 0
