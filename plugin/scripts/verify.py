"""Project harness check for .senior/: runs every [[check]] in .senior/checks.toml, prints PASS/FAIL.
python3 verify.py            run all checks (exit 0 = all pass)
python3 verify.py lock       fingerprint checks.toml + checks/ after the junior approved them
Checks are approved by the junior; a changed fingerprint fails until the junior re-approves and locks."""
import hashlib, json, subprocess, sys, tomllib
from pathlib import Path

H = Path(".senior")
LOCK = H / "lock.json"


def fingerprint():
    h = hashlib.sha256()
    for p in [H / "checks.toml", *sorted((H / "checks").rglob("*"))]:
        if p.is_file():
            h.update(str(p).encode()); h.update(p.read_bytes())
    return h.hexdigest()


def main():
    if not (H / "checks.toml").exists():
        sys.exit("FAIL: no .senior/checks.toml; run /senior first")
    if sys.argv[1:] == ["lock"]:
        LOCK.write_text(json.dumps({"fingerprint": fingerprint()}))
        print("locked"); return
    rows = []
    locked = json.loads(LOCK.read_text())["fingerprint"] if LOCK.exists() else None
    same = locked == fingerprint()
    note = "checks never locked" if not locked else "checks unchanged since approval" if same else "checks CHANGED since approval"
    rows.append((same, "fingerprint", note))
    for c in tomllib.loads((H / "checks.toml").read_text()).get("check", []):
        p = subprocess.run(c["cmd"], shell=True, capture_output=True, text=True)
        tail = (p.stdout + p.stderr).strip().splitlines()[-1:] or [""]
        rows.append((p.returncode == 0, c["name"], tail[0]))
    for ok, name, note in rows:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  {note}")
    bad = sum(not ok for ok, *_ in rows)
    print(f"RESULT: {'PASS' if not bad else f'FAIL ({bad})'}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
