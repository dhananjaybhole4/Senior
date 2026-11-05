# STATUS — 2026-11-05
**Phase:** M2 approved 2026-11-05 (D1-3, 5-8); open: D4, research step, SPEC #6 wording
**Done:** explore 1-3; venv; data. M1: (1) eval/run.py + 8 situations + 12 self-tests (fake CLI, 0 tokens). (2) sanity round: stock 5/8 vs oracle 8/8 (gap 37.5 pts, need ≥20) → eval/results/sanity.json. (3) plugin/: /senior skill + init/run refs, verify.py (lock), role.py (bwrap roles). (4) `claude plugin validate` PASS; smoke on made-up projects: `/senior check` ran verify, `/senior` init asked 2 plain questions with defaults, built nothing (after allowed-tools fix).
**In progress:** —
**Next:** M2 (re-confirm definition): situation bank (~30, harder + history + false self-report), simulated junior, first senior round, holdout set.
**Needs owner:** Q8 SPEC #6 wording · Q9 judge model · Q10 failure research step (see chat 2026-11-05)
**Not verified:** isolation against a real agent; init smoke ran on Haiku, not Sonnet; history situations with the plugin (history turns run stock); macOS.
**Verify:** 2026-11-04 self-test/fingerprint/size/hardcode/docs PASS; 7 result checks fail (no senior round yet, by design) · **Holdout:** not sealed
