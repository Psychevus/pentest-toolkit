from modules.base import Finding
from utils.notifiers import (
    SlackNotifier,
    TeamsNotifier,
    DiscordNotifier,
    TelegramNotifier,
    ElasticsearchNotifier,
    SplunkNotifier,
)
import requests
import pytest


def _sample():
    return [Finding(tool="dummy", data={"foo": "bar"})]


def _fake_post(payloads):
    def _post(url, json=None, headers=None, timeout=10):
        payloads["url"] = url
        payloads["json"] = json
        payloads["headers"] = headers
        class Resp:
            status_code = 200
            def raise_for_status(self):
                pass
        return Resp()
    return _post


def test_slack_notifier(monkeypatch):
    payloads = {}
    monkeypatch.setattr("utils.notifiers.requests.post", _fake_post(payloads))
    SlackNotifier("http://example.com").send(_sample())
    assert payloads["url"] == "http://example.com"
    assert "Pentest-Toolkit" in payloads["json"]["text"]


def test_teams_notifier(monkeypatch):
    payloads = {}
    monkeypatch.setattr("utils.notifiers.requests.post", _fake_post(payloads))
    TeamsNotifier("http://example.com").send(_sample())
    assert payloads["url"] == "http://example.com"
    assert "Pentest-Toolkit" in payloads["json"]["text"]


def test_discord_notifier(monkeypatch):
    payloads = {}
    monkeypatch.setattr("utils.notifiers.requests.post", _fake_post(payloads))
    DiscordNotifier("http://example.com").send(_sample())
    assert payloads["url"] == "http://example.com"
    assert "Pentest-Toolkit" in payloads["json"]["content"]


def test_telegram_notifier(monkeypatch):
    payloads = {}
    monkeypatch.setattr("utils.notifiers.requests.post", _fake_post(payloads))
    TelegramNotifier("tok", "chat").send(_sample())
    assert "bottok" in payloads["url"]
    assert payloads["json"]["chat_id"] == "chat"


def test_elasticsearch_notifier(monkeypatch):
    payloads = {}
    monkeypatch.setattr("utils.notifiers.requests.post", _fake_post(payloads))
    ElasticsearchNotifier("http://es").send(_sample())
    assert payloads["url"] == "http://es"
    assert isinstance(payloads["json"], list)


def test_splunk_notifier(monkeypatch):
    payloads = {}
    monkeypatch.setattr("utils.notifiers.requests.post", _fake_post(payloads))
    SplunkNotifier("http://spl", "tok").send(_sample())
    assert payloads["headers"]["Authorization"] == "Splunk tok"


def test_notifier_failure(monkeypatch):
    def boom(url, json=None, headers=None, timeout=10):
        raise requests.RequestException("fail")
    monkeypatch.setattr("utils.notifiers.requests.post", boom)
    with pytest.raises(requests.RequestException):
        SlackNotifier("http://bad", strict=True).send(_sample())
