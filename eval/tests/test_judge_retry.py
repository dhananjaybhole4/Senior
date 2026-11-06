import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import judge

GOOD = [{"n": 1, "real": True, "plan": True, "plain": True, "default": True, "why": "w"}]
BAD = [{"n": 1, "real": True, "plan": True, "default": True, "why": "w"}]  # 'plain' missing


def fake(answers):
    def grade(request, reply, items, cwd):
        g = answers.pop(0)
        if any(k not in x for x in g for k in judge.KEYS):
            raise judge.MalformedJudge("missing", 3)
        return g, 5
    return grade


def test_retry_after_missing_field(monkeypatch):
    monkeypatch.setattr(judge, "_grade", fake([BAD, GOOD]))
    graded, tok = judge.grade_once("r", "x?", ["x?"], ".")
    assert graded == GOOD and tok == 8


def test_fails_loudly_when_retry_also_bad(monkeypatch):
    monkeypatch.setattr(judge, "_grade", fake([BAD, BAD]))
    with pytest.raises(RuntimeError, match="missing"):
        judge.grade_once("r", "x?", ["x?"], ".")
