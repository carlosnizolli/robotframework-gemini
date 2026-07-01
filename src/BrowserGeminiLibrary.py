"""Backward-compatible shim for ``Library    BrowserGeminiLibrary``."""

from robotframework_gemini.library import GeminiLibrary


class BrowserGeminiLibrary(GeminiLibrary):
    """Alias of :class:`robotframework_gemini.library.GeminiLibrary`."""


__all__ = ["BrowserGeminiLibrary"]
