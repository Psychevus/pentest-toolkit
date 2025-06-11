from __future__ import annotations

"""Dynamic plugin loader for Pentest-Toolkit."""

import importlib.util
import os
from pathlib import Path

from utils.logger import get_logger

logger = get_logger()


def load_plugins(directory: Path | None = None) -> None:
    """Load all plugin modules from *directory*.

    If *directory* is ``None`` the location is resolved from the
    ``PENTEST_TOOLKIT_PLUGIN_DIR`` environment variable or defaults to a local
    ``plugins`` folder. Python files and packages are imported and any
    ``Module`` subclasses defined within will auto-register via
    ``Module.__init_subclass__``.
    """
    if directory is None:
        env = os.environ.get("PENTEST_TOOLKIT_PLUGIN_DIR")
        directory = Path(env) if env else Path("plugins")

    if not directory.exists():
        logger.info("No plugin directory %s", directory)
        return

    for path in directory.iterdir():
        if path.name.startswith("_"):
            continue
        if path.is_dir() and (path / "__init__.py").exists():
            file = path / "__init__.py"
        elif path.is_file() and path.suffix == ".py":
            file = path
        else:
            continue

        spec = importlib.util.spec_from_file_location(path.stem, file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                logger.info("\ud83d\udd0c Plugin loaded: %s", path.stem)
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to load plugin %s: %s", path, exc)
        else:
            logger.warning("Could not load plugin %s", path)

