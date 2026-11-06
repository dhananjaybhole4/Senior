"""Long-project gate: traps qualify only on an earlier stock round; rule breaks, harm and tokens gate too."""
import json, subprocess, sys
from pathlib import Path

import pytest

GATE = Path(__file__).resolve().parents[2] / "harness" / "checks" / "gate.py"
ARGS = ["--min-rate", "0.8", "--max-rule-breaks", "0", "--max-regressions", "0", "--max-ratio", "1.3"]


def project(senior_trap=(True, True), breaks=(0, 0), senior_guard=(True, True), senior_tok=(110, 110)):
    return {"id": "p", "traps": {"slipped": {"kind": "D6", "base": [False, True], "senior": list(senior_trap)},
                                 "lucky": {"kind": "D6", "base": [False, False], "senior": [False, False]}},
            "guards": {"g": {"base": [True, True], "senior": list(senior_guard)}},
            "rule_breaks": {"base": [1, 1], "senior": list(breaks)},
            "tokens": {"base": [100, 100], "senior": list(senior_tok)}, "weighted": {"base": [10, 10], "senior": [11, 11]}}


def run(tmp_path, monkeypatch, **kw):
    sys.path.insert(0, str(GATE.parent)); import gate
    (tmp_path / "q.json").write_text(json.dumps({"projects": [{"id": "p", "traps": {
        "slipped": {"base": [True, False]}, "stock_ok": {"base": [True, True]}}}]}))  # "lucky" never qualified earlier
    (tmp_path / "l.json").write_text(json.dumps({"senior_hash": "h", "projects": [project(**kw)]}))
    monkeypatch.setattr(gate, "LONG", tmp_path / "l.json"); monkeypatch.setattr(gate, "QUALIFY", tmp_path / "q.json")
    monkeypatch.setattr(gate, "plugin_hash", lambda: "h")
    monkeypatch.setattr(sys, "argv", ["gate.py", "long", *ARGS])
    with pytest.raises(SystemExit) as e:
        gate.main()
    return e.value.code


def test_pass_counts_only_traps_that_slipped_earlier(tmp_path, monkeypatch, capsys):
    assert run(tmp_path, monkeypatch) == 0
    out = capsys.readouterr().out
    assert "traps where stock slipped: 1" in out and "p/stock_ok" in out  # 'lucky' not counted, stock 2/2 reported as dropped


@pytest.mark.parametrize("kw", [{"senior_trap": (True, False)}, {"breaks": (0, 1)}, {"senior_guard": (False, False)},
                                {"senior_tok": (140, 140)}])
def test_each_condition_can_fail(tmp_path, monkeypatch, kw):
    assert run(tmp_path, monkeypatch, **kw) == 1
