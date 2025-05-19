import json
import shlex
import subprocess
from typing import List

from utils.logger import get_logger
from modules.base import Module, Finding

logger = get_logger()


class Subfinder(Module):
    name = "subfinder"
    TIMEOUT = 120

    def run(self, target: str) -> List[Finding]:
        logger.info("🔎 subfinder …")
        cmd = f"{self.bin('subfinder')} -silent -json -d {shlex.quote(target)}"
        try:
            proc = subprocess.run(
                shlex.split(cmd),
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"subfinder failed: {exc.stderr}")

        findings = [
            Finding(self.name, json.loads(line))
            for line in proc.stdout.splitlines()
            if line.strip()
        ]
        logger.info("🔎 subfinder -> %s hosts", len(findings))
        return findings
