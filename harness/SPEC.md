# SPEC — senior
_Approved by owner: 2026-11-04. Changes need owner approval._

## Goal
`/senior`: a Claude Code plugin that lets a junior (intern-level, knows Claude Code) on stock
Claude Code reach a working, well-built project. **Why:** the AI can code, but the junior can't
give it senior direction. **For:** the owner first, then juniors in general.
Senior only steers the AI (what it's told, when, what each role can see). The model is never changed.

## Examples (test situations)
| Situation | Expected Senior behaviour | Note |
|---|---|---|
| Junior: "commit all stuff" with code+tests+docs+config changed | separate commits per concern | typical |
| Junior: "make it work on these videos" (2 samples) | flags too few samples, no sample-tuned values, hidden videos don't get worse | edge |
| Junior: "mark seat empty after 3 frames" at 30 fps | flags 3 frames = 0.1 s before building | edge |
| Clear, small, unambiguous request | just does it, asks nothing | over-asking trap |

## Done when (v0)
| # | Criterion | Checked by |
|---|---|---|
| 1 | ≥80% of visible situations handled (3 runs each) | check: situations |
| 2 | ≥8 of 10 sealed situations handled | holdout |
| 3 | on situations where stock Claude slips (fails ≥1 run), Senior handles ≥80%; situations stock always handles only guard against harm (#4) | check: situations (weak_rate) |
| 4 | 0 situations stock Claude passed that Senior fails | check: regressions |
| 5 | ≤ +30% total tokens vs stock Claude (all processes counted) | check: situations (METRIC tokens) |
| 6 | questions to the junior could change the plan (some answer leads to different work), use plain words, state a default; Senior's good-question rate ≥ stock's + 20 pts (same judge on both), two independent judge passes give good-question rates within 5 pts | check: question judge |
| 7 | each role cannot read what it must not, even when told to try | check: isolation |
| 8 | direction check proposes a real alternative on "stuck route" situations | check: situations (direction) |
| 9 | works on Sonnet and Opus | check: situations --model both (M5) |
| 10 | built-in harness works on a made-up project with nothing of the owner's setup | manual: owner tries it once |

## Non-functional
- Effectiveness first: use whatever raises the score (rules, hooks, roles, scripts, checks).
  Every component must improve the score in a with/without test, or it is removed. The only
  cost limit is #5 (≤ +30% tokens vs stock).

## Out of scope (v0)
- Drift in long sessions; expected-to-fail test types; use on work projects (on hold).

## Unknowns
| Unknown | Plan |
|---|---|
| SWE-chat license, size | explore ≤1 session, ask before download |
| What plugin hooks/processes can enforce on WSL | explore ≤1 session |
| Do failures appear in long real sessions? | explore ≤1 session on public sessions |
