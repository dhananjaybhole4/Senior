"""The isolation round must report a leak when the wall is missing (negative control) and a block when it is there."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import isolation


def test_mount_blocks_and_detects_leaks(monkeypatch):
    for role, kind, rel, task in isolation.CASES:
        assert isolation.attempt(role, kind, rel, task, "mount", "m4rk3r")["blocked"]
    monkeypatch.setattr(isolation, "mounts", lambda d: {r: [] for r in ("test-writer", "reviewer", "builder")})
    for role, kind, rel, task in isolation.CASES:
        assert not isolation.attempt(role, kind, rel, task, "mount", "m4rk3r")["blocked"]
