"""Run each scenario with/without oracle direction, REPS times, and rule-check it.
Usage: python3 run.py <outdir> [model] [reps]"""
import json, os, subprocess, sys, itertools, shutil
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from scenarios import SCENARIOS

OUT = sys.argv[1] if len(sys.argv) > 1 else "pilot"
MODEL = sys.argv[2] if len(sys.argv) > 2 else "sonnet"
REPS = int(sys.argv[3]) if len(sys.argv) > 3 else 2
# Sequential on purpose: owner trades time for tokens; back-to-back runs reuse the prompt cache.
PARALLEL, MAX_TURNS, TIMEOUT_S = 1, 12, 600
BUILTIN_TOOLS = "Read Edit Write Glob Grep Bash"  # fewer tool definitions = smaller prompt, no subagent spawns
TOOLS = "Read Edit Write Glob Grep Bash(git *) Bash(ls *) Bash(cat *) Bash(python -m pytest*) Bash(python3 -m pytest*)"

def git(d, *a):
    return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, check=True).stdout

def write(d, files):
    for p, c in files.items():
        os.makedirs(os.path.dirname(os.path.join(d, p)) or d, exist_ok=True)
        open(os.path.join(d, p), "w").write(c)

def setup(d, sc):
    os.makedirs(d)
    write(d, sc["files"])
    git(d, "init", "-q", "-b", "main"); git(d, "config", "user.name", "junior"); git(d, "config", "user.email", "j@example.com")
    git(d, "add", "-A"); git(d, "commit", "-qm", "initial")
    write(d, sc.get("after_commit", {}))

def run(job):
    name, variant, rep = job
    sc = SCENARIOS[name]
    d = os.path.join(OUT, f"{name}.{variant}.{rep}")
    setup(d, sc)
    cmd = ["claude", "-p", sc["prompt"], "--model", MODEL, "--setting-sources", "project,local", "--strict-mcp-config",
           "--no-session-persistence", "--tools", BUILTIN_TOOLS, "--max-turns", str(MAX_TURNS), "--permission-mode", "acceptEdits",
           "--allowedTools", TOOLS, "--output-format", "stream-json", "--verbose"]
    if variant == "oracle":
        cmd += ["--append-system-prompt", sc["oracle"]]
    p = subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=TIMEOUT_S)
    open(d + ".log", "w").write(p.stdout + "\n#STDERR\n" + p.stderr)
    t, tok, _ = parse(p.stdout, d)
    t["new_commits"] = int(git(d, "rev-list", "--count", "HEAD")) - 1
    t["branches"] = len(git(d, "branch", "--list").split("\n")) - 1
    return dict(scenario=name, variant=variant, rep=rep, passed=bool(sc["check"](t)), tokens=tok, tools=len(t["tools"]))

def parse(stdout, where):
    """stream-json -> ({tools, final}, total tokens, session_id)."""
    tools, final, usage, sid = [], None, {}, None
    for line in stdout.splitlines():
        try: ev = json.loads(line)
        except json.JSONDecodeError: continue
        if ev.get("type") == "assistant":
            tools += [{"name": c["name"], "input": c.get("input", {})} for c in ev["message"]["content"] if c.get("type") == "tool_use"]
        if ev.get("type") == "result":
            final, usage, sid = ev.get("result"), ev.get("usage", {}), ev.get("session_id")
    if final is None:
        raise RuntimeError(f"{where}: no result event; see its .log")
    tok = sum(usage.get(k, 0) for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    return {"tools": tools, "final": final}, tok, sid

if __name__ == "__main__":
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    jobs = list(itertools.product(SCENARIOS, ["base", "oracle"], range(REPS)))
    with ThreadPoolExecutor(PARALLEL) as ex:
        res = list(ex.map(run, jobs))
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    print(f"{'scenario':24} {'rule':36} base   oracle  avg_tokens(b/o)")
    for name, sc in SCENARIOS.items():
        r = {v: [x for x in res if x["scenario"] == name and x["variant"] == v] for v in ("base", "oracle")}
        f = lambda v: f"{sum(x['passed'] for x in r[v])}/{len(r[v])}"
        a = lambda v: sum(x["tokens"] for x in r[v]) // len(r[v])
        print(f"{name:24} {sc['rule']:36} {f('base'):6} {f('oracle'):7} {a('base')}/{a('oracle')}")
