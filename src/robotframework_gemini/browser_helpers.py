"""Capture screenshot / page source from an active Robot Framework Browser library."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def get_open_browser_library():
    """Return the live Browser library instance (Playwright) from Robot BuiltIn."""
    try:
        from robot.libraries.BuiltIn import BuiltIn
    except ImportError as e:
        raise RuntimeError("robotframework-gemini: Robot Framework not available") from e

    try:
        return BuiltIn().get_library_instance("Browser")
    except Exception as e:
        raise RuntimeError(
            "robotframework-gemini: Browser library is not open or not imported as 'Browser'"
        ) from e


def take_screenshot_to_path(
    output_path: str | Path,
    *,
    selector: str | None = None,
) -> str:
    """
    Call Browser.take_screenshot and return the path returned by the library.

    `selector` matches Browser kwarg when capturing an element region.
    """
    browser = get_open_browser_library()
    kw: dict[str, Any] = {"filename": str(output_path)}
    if selector:
        kw["selector"] = selector
    path = browser.take_screenshot(**kw)
    logger.debug("Screenshot written: %s", path)
    return str(path)


def get_page_source_text() -> str:
    browser = get_open_browser_library()
    if not hasattr(browser, "get_page_source"):
        raise RuntimeError("Browser library has no get_page_source")
    return browser.get_page_source()
