# STATUS — 2026-11-06
**Phase:** SPEC + checks updated: goal = keep a long project on course; score only traps where stock slips. Next milestone: long-project trap set.
**Done today:**
- Reset: single-moment tests mostly measure what stock already does; real failure = losing direction over many turns.
- Test fixes: folder-name leak (projects now outside repo, neutral paths); roles cheap and isolated (own tools only, no apps/user settings, session's model); long-run runner stops on error turns; graders traced to the junior's facts.
- Long explore (expense tracker, simulated junior): stock added the alert column (breaks partner's file) in 3/3 runs, 0 tests.
- Standing-rules ledger (rule 13 + UserPromptSubmit hook): 2 runs/arm → rule recorded 2/2, Senior broke format 0/2 vs stock 2/2, guards 8,7 vs 7,7, tokens ~1.07x.
- SPEC rewritten (D1-D7, long traps, long holdout); checks: "long traps" added (traps qualify on an earlier stock round), "situations"/"direction" retired, hardcode scan covers new tests.
**Next:** long round runner (projects × reps × arms → long_qualify.json / long_latest.json) → 3 more long projects, traps stock likely fails → stock qualify round → official round → owner seals 3 long projects.
**Last verify 2026-11-06:** self-test (70), size, hardcode, docs PASS; fresh/regressions/tokens/questions/isolation/long traps FAIL (no results for current plugin, no long round yet — expected).
**Needs owner:** relock the checks in your own terminal (`harness/verify --lock`), since checks.toml changed.
**Not verified:** Opus; macOS; simulated junior ≠ real junior; long results n=2 per arm on 1 project; all scores before the leak fix (incl. exam run 1) carry the folder-name hint.
**Holdout:** old 10-situation seal retired (run 1: Senior 7/10, stock 6/10, with leak); new seal = 3 long projects (not yet written).
