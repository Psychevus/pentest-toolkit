import importlib
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
import modules.base as base


def test_bin_override(monkeypatch):
    monkeypatch.setenv("PENTEST_TOOLKIT_BIN_DIR", "/opt/tools")
    importlib.reload(base)

    class Dummy(base.Module):
        name = "dummy"
        def run(self, target: str):
            return []

    assert Dummy.bin("foo") == str(Path("/opt/tools") / "foo")
