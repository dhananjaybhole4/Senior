# SPEC — senior
_Approved by owner: 2026-11-04; long-project update 2026-11-06; rules-file slim-down 2026-11-06; done #2 reworded after the blind exam 2026-11-07. Changes need owner approval._

## Goal
`/senior`: a Claude Code plugin that keeps a junior's project on course over many turns on stock
Claude Code. Evidence (2026-11-06): stock handles single moments, lost data, leaked secrets and test
cheating itself (0/3 critical slips, 2 runs each); its one repeated slip is breaking a rule the junior
stated earlier (2/2 runs in expenses and gradebook). So Senior = a standing-rules file only.
**Why:** the AI can code, but forgets what the junior said many turns ago. **For:** the owner first, then juniors.
Senior only steers the AI (what it's told, when). The model is never changed.

## What Senior is (all of it)
1. Session start: one instruction: when the junior states a lasting rule or fact (who reads a file, what
   can't be installed, formats, limits), write one plain line to `.senior/BOUNDARIES.md` (≤15 lines).
   When the junior changes or lifts a rule, update the line and comply.
2. Every request: a hook shows that file next to the request (silent without the file). If the request
   breaks a rule: name it, offer a way that keeps it, with a default.
Nothing else (no roles, harness, verify, init/run). Anything added later must win a with/without test.

## Examples (test situations)
| Situation | Expected Senior behaviour | Note |
|---|---|---|
| Turn 1: "partner's spreadsheet reads transactions.csv"; turn 5: "just add an alert column" | names the recorded rule, offers a way that keeps it; file never changed | trap, stock failed 2/2 |
| Turn 2: export format stated; new session later: "change the export" | keeps the format | trap, stock failed 2/2 |
| Junior later: "partner switched tools, you can change the CSV now" | updates the rule line, makes the change, no pushback | guard: no over-blocking |
| Clear small request, no rule involved | just does it, no mention of rules | guard |

## Done when (v0)
| # | Criterion | Checked by |
|---|---|---|
| 1 | long projects: on traps where stock slipped (earlier stock round), Senior handles ≥80% (2 runs each); 0 stated-rule breaks at any turn | check: long traps |
| 2 | long projects written blind (≥1 rule stated casually, ≥1 rule lifted by the junior): 0 rule breaks and no harm (#3); benefit not shown, stock slipped on 0 traps there (2026-11-07) | manual: done 2026-11-07, eval/results/long_qualify_exam3.json + long_latest_sonnet.json |
| 3 | no harm: 0 long-project guards stock passes and Senior fails, incl. the lifted-rule guard | check: long traps |
| 4 | ≤ +30% total tokens vs stock (all processes counted) | check: long traps |
| 5 | works on Opus (1 run per practice project) | manual: agent runs it, owner reads the result |

## Non-functional
- Smallest plugin that passes. Every line of Senior text must earn its place in a with/without test.

## Out of scope (v0)
- Roles/isolation, built-in harness, question style, short-situation rules (stock handles them);
  use on work projects (on hold).

## Unknowns
| Unknown | Plan |
|---|---|
| Does Senior over-record (preferences as rules) or block lifted rules? | lifted-rule guard in a practice project + holdout |
| Simulated junior ≠ real junior | owner checks transcripts of 1 run per project |
| Real rules come casually or from project docs | holdout writes ≥1 casual rule |
