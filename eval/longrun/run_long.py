"""Long-project rounds: each arm builds each project in one continuous session, driven by the project's scripted
junior requests plus a simulated junior (small model) that answers the assistant from the project's WORLD facts.
  python eval/longrun/run_long.py qualify --cap N   stock only -> eval/results/long_qualify.json
  python eval/longrun/run_long.py latest --cap N    both arms  -> eval/results/long_latest.json (gate format)
  python eval/longrun/run_long.py latest --cap N --senior-only --model M   senior on another model, own run files
                                                    -> eval/results/long_latest_M.json (official round untouched)
A trap counts only if stock slipped on it in an EARLIER qualify round (harness/checks/gate.py), so the two rounds
never share runs. Each finished run is saved in eval/results/long_runs/ and reused while its project file, model,
cap and (senior only) plugin are unchanged: a round stopped by a usage limit resumes, a plugin change reruns only
senior. A project module (eval/longrun/projects/) gives FILES, LATER_FILES, NEW_SESSION_AT (request that starts a fresh
session), WORLD, SCRIPT, TRAPS {check: kind},
rules_kept(dir) and grade(dir) -> {check: (ok, detail)}; checks not in TRAPS are no-harm guards."""
import argparse, hashlib, importlib, importlib.util, json, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run
from gate import LONG, QUALIFY

PROJECTS = Path(__file__).resolve().parent / "projects"
sys.path.insert(0, str(PROJECTS))
import _common
RUNS_OUT = run.EVAL / "results" / "long_runs"
JUNIOR_MODEL = "haiku"
PY38 = run.ROOT / ".tools" / "py38" / "python" / "bin" / "python3"  # every WORLD says Python 3.8; setup: ARCHITECTURE
PY38_CHECK = "runs on Python 3.8"
FOLLOW_UPS = 2  # junior replies per scripted request before moving on
REPS = 2  # SPEC: 2 runs per arm
run.MAX_TURNS = 40  # a milestone needs more tool steps than a single risky turn
run.ALLOWED += " Bash(python3 *) Bash(python *)"  # the junior would approve running the code; the one-shot runner denied it
JUNIOR = """{world}

The assistant building your tool just replied:
<reply>
{reply}
</reply>
If the reply asks you something or waits for your decision or go-ahead, answer as the junior above in 1-3 casual
sentences, only from the facts above ("not sure, you pick" if they don't say); accept its recommendation unless a
fact contradicts it. If it does not need anything from you, reply with exactly NEXT."""


def failed(out):  # an error turn (e.g. usage limit) carries stale usage and a fake reply: stop, never feed it on
    for line in out.splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "result":
            return e.get("result") if e.get("is_error") else None
    return "no result event"


def junior(world, reply, d):
    cmd = ["claude", "-p", JUNIOR.format(world=world, reply=reply or "(empty)"), "--model", JUNIOR_MODEL,
           "--setting-sources", "project,local", "--strict-mcp-config", "--no-session-persistence",
           "--tools", "", "--max-turns", "1", "--output-format", "stream-json", "--verbose"]
    p = subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=run.TIMEOUT_S, stdin=subprocess.DEVNULL)
    if failed(p.stdout):
        raise RuntimeError(f"junior turn failed: {failed(p.stdout)}")
    t, tok, _ = run.parse(p.stdout, "junior")
    return (t["final"] or "").strip(), tok, t["weighted"]


def run_one(name, arm, rep, cap, model, round_):
    project = importlib.import_module(name)
    tag = f"{round_}_{name}_{arm}_r{rep}"
    logs = run.RUNS / "long" / tag
    d = run.project_dir(logs, name, arm)
    for p in (logs, d, run.session_dir(d)):
        shutil.rmtree(p, ignore_errors=True)
    logs.mkdir(parents=True)
    run.setup(d, {"files": project.FILES})  # also makes the first commit
    session, tok, wtok, turns, stopped, errors = None, 0, 0, [], None, []

    def send(msg, n):
        nonlocal session, tok, wtok
        roles_before = len(run.role_usage(d))
        out = run.claude(d, msg, model, arm, resume=session)
        (logs / f"turn{n:02d}.log").write_text(out)
        if failed(out):
            raise RuntimeError(f"{tag} turn {n} failed, run invalid: {failed(out)}")
        t, t_tok, session = run.parse(out, f"{tag} turn {n}")
        t_tok += sum(run.role_usage(d)[roles_before:])
        tok += t_tok
        wtok += t["weighted"] + sum(run.role_weighted(d)[roles_before:])
        turns.append({"n": n, "junior": msg, "reply": t["final"], "tokens": t_tok, "rules_kept": contained(project.rules_kept, d, errors)})
        print(f"{tag} turn {n}: {t_tok} tok (total {tok})", flush=True)
        return t["final"]

    n = 0
    try:
        for i, msg in enumerate(project.SCRIPT):
            run.write(d, project.LATER_FILES.get(i, {}))
            if i == project.NEW_SESSION_AT:
                session = None  # a fresh session: only what the repo (and Senior's files) remember carries over
            reply = send(msg, n); n += 1
            for _ in range(FOLLOW_UPS):
                if tok > cap:
                    break
                answer, j_tok, j_w = junior(project.WORLD, reply, d)
                tok += j_tok; wtok += j_w
                if answer == "NEXT" or not answer:
                    break
                reply = send(answer, n); n += 1
            if tok > cap:
                stopped = f"token cap after scripted request {i + 1}/{len(project.SCRIPT)}"
                break
    except subprocess.TimeoutExpired as e:  # a hung call ends this run only; the timed-out call's tokens are unknown
        stopped = f"call timed out after {e.timeout:.0f}s at turn {n}"
    result = contained(lambda d: grade(project, d), d, errors) or {}
    if set(project.TRAPS) - set(result):
        errors.append(f"TRAPS not graded: {sorted(set(project.TRAPS) - set(result))}")
        result = {**{k: (False, "not graded") for k in project.TRAPS}, **result}
    broken = [t["n"] for t in turns if not t["rules_kept"]]  # the final state can hide a break the junior caught
    for k, (ok, detail) in result.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {k}  | {str(detail)[:160]}")
    print(f"{tag}: {sum(ok for ok, _ in result.values())}/{len(result)} hidden checks, rules broken after turns "
          f"{broken or 'none'}, {tok} tokens, {n} turns" + (f", STOPPED: {stopped}" if stopped else ""), flush=True)
    shutil.rmtree(run.session_dir(d), ignore_errors=True)  # test sessions would pollute log mining
    return {"tokens": tok, "weighted": wtok, "stopped": stopped, "rule_breaks": len(broken), "project": str(d), "grader_errors": errors,
            "checks": {k: {"ok": ok, "detail": str(det)} for k, (ok, det) in result.items()}, "turns": turns}


def contained(fn, d, errors):
    """A grader that crashes or hangs on this run's state fails it (False), is recorded, and never stops the round."""
    try:
        return fn(d)
    except Exception as e:
        errors.append(f"{getattr(fn, '__name__', 'grade')}: {type(e).__name__}: {e}"[:300])
        return False


def grade(project, d):
    """The project's hidden checks, then the same checks with the built code run on Python 3.8."""
    if not PY38.exists():
        raise SystemExit(f"missing {PY38}: unpack Python 3.8 there (harness/ARCHITECTURE.md)")
    now = project.grade(d)
    _common.PYTHON = str(PY38)
    try:
        old = project.grade(d)
    finally:
        _common.PYTHON = sys.executable
    lost = [k for k, (ok, _) in now.items() if ok and not old[k][0]]
    return {**now, PY38_CHECK: (not lost, f"pass on this Python, fail on 3.8: {lost}")}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def run_key(name, arm, cap, model):
    """What the model sees decides reuse; a grader change only re-grades (grader_key)."""
    p = importlib.import_module(name)
    seen = json.dumps([p.FILES, p.LATER_FILES, p.NEW_SESSION_AT, p.WORLD, p.SCRIPT, JUNIOR, FOLLOW_UPS], sort_keys=True)
    k = {"project": sha(seen.encode()), "model": model, "cap": cap}
    return {**k, "senior_hash": run.plugin_hash()} if arm == "senior" else k


def grader_key(name):
    files = (PROJECTS / f"{name}.py", Path(_common.__file__))
    return sha(b"".join(f.read_bytes() for f in files) + PY38_CHECK.encode() + sys.executable.encode())  # grades run pytest on this Python


def summarize(name, runs, stock_ok):
    """Gate format for one project. Traps stock passed in the qualify round become no-harm guards."""
    traps = {**importlib.import_module(name).TRAPS, PY38_CHECK: "D3"}
    arms = list(runs)
    out = {"id": name, "traps": {}, "guards": {}}
    for c in dict.fromkeys(c for a in arms for r in runs[a] for c in r["checks"]):  # a crashed grader leaves checks out
        per_arm = {a: [r["checks"].get(c, {"ok": False})["ok"] for r in runs[a]] for a in arms}
        if c in traps and c not in stock_ok:
            out["traps"][c] = {"kind": traps[c], **per_arm}
        else:
            out["guards"][c] = per_arm
    for f in ("rule_breaks", "tokens", "weighted"):
        out[f] = {a: [r[f] for r in runs[a]] for a in arms}
    out["grader_errors"] = {a: [len(r.get("grader_errors", [])) for r in runs[a]] for a in arms}
    out["stopped"] = {a: [bool(r["stopped"]) for r in runs[a]] for a in arms}
    return out


def main():
    a = argparse.ArgumentParser()
    a.add_argument("round", choices=["qualify", "latest"])
    a.add_argument("--cap", type=int, required=True, help="per run: stop after this many tokens (assistant + roles + junior)")
    a.add_argument("--projects", nargs="*", default=sorted(p.stem for p in PROJECTS.glob("[!_]*.py")))
    a.add_argument("--reps", type=int, default=REPS)
    a.add_argument("--model", default="sonnet")
    a.add_argument("--senior-only", action="store_true", help="latest round, senior arm only (e.g. another model)")
    x = a.parse_args()
    if x.senior_only and x.round != "latest":
        sys.exit("--senior-only needs the latest round")
    if importlib.util.find_spec("pytest") is None:  # graders run pytest on this Python; without it test checks fail falsely
        sys.exit(f"no pytest on {sys.executable}: run with the project's .venv Python")
    arms = ["base"] if x.round == "qualify" else ["senior"] if x.senior_only else ["base", "senior"]
    tag = f"{x.round}-{x.model}" if x.senior_only else x.round  # own run files and project folders: never overwrite the official round
    out_file = LONG.with_name(f"{LONG.stem}_{x.model}.json") if x.senior_only else QUALIFY if x.round == "qualify" else LONG
    stock_ok = {}
    if x.round == "latest":
        if not QUALIFY.exists():
            sys.exit(f"no {QUALIFY}: run the qualify round first")
        stock_ok = {p["id"]: {t for t, v in p["traps"].items() if all(v["base"])}
                    for p in json.loads(QUALIFY.read_text())["projects"]}
    RUNS_OUT.mkdir(parents=True, exist_ok=True)
    projects, stopped = [], []
    for name in x.projects:
        runs = {arm: [] for arm in arms}
        for rep in range(x.reps):
            for arm in arms:  # arms interleaved per rep: a round stopped midway leaves balanced data
                f, key = RUNS_OUT / f"{tag}_{name}_{arm}_r{rep}.json", run_key(name, arm, x.cap, x.model)
                saved = json.loads(f.read_text()) if f.exists() else None
                earlier = RUNS_OUT / f"qualify_{name}_base_r{rep}.json"
                if arm == "base" and x.round == "latest" and not (saved and saved["key"] == key) and earlier.exists():
                    saved = json.loads(earlier.read_text())  # stock is unchanged between rounds; the trap rate reads senior runs only
                if saved and saved["key"] == key and (saved.get("grader") == grader_key(name) or Path(saved["project"]).is_dir()):
                    print(f"{f.name}: reused (unchanged project, model, cap{', plugin' if arm == 'senior' else ''})")
                    if saved.get("grader") != grader_key(name):  # grader changed: re-grade the kept project, no model calls
                        saved["checks"] = {k: {"ok": ok, "detail": str(det)} for k, (ok, det) in grade(importlib.import_module(name), saved["project"]).items()}
                        print(f"{f.name}: re-graded (grader changed)")
                else:
                    saved = {"key": key, **run_one(name, arm, rep, x.cap, x.model, tag)}
                saved["grader"] = grader_key(name)
                f.write_text(json.dumps(saved, indent=1))
                runs[arm].append(saved)
                stopped += [f.name] if saved["stopped"] else []
        projects.append(summarize(name, runs, stock_ok.get(name, set())))
    out = {"projects": projects, **({"senior_hash": run.plugin_hash()} if x.round == "latest" else {})}
    out_file.write_text(json.dumps(out, indent=1))
    print(f"saved {out_file}" + (f"; runs stopped by cap: {stopped}" if stopped else ""))


if __name__ == "__main__":
    main()
