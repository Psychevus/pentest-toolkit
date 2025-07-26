import importlib
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main import _diff_findings, pipeline
from modules.base import Module, Finding


def test_diff_findings():
    old = [Finding(tool="a", data={"x": 1})]
    new = [Finding(tool="a", data={"x": 1}), Finding(tool="b", data={"y": 2})]
    diff = _diff_findings(new, old)
    assert len(diff) == 1
    assert diff[0].tool == "b"


def test_pipeline_skip(monkeypatch):
    import main
    importlib.reload(main)
    monkeypatch.setattr(Module, "registry", {})
    monkeypatch.setattr(main.Module, "registry", Module.registry)

    called = []

    class Sub(Module):
        name = "subfinder"
        def run(self, target: str):
            return [Finding(tool=self.name, data={"host": "a.example"})]

    class Hx(Module):
        name = "httpx"
        def run(self, target: str):
            return [Finding(tool=self.name, data={"url": "https://a.example", "host": "a.example"})]

    class Nuc(Module):
        name = "nuclei"
        def run(self, target: str):
            called.append("nuclei")
            return [Finding(tool=self.name, data={})]

    prev = [Finding(tool="httpx", data={"url": "https://a.example"})]
    modules = ["subfinder", "httpx", "nuclei"]
    pipeline("example.com", modules, use_pipeline=True, prev_state=prev)
    assert not called
