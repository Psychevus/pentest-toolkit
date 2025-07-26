import shlex
import subprocess
from pathlib import Path
from typing import List

from utils.logger import get_logger
from modules.base import Module, Finding
from utils.output import timestamp, safe_filename_component

logger = get_logger()


class Screenshot(Module):
    """Capture webpage screenshots using headless Chrome."""

    name = "screenshot"
    TIMEOUT = 120
    input_types = ["url"]

    def run(self, target: str) -> List[Finding]:
        logger.info("📸 screenshot …")
        out_dir = Path("output")
        out_dir.mkdir(exist_ok=True)
        safe = safe_filename_component(target)
        out_file = out_dir / f"screenshot_{safe}_{timestamp()}.png"
        cmd = (
            f"{self.bin('google-chrome')} --headless --disable-gpu "
            f"--screenshot={out_file} --window-size=1280,1024 {shlex.quote(target)}"
        )
        try:
            subprocess.run(shlex.split(cmd), check=True, timeout=self.TIMEOUT)
        except subprocess.CalledProcessError:
            raise RuntimeError("screenshot failed")

        logger.info("📸 screenshot -> %s", out_file)
        return [Finding(self.name, {"image": str(out_file)})]
