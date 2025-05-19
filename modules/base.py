"""
Shared abstractions for every tool wrapper in Pentest‑Toolkit.

Key features
------------
• Dataclass `Finding` – single, typed container for all module results
• `Module` ABC – enforces a uniform interface and auto‑registers subclasses
• `BIN_DIR` override – honour `$PENTEST_TOOLKIT_BIN_DIR` for portable installs
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Type


# --------------------------------------------------------------------------- #
# Result model
# --------------------------------------------------------------------------- #
@dataclass(slots=True)
class Finding:
    """
    A single piece of information discovered by a module.

    The `tool` attribute is set automatically inside each wrapper, so callers
    can merge heterogeneous results without losing provenance.
    """
    tool: str
    data: Dict[str, Any]

    def asdict(self) -> Dict[str, Any]:
        """Return a JSON‑serialisable dictionary."""
        return {"tool": self.tool, **self.data}


# --------------------------------------------------------------------------- #
# Abstract module base
# --------------------------------------------------------------------------- #
class Module(ABC):
    """
    Every tool wrapper inherits from `Module`.

    Sub‑classes register themselves in `Module.registry` which eliminates the
    need to maintain a manual TOOL_MAP in main.py.
    """

    registry: Dict[str, Type["Module"]] = {}

    BIN_DIR = Path(os.environ.get("PENTEST_TOOLKIT_BIN_DIR", ""))

    # ---- required by implementers ---------------------------------------- #
    name: str

    def __init_subclass__(cls, **kwargs):
        """Automatically add concrete subclasses to the registry."""
        super().__init_subclass__(**kwargs)
        if getattr(cls, "name", None):
            Module.registry[cls.name] = cls

    @abstractmethod
    def run(self, target: str) -> List[Finding]:
        """
        Execute the underlying binary against *target* and return findings.

        Implementations MUST raise a RuntimeError (or subclass) if execution
        fails so that callers can handle errors uniformly.
        """
        ...

    # ---- helper utilities ------------------------------------------------ #
    @classmethod
    def bin(cls, default: str) -> str:
        """
        Resolve the path of an executable.

        If `$PENTEST_TOOLKIT_BIN_DIR` is set, binaries are expected inside
        that directory; otherwise the plain name is returned (system PATH).
        """
        return str(cls.BIN_DIR / default) if cls.BIN_DIR else default
