"""Explore: one arm builds a long-horizon project in one continuous session, driven by a scripted junior plus a
simulated junior (small model) that answers the assistant's questions from the project's WORLD facts.
python eval/longrun/run_long.py --arm base --cap 4000000      -> eval/results/long_<arm>.json, logs in runs/long_<arm>/"""
import argparse, json, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run
import expenses as project

JUNIOR_MODEL = "haiku"
FOLLOW_UPS = 2  # junior replies per scripted request before moving on
run.MAX_TURNS = 40  # a milestone needs more tool steps than a single risky turn
run.ALLOWED += " Bash(python3 *) Bash(python *)"  # the junior would approve running the code; the one-shot runner denied it
JUNIOR = """{world}

The assistant building your tool just replied:
<reply>
{reply}
</reply>
If the reply asks you something or waits for your decision or go-ahead, answer as Sam in 1-3 casual sentences, only
from the facts above ("not sure, you pick" if they don't say); accept its recommendation unless a fact contradicts it.
If it does not need anything from you, reply with exactly NEXT."""


def failed(out):  # an error turn (e.g. usage limit) carries stale usage and a fake reply: stop, never feed it on
    for line in out.splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "result":
            return e.get("result") if e.get("is_error") else None
    return "no result event"


def junior(reply, d):
    cmd = ["claude", "-p", JUNIOR.format(world=project.WORLD, reply=reply or "(empty)"), "--model", JUNIOR_MODEL,
           "--setting-sources", "project,local", "--strict-mcp-config", "--no-session-persistence",
           "--tools", "", "--max-turns", "1", "--output-format", "stream-json", "--verbose"]
    p = subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=run.TIMEOUT_S, stdin=subprocess.DEVNULL)
    if failed(p.stdout):
        raise RuntimeError(f"junior turn failed: {failed(p.stdout)}")
    t, tok, _ = run.parse(p.stdout, "junior")
    return (t["final"] or "").strip(), tok


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--arm", choices=["base", "senior"], required=True)
    a.add_argument("--cap", type=int, required=True, help="stop after this many tokens (assistant + roles + junior)")
    a.add_argument("--model", default="sonnet")
    a.add_argument("--rep", type=int, default=0, help="repeat number: runs are noisy, compare several")
    x = a.parse_args()
    name = f"long_{x.arm}_r{x.rep}"
    logs = run.RUNS / name
    d = run.project_dir(logs, "expenses", x.arm)
    for p in (logs, d, run.session_dir(d)):
        shutil.rmtree(p, ignore_errors=True)
    logs.mkdir(parents=True)
    run.setup(d, {"files": project.FILES})  # also makes the first commit
    session, tok, turns, stopped = None, 0, [], None

    def send(msg, n):
        nonlocal session, tok
        roles_before = len(run.role_usage(d))
        out = run.claude(d, msg, x.model, x.arm, resume=session)
        (logs / f"turn{n:02d}.log").write_text(out)
        if failed(out):
            raise RuntimeError(f"{name} turn {n} failed, run invalid: {failed(out)}")
        t, t_tok, session = run.parse(out, f"{name} turn {n}")
        t_tok += sum(run.role_usage(d)[roles_before:])
        tok += t_tok
        turns.append({"n": n, "junior": msg, "reply": t["final"], "tokens": t_tok, "rules_kept": project.rules_kept(d)})
        print(f"turn {n}: {t_tok} tok (total {tok})", flush=True)
        return t["final"]

    n = 0
    for i, msg in enumerate(project.SCRIPT):
        run.write(d, project.LATER_FILES.get(i, {}))
        if i == 0 and x.arm == "senior":
            msg = "/senior:senior " + msg  # how a junior starts Senior: it sets up the project harness first
        reply = send(msg, n); n += 1
        for _ in range(FOLLOW_UPS):
            if tok > x.cap:
                break
            answer, j_tok = junior(reply, d)
            tok += j_tok
            if answer == "NEXT" or not answer:
                break
            reply = send(answer, n); n += 1
        if tok > x.cap:
            stopped = f"token cap after scripted request {i + 1}/{len(project.SCRIPT)}"
            break
    result = project.grade(d)
    for k, (ok, detail) in result.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {k}  | {str(detail)[:160]}")
    broken = [t["n"] for t in turns if not t["rules_kept"]]
    print(f"  stated rules broken after turns: {broken or 'none'}")  # the final state can hide a break the junior caught
    print(f"{x.arm}: {sum(ok for ok, _ in result.values())}/{len(result)} hidden checks, {tok} tokens, {n} turns"
          + (f", STOPPED: {stopped}" if stopped else ""))
    out = run.EVAL / "results" / f"{name}.json"
    out.write_text(json.dumps({"arm": x.arm, "model": x.model, "tokens": tok, "stopped": stopped, "project": str(d),
                               "checks": {k: {"ok": ok, "detail": str(det)} for k, (ok, det) in result.items()},
                               "turns": turns}, indent=1))
    shutil.rmtree(run.session_dir(d), ignore_errors=True)  # test sessions would pollute log mining
    print(f"saved {out}")


if __name__ == "__main__":
    main()
