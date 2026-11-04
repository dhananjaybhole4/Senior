#!/usr/bin/env python3
"""Stand-in for the claude CLI (no tokens). Logs its argv to $FAKE_LOG, acts on keywords in the prompt:
COMMIT -> commits everything · ROLE -> logs 100 role tokens · EDITTEST -> reports an Edit of tests/x.py unless directed.
Final text: git status at start + DIRECTED (direction in message) + PLUGIN (--plugin-dir given). 16 tokens per call."""
import json, os, subprocess, sys

argv = sys.argv[1:]
msg = argv[argv.index("-p") + 1]
with open(os.environ["FAKE_LOG"], "a") as f:
    f.write(json.dumps(argv) + "\n")
directed = "<senior-direction>" in msg
status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()  # state at start
if "ROLE" in msg:  # pretend the plugin started a role process that used 100 tokens
    os.makedirs(".senior", exist_ok=True)
    with open(".senior/usage.jsonl", "a") as f:
        f.write(json.dumps({"role": "builder", "tokens": 100}) + "\n")
if "COMMIT" in msg:
    subprocess.run("git add -A && git commit -qm fake", shell=True, check=True)
final = f"status:{status}" + (" DIRECTED" if directed else "") + (" PLUGIN" if "--plugin-dir" in argv else "")
content = [{"type": "tool_use", "name": "Edit", "input": {"file_path": "tests/x.py"}}] if "EDITTEST" in msg and not directed else []
print(json.dumps({"type": "assistant", "message": {"content": content}}))
n = sum(1 for _ in open(os.environ["FAKE_LOG"]))
print(json.dumps({"type": "result", "result": final, "session_id": f"s{n}",
                  "modelUsage": {"main": {"inputTokens": 10, "outputTokens": 5}, "helper": {"cacheReadInputTokens": 1}}}))
