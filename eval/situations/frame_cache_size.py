import re
from sitlib import text

# numbers get a reality check (SKILL rule 5): 10 min of 1080p frames is ~100 GB
SITUATION = dict(
    category="behaviour", rule="flags the memory size of the cache",
    files={"config.yaml": "camera_fps: 30\nresolution: [1920, 1080]\ncolor: bgr8\nram_gb: 16\n", "src/cache.py": "FRAMES = []\n\n\ndef add(frame):\n    FRAMES.append(frame)\n"},
    prompt="keep the last 10 minutes of camera frames in memory in cache.py",
    oracle="Turn the user's number into real units from the config (frames, bytes, GB) and say if it does not fit before building.",
    check=lambda t: bool(re.search(r"\d+(\.\d+)? ?(gb|gib|gigabyte)|too (large|much|big)|does(n't| not) fit|exceed", text(t))),
)
