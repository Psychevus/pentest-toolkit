import json
import shlex
import subprocess
from pathlib import Path
from typing import List

from utils.logger import get_logger
from modules.base import Module, Finding
from utils.output import timestamp, safe_filename_component

logger = get_logger()


class Katana(Module):
    """Endpoint crawler using katana."""

    name = "katana"
    TIMEOUT = 300
    input_types = ["url"]

    def run(self, target: str) -> List[Finding]:
        logger.info("🕷️ katana …")
        out_dir = Path("output")
        out_dir.mkdir(exist_ok=True)
        safe = safe_filename_component(target)
        out_file = out_dir / f"katana_{safe}_{timestamp()}.json"
        cmd = f"{self.bin('katana')} -u {shlex.quote(target)} -json -o {out_file}"
        try:
            subprocess.run(shlex.split(cmd), check=True, timeout=self.TIMEOUT)
        except subprocess.CalledProcessError:
            raise RuntimeError("katana failed")

        findings: List[Finding] = []
        for line in out_file.read_text().splitlines():
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except Exception:
                continue
            findings.append(Finding(self.name, data))
        findings.append(Finding(self.name, {"report": str(out_file)}))
        logger.info("🕷️ katana -> %s entries", len(findings) - 1)
        return findings
