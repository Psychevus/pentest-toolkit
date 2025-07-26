from __future__ import annotations

"""Distributed orchestrator for Pentest-Toolkit."""

from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable, List

import requests

from modules.base import Finding
from utils.logger import get_logger

logger = get_logger()


class DistributedOrchestrator:
    """Dispatch targets to remote runners via HTTP."""

    def __init__(
        self,
        runners: Iterable[str],
        *,
        timeout: int = 600,
        runner: Callable[[str, List[str], bool], List[Finding]] | None = None,
    ) -> None:
        self.runners = list(runners)
        self.timeout = timeout
        self.runner = runner

    def _health(self) -> List[str]:
        available: List[str] = []
        for url in self.runners:
            try:
                resp = requests.get(f"{url.rstrip('/')}/health", timeout=5)
                if resp.status_code == 200:
                    available.append(url.rstrip('/'))
            except requests.RequestException:
                logger.warning("\u26a0\ufe0f Runner %s unavailable", url)
        return available

    def _run_local(self, target: str, tools: List[str], pipeline_mode: bool) -> List[Finding]:
        logger.info("\u23f1\ufe0f Local fallback for %s", target)
        run = self.runner
        if run is None:
            from main import pipeline as _pipeline

            def run(t: str, tl: List[str], pm: bool) -> List[Finding]:
                return _pipeline(t, tl, use_pipeline=pm, show_summary=False)

        return run(target, tools, pipeline_mode)

    def dispatch(
        self,
        targets: List[str],
        tools: List[str],
        *,
        pipeline_mode: bool = False,
    ) -> List[Finding]:
        """Send targets to available runners and aggregate results."""
        available = self._health()
        if not available:
            logger.warning("No runners available, running locally")
            results: List[Finding] = []
            for t in targets:
                results.extend(self._run_local(t, tools, pipeline_mode))
            return results

        results: List[Finding] = []

        def send(url: str, tgt: str) -> List[Finding]:
            try:
                resp = requests.post(
                    f"{url}/scan",
                    json={"target": tgt, "tools": tools, "pipeline": pipeline_mode},
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                data = resp.json().get("findings", [])
                return [Finding(tool=d.pop("tool"), data=d) for d in data]
            except Exception as exc:  # noqa: BLE001
                logger.error("Runner %s failed for %s: %s", url, tgt, exc)
                return self._run_local(tgt, tools, pipeline_mode)

        with ThreadPoolExecutor() as pool:
            futs = []
            for idx, tgt in enumerate(targets):
                url = available[idx % len(available)]
                futs.append(pool.submit(send, url, tgt))
            for fut in futs:
                results.extend(fut.result())

        return results
