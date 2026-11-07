# STATUS — 2026-11-07
**Phase:** v0 DONE (SessionStart instruction + ledger hook); benefit on blind projects not shown.
**Done:**
- Official round (visible, 2 runs each): expenses partner trap 2/2 (stock 1/2); 0 rule breaks (stock gradebook 1+1,
  expenses 4); invoices changed rule followed 2/2; 0 harm. Tokens 0.89x (expenses 0.57x, gradebook 1.37x, invoices 1.09x).
- Opus (done #5, 1 run each, 2.16M): trap kept, 0 rule breaks, changed rule followed, no harm; agent judged met, owner ok.
- Hidden exam (blind writer, 3 projects): 0/1 FAIL (Q1 b). Retired into visible bin_reminder, cafe_board, foodbank_rota.
- Study (1 run each): exam's missed trap most likely a grader bug (hidden tips.csv overwrote a file the junior agreed
  to change → crash; fixed, re-graded 8/9). Stock vs Senior there: stock slipped on 0 traps; 0 rule breaks both;
  Senior followed the lifted rule where stock didn't (foodbank), 1 failing own test where stock didn't (cafe);
  tokens 0.83x. No plugin change needed. Spent today: study 2.09M + stock 2.51M.
- Exam runner hardened: preflight (0 tokens), grader crash/hang or hung call fails only that run, counts only.
**Decided:** Q3 b — v0 accepted, SPEC done #2 reworded (owner). All done-criteria met or explicitly "not shown".
**Next:** real use on an owner project (not work). Code size 98% of budget: trim old short-test machinery only if needed.
**Needs owner:** re-sign the rulebook in your terminal (verify, lock option: SPEC changed). Say "commit" to commit (~20 files).
**Last verify 2026-11-07:** PASS — long traps (rate 1.0, ratio 0.89, breaks 0), self-test 78, fingerprint, size
  3423/3500 (98%), hardcode, docs.
**Not verified:** benefit on blind projects (0 slips to fix); n=1 on the 3 former exam projects; Opus vs Opus stock;
  gradebook tokens 1.37x; simulated junior ≠ real junior; mild over-recording (rules files hold facts too).
**Hidden exam:** retired (now visible); vault suite spent, next seal replaces it.
