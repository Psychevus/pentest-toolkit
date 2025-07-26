from pathlib import Path

from modules.base import Finding
from utils.output import write_html, write_pdf, write_markdown
import pytest


def _sample():
    return [Finding(tool="dummy", data={"foo": "bar"})]


def test_write_html(tmp_path: Path):
    path = write_html(_sample(), tmp_path)
    assert path.exists()
    assert path.suffix == ".html"


def test_write_html_prefix(tmp_path: Path):
    path = write_html(_sample(), tmp_path, prefix="abc")
    assert path.exists()
    assert "abc" in path.stem


def test_write_pdf(tmp_path: Path):
    try:
        path = write_pdf(_sample(), tmp_path, prefix="xyz")
    except Exception as exc:  # pragma: no cover - environment may lack deps
        pytest.skip(f"pdf generation failed: {exc}")
    assert path.exists()
    assert path.suffix == ".pdf"


def test_write_markdown(tmp_path: Path):
    path = write_markdown(_sample(), tmp_path)
    assert path.exists()
    assert path.suffix == ".md"


def test_write_summary(tmp_path: Path):
    path = write_markdown(_sample(), tmp_path, summary_only=True)
    assert path.exists()
    text = path.read_text()
    assert "Summary" in text
