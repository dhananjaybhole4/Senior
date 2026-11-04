# run: build until done or a question for the junior

Read `.senior/SPEC.md`, `BOUNDARIES.md`, `STATUS.md`. Run `verify.py` once for a baseline.

Loop:
1. Pick the next unblocked step in STATUS; small slice, traced to one SPEC line.
2. `role.py builder "<step, SPEC line, which checks must turn green; do not edit .senior/>"`.
3. `verify.py`. Read results, not code. Overwrite STATUS; log judgment calls in DECISIONS.
4. Repeat.

Stop and tell the junior (≤5 lines) when: a milestone's checks pass · a lasting decision is needed
(rule 3) · the same check failed 3 times · something contradicts SPEC.

**Direction check** when stuck (same check failed 3 times, or progress stalled):
`role.py reviewer "Goal, results and decisions are in .senior/. The current route is stuck: <what failed>. Propose one different route and why."`
Bring the junior the alternative with a recommendation; do not keep retrying the same route.

Never: change approved files or checks without the junior's yes · weaken a check · report done without a full verify PASS.
