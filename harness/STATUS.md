# STATUS — 2026-11-04
**Phase:** M1 done (steps 1-4), waiting for owner sign-off
**Done:** explore 1-3; venv; data. M1: (1) eval/run.py + 8 situations + 12 self-tests (fake CLI, 0 tokens). (2) sanity round: stock 5/8 vs oracle 8/8 (gap 37.5 pts, need ≥20) → eval/results/sanity.json. (3) plugin/: /senior skill + init/run refs, verify.py (lock), role.py (bwrap roles). (4) `claude plugin validate` PASS; smoke on made-up projects: `/senior check` ran verify, `/senior` init asked 2 plain questions with defaults, built nothing (after allowed-tools fix).
**In progress:** —
**Next:** M2 (re-confirm definition): situation bank (~30, harder + history + false self-report), simulated junior, first senior round, holdout set.
**Needs owner:**
Q5. Ratify 5 agent decisions of 2026-11-04 in DECISIONS (situation format, oracle in message, simulated junior → M2, role views, skill allowed-tools).
Q6. Real-agent isolation test (a role told to break out) — auto-mode may block it; OK to run in M2? a) yes ← recommended: SPEC #7 says "even when told to try"  b) fake-CLI test only — cheaper, weaker proof
**Not verified:** isolation against a real agent; init smoke ran on Haiku, not Sonnet; history situations with the plugin (history turns run stock); macOS.
**Verify:** 2026-11-04 self-test/fingerprint/size/hardcode/docs PASS; 7 result checks fail (no senior round yet, by design) · **Holdout:** not sealed
