from __future__ import annotations

"""Helpers for automatically installing external pentest tools."""

import platform
import shutil
import subprocess
from typing import Callable, Dict, Iterable, List, Optional

from utils.logger import get_logger

logger = get_logger()


def _os() -> str:
    """Return simplified OS name."""
    return platform.system().lower()


def _package_manager() -> Optional[str]:
    """Guess available package manager."""
    if _os() == "darwin" and shutil.which("brew"):
        return "brew"
    if _os() == "linux":
        if shutil.which("apt-get"):
            return "apt-get"
        if shutil.which("yum"):
            return "yum"
    return None


def _go_install(pkg: str) -> List[str]:
    return ["go", "install", pkg]


def _nmap_cmd() -> Optional[List[str]]:
    pm = _package_manager()
    if not pm:
        return None
    if pm == "brew":
        return ["brew", "install", "nmap"]
    return ["sudo", pm, "install", "-y", "nmap"]


INSTALL_CMDS: Dict[str, Callable[[], Optional[List[str]]]] = {
    "subfinder": lambda: _go_install(
        "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    ),
    "httpx": lambda: _go_install(
        "github.com/projectdiscovery/httpx/cmd/httpx@latest"
    ),
    "nuclei": lambda: _go_install(
        "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
    ),
    "nmap": _nmap_cmd,
    "testssl.sh": lambda: [
        "git",
        "clone",
        "--depth",
        "1",
        "https://github.com/drwetter/testssl.sh.git",
    ],
}


def install_tool(binary: str) -> bool:
    """Attempt to install *binary*. Return ``True`` on success."""
    fn = INSTALL_CMDS.get(binary)
    if not fn:
        logger.warning("No installation recipe for %s", binary)
        return False
    cmd = fn()
    if not cmd:
        logger.warning("Unsupported OS or missing package manager for %s", binary)
        return False
    logger.info("📦 Installing %s …", binary)
    try:
        subprocess.run(cmd, check=True)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to install %s: %s", binary, exc)
        return False
    logger.info("✅ Installed %s", binary)
    return True


def install_missing_tools(binaries: Iterable[str]) -> None:
    """Install all binaries in *binaries* if possible."""
    for binary in binaries:
        install_tool(binary)
