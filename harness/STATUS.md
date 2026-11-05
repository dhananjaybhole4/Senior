# STATUS — 2026-11-05
**Phase:** M2 in progress (plan + Q8-Q10 approved 2026-11-05)
**Done:** explore 1-3; venv; data. M1: (1) eval/run.py + 8 situations + 12 self-tests (fake CLI, 0 tokens). (2) sanity round: stock 5/8 vs oracle 8/8 (gap 37.5 pts, need ≥20) → eval/results/sanity.json. (3) plugin/: /senior skill + init/run refs, verify.py (lock), role.py (bwrap roles). (4) `claude plugin validate` PASS; smoke on made-up projects: `/senior check` ran verify, `/senior` init asked 2 plain questions with defaults, built nothing (after allowed-tools fix).
**In progress:** M2 built: 30 situations (all validated, 0 tokens), Haiku question judge (checked on a real reply), exam writer (sandboxed, owner runs it). No Senior round yet.
**Next:** owner makes + seals hidden exam → /clear, switch to Sonnet → half round 1 (15 × 2) → owner spot-checks 5 judge verdicts → iterate → full round
**Needs owner:** Q11 simulated junior: build now or when a situation needs it (see chat) · run eval/make_holdout.py then seal (own terminal)
**Not verified:** isolation against a real agent; init smoke ran on Haiku, not Sonnet; history situations with the plugin (history turns run stock); macOS.
**Verify:** 2026-11-05 46 self-tests, fingerprint, size 1368/3000, hardcode, docs PASS; 7 result checks fail (no senior round yet) · **Holdout:** not sealed
