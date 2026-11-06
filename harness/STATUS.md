# STATUS — 2026-11-06
**Phase:** long-project trap set. 4 practice projects written; next = stock qualify round (needs Q33).
**Done today:**
- Reset: goal = keep a long project on course; score only traps where stock slips (SPEC D1-D7, long traps check).
- Standing-rules ledger: Senior broke partner's format 0/2 vs stock 2/2 (n=2, 1 project).
- Round runner: `python3 eval/longrun/run_long.py qualify|latest --cap N`; resumable; stock-passed traps become guards.
- 3 new long projects, 6 requests each: gradebook (typo'd weight, export format vs "add names", bonus past 100,
  blank homework), photos (synced folder vs "just move them", same-name photos), plant (junior's premise vs the
  sensor's datasheet, "3 readings = 3 hours", "exactly WATER or OK" vs "show the average"). Graders validated:
  reference passes all; stock-like build fails every trap; one mistake fails only its own trap.
**Next:** stock qualify round → official round (both arms) → owner seals 3 long projects (written blind).
**Needs owner:**
Q33. Token budget for the stock qualify round (4 projects × 2 runs ≈ 8 runs × ~5M ≈ 40M tokens, ~2-4 usage windows)
    a) cap 6M per run, all 4 projects — full picture, ~40M
    b) cap 6M per run, expenses + 1 new project first (~20M), add the rest after — ← recommended: checks the new runner and trap rate before spending the rest
    Blocks: qualify round (all remaining work). Not blocking: nothing left.
**Last verify 2026-11-06 15:11:** self-test (74), fingerprint, size 2837/3500, hardcode, docs PASS; fresh/regressions/tokens/questions/isolation/long traps FAIL (plugin changed and no long round yet — expected).
**Not verified:** runner tested only with the fake CLI (no real round yet); whether stock actually slips on the new traps (qualify round decides); Opus; macOS; simulated junior ≠ real junior; long results n=2 per arm on 1 project.
**Holdout:** old 10-situation seal retired; new seal = 3 long projects (not yet written; owner writes or reviews them blind).
