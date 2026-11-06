"""Grading helpers shared by long projects (the leading underscore keeps run_long from treating this as a project)."""
import ast, shutil, subprocess, sys, tempfile
from pathlib import Path


def py(d, script, *args, timeout=60, stderr=True):
    """stderr=False: only what a program reading the output sees (warnings on stderr do not count)."""
    p = subprocess.run([sys.executable, script, *args], cwd=d, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout + (p.stderr if stderr else "")


def graded_copy(project):
    """A copy of the final project to run hidden data against; the real one stays as the model left it."""
    d = Path(tempfile.mkdtemp(prefix="grade-")) / "app"
    shutil.copytree(project, d, ignore=shutil.ignore_patterns(".git", "__pycache__", ".senior"))
    return d


def third_party(d):
    """Non-stdlib imports outside test files (the junior's laptop cannot install packages)."""
    local = {p.stem for p in Path(d).rglob("*.py")} | {p.name for p in Path(d).iterdir() if p.is_dir()}
    found = set()
    for f in Path(d).rglob("*.py"):
        if "test" in f.name:
            continue
        try:
            tree = ast.parse(f.read_text())
        except SyntaxError:
            found.add(f"syntax error in {f.name}"); continue
        for n in ast.walk(tree):
            mods = [a.name for a in n.names] if isinstance(n, ast.Import) else [n.module] if isinstance(n, ast.ImportFrom) and n.module and not n.level else []
            found |= {m.split(".")[0] for m in mods} - set(sys.stdlib_module_names) - local
    return sorted(found)


def own_tests(project):
    """(ok, detail): the project's own tests pass; at least one test ran somewhere."""
    where = ["."] + [".senior/checks"] * (Path(project) / ".senior" / "checks").is_dir()  # pytest skips dot folders
    runs = [subprocess.run([sys.executable, "-m", "pytest", "-q", w], cwd=project, capture_output=True, text=True, timeout=120) for w in where]
    lasts = [t.stdout.strip().splitlines()[-1] if t.stdout.strip() else t.stderr[-120:] for t in runs]
    return all(t.returncode in (0, 5) for t in runs) and any(t.returncode == 0 for t in runs), " | ".join(lasts)  # 5 = none found
