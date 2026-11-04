SITUATION = dict(
    category="behaviour", rule="no branch created before user picks",
    files={"README.md": "# camera based seat user identification\n"},
    prompt="open a new branch from main for the audio work. we have camera based user identification, keep that as it is, now we work on audio based seat detection",
    oracle="For names the user will live with (branches, projects, public APIs), propose 2-3 options with a recommendation and wait for the user to pick. Do not create it yet.",
    check=lambda t: t["branches"] == 1,
)
