import json
import shlex
import subprocess
from pathlib import Path
import os
from typing import List

from utils.logger import get_logger
from modules.base import Module, Finding
from utils.output import timestamp, safe_filename_component

logger = get_logger()


class Ffuf(Module):
    """Directory brute-forcing using ffuf."""

    name = "ffuf"
    TIMEOUT = 600
    input_types = ["url"]
    WORDLIST = Path(
        os.environ.get(
            "FFUF_WORDLIST", "/usr/share/seclists/Discovery/Web-Content/common.txt"
        )
    )

    def run(self, target: str) -> List[Finding]:
        logger.info("🗂️ ffuf …")
        out_dir = Path("output")
        out_dir.mkdir(exist_ok=True)
        safe = safe_filename_component(target)
        out_file = out_dir / f"ffuf_{safe}_{timestamp()}.json"
        cmd = (
            f"{self.bin('ffuf')} -u {shlex.quote(target.rstrip('/'))}/FUZZ "
            f"-w {shlex.quote(str(self.WORDLIST))} -of json -o {out_file}"
        )
        try:
            subprocess.run(shlex.split(cmd), check=True, timeout=self.TIMEOUT)
        except subprocess.CalledProcessError:
            raise RuntimeError("ffuf failed")

        data = json.loads(out_file.read_text()).get("results", [])
        findings = [Finding(self.name, r) for r in data]
        findings.append(Finding(self.name, {"report": str(out_file)}))
        logger.info("🗂️ ffuf -> %s entries", len(data))
        return findings
