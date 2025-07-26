from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from distributed import DistributedOrchestrator
from modules.base import Finding
import main


class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: D401
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):  # noqa: D401
        if self.path != "/scan":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length) or b"{}")
        out = json.dumps({"findings": [{"tool": "dummy", "target": payload["target"]}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)


def _start_server():
    srv = HTTPServer(("localhost", 0), DummyHandler)
    thread = threading.Thread(target=srv.serve_forever)
    thread.daemon = True
    thread.start()
    return srv, thread


def test_dispatched_results(monkeypatch):
    monkeypatch.setattr(main, "pipeline", lambda *a, **k: [Finding(tool="local", data={})])
    srv, th = _start_server()
    orch = DistributedOrchestrator([f"http://localhost:{srv.server_address[1]}"])
    res = orch.dispatch(["a.com", "b.com"], ["dummy"])
    srv.shutdown()
    th.join()
    assert len(res) == 2
    assert any(f.tool == "dummy" for f in res)


def test_fallback(monkeypatch):
    monkeypatch.setattr(main, "pipeline", lambda *a, **k: [Finding(tool="local", data={"t": a[0]})])
    orch = DistributedOrchestrator(["http://localhost:12345"])
    res = orch.dispatch(["x.com"], ["dummy"])
    assert res[0].tool == "local"

