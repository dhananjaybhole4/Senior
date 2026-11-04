# STATUS — 2026-11-04
**Phase:** M1 (approved 2026-11-04, Q4 a)
**Done:** explore 1 (SWE-chat licence/size), 2 (bubblewrap walls roles, tested), 3 (failures in long sessions: yes, same types; DECISIONS). Venv + requirements + README. Misalignment labels (MIT) downloaded; analysis script eval/research/failures_by_length.py.
**In progress:** — (SWE-chat sessions + conversations downloaded, byte-exact, 11,607,572 rows)
**Next:** M1 step 1 runner eval/run.py + eval/tests → 2 sanity round (pilot 8 × stock/oracle × 2, gap ≥20 pts) → 3 plugin skeleton, /senior harness core (.senior/), bwrap role launcher → 4 `claude plugin validate` + /senior smoke on a made-up project. Plan details: DECISIONS 2026-11-04 Q4 a line.
**Needs owner:** — (M2-M5 definitions to re-confirm after M1)
**Not verified:** bwrap against a real agent attempt (M2); macOS (no bwrap); long-session failure rate per message may be undercounted by the source labels. No plugin yet; result checks red by design.
**Verify:** 2026-11-04 (venv active) 8 fail (no results/tests yet, expected), fingerprint/size/hardcode/docs PASS · **Holdout:** not sealed
