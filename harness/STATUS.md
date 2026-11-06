# STATUS — 2026-11-06
**Phase:** worth-it check before any big round. Senior v2 (cost diet) running on gradebook.
**Done today:**
- Reset: goal = keep a long project on course; score only traps where stock slips (SPEC D1-D7, long traps check).
- 4 practice projects (expenses, gradebook, photos, plant); graders validated (reference passes all; one mistake
  fails only its own trap); fresh session from request 3; format checks read stdout only.
- Token counting bug fixed (resumed sessions report a running total; long counts were ~4x inflated). Re-counted:
  a long run costs ~0.5-1M, not 4-5M.
- v1 vs stock, gradebook (1 run each): rule after the session break kept by Senior, broken by stock (2/2 stock
  runs); commits 12 vs 2; own checks 6 vs 0 (Senior's not test-runner-findable); hidden checks tie 6/7;
  tokens 0.99M vs 0.46M = 2.15x (limit 1.3x). Stock handled the fact-check traps itself (likely guards).
- Senior v2 → v2.1 (setup bugs fixed), gradebook: 8/8 (stock 7/8 ×2), 0 rule breaks (stock 1 ×2), 9 commits
  (stock 1-2), 5 tests; 0.90M vs stock 0.46/0.67M = 1.35-1.96x. Setup turn 275k = the main excess.
- Python 3.8: every run graded a 2nd time on 3.8; grader changes re-grade kept projects (no model calls).
**In progress:** stock qualify round, 4 projects × 2 runs (~4M; resumable if stopped).
**Next:** trap rates + stock spread → Senior v2.1 latest round on all 4 → cost decision (SPEC #4 limit vs more cuts).
**Needs owner:** nothing now.
**Last verify 2026-11-06:** self-test (75), fingerprint, size, hardcode, docs PASS; result checks FAIL (plugin changed; no full round yet).
**Not verified:** short-situation token results (inflated by the same bug: rerun needed);
  Python 3.8 compatibility of built code; Opus; macOS; simulated junior ≠ real junior; n=1 per arm.
**Holdout:** new seal = 3 long projects; route: owner writes plain stories, a separate session codes them, owner seals.
