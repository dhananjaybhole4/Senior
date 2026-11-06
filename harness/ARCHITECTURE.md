# ARCHITECTURE — senior (agent-facing; keep current) — M1 skeleton built 2026-11-04

## Map
plugin/ — shipped plugin: .claude-plugin/plugin.json; skills/senior/SKILL.md (route + 10 rules + roles) + references/{init,run}.md;
  scripts/verify.py (.senior/checks.toml runner, `lock` = fingerprint); scripts/role.py (bwrap roles, tokens → .senior/usage.jsonl). No hooks yet.
eval/ — run.py (arms base/oracle/senior, fresh git repo per run, history built once then forked, tokens = all models + role usage);
  situations/<id>.py (30; SITUATION dict, check(t) on {tools, final, new_commits, branches, repo}); sitlib.py (helpers incl. committed_files, changed_files, read, tests_pass);
  judge.py (Haiku question grader, SPEC #6); isolation.py (SPEC #7: forbidden reads/writes per role, sandbox-only + real role agents → latest.json "isolation"); validate.py (situations build + checks run, counts only); rejudge.py (re-grade saved replies);
  merge_arms.py (Senior-only round + stock rows of an earlier round → one result file; isolation carried over);
  longrun/: projects/<name>.py = long project (FILES, LATER_FILES, WORLD, SCRIPT, TRAPS {check: D-kind}, rules_kept, hidden grade());
    projects: expenses, gradebook, photos, plant; projects/_common.py = shared grading helpers (underscore = not a project).
    run_long.py qualify|latest = projects × reps × arms (one session per run + Haiku junior) → long_qualify.json / long_latest.json;
    finished runs saved in results/long_runs/, reused while project file, model, cap (+plugin for senior) unchanged.
  plugin/scripts/ledger.py: UserPromptSubmit hook, shows .senior/BOUNDARIES.md (standing rules) with every request.
  run.py test projects live in tempdir/proj-runs/<round>/<hash>/app (neutral, outside repo); logs in runs/.
  make_holdout.py (owner runs; exam writer in bwrap with visible situations/pilot/results/runs/.git hidden; --fresh = agent-run, 15 new visible situations → eval/situations_fresh/, plugin/ hidden too);
  tests/ (fake claude CLI, zero tokens); results/<name>.json
runs/ — generated test projects + logs per round (repo root, gitignored; outside the code-size count)
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
round: python3 eval/run.py [--only ID..] [--arms base senior] [--reps 3] [--out eval/results/latest.json] [--max-tokens N] [--resume]  (progress saved per situation to <out>.partial.json)
plugin-only change: python3 -B eval/run.py --arms senior --reps 2 --out eval/results/senior_only.json; python3 -B eval/merge_arms.py eval/results/senior_only.json eval/results/latest.json eval/results/latest.json
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
- history built per group: stock (base+oracle) and senior (plugin from turn 1); arm tokens = its runs + its group history
- bwrap tmpfs-hidden folders accept writes inside the sandbox but nothing reaches disk
- plugin skill reading its own files needs allowed-tools Read(/${CLAUDE_PLUGIN_ROOT}/**) (absolute path rules start with //)
- child `claude -p` without stdin=DEVNULL waits 3 s for stdin each call
- importing plugin scripts from eval writes __pycache__ into plugin/ → plugin hash changes → all result checks go stale; use python -B
