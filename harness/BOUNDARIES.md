# BOUNDARIES — senior
_Approved by owner: 2026-11-04. Changes need owner approval. Max 15 rules._

## Never
1. Change the owner's live ~/.claude setup (dj-harness, CLAUDE.md, settings) or the AI model.
2. Use work projects (in-vehicle-user-identification) or work data in tests.
3. Send the owner's chat logs anywhere; read them locally only.
4. Tune Senior's text to specific test situations; rules must be general.
5. Hardcode values or special-case sample/test inputs.
6. Weaken, skip or delete a check or test to make it pass.
7. Touch the holdout vault or harness/_holdout_staging/ contents.
8. Add attribution lines in commits or PRs.

## Ask first
9. New dependency or paid service; dataset downloads (license + size first).
10. A test round bigger than ~30 situations × 3 runs; anything irreversible.

## Free
11. Code and tests in this repo; small focused commits; push to GitHub.
12. Architecture changes backed by research or test results, logged in DECISIONS with evidence.
13. Test runs within budget: sequential, connected apps off, only affected situations rerun.
