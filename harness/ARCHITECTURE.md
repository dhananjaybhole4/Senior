# ARCHITECTURE — senior (agent-facing; keep current) — PLANNED, nothing built

## Map
plugin/ — the shipped Claude Code plugin (.claude-plugin/plugin.json, skills/senior/, hooks/, scripts/)
eval/ — test machinery: situations/, run.py (writes eval/results/latest.json), tests/ (self-test)
eval/pilot/ — throwaway pilot runner from 2026-11-04 (scenarios.py, run.py, long.py); reference only
harness/ — dj-harness rulebook used to BUILD Senior (not shipped)

## Data flow
junior request → Senior skill (interview, spec in .senior/) → just-in-time hooks inject direction at risky moments →
roles as separate processes (test-writer: spec only; builder: spec + read-only tests; direction reviewer: goal + results + decisions) →
scripts produce outcome report → Senior decides / asks junior

## Key choices
see harness/DECISIONS.md

## Run
setup: python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt; keep venv active for verify/eval
pilot: python3 eval/pilot/run.py <outdir> [model] [reps]; python3 eval/pilot/long.py <outdir> [model] [reps]

## Gotchas
- claude.ai connectors add ~100k tokens/session → always --strict-mcp-config in test runs
- resumed sessions keep their first system prompt → inject direction in the message, not --append-system-prompt
- test runs write sessions to ~/.claude/projects/<cwd> → delete after, or they pollute log mining
- --bare needs an API key (no subscription) → use --setting-sources project,local instead
- role isolation: `bwrap --dev-bind / / --tmpfs <hidden dir> -- claude -p …` (tested 2026-11-04); built-in sandbox needs socat (missing)
- `claude plugin eval` exists (plugin eval suites) → check before building eval/run.py (reuse first)
- auto-mode classifier blocks headless agents told to break isolation → adversarial isolation runs need owner OK
- system `pip3` on PATH belongs to another project's venv → always `python -m pip` inside .venv
- dj-harness guard blocks shell commands that mention owner-only verify flags → write such files with Write/Edit
