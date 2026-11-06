# STATUS — 2026-11-06
**Phase:** long-project trap set. Round runner built; next = more long projects.
**Done today:**
- Reset: goal = keep a long project on course; score only traps where stock slips (SPEC D1-D7, long traps check).
- Standing-rules ledger: Senior broke partner's format 0/2 vs stock 2/2 (n=2, 1 project).
- Round runner: `python3 eval/longrun/run_long.py qualify|latest --cap N` → long_qualify.json / long_latest.json in the gate's format; every project × 2 reps × arms; finished runs reused (usage-limit resume; plugin change reruns only Senior); stock-passed traps become no-harm guards.
- Limit-weighted tokens recorded (output 5x, cache read 0.1x); role processes log per-type counts.
- expenses project declares its candidate traps (partner format, no packages, re-import, own tests).
**Next:** 3 more long projects (traps stock likely fails, each grader validated: reference passes all, broken fails) → stock qualify round → official round → owner seals 3 long projects.
**Needs owner:**
Q33. Token budget for the stock qualify round (4 projects × 2 runs ≈ 8 runs × ~5M ≈ 40M tokens, ~2-4 usage windows)
    a) cap 6M per run, all 4 projects — full picture, ~40M
    b) cap 6M per run, expenses + 1 new project first (~20M), add the rest after — ← recommended: checks the new runner and trap rate before spending the rest
    Blocks: qualify round. Not blocking: writing the 3 projects.
**Last verify 2026-11-06 15:20:** self-test (73), fingerprint, size 2568/3500, hardcode, docs PASS; fresh/regressions/tokens/questions/isolation/long traps FAIL (plugin changed (role.py token log) and no long round yet — expected).
**Not verified:** runner tested only with the fake CLI (no real round yet); Opus; macOS; simulated junior ≠ real junior; long results n=2 per arm on 1 project; scores before the leak fix carry the folder-name hint.
**Holdout:** old 10-situation seal retired (run 1: Senior 7/10, stock 6/10, with leak); new seal = 3 long projects (not yet written).
