# INTERVIEW LOG — senior (agent-facing; never re-ask what is here)

## Readiness
| Area | State | Gap |
|---|---|---|
| A Purpose | ready | user = owner (intern-level); value = direction ability > result |
| B Context | ready | pilots + 2026 research done |
| C Inputs & outputs | ready | in = junior requests + project; out = direction, harness files, built project; samples = situation bank (plan) |
| D Success | ready | SPEC done #1-10 approved |
| E Boundaries | ready | rules draft Q7 accepted; budget delegated |
| F Risks & unknowns | weak | premortem Q8 done; isolation scope open |
| G Approach | ready | v0 scope confirmed Q4 |
| H Working agreement | ready | M1-M5, stop after each, short updates |

## Open items
- Dogfooding on in-vehicle-user-identification: HALTED by owner (2026-11-04) until further notice → test on made-up projects only.
- SWE-chat licence/size: done (DECISIONS 2026-11-04); download waits on Q1.
- Explore task: mine 2026 correction sources into a lesson bank — arXiv 2605.29442 (20,574 sessions, 7 misalignment forms), 2602.17037 (Wink taxonomy + self-intervention), 2603.05941; CLAUDE.md rule write-ups (anecdotal). Owner asked for this.

## Prefilled (decided before init, in session 9f3b28c8)
- Goal: Claude Code plugin `/senior`; non-senior gets a well-built project with low effort; AI model never changed, only steered.
- Evidence: oracle pilot (8 short situations) + long-history test (4 situations, ~6-turn history), Sonnet, global CLAUDE.md off.
  Plain Claude failed: one big commit 0/2, branch name without asking 0/2, too many questions to a junior 0/2, 3-frames unflagged 1/3 (long).
  Plain Claude passed: build-before-go-ahead, test cheating, leakage. Perfect text direction fixed every failure.
- v0 scope: one skill (question style: explain first, ≤2 questions with defaults) + just-in-time hooks (commit, naming, user-given numbers) + correction log; tests = existing runner + SWE-chat-derived situations; run on Opus too.
- Token rules for tests: `--setting-sources project,local --strict-mcp-config --tools <6>`; sequential runs; owner trades time for tokens.
- Owner's real corrections (~20 in 223 msgs): questions before explaining/jargon ~6, decided without asking ~4, wrong domain assumption ~4, over-complicating ~3, missed constraint ~2.

## Log
### 2026-11-04 init
- Q1 who/what/measure → User = owner (intern-level, knows Claude Code + agents). Problems: (a) Claude lacks real-world conditions; only source is junior's vague input; (b) Claude takes its own route even when directed, junior goes along because Claude knows more, route doesn't lead to success; (c) Claude hardcodes even when told to generalise. Success = result reached; MORE important = Senior's ability to direct Claude, interview out every needed detail, send owner to research when a key decision lacks info.
  - NEW vs v0 scope: (b) drift from agreed direction and (c) hardcoding were not in the pilot tests → must decide in/out of v0.
  - Weak: success not yet measurable.
- Q2 real wrong-route case → (1) Given 2 sample videos, Claude tuned code to them, never flagged "only 2 samples → this is hardcoding, not generalisable". Gap = judgment about sample size / generalisation, not coding. (2) Tests written from architecture: some failures are EXPECTED (out of scope), agent treats every test as must-pass → matches design's typed tests (hard gate/target/stretch/diagnostic). (3) Core ask: "thousands of such things matter that I can't say; agent should do it right" → Senior must supply unspoken senior judgment. When noticed / cost: not answered.
- 🎯 Q3 eval design (medium, ok): pass = don't hardcode, weigh generalisation; fail = algorithm fits the 2 videos but irrelevant in general. Missing: situation + observable signals. Senior version: hidden extra videos (holdout) + flag-sample-size + hardcode scan.
- Q4 v0 scope → 1 reframed: questions are fine; they must extract the most important info AND be easy for a junior (not 'fewer'). 2,3,4 ok. 5 ok + extension: if the agreed direction itself isn't moving toward the output, reconsider (replan). 6 ok. Confirmed: v0 = 1 (useful+easy questions), 2 (ask before lasting decisions), 3 (flag unrealistic numbers), 4 (hardcoding/generalisation), + direction check (event-triggered fresh reviewer: route reaching output? else 2 alternatives → owner). v1 = 5 drift, 6 expected-fail tests.
- 🎯 Q5 eval design (easy, ok): owner target 8-9 of 10 situations, 10 = perfect. Draft criteria proposed: ≥80% on situations (3 runs each), ≥ baseline+30 pts, 0 regressions vs plain Claude, holdout same rule, tokens ≤ +30%, ~30 situations not 10.
- Research (owner asked): drift/wrong-direction/hardcoding 2026 sources mapped to Senior; see DECISIONS once approved. Skip: activation steering (needs model weights), RL reward design (we don't train).
- Q6 employer → (a) personal repo on work laptop + push to GitHub: OK for now. (b) trying Senior on in-vehicle-user-identification: halted.
- Q7 boundaries+budget → rules draft accepted (no objection). Budget: delegated to agent, must be token-efficient. Agent choice: iterate on half rounds (~15 situations × 2 runs, only affected ones rerun, stop early when clear); full round (~30×3) only for milestone sign-off. Situation bank from internet sources (taxonomies, SWE-chat, benchmarks) + model knowledge + owner corrections, owner re-asked for this.
- 🎯 Q8 premortem (systems thinking, medium, weak): owner gave 'same failures still happen with Senior'. Agent added: sim≠real, annoyance→turned off, model update, Senior's own text bloats context/gets ignored, owner's CLAUDE.md already covers it, bad direction-check advice→trust lost.
  - NEW requirement: Senior must set up an architecture where roles get only the info they need (need-to-know) to keep quality high → confirm v0 scope of isolation.
- Q9 isolation scope → owner: when using Senior they will NOT use dj-harness; Senior must handle everything incl. the harness (spec, boundaries, checks, holdout, verify, status). Implies v0 = harness core (from dj-harness copy) + roles isolation (all 3, implied yes, confirm in playback) + JIT direction + direction check + question style + correction log. Risk: owner's global settings run dj-harness hooks in every project → may double up with Senior's hooks; must handle.
- Q10 → when using Senior, owner uses ONLY stock Claude Code + Senior (none of own setup: global CLAUDE.md, dj-harness, dj-learn, hooks). ⇒ Senior self-contained; main baseline = stock Claude Code; Senior must carry the needed rules from owner's CLAUDE.md itself (confirming). Milestones M1-M5 proposal pending answer.
- Q11 → a) yes; agent decides which CLAUDE.md rules to carry (delegated, think critically). b) M1 changed: do NOT copy dj-harness; take inspiration, integrate into Senior's own architecture. M1-M5 otherwise OK, stop after each.
- Red-team (7 guards) shown; 🎯 hard Q skipped. Owner asked: think hard about what can go wrong at every architecture step (e.g. senior layer never sees code). Risk review given; key adds: interface contract before tests, mutation-check test quality, structured handoffs, holdout run budget, reviewer gets DECISIONS log, each component must earn its place by ablation, trigger false-pos/neg tests, rule budget.
- Q12 risk review feedback → (1) hardcoding/clutter: prevent via proper instructions to builder + tests catch it; agent keeps cheap scripted metrics as backup (zero token cost). (2) Senior layer must know what the tests are (plain-language list + type), not test code. Owner: 'treat my opinion as information; do what's best to make it work' → design decisions delegated to agent, recorded with reasons.
- Playback approved; SPEC + BOUNDARIES + checks approved 2026-11-04. Holdout deferred to M2 (separate generator process).
- Update 2026-11-06 (after hidden exam 7/10): Q26 self-test → .venv python, yes. Q27 ratify rubric + rule 11, yes. Q28 ≤1 more exam run on this seal, then reseal 10 new, yes. Q29 ~15 new blind-written situations × 2/arm, cap 8M, yes. Q25 (🎯 eval design, hard: two explanations for 37/37 vs 7/10 + how to tell apart) re-asked in more detail; pending. Commit of today's work: asked, not answered.
- 2026-11-06 reset: owner asked "are we going the right direction?" Agent: drifted (rules patched per situation; checks grade capability not direction; graders disagree). Owner approved D1-D7 "direction moment" definition + sort (45 direction / 7 guard) + revert rule 11 build step + keep rule 12 pending ablation. Owner insight: stock handles single moments but loses direction over a big project → that's Senior's job. Agent proposed: long-horizon explore (1 made-up project, simulated junior, both arms, cap ~5M) to test the premise; SPEC write held so it changes once. Asked owner for 2-3 real moments where direction was lost (what, ~which turn). Pending.
- 2026-11-06 owner: test only where stock fails and needs direction; stock-handled = guard (said twice).
- Update 2026-11-06 (after last bounded test, stock 0/3): owner said "think critically, answer and go forward" → agent answered: Q1 keep ledger only (only part with evidence); Q2 done #1/#3/#4 on long projects, drop #5/#6/#8, Opus manual; Q3 retire old exam, new blind long exam; 🎯 Q4 (eval design, hard) skipped by owner → agent: over-blocking (needs lifted-rule guard) and easy, explicit, post-hoc rules (exam must state ≥1 rule casually). Decisions logged "ratify".
