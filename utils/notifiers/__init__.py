from __future__ import annotations

"""Notification plugins for Pentest‑Toolkit."""

import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Type

import requests

from modules.base import Finding
from utils.logger import get_logger

logger = get_logger()


class Notifier(ABC):
    """Base class for notification plugins."""

    registry: Dict[str, Type["Notifier"]] = {}
    name: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if getattr(cls, "name", None):
            Notifier.registry[cls.name] = cls

    @abstractmethod
    def send(self, findings: List[Finding]) -> None:
        """Send *findings* to the destination."""
        ...


class SlackNotifier(Notifier):
    """Send results to a Slack webhook."""

    name = "slack"

    def __init__(self, webhook: str | None = None, *, strict: bool = False):
        self.webhook = webhook or os.environ.get("SLACK_WEBHOOK")
        self.strict = strict

    def send(self, findings: List[Finding]) -> None:
        if not self.webhook:
            logger.warning("Slack webhook not configured")
            return
        payload = {
            "text": "Pentest-Toolkit results:\n```%s```"
            % json.dumps([f.asdict() for f in findings], indent=2)
        }
        try:
            resp = requests.post(self.webhook, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info("\U0001F4E3 Slack notification -> %s", resp.status_code)
        except requests.RequestException as exc:  # noqa: BLE001
            logger.warning("\u26A0\uFE0F Slack notification failed: %s", exc)
            if self.strict:
                raise


class TeamsNotifier(Notifier):
    """Send results to a Microsoft Teams webhook."""

    name = "teams"

    def __init__(self, webhook: str | None = None, *, strict: bool = False):
        self.webhook = webhook or os.environ.get("TEAMS_WEBHOOK")
        self.strict = strict

    def send(self, findings: List[Finding]) -> None:
        if not self.webhook:
            logger.warning("Teams webhook not configured")
            return
        payload = {
            "text": "Pentest-Toolkit results:\n%s"
            % json.dumps([f.asdict() for f in findings], indent=2)
        }
        try:
            resp = requests.post(self.webhook, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info("\U0001F4E3 Teams notification -> %s", resp.status_code)
        except requests.RequestException as exc:  # noqa: BLE001
            logger.warning("\u26A0\uFE0F Teams notification failed: %s", exc)
            if self.strict:
                raise


class DiscordNotifier(Notifier):
    """Send results to a Discord webhook."""

    name = "discord"

    def __init__(self, webhook: str | None = None, *, strict: bool = False):
        self.webhook = webhook or os.environ.get("DISCORD_WEBHOOK")
        self.strict = strict

    def send(self, findings: List[Finding]) -> None:
        if not self.webhook:
            logger.warning("Discord webhook not configured")
            return
        payload = {
            "content": "Pentest-Toolkit results:\n```%s```"
            % json.dumps([f.asdict() for f in findings], indent=2)
        }
        try:
            resp = requests.post(self.webhook, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info("\U0001F4E3 Discord notification -> %s", resp.status_code)
        except requests.RequestException as exc:  # noqa: BLE001
            logger.warning("\u26A0\uFE0F Discord notification failed: %s", exc)
            if self.strict:
                raise


class TelegramNotifier(Notifier):
    """Send results via the Telegram Bot API."""

    name = "telegram"

    def __init__(
        self,
        token: str | None = None,
        chat_id: str | None = None,
        *,
        strict: bool = False,
    ):
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
        self.strict = strict

    def send(self, findings: List[Finding]) -> None:
        if not self.token or not self.chat_id:
            logger.warning("Telegram token/chat_id not configured")
            return
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": "Pentest-Toolkit results:\n```%s```"
            % json.dumps([f.asdict() for f in findings], indent=2),
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info("\U0001F4E3 Telegram notification -> %s", resp.status_code)
        except requests.RequestException as exc:  # noqa: BLE001
            logger.warning("\u26A0\uFE0F Telegram notification failed: %s", exc)
            if self.strict:
                raise


class ElasticsearchNotifier(Notifier):
    """Push results to an Elasticsearch HTTP endpoint."""

    name = "elasticsearch"

    def __init__(self, url: str | None = None, *, strict: bool = False):
        self.url = url or os.environ.get("ELASTICSEARCH_URL")
        self.strict = strict

    def send(self, findings: List[Finding]) -> None:
        if not self.url:
            logger.warning("Elasticsearch URL not configured")
            return
        try:
            resp = requests.post(
                self.url,
                json=[f.asdict() for f in findings],
                timeout=10,
            )
            resp.raise_for_status()
            logger.info(
                "\U0001F4E3 Elasticsearch notification -> %s",
                resp.status_code,
            )
        except requests.RequestException as exc:  # noqa: BLE001
            logger.warning("\u26A0\uFE0F Elasticsearch notification failed: %s", exc)
            if self.strict:
                raise


class SplunkNotifier(Notifier):
    """Send results to Splunk via HTTP Event Collector."""

    name = "splunk"

    def __init__(
        self,
        url: str | None = None,
        token: str | None = None,
        *,
        strict: bool = False,
    ):
        self.url = url or os.environ.get("SPLUNK_HEC_URL")
        self.token = token or os.environ.get("SPLUNK_HEC_TOKEN")
        self.strict = strict

    def send(self, findings: List[Finding]) -> None:
        if not self.url or not self.token:
            logger.warning("Splunk HEC configuration missing")
            return
        headers = {"Authorization": f"Splunk {self.token}"}
        payload = [{"event": f.asdict()} for f in findings]
        try:
            resp = requests.post(self.url, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            logger.info("\U0001F4E3 Splunk notification -> %s", resp.status_code)
        except requests.RequestException as exc:  # noqa: BLE001
            logger.warning("\u26A0\uFE0F Splunk notification failed: %s", exc)
            if self.strict:
                raise


__all__ = [
    "Notifier",
    "SlackNotifier",
    "TeamsNotifier",
    "DiscordNotifier",
    "TelegramNotifier",
    "ElasticsearchNotifier",
    "SplunkNotifier",
]
