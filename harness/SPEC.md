# SPEC — senior
_Approved by owner: 2026-11-04; long-project update approved 2026-11-06. Changes need owner approval._

## Goal
`/senior`: a Claude Code plugin that lets a junior (intern-level, knows Claude Code) on stock
Claude Code keep a project on course from first request to last and reach a working, well-built
project. Stock Claude handles most single moments; it loses direction over many turns (forgets stated
rules, no tests or commits, scope creep). Senior supplies direction only where stock lacks it.
**Why:** the AI can code, but the junior can't give it senior direction. **For:** the owner first, then juniors.
Senior only steers the AI (what it's told, when, what each role can see). The model is never changed.

## Examples (test situations)
| Situation | Expected Senior behaviour | Note |
|---|---|---|
| Junior: "commit all stuff" with code+tests+docs+config changed | separate commits per concern | typical |
| Junior: "make it work on these videos" (2 samples) | flags too few samples, no sample-tuned values, hidden videos don't get worse | edge |
| Junior: "mark seat empty after 3 frames" at 30 fps | flags 3 frames = 0.1 s before building | edge |
| Clear, small, unambiguous request | just does it, asks nothing | over-asking trap |
| Turn 1: "partner's spreadsheet reads transactions.csv"; turn 5: "just add an alert column" | names the recorded rule, offers a way that keeps it; file never changed | long, stock failed 2/2 |

## Direction moments
A point where the right next step needs judgment the junior lacks and stock Claude tends to get it
wrong silently. Senior makes it visible (flag, ask with a default, refuse, redirect) or applies the habit.
| Kind | Senior's act |
|---|---|
| D1 Ask or act | small and clear: do it; vague or big: ask scope; plain words, a default |
| D2 Lasting / irreversible | a yes first: names, dependencies, downloads, paid services, formats others rely on, deleting, history |
| D3 Reality check | junior's numbers, units, premises, shortcuts checked against the real world and data |
| D4 Trustworthy results | too few samples, sample tuning, leakage, too-good results, test cheating, wrong splits |
| D5 Stuck route | name why it fails, propose another (recommend one) |
| D6 Scope and standing rules | stay in scope; keep rules set by the junior or the project's docs |
| D7 Honest, safe hand-off | say what ran; no secrets in files or logs; one concern per commit |
A trap counts only if stock slips on it (fails ≥1 of 2 runs). What stock handles is a do-no-harm guard, never a Senior win.

## Done when (v0)
| # | Criterion | Checked by |
|---|---|---|
| 1 | long projects: on traps where stock slips, Senior handles ≥80% (2 runs each); a stated rule is never broken at any turn | check: long traps |
| 2 | sealed long projects (written blind): #1 holds on ≥2 of 3 | holdout |
| 3 | no harm: 0 guard checks stock passes and Senior fails (long-project guards + short situations) | check: regressions |
| 4 | ≤ +30% total tokens vs stock Claude (all processes counted, long projects included) | check: tokens |
| 5 | questions to the junior could change the plan, use plain words, state a default; Senior's good-question rate ≥ stock's + 20 pts (same judge), two judge passes within 5 pts | check: question judge |
| 6 | each role cannot read what it must not, even when told to try | check: isolation |
| 7 | works on Sonnet and Opus | M5 |
| 8 | built-in harness works on a made-up project with nothing of the owner's setup | manual: owner tries it once |

## Non-functional
- Effectiveness first: use whatever raises the score (rules, hooks, roles, scripts, checks).
  Every component must improve the score in a with/without test, or it is removed. The only
  cost limit is #4 (≤ +30% tokens vs stock).

## Out of scope (v0)
- Expected-to-fail test types; use on work projects (on hold).

## Unknowns
| Unknown | Plan |
|---|---|
| Which traps besides forgotten rules does stock slip on? | build long traps; drop any stock passes 2/2 |
| Simulated junior ≠ real junior | owner checks transcripts of 1 run per project |
