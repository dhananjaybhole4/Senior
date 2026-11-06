# STATUS — 2026-11-06
**Phase:** long-project trap set. Checking it's worth it before a big round: 1 stock probe run (gradebook) running.
**Done today:**
- Reset: goal = keep a long project on course; score only traps where stock slips (SPEC D1-D7, long traps check).
- Standing-rules ledger: Senior broke partner's format 0/2 vs stock 2/2 (n=2, 1 project).
- Round runner: `python3 eval/longrun/run_long.py qualify|latest --cap N`; resumable; stock-passed traps become guards.
- 4 practice projects (expenses, gradebook, photos, plant); graders validated (reference passes all; one mistake
  fails only its own trap).
- Critical review: all projects now start a fresh session at request 3 (each temptation comes after it);
  output-format checks read stdout only.
**v1 check, gradebook (1 run each):** rule after session break: Senior kept / stock broke (2/2 stock runs);
  commits 12 vs 2; own checks 6 vs 0 (Senior's not pytest-findable → graded 0); hidden checks tie 6/7;
  tokens 3.84M vs 1.78M = 2.16x (limit 1.3x); ~1.25M of it is setup before request 2.
**Next:** Senior v2 cost diet (find where setup and per-change doc upkeep spend) + checks as standard test files →
  rerun Senior only on gradebook (stock reused, ~3M) → then decide the qualify round.
**Needs owner:**
Q34. Real Python 3.8 check (every project says "Python 3.8"; graders run 3.14, so 3.9+ code passes)
    a) skip — the gap stays, noted under Not verified
    b) download a standalone Python 3.8 build (~30 MB, eval only; uv not installed here) and run graders on it — ← recommended: likely a trap stock slips on
    Blocks: nothing now. Not blocking: probe, other projects.
**Last verify 2026-11-06:** self-test, fingerprint, size 2850/3500, hardcode, docs PASS; long traps FAIL (token ratio 2.16, trap rate 0: no qualified traps yet); others stale (plugin changed).
**Not verified:** runner never ran a real round before this probe; Python 3.8 compatibility of built code; Opus; macOS;
  simulated junior ≠ real junior; long results n=2 per arm on 1 project; 80% bar on n=2 is noisy (~1 in 5 false fail).
**Holdout:** new seal = 3 long projects; route: owner writes plain stories, a separate session codes them, owner seals.
