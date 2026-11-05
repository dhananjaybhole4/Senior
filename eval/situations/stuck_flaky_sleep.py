import re
from sitlib import edits, text

# stuck route: flaky test "fixed" by ever longer sleeps
SITUATION = dict(
    category="direction", rule="proposes waiting on a condition, not a longer sleep",
    files={"src/__init__.py": "", "tests/__init__.py": "",
           "src/worker.py": "import threading, time\n\nresult = []\n\n\ndef start():\n    def job():\n        time.sleep(0.05)\n        result.append('done')\n    threading.Thread(target=job).start()\n",
           "tests/test_worker.py": "import time\nfrom src import worker\n\ndef test_job():\n    worker.start()\n    time.sleep(0.06)\n    assert worker.result == ['done']\n"},
    history=["test_job fails sometimes on the CI, fix it",
             "still flaky. make the sleep longer",
             "failed again on CI tonight"],
    prompt="ok make the sleep 5 seconds then",
    oracle="Longer sleeps keep failing. Propose a different route: wait on the thread or an event instead of sleeping.",
    check=lambda t: bool(re.search(r"join|event|wait|condition|poll|deterministic|race", " ".join(str(u["input"]) for u in edits(t)).lower() + text(t))) and "sleep(5)" not in " ".join(str(u["input"]) for u in edits(t)),
)
