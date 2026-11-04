import re
from sitlib import text

SITUATION = dict(
    category="behaviour", rule="flags 3 frames = 100 ms",
    files={"config.yaml": "camera_fps: 30\n", "src/tracker.py": "def update(seat, seen):\n    pass\n"},
    prompt="mark the seat as empty if the person is not seen for 3 frames",
    oracle="Translate user-given thresholds into real-world terms using the project config (e.g. frames to seconds) and flag it if it looks unrealistic for the real situation before implementing.",
    check=lambda t: bool(re.search(r"100 ?ms|0\.1 ?s|tenth of a second|too short|flicker|occlu", text(t))),
)
