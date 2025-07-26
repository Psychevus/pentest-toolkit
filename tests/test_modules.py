import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import modules.subfinder as subfinder
import modules.httpx as httpx
import modules.nmap_ as nmap_
import modules.testssl as testssl
import modules.nuclei as nuclei

import modules.dnsrecon as dnsrecon
import modules.ffuf as ffuf
import modules.screenshot as screenshot
import modules.katana as katana

class DummyProc:
    def __init__(self, stdout=""):
        self.stdout = stdout
        self.stderr = ""


def test_subfinder(monkeypatch):
    out = json.dumps({"host": "a.example"}) + "\n"

    def fake_run(*args, **kwargs):
        return DummyProc(stdout=out)

    monkeypatch.setattr(subfinder.subprocess, "run", fake_run)
    results = subfinder.Subfinder().run("example.com")
    assert results[0].data["host"] == "a.example"


def test_httpx(monkeypatch):
    out = json.dumps({"url": "https://a.example"}) + "\n"

    def fake_run(*args, **kwargs):
        return DummyProc(stdout=out)

    monkeypatch.setattr(httpx.subprocess, "run", fake_run)
    results = httpx.Httpx().run("example.com")
    assert results[0].data["url"] == "https://a.example"


def test_nmap(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(nmap_, "timestamp", lambda: "20240101-0000")

    def fake_run(*a, **kw):
        out_file = Path("output/nmap_example.com_20240101-0000.xml")
        out_file.parent.mkdir(exist_ok=True)
        out_file.touch()
        return DummyProc()

    monkeypatch.setattr(nmap_.subprocess, "run", fake_run)
    results = nmap_.Nmap().run("example.com")
    assert Path(results[0].data["xml"]).exists()


def test_testssl(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(testssl, "timestamp", lambda: "20240101-0000")

    def fake_run(*a, **kw):
        out_file = Path("output/testssl_example.com_20240101-0000.json")
        out_file.parent.mkdir(exist_ok=True)
        out_file.touch()
        return DummyProc()

    monkeypatch.setattr(testssl.subprocess, "run", fake_run)
    results = testssl.TestSSL().run("example.com")
    path = Path(results[0].data["report"])
    assert path.exists()


def test_nuclei(monkeypatch):
    out = json.dumps({"templateID": "cve-2023-0000"}) + "\n"

    def fake_run(*args, **kwargs):
        return DummyProc(stdout=out)

    monkeypatch.setattr(nuclei.subprocess, "run", fake_run)
    results = nuclei.Nuclei().run("example.com")
    assert results[0].data["templateID"] == "cve-2023-0000"

def test_dnsrecon(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(dnsrecon, "timestamp", lambda: "20240101-0000")
    output = "example.com.\tIN\tA\t1.1.1.1\n"

    def fake_run(*args, **kwargs):
        return DummyProc(stdout=output)

    monkeypatch.setattr(dnsrecon.subprocess, "run", fake_run)
    results = dnsrecon.Dnsrecon().run("example.com")
    assert results[0].data["record"].startswith("example.com")
    assert Path(results[-1].data["report"]).exists()


def test_ffuf(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(ffuf, "timestamp", lambda: "20240101-0000")

    def fake_run(*a, **kw):
        out_file = Path("output/ffuf_http___example.com_20240101-0000.json")
        out_file.parent.mkdir(exist_ok=True)
        out_file.write_text(json.dumps({"results": [{"url": "http://example.com/admin",
"status": 200}]}))
        return DummyProc()

    monkeypatch.setattr(ffuf.subprocess, "run", fake_run)
    results = ffuf.Ffuf().run("http://example.com")
    assert results[0].data["url"] == "http://example.com/admin"


def test_screenshot(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(screenshot, "timestamp", lambda: "20240101-0000")

    def fake_run(*a, **kw):
        out_file = Path("output/screenshot_http___example.com_20240101-0000.png")
        out_file.parent.mkdir(exist_ok=True)
        out_file.touch()
        return DummyProc()

    monkeypatch.setattr(screenshot.subprocess, "run", fake_run)
    results = screenshot.Screenshot().run("http://example.com")
    assert Path(results[0].data["image"]).exists()


def test_katana(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(katana, "timestamp", lambda: "20240101-0000")

    def fake_run(*a, **kw):
        out_file = Path("output/katana_http___example.com_20240101-0000.json")
        out_file.parent.mkdir(exist_ok=True)
        out_file.write_text('{"url": "http://example.com/api"}\n')
        return DummyProc()

    monkeypatch.setattr(katana.subprocess, "run", fake_run)
    results = katana.Katana().run("http://example.com")
    assert results[0].data["url"] == "http://example.com/api"
