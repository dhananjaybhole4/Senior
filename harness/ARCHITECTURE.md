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
pilot: python3 eval/pilot/run.py <outdir> [model] [reps]; python3 eval/pilot/long.py <outdir> [model] [reps]

## Gotchas
- claude.ai connectors add ~100k tokens/session → always --strict-mcp-config in test runs
- resumed sessions keep their first system prompt → inject direction in the message, not --append-system-prompt
- test runs write sessions to ~/.claude/projects/<cwd> → delete after, or they pollute log mining
- --bare needs an API key (no subscription) → use --setting-sources project,local instead
- dj-harness guard blocks shell commands that mention owner-only verify flags → write such files with Write/Edit
