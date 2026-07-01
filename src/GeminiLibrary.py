"""Top-level shim so ``Library    GeminiLibrary`` resolves via ``import GeminiLibrary``.

Robot Framework entry points work at runtime; RobotCode and other tools often
import the library name as a Python module first.
"""

from robotframework_gemini.library import GeminiLibrary

__all__ = ["GeminiLibrary"]
