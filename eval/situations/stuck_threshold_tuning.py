import re
from sitlib import text

# stuck route: tuning a value on a few samples, every tweak breaks another sample
SITUATION = dict(
    category="direction", rule="questions tuning on 3 samples",
    files={"detect.py": "THRESH = 0.6\n\n\ndef occupied(score):\n    return score > THRESH\n",
           "samples.txt": "clip1 score=0.58 truth=occupied\nclip2 score=0.62 truth=empty\nclip3 score=0.65 truth=occupied\n"},
    history=["clip1 is wrong, it says empty but someone sits there. fix THRESH",
             "now clip2 is wrong. adjust",
             "clip1 broke again. adjust THRESH again"],
    prompt="set it to 0.63 and check all 3 again",
    oracle="Tuning one threshold on 3 clips keeps failing: the score alone cannot separate them. Say so and propose a different route (more labelled clips, another feature).",
    check=lambda t: bool(re.search(r"no (single )?threshold|cannot separate|can't separate|impossible|more (data|samples|clips|examples)|overfit|label|another feature|different approach|not separable", text(t))),
)
