"""Tests for the plugin's hook scripts (no tokens)."""
import json, subprocess, sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "plugin" / "scripts"


def sh(cwd, *args, env=None):
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd, capture_output=True, text=True, env=env)


def test_primer_prints_the_standing_rules_instruction():
    out = sh(".", SCRIPTS / "primer.py").stdout
    assert ".senior/BOUNDARIES.md" in out and "lifts a rule" in out


def test_ledger_shows_standing_rules_only_when_present(tmp_path):
    def hook():
        return subprocess.run([sys.executable, SCRIPTS / "ledger.py"], input=json.dumps({"cwd": str(tmp_path)}),
                              capture_output=True, text=True)
    assert hook().stdout == "" and hook().returncode == 0  # no file: silent, no tokens
    (tmp_path / ".senior").mkdir()
    (tmp_path / ".senior" / "BOUNDARIES.md").write_text("- partner's sheet reads transactions.csv: keep its columns\n")
    out = hook().stdout
    assert "keep its columns" in out and "Standing rules" in out
