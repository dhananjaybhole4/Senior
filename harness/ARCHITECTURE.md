# ARCHITECTURE — senior (agent-facing; keep current) — M1 skeleton built 2026-11-04

## Map
plugin/ — shipped plugin: .claude-plugin/plugin.json; skills/senior/SKILL.md (route + 10 rules + roles) + references/{init,run}.md;
  scripts/verify.py (.senior/checks.toml runner, `lock` = fingerprint); scripts/role.py (bwrap roles, tokens → .senior/usage.jsonl). No hooks yet.
eval/ — run.py (arms base/oracle/senior, fresh git repo per run, history built once then forked, tokens = all models + role usage);
  situations/<id>.py (SITUATION dict, check(t) on {tools, final, new_commits, branches}); sitlib.py (check helpers);
  tests/ (fake claude CLI, zero tokens); results/<name>.json; runs/<name>/ logs (gitignored)
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
round: python3 eval/run.py [--only ID..] [--arms base senior] [--reps 3] [--out eval/results/latest.json]
sanity: python3 eval/run.py --arms base oracle --reps 2 --out eval/results/sanity.json
self-test: python -m pytest -q eval/tests

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
- history turns run without the plugin in every arm; senior arm loads it from the risky turn only
- bwrap tmpfs-hidden folders accept writes inside the sandbox but nothing reaches disk
- plugin skill reading its own files needs allowed-tools Read(/${CLAUDE_PLUGIN_ROOT}/**) (absolute path rules start with //)
- child `claude -p` without stdin=DEVNULL waits 3 s for stdin each call
