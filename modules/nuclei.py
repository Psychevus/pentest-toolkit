import json
import shlex
import subprocess
from typing import List

from utils.logger import get_logger
from modules.base import Module, Finding

logger = get_logger()


class Nuclei(Module):
    name = "nuclei"
    TIMEOUT = 600

    def run(self, target: str) -> List[Finding]:
        logger.info("\u2694\ufe0f nuclei \u2026")
        cmd = f"{self.bin('nuclei')} -json -l -"
        try:
            proc = subprocess.run(
                shlex.split(cmd),
                input=target,
                text=True,
                capture_output=True,
                timeout=self.TIMEOUT,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"nuclei failed: {exc.stderr}")

        findings = [
            Finding(self.name, json.loads(line))
            for line in proc.stdout.splitlines()
            if line.strip()
        ]
        logger.info("\u2694\ufe0f nuclei -> %s findings", len(findings))
        return findings
