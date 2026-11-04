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
