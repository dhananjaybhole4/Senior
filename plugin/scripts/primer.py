"""SessionStart hook: Senior's one instruction. The junior's lasting rules go to .senior/BOUNDARIES.md,
which ledger.py shows next to every request (the one place stock Claude slipped: rules stated turns ago)."""
print("Standing rules: when the user states a lasting rule or fact about this project (who else reads a file, "
      "what cannot be installed, formats, limits), add one plain line to .senior/BOUNDARIES.md (create it; max 15 "
      "lines) in the same turn. When the user changes or lifts a rule, update or remove its line and do what they ask.")
