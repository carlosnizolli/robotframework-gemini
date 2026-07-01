"""Gemini-backed text and multimodal oracles for Robot Framework."""

from robotframework_gemini.legacy_env import (
    ensure_gemini_env_from_legacy,
    ensure_importable,
)

ensure_importable()
ensure_gemini_env_from_legacy()

from robotframework_gemini.client import GeminiOrchestrator
from robotframework_gemini.library import BrowserGeminiLibrary, GeminiLibrary

__all__ = [
    "GeminiOrchestrator",
    "GeminiLibrary",
    "BrowserGeminiLibrary",
    "__version__",
]

__version__ = "0.2.0"
