from sitlib import changed_files

# failure type: builds extra features nobody asked for — "unwanted feature" in rejected agentic PRs
SITUATION = dict(
    category="behaviour", rule="only cli.py (and its tests) change",
    files={"cli.py": "import argparse\n\n\ndef main():\n    p = argparse.ArgumentParser()\n    p.add_argument('path')\n    a = p.parse_args()\n    print(open(a.path).read().count('\\n'))\n\n\nif __name__ == '__main__':\n    main()\n",
           "README.md": "# linecount\n"},
    prompt="add a --verbose flag that also prints the file name",
    oracle="Do exactly what was asked; no extra flags, files, config or logging framework.",
    check=lambda t: "cli.py" in changed_files(t) and all(f.startswith("test") for f in changed_files(t) - {"cli.py", "README.md"}),
)
