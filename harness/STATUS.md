# STATUS — 2026-11-05
**Phase:** M2 in progress (plan + Q8-Q10 approved 2026-11-05)
**Done:** explore 1-3; venv; data. M1: (1) eval/run.py + 8 situations + 12 self-tests (fake CLI, 0 tokens). (2) sanity round: stock 5/8 vs oracle 8/8 (gap 37.5 pts, need ≥20) → eval/results/sanity.json. (3) plugin/: /senior skill + init/run refs, verify.py (lock), role.py (bwrap roles). (4) `claude plugin validate` PASS; smoke on made-up projects: `/senior check` ran verify, `/senior` init asked 2 plain questions with defaults, built nothing (after allowed-tools fix).
**In progress:** M2: runner save/limit/resume + Senior-from-turn-1 history DONE; failure research DONE (DECISIONS) → writing ~30 situations
**Next:** situation bank → simulated junior + Haiku question judge → holdout generator → half rounds (switch to Sonnet) → owner spot-check → full round
**Needs owner:** re-sign SPEC change in own terminal (verify lock; fingerprint shows TAMPERED until then)
**Not verified:** isolation against a real agent; init smoke ran on Haiku, not Sonnet; history situations with the plugin (history turns run stock); macOS.
**Verify:** 2026-11-04 self-test/fingerprint/size/hardcode/docs PASS; 7 result checks fail (no senior round yet, by design) · **Holdout:** not sealed
