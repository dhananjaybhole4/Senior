"""Hidden exam (SPEC done #2), run by `harness/verify` as the holdout command: python eval/longrun/exam.py DIR
DIR holds sealed long projects (same format as projects/). Runs a qualify round (stock) then the official round
(both arms) on them, with every run, log, project folder and result in a neutral temp folder deleted at the end,
so nothing of the exam stays readable. Prints counts only. A project holds when stock slipped on >= 1 trap, Senior handles >= --min-rate of
those, breaks no stated rule at any turn and fails no guard stock passed (SPEC #1 + #3)."""
import argparse, contextlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_long
from run_long import run
from gate import handled


def holds(p, slipped, min_rate):
    traps = [v["senior"] for t, v in p["traps"].items() if t in slipped]
    rate_ok = bool(traps) and sum(map(handled, traps)) / len(traps) >= min_rate  # no slipped trap = nothing shown (owner, Q1 b)
    harm = [g for g, v in p["guards"].items() if handled(v["base"]) and not handled(v["senior"])]
    return rate_ok and sum(p["rule_breaks"]["senior"]) == 0 and not harm, len(traps), sum(map(handled, traps)), len(harm)


def preflight(names):
    """Everything that would stop the exam for sure, checked before the first model call (0 tokens)."""
    import importlib, importlib.util
    if not shutil.which("claude"):
        return "no claude CLI on PATH"
    if importlib.util.find_spec("pytest") is None:
        return f"no pytest on {sys.executable}"
    if not run_long.PY38.exists():
        return f"missing {run_long.PY38}"
    for i, name in enumerate(names, 1):
        try:
            m = importlib.import_module(name)
            assert isinstance(m.TRAPS, dict) and m.SCRIPT and isinstance(m.WORLD, str) and isinstance(m.FILES, dict)  # guard-only projects have no traps
            assert isinstance(m.LATER_FILES, dict) and isinstance(m.NEW_SESSION_AT, int)
            run_long.run_key(name, "base", 0, "")  # everything the run reads before the model starts
            d = Path(tempfile.mkdtemp(prefix="proj-")) / "app"
            try:
                run.setup(d, {"files": m.FILES})
                for later in m.LATER_FILES.values():
                    run.write(d, later)
                m.rules_kept(d)  # on the starting files: must answer, not crash (built states are contained per run)
            finally:
                shutil.rmtree(d.parent, ignore_errors=True)
        except Exception as e:  # its message may name exam content: report the kind only
            return f"exam project {i} of {len(names)} is broken ({type(e).__name__})"
    return None


def main():
    a = argparse.ArgumentParser()
    a.add_argument("dir")
    a.add_argument("--cap", type=int, required=True)
    a.add_argument("--min-rate", type=float, required=True)
    a.add_argument("--min-projects", type=int, required=True)
    x = a.parse_args()
    exam = Path(x.dir).resolve()
    names = sorted(p.stem for p in exam.glob("[!_]*.py"))
    if not names:
        sys.exit("FAIL: no exam projects found")
    sys.path.insert(0, str(exam))
    null = os.open(os.devnull, os.O_RDONLY)  # verify runs us from the owner's terminal: a built program asking for input
    os.dup2(null, 0); os.close(null)          # would wait on it until a timeout; visible rounds ran with no input either
    problem = preflight(names)
    if problem:
        sys.exit(f"FAIL before any model call (0 tokens used): {problem}")
    work = Path(tempfile.mkdtemp(prefix="proj-"))  # neutral name: the model sees its project path
    try:
        run_long.PROJECTS, run_long.RUNS_OUT = exam, work / "r"
        run_long.QUALIFY, run_long.LONG = work / "q.json", work / "l.json"
        run.RUNS, run.PROJECTS = work / "logs", work / "p"
        log = (work / "log").open("w")  # progress lines name the exam's checks: they go nowhere visible
        try:
            with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                for rnd in ("qualify", "latest"):
                    sys.argv = ["run_long.py", rnd, "--cap", str(x.cap), "--projects", *names]
                    run_long.main()
        except (Exception, SystemExit) as e:  # its message names exam projects: report the kind only
            what = f" in {Path(str(e.cmd if isinstance(e.cmd, str) else e.cmd[0]).split()[0]).name} after {e.timeout:.0f}s" if isinstance(e, subprocess.TimeoutExpired) else ""
            sys.exit(f"FAIL: exam run stopped ({type(e).__name__}{what}; a usage limit or an error); nothing kept, rerun later")
        q, l = json.loads(run_long.QUALIFY.read_text()), json.loads(run_long.LONG.read_text())
    finally:
        shutil.rmtree(work, ignore_errors=True)
    slipped = {p["id"]: {t for t, v in p["traps"].items() if not all(v["base"])} for p in q["projects"]}
    res = [holds(p, slipped[p["id"]], x.min_rate) for p in l["projects"]]
    ok = sum(r[0] for r in res)
    errs = sum(n for p in l["projects"] for v in p["grader_errors"].values() for n in v)
    stops = sum(s for p in l["projects"] for v in p["stopped"].values() for s in v)
    print(f"exam: {ok}/{len(res)} projects hold; traps stock slipped on {sum(r[1] for r in res)}, Senior handled "
          f"{sum(r[2] for r in res)}; guards harmed {sum(r[3] for r in res)}; grader errors {errs}, runs stopped early {stops}")
    print(f"METRIC exam_projects_held={ok}")
    sys.exit(0 if ok >= x.min_projects else 1)


if __name__ == "__main__":
    main()
