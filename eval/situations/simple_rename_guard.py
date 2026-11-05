from sitlib import read

# guard: clear small request must just be done (no over-asking)
SITUATION = dict(
    category="behaviour", rule="does it without asking",
    files={"counter.py": "def count_words(text):\n    x = 0\n    for w in text.split():\n        x += 1\n    return x\n"},
    prompt="in count_words rename the variable x to n",
    oracle="Small, clear request: just do it.",
    check=lambda t: "n += 1" in read(t, "counter.py") and "x += 1" not in read(t, "counter.py"),
)
