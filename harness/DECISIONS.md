# DECISIONS — senior
<!-- one line each: date — decision — why — who (owner/agent/delegated) -->
2026-11-04 — AI model never changed; Senior only steers (text, timing, what each role sees) — owner's founding rule — owner
2026-11-04 — Test situations at save points, not whole projects — 50-100× cheaper, failures pinpointed — agent, owner agreed
2026-11-04 — Test runs: --setting-sources project,local, --strict-mcp-config, 6 built-in tools, sequential — measured 617k→56k tokens/run; owner trades time for tokens — agent
2026-11-04 — v0 scope: useful+easy questions, ask before lasting decisions, flag unrealistic numbers, no sample-hardcoding, direction check; drift + expected-fail tests in v1 — pilots: plain Claude failed these, text direction fixed them — owner
2026-11-04 — Senior is self-contained: stock Claude Code + Senior only; carries general rules from owner's CLAUDE.md (agent picks), not personal ones — owner won't use own setup with Senior — owner/delegated
2026-11-04 — Built-in harness is Senior's own design inspired by dj-harness, not a copy; lives in .senior/ to avoid clashing with dj-harness hooks — owner + agent
2026-11-04 — Isolated roles (test-writer, builder, direction reviewer) as separate processes/folders — "can't look even if they try" — owner
2026-11-04 — Checks judge saved results tagged with plugin hash; verify spends no tokens — token economy — agent
2026-11-04 — "Clearly above stock" = ≥20 points; code budget 3000 lines; skill ≤150 lines — agent's numbers, owner may change — delegated
2026-11-04 — When something doesn't work: consider architecture change, never patch/hardcode — owner
2026-11-04 — Architecture may change on research/test evidence, logged here — owner delegated
2026-11-04 — Holdout situations generated later (M2) by a separate process the builder never sees — format not defined yet; avoids builder seeing them — agent
2026-11-04 — SWE-chat (SALT-NLP/SWE-chat): ODC-BY (attribution, commercial OK), gated (HF login + accept terms), 47 GB total; 17,968 sessions; transcripts ~0.5 MB median; sessions.parquet 37 MB — explore task 1 — agent
2026-11-04 — Plugin can ship skills/agents/hooks/bin/MCP but NOT permissions or sandbox settings (plugin settings only take `agent`, `subagentStatusLine`) — plugins-reference docs — agent
2026-11-04 — Built-in Bash sandbox unusable here: refuses to start without socat (bwrap present); also it never covers Read/Grep tools — tested with failIfUnavailable — agent
2026-11-04 — Role isolation = run each role's `claude -p` inside bubblewrap with forbidden folders replaced by empty tmpfs; tested: cat/python see nothing, writes discarded, claude signs in and answers inside. Linux/WSL only (no macOS) — no new dependency, covers every tool — agent, ratified by owner 2026-11-04
2026-11-04 — An agent run with all permissions told to "try to read the hidden file" is blocked by the auto-mode classifier → isolation check #7 needs an owner-approved way to run — observed — agent
2026-11-04 — Isolation check #7: the attacker gets a normal task that needs the hidden file, default permissions (Q2 a) — no auto-mode classifier conflict, still tests the wall — owner
2026-11-04 — No socat; the bubblewrap wrapper is the only isolation wall in v0 (Q3 a) — tested, no new dependency — owner
2026-11-04 — Project venv (.venv, Python 3.14.4) + pinned requirements.txt; setup in README — owner wants it reproducible on other devices — owner
2026-11-04 — SWE-chat: download sessions + conversations tables only (6.5 GB) via eval/fetch_swechat.sh into gitignored eval/data/; pyarrow 26.0.1 added to read them (Q1 b) — all user messages, skips unused 40 GB — owner
2026-11-04 — Token rule for data mining: scripts filter/count the data; the AI reads only small filtered samples — owner asked for token efficiency — owner
2026-11-04 — Added resource: arXiv 2605.29442 labels (MIT, 37 MB, 16,118 failures in 20,574 sessions, joins to SWE-chat) via eval/fetch_data.sh — owner said use good internet resources; small + permissive — agent, ratified by owner 2026-11-04
2026-11-04 — Explore 3 answer: yes, failures appear in long real sessions — 80-83% of CLI sessions with 21+ user turns have ≥1 vs 16% at 1-5; failure TYPES are the same at every length (constraint violation ~50%, ignored instruction ~50%, false self-report ~27%, misread intent ~23%); per-message rate falls 8.7→2.0/100 but labels may undercount long sessions (paper drops truncated evidence). Vague Requester (junior proxy) looks like the rest. ⇒ v0 targets stand; add false self-report to the M2 situation bank; drift stays out of v0 — eval/research/failures_by_length.py — agent
2026-11-04 — `claude plugin eval` reviewed: has baseline arm/runs/LLM graders/cost cap, but Bash needs sandbox (socat), history-file cases get no baseline, no simulated user — docs plugin-evals — agent
2026-11-04 — Q4 a: own test runner extending eval/pilot (baseline arm for every situation incl. history, simulated junior, exact tokens, bwrap); M1 plan approved (runner + self-tests, sanity round pilot 8 × stock/oracle × 2 runs needs ≥20 pt gap, plugin skeleton + /senior harness core in .senior/ + bwrap role launcher, claude plugin validate) — owner "ok" to recommendation — owner
2026-11-04 — Situation format: one Python file per situation (eval/situations/<id>.py, SITUATION dict with a check function); holdout situations use the same format — reuses pilot checks, no parser — agent, ratify
2026-11-04 — Oracle direction goes in the message (<senior-direction>) for every situation, not the system prompt — one code path, works for resumed history — agent, ratify
2026-11-04 — Simulated junior deferred from M1 runner to M2 — nothing answers questions until the plugin asks them; needed for the questions check — agent, ratify
2026-11-04 — Role views: test-writer sees only .senior/ (writes there), builder sees all but .senior/checks* read-only, reviewer reads .senior/ only — need-to-know per design; tested with a fake CLI (eval/tests) — agent, ratify
2026-11-04 — M1 sanity round passed: stock 5/8 vs oracle 8/8 handled (gap 37.5 pts ≥ 20), Sonnet, 2 runs; stock already passes 5 single-turn pilot situations ⇒ M2 bank needs harder/history situations — eval/results/sanity.json — agent
2026-11-04 — Skill frontmatter allowed-tools `Read(/${CLAUDE_PLUGIN_ROOT}/**)` + `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/*)`: without it the junior's session cannot read the skill's references (smoke: init failed); absolute Read rules need the leading `/` — smoke runs 2026-11-04 — agent, ratify
2026-11-04 — Q5: the 5 "agent, ratify" decisions of 2026-11-04 ratified — owner "ok" — owner
2026-11-04 — Q6 a: real-agent isolation test (role told to break out) allowed in M2 — SPEC #7 "even when told to try" — owner "ok" to recommendation
2026-11-05 — M2 plan approved: D1 done = full round with real numbers for situations/regressions/tokens/questions/isolation (passing = M3, direction = M3); D2 sources = owner corrections (local) + public-data failure types + agent-written, half with history; D3 a keep stock-failing + 5 easy guards (holdout is the honest score); D5 holdout by a separate process, owner seals; D6 b Senior loaded from the first history turn; D7 budget ≈13M tokens (≤6 half rounds + 1 full); D8 owner spot-checks 5 judge verdicts after round 1 — owner
