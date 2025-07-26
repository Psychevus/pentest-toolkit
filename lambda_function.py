"""AWS Lambda entrypoint for Pentest-Toolkit."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from modules.base import Module
from utils.deps import check_dependencies, DependencyError
from utils.logger import get_logger
from utils.notifiers import Notifier
from utils.output import (
    write_html,
    write_json,
    write_pdf,
    write_markdown,
    safe_filename_component,
)
from utils.plugins import load_plugins
from main import pipeline

load_plugins()

logger = get_logger()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda entrypoint.

    Expected *event* keys:
        - ``target``: domain or IP address to scan (required)
        - ``tools``: optional list of tools
        - ``report``: ``"html"``, ``"pdf"``, ``"markdown"`` or ``"summary"``
        - ``notify``: list of notifier names (e.g. ``["slack"]``)
        - ``auto_install``: attempt to install missing binaries (bool)
    """

    target = event["target"]
    tools: List[str] = event.get("tools", list(Module.registry.keys()))
    report = event.get("report")
    notify_names: List[str] = event.get("notify", [])
    strict_notify = event.get("strict_notify", False)
    auto_install = event.get("auto_install", False)
    pipeline_mode = event.get("pipeline", False)

    out_dir = Path("/tmp/output")

    notifiers = [
        Notifier.registry[name](strict=strict_notify)
        for name in notify_names
        if name in Notifier.registry
    ]

    try:
        check_dependencies(tools, auto_install=auto_install)
    except DependencyError as exc:
        logger.error("❌ %s", exc)
        raise RuntimeError(str(exc))

    findings = pipeline(target, tools, use_pipeline=pipeline_mode, show_summary=False)
    ai_text: str | None = None
    if event.get("triage"):
        from utils.analyst import analyse_findings

        ai_text = analyse_findings(findings)
    prefix = safe_filename_component(target)
    json_path = write_json(findings, out_dir, prefix=prefix)

    if report == "html":
        write_html(findings, out_dir, prefix=prefix)
    elif report == "pdf":
        write_pdf(findings, out_dir, prefix=prefix, ai_summary=ai_text)
    elif report == "markdown":
        write_markdown(findings, out_dir, prefix=prefix, ai_summary=ai_text)
    elif report == "summary":
        write_markdown(findings, out_dir, prefix=prefix, summary_only=True, ai_summary=ai_text)

    for notifier in notifiers:
        try:
            notifier.send(findings)
        except Exception as exc:  # noqa: BLE001
            logger.error("❌ Notifier error: %s", exc)
            if strict_notify:
                raise RuntimeError(str(exc))

    return {"count": len(findings), "json": str(json_path)}
