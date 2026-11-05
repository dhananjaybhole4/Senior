"""Helpers for situation check functions. t = {tools, final, new_commits, branches, repo}."""
import subprocess, sys

SAVEPOINT = "savepoint"  # git branch the runner resets to before every run


def edits(t):  # Edit/Write tool uses
    return [u for u in t["tools"] if u["name"] in ("Edit", "Write", "MultiEdit", "NotebookEdit")]


def bash_cmds(t):
    return [u["input"].get("command", "") for u in t["tools"] if u["name"] == "Bash"]


def text(t):
    return (t["final"] or "").lower()


# The helpers below look at the test project itself (t["repo"]) after the run, relative to the save point.


def _git(t, *a):
    return subprocess.run(["git", "-C", str(t["repo"]), *a], capture_output=True, text=True, check=True).stdout


def committed_files(t):  # files in commits made during the run
    return set(_git(t, "diff", "--name-only", SAVEPOINT, "HEAD").split())


def changed_files(t):  # committed + uncommitted + new files since the save point (includes after_commit files)
    return set(_git(t, "diff", "--name-only", SAVEPOINT).split()) | set(_git(t, "ls-files", "--others", "--exclude-standard").split())


def read(t, path):  # file content now, "" if missing
    p = t["repo"] / path
    return p.read_text() if p.is_file() else ""


def tests_pass(t):  # run the project's tests on the final state
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=t["repo"],
                          capture_output=True, text=True).returncode == 0
