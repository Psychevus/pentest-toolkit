import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main import pipeline


def test_pipeline(monkeypatch):
    from modules.base import Module, Finding
    import importlib
    import main
    importlib.reload(main)
    monkeypatch.setattr(Module, 'registry', {})
    monkeypatch.setattr(main.Module, 'registry', Module.registry)

    captured = {}

    class A(Module):
        name = 'subfinder'
        def run(self, target: str):
            return [Finding(tool=self.name, data={'host': 'a.example'})]

    class B(Module):
        name = 'httpx'
        def run(self, target: str):
            captured['input'] = target
            return [Finding(tool=self.name, data={'url': f'https://{target}'})]

    results = pipeline('example.com', ['subfinder', 'httpx'], use_pipeline=True)
    assert captured['input'] == 'a.example'
    assert len(results) == 2


def test_summary(monkeypatch, tmp_path: Path):
    from modules.base import Module, Finding
    import importlib
    import main
    importlib.reload(main)
    monkeypatch.setattr(Module, 'registry', {})
    monkeypatch.setattr(main.Module, 'registry', Module.registry)

    summary_data = {}
    monkeypatch.setattr(main, '_print_summary', lambda s: summary_data.update(s))

    class Sub(Module):
        name = 'subfinder'
        def run(self, target: str):
            return [Finding(tool=self.name, data={'host': 'a.example'})]

    class Http(Module):
        name = 'httpx'
        def run(self, target: str):
            return [Finding(tool=self.name, data={'url': f'https://{target}', 'host': target})]

    class Nuc(Module):
        name = 'nuclei'
        def run(self, target: str):
            return [Finding(tool=self.name, data={'id': 'x'})]

    class Nm(Module):
        name = 'nmap'
        def run(self, target: str):
            p = tmp_path / 'out.xml'
            xml = (
                '<nmaprun><host><ports><port><state state="open"/></port>'
                '</ports></host></nmaprun>'
            )
            p.write_text(xml)
            return [Finding(tool=self.name, data={'xml': str(p)})]

    class Tssl(Module):
        name = 'testssl'
        def run(self, target: str):
            p = tmp_path / 'out.json'
            p.write_text('[{"severity":"WARN"}]')
            return [Finding(tool=self.name, data={'report': str(p)})]

    tools = ['subfinder', 'httpx', 'nuclei', 'nmap', 'testssl']
    pipeline('example.com', tools, use_pipeline=True, show_summary=True)
    assert summary_data == {
        'subdomains': 1,
        'live_hosts': 1,
        'nuclei': 1,
        'open_ports': 1,
        'ssl_issues': 1,
    }


def test_parallel_execution(monkeypatch):
    import time
    from modules.base import Module, Finding
    import importlib
    import main

    importlib.reload(main)
    monkeypatch.setattr(Module, 'registry', {})
    monkeypatch.setattr(main.Module, 'registry', Module.registry)

    class A(Module):
        name = 'a'
        TIMEOUT = 1

        def run(self, target: str):
            time.sleep(0.2)
            return [Finding(tool=self.name, data={})]

    class B(Module):
        name = 'b'
        TIMEOUT = 1

        def run(self, target: str):
            time.sleep(0.2)
            return [Finding(tool=self.name, data={})]

    start = time.perf_counter()
    res = pipeline('example.com', ['a', 'b'], parallel=True)
    duration = time.perf_counter() - start
    assert len(res) == 2
    assert duration < 0.35

