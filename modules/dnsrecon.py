import shlex
import subprocess
from pathlib import Path
from typing import List

from utils.logger import get_logger
from modules.base import Module, Finding
from utils.output import timestamp, safe_filename_component

logger = get_logger()


class Dnsrecon(Module):
    """DNS zone transfer checks using dnsrecon."""

    name = "dnsrecon"
    TIMEOUT = 120
    input_types = ["domain"]

    def run(self, target: str) -> List[Finding]:
        logger.info("🔎 dnsrecon …")
        out_dir = Path("output")
        out_dir.mkdir(exist_ok=True)
        safe = safe_filename_component(target)
        out_file = out_dir / f"dnsrecon_{safe}_{timestamp()}.txt"
        cmd = f"{self.bin('dnsrecon')} -d {shlex.quote(target)} -t axfr"
        try:
            proc = subprocess.run(
                shlex.split(cmd),
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"dnsrecon failed: {exc.stderr}")

        out_file.write_text(proc.stdout)
        records = [
            Finding(self.name, {"record": line.strip()})
            for line in proc.stdout.splitlines()
            if line.strip()
        ]
        records.append(Finding(self.name, {"report": str(out_file)}))
        logger.info("🔎 dnsrecon -> %s records", len(records) - 1)
        return records
