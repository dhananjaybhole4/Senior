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
- Senior v2, gradebook: 7/7 hidden (stock 6/7), rule kept, 14 tests found; 0.83M = 1.80x stock (v1 2.15x);
  0 commits. Setup turn wasted calls on my template bug + lock broken by test caches → fixed (v2.1).
**In progress:** Senior v2.1 rerun on gradebook (~0.8M).
**Next:** if ≤ ~1.5x, commits back and rule kept → qualify round, all 4 projects (~6M). If still >1.3x: owner
  decision on SPEC #4 (Senior writes tests and docs stock skips; is +30% the right limit?).
**Needs owner:**
Q34. Real Python 3.8 check: run the `!` unpack command given in chat (26 MB build, checksum verified) — or say skip.
    Blocks: nothing now.
**Last verify 2026-11-06:** self-test (74), fingerprint, size 2851/3500, hardcode, docs PASS; fresh/regressions/
  tokens/questions/isolation/long traps FAIL (plugin changed; Senior 2.15x tokens).
**Not verified:** v2 behaviour; short-situation token results (inflated by the same bug: rerun needed);
  Python 3.8 compatibility of built code; Opus; macOS; simulated junior ≠ real junior; n=1 per arm.
**Holdout:** new seal = 3 long projects; route: owner writes plain stories, a separate session codes them, owner seals.
