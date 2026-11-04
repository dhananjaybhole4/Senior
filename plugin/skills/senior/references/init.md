# init: set up the harness with the junior

Goal: get what the junior wants into `.senior/` so results can be judged by behaviour, not by reading code.

1. Read the repo briefly (README, layout, config). Restate the goal in one line.
2. Interview, max 2 questions per message, each with a default. Cover only what is still unknown:
   goal and who uses it · 2-4 example situations with real numbers · done-when (measurable) ·
   never / ask-first rules · data: how many samples, which ones stay hidden.
3. Write, then show the junior in plain words and get a yes:
   - `.senior/SPEC.md` (≤60 lines): goal, examples table, done-when table where each line names its check.
   - `.senior/BOUNDARIES.md` (≤15 rules): never / ask first / free.
   - `.senior/checks.toml`: `[[check]]` entries with `name`, `cmd` (exit 0 = pass), `why` (SPEC line).
   - `.senior/STATUS.md` (≤30 lines, overwritten): done / next / needs junior / not verified.
   - `.senior/DECISIONS.md`: one line per decision, `date — decision — why — who`.
4. Acceptance tests: `role.py test-writer "Write acceptance tests in .senior/checks/ for SPEC done-when lines …"`.
   Show the junior what each test checks in plain words. On yes: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify.py lock`.
5. Commit the harness (one commit). Next step: `/senior run`.
