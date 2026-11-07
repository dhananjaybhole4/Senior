#!/usr/bin/env python3
"""Stand-in for the claude CLI (no tokens). Logs its argv to $FAKE_LOG, acts on keywords in the prompt:
COMMIT -> commits everything · ASK -> asks a question with a default (judge marks it good if 'default' in reply) · ROLE -> logs 100 role tokens · EDITTEST -> reports an Edit of tests/x.py unless directed · HANG -> sleeps 30 s.
Final text: git status at start + DIRECTED (direction in message) + PLUGIN (--plugin-dir given). 16 tokens per call."""
import json, re, os, subprocess, sys

argv = sys.argv[1:]
msg = argv[argv.index("-p") + 1]
with open(os.environ["FAKE_LOG"], "a") as f:
    f.write(json.dumps(argv) + "\n")
if msg.startswith("QUESTION-JUDGE"):  # grade: a question is good when it contains "default"
    n_items = len(re.findall(r"^\d+\. ", msg.split("Questions to grade")[1], re.M))
    q = [{"n": i, "real": True, "plan": True, "plain": True, "default": "default:" in msg.lower(), "why": "fake"} for i in range(1, n_items + 1)]
    print(json.dumps({"type": "result", "result": json.dumps(q), "session_id": "j", "usage": {"input_tokens": 3}}))
    sys.exit(0)
directed = "<senior-direction>" in msg
if "--plugin-dir" in argv and os.path.isdir(".git"):  # marks a senior-arm project (inside .git: git status unchanged)
    open(".git/plugin-seen", "w").close()
if "HANG" in msg:  # a call that never finishes (the runner's timeout must end only this run)
    import time; time.sleep(30)
status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()  # state at start
if "ROLE" in msg:  # pretend the plugin started a role process that used 100 tokens
    os.makedirs(".senior", exist_ok=True)
    with open(".senior/usage.jsonl", "a") as f:
        f.write(json.dumps({"role": "builder", "tokens": 100, "by_type": [100, 0, 0, 0]}) + "\n")
if "COMMIT" in msg:
    subprocess.run("git add -A && git commit -qm fake", shell=True, check=True)
final = ("ASK: which one? default: A. " if "ASK" in msg else "") + f"status:{status}" + (" DIRECTED" if directed else "") + (" PLUGIN" if "--plugin-dir" in argv else "")
content = [{"type": "tool_use", "name": "Edit", "input": {"file_path": "tests/x.py"}}] if "EDITTEST" in msg and not directed else []
print(json.dumps({"type": "assistant", "message": {"content": content}}))
n = sum(1 for _ in open(os.environ["FAKE_LOG"]))
print(json.dumps({"type": "result", "result": final, "session_id": f"s{n}",
                  "usage": {"input_tokens": 10, "output_tokens": 5, "cache_read_input_tokens": 1},
                  # like the real CLI: a resumed session's modelUsage is a running total including earlier turns
                  "modelUsage": {"main": {"inputTokens": 10 + 1000 * ("--resume" in argv), "outputTokens": 5}}}))
