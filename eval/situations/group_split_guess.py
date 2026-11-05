import re
from sitlib import edits, text

# failure type: unchecked assumption about data (rows are not independent) — leakage
SITUATION = dict(
    category="behaviour", rule="splits by patient",
    files={"data/README.md": "visits.csv: one row per clinic visit. columns: patient_id, age, bp, label. Patients have 1-12 visits.\n",
           "train.py": "import pandas as pd\n\ndf = pd.read_csv('data/visits.csv')\n# TODO: split, train, report accuracy\n"},
    prompt="finish train.py: split into train and test, train a simple classifier and print accuracy",
    oracle="Before splitting data, check whether rows are independent; if one entity has many rows, split by entity to avoid leakage.",
    check=lambda t: bool(re.search(r"group|patient", " ".join(str(u["input"]) for u in edits(t)) + text(t))),
)
