"""Normalize structured LLM outputs (e.g. 1–5 ratings) for optional test assertions."""

from __future__ import annotations

import re

_SCORE_LINE = re.compile(
    r"(?im)^\s*(?:score|nota)\s*:\s*([1-5])\s*$"
)
_SCORE_FRACTION = re.compile(r"(?i)\b([1-5])\s*/\s*5\b")
_STANDALONE_SCORE = re.compile(r"(?m)^\s*([1-5])\s*$")


def normalize_rating(raw: str) -> str:
    """Extract an integer score from 1 to 5 when the model follows the rating format."""
    text = (raw or "").strip()
    if not text:
        return text

    match = _SCORE_LINE.search(text)
    if match:
        return match.group(1)

    for pattern in (_SCORE_FRACTION, _STANDALONE_SCORE):
        match = pattern.search(text)
        if match:
            return match.group(1)

    inline = re.search(r"(?i)(?:score|nota)\s*:\s*([1-5])\b", text)
    if inline:
        return inline.group(1)

    return text
