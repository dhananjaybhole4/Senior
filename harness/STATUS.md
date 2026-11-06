# STATUS — 2026-11-06
**Phase:** practice milestone PASSED for the rules-file Senior (SessionStart instruction + ledger hook).
**Done:**
- Slim-down: skill, roles, harness, verify deleted. Unit tests 69 pass.
- Guard project invoices (junior changes a stated rule after a session break); runner reuses earlier stock runs.
- Official round (2 Senior runs each, ~2.9M; stock reused): expenses partner trap 2/2 (stock 1/2); 0 rule breaks
  at any turn (stock: gradebook 1+1, expenses 4); invoices change followed 2/2, rules file updated; 0 guard harm.
- Tokens 0.89x overall, but per project: expenses 0.57x, gradebook 1.37x, invoices 1.09x. The overall figure is
  helped by one 1.28M stock expenses run.
**Next:**
1. Opus check (done #5): the runner can't run Senior-only on another model without rerunning stock and overwriting
   the round file; needs a small runner option (~1-2M tokens for 3 runs).
2. Hidden exam (done #2) once the owner's stories exist.
**Needs owner:**
1. Hidden exam: write 2-3 plain long stories blind (≥1 rule said casually, ≥1 rule you later change);
   a separate session codes them; you seal them, then run the exam.
2. Say "commit" when you want the work committed (plugin, tests, eval, harness as separate commits).
**Last verify 2026-11-06 21:22:** PASS — long traps (trap rate 1.0, token ratio 0.89, rule breaks 0), self-test,
  fingerprint, size 2815/3500, hardcode, docs.
**Not verified:** Opus; the hidden exam; n=2 per arm on 3 projects; gradebook tokens 1.37x (above 1.3 on that project);
  simulated junior ≠ real junior; mild over-recording (gradebook rules file holds facts, not only rules).
**Hidden exam:** old one retired; new long-project suite pending owner stories.
