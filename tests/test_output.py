import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from modules.base import Finding
from utils.output import write_json


def _sample():
    return [Finding(tool="dummy", data={"foo": "bar"})]


def test_write_json(tmp_path: Path):
    path = write_json(_sample(), tmp_path)
    assert path.exists()
    assert path.suffix == ".json"
    data = json.loads(path.read_text())
    assert data[0]["foo"] == "bar"


def test_write_json_prefix(tmp_path: Path):
    path = write_json(_sample(), tmp_path, prefix="test")
    assert path.exists()
    assert "test" in path.stem
