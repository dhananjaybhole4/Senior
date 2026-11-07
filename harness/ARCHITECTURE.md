# ARCHITECTURE — senior (agent-facing; keep current) — M1 skeleton built 2026-11-04

## Map
plugin/ — shipped plugin (rules-file only since 2026-11-06): .claude-plugin/plugin.json; hooks/hooks.json;
  scripts/primer.py (SessionStart: the one instruction, record lasting rules in .senior/BOUNDARIES.md);
  scripts/ledger.py (UserPromptSubmit: shows that file with every request, silent without it). No skill, no slash command.
eval/ — run.py (arms base/oracle/senior, fresh git repo per run, history built once then forked, tokens = all models + role usage);
  situations/<id>.py (30; SITUATION dict, check(t) on {tools, final, new_commits, branches, repo}); sitlib.py (helpers incl. committed_files, changed_files, read, tests_pass);
  judge.py (Haiku question grader, SPEC #6); validate.py (situations build + checks run, counts only); rejudge.py (re-grade saved replies);
  merge_arms.py (Senior-only round + stock rows of an earlier round → one result file; isolation carried over);
  longrun/: projects/<name>.py = long project (FILES, LATER_FILES, WORLD, SCRIPT, TRAPS {check: D-kind}, rules_kept, hidden grade());
    projects: expenses, gradebook, invoices (guard only: junior changes a stated rule), photos, plant, tasks;
      bin_reminder, cafe_board, foodbank_rota (retired blind exam 2026-11-07, written by the blind writer); projects/_common.py = shared grading helpers (underscore = not a project).
    run_long.py qualify|latest = projects × reps × arms (one session per run + Haiku junior) → long_qualify.json / long_latest.json;
    latest reuses qualify_<p>_base_r<n> stock runs when their key matches (stock is unchanged between rounds);
    latest --senior-only --model M = senior arm only on model M → latest-M_* run files + long_latest_M.json;
    exam.py DIR = hidden exam (holdout cmd): qualify + latest on sealed projects, everything in a deleted neutral
    temp folder, prints counts only; holds only with ≥1 stock-slipped trap; 0-token preflight first; grader crash/hang or hung call = that run fails/stops (counted), never the exam.
    finished runs saved in results/long_runs/, reused while what the model sees (files, script, WORLD, junior prompt),
    model, cap (+plugin for senior) are unchanged; a grader change only re-grades the kept project folder (no model calls).
    Every run is graded twice: normal, then with the built code on Python 3.8 (.tools/py38/python/bin/python3,
    gitignored; python-build-standalone 3.8.20+20241002 x86_64 linux install_only, sha256 285e141c…) → 'runs on Python 3.8'.
  run.py test projects live in tempdir/proj-runs/<round>/<hash>/app (neutral, outside repo); logs in runs/.
  make_holdout.py --long (agent may run: 3 blind long projects → staging, writer can't see visible projects/notes/plugin/old runs/transcripts);
  make_holdout.py (owner runs; exam writer in bwrap with visible situations/pilot/results/runs/.git hidden; --fresh = agent-run, 15 new visible situations → eval/situations_fresh/, plugin/ hidden too);
  tests/ (fake claude CLI, zero tokens); results/<name>.json
runs/ — generated test projects + logs per round (repo root, gitignored; outside the code-size count)
eval/pilot/ — throwaway pilot runner from 2026-11-04 (scenarios.py, run.py, long.py); reference only
harness/ — dj-harness rulebook used to BUILD Senior (not shipped)

## Data flow
session start → primer instruction → junior states a rule → model writes a line to .senior/BOUNDARIES.md →
every later request → ledger hook prints the file next to it → model checks the request against it.
Short-situation machinery (run.py, situations/, judge, merge_arms) is kept but no check uses it now.

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
- `claude plugin eval` exists (plugin eval suites) → check before building eval/run.py (reuse first)
- auto-mode classifier blocks headless agents told to break isolation → adversarial isolation runs need owner OK
- system `pip3` on PATH belongs to another project's venv → always `python -m pip` inside .venv
- dj-harness guard blocks shell commands that mention owner-only verify flags → write such files with Write/Edit
- history built per group: stock (base+oracle) and senior (plugin from turn 1); arm tokens = its runs + its group history
- bwrap tmpfs-hidden folders accept writes inside the sandbox but nothing reaches disk
- plugin skill reading its own files needs allowed-tools Read(/${CLAUDE_PLUGIN_ROOT}/**) (absolute path rules start with //)
- child `claude -p` without stdin=DEVNULL waits 3 s for stdin each call
- importing plugin scripts from eval writes __pycache__ into plugin/ → plugin hash changes → all result checks go stale; use python -B
