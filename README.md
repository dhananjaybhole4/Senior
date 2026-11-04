# Senior

Claude Code plugin `/senior` (in development). Goal and rules: `harness/SPEC.md`.

## Setup (any Linux/WSL machine)
```bash
python3 -m venv .venv            # tested with Python 3.14.4
source .venv/bin/activate
python -m pip install -r requirements.txt
```
Keep the venv active when running `harness/verify` or anything under `eval/`.
Role isolation needs `bwrap` (bubblewrap) on the system: `sudo apt install bubblewrap`.
