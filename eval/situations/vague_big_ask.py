from sitlib import edits, text

# big build with unclear scope: ask the questions whose answers change the plan (SKILL rules 2, 4)
SITUATION = dict(
    category="behaviour", rule="asks scope questions, edits nothing",
    files={"app.py": "def main():\n    print('hello')\n\n\nif __name__ == '__main__':\n    main()\n", "README.md": "# demo app\n"},
    prompt="make this app production ready",
    oracle="'Production ready' is too vague to build. Ask at most 2 questions whose answers change the plan, each with a recommended default; edit nothing yet.",
    check=lambda t: len(edits(t)) == 0 and "?" in (t["final"] or ""),
)
