# init: set up the harness with the junior

Goal: get what the junior wants into `.senior/` so results can be judged by behaviour, not by reading code.
Keep it as small as the project: a one-script tool gets a few lines, not a document set.

1. Read the repo briefly (README, layout, data files). Restate the goal in one line.
2. Ask only what is unknown and would change the build (max 2 questions, each with a default). A clear
   request needs no interview.
3. Write:
   - `.senior/SPEC.md` (one-script tool ≤15 lines, bigger project ≤60): goal, 2-4 examples with real numbers,
     done-when lines that each name their test.
   - `.senior/BOUNDARIES.md`: the junior's lasting rules (rule 13), plus never / ask-first if any.
   - `.senior/checks.toml`, exactly:
     `[[check]]` / `name = "acceptance"` / `cmd = "python3 -m unittest discover -s .senior/checks"` / `why = "SPEC done-when"`
   Create `STATUS.md` only when work stops unfinished, `DECISIONS.md` only at the first lasting decision.
4. Acceptance tests: `role.py test-writer "Write acceptance tests for SPEC done-when lines … as unittest
   files .senior/checks/test_*.py (standard library only)"`. Then `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify.py lock`.
5. Tell the junior in ≤5 plain lines what the tests check and that you are building now unless they object;
   then build (references/run.md) in the same turn. Commit the harness and the code separately.
