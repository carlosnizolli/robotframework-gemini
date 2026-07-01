"""Map legacy QA env vars to GEMINI_* and ensure the package is importable in Docker mounts."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def ensure_importable() -> None:
    """Add ``src/`` to ``sys.path`` when the package is not installed (repo volume mount)."""
    try:
        import robotframework_gemini.client  # noqa: F401
        return
    except ImportError:
        pass
    src = Path(__file__).resolve().parent.parent
    src_str = str(src)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


def ensure_gemini_env_from_legacy() -> None:
    """
  Set GEMINI_API_KEY / GEMINI_MODEL from names used by NCM PRO and LIA suites
  when the new variables are not already defined.
  """
    if not os.environ.get("GEMINI_API_KEY"):
        for key in ("LLM_API_KEY", "LLM_API_KEY_LIA"):
            value = os.environ.get(key)
            if value:
                os.environ["GEMINI_API_KEY"] = value
                break
    if not os.environ.get("GEMINI_MODEL"):
        value = os.environ.get("LLM_LIA_MODEL")
        if value:
            os.environ["GEMINI_MODEL"] = value
