"""Robot Framework library: Gemini oracles (text-only and optional Browser screenshots)."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

try:
    from robot.api.deco import keyword
except ImportError:  # pragma: no cover

    def keyword(name: str | None = None, tags=()) -> Any:
        def decorator(func):
            return func

        return decorator


from robotframework_gemini.legacy_env import (
    ensure_gemini_env_from_legacy,
    ensure_importable,
)
from robotframework_gemini.browser_helpers import (
    get_page_source_text,
    take_screenshot_to_path,
)
from robotframework_gemini.client import GeminiOrchestrator

ensure_importable()
ensure_gemini_env_from_legacy()


class GeminiLibrary:
    """Keywords for Gemini text oracles and optional Browser screenshot capture."""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        self._api_key = api_key if api_key and str(api_key).strip() else None
        self._model = model if model and str(model).strip() else None
        self._orchestrator: GeminiOrchestrator | None = None

    def _get_orchestrator(self) -> GeminiOrchestrator:
        if self._orchestrator is None:
            self._orchestrator = GeminiOrchestrator(
                api_key=self._api_key,
                model=self._model,
            )
        return self._orchestrator

    # --- Generic evaluation (context + criteria) ---

    @keyword("Gemini Evaluate With Image File")
    def gemini_evaluate_with_image_file(
        self,
        context: str,
        evaluation: str,
        image_path: str,
        extra_instructions: str | None = None,
    ) -> str:
        """Send context + evaluation with an existing image file (multimodal)."""
        return self._get_orchestrator().evaluate_with_image(
            context,
            evaluation,
            image_path,
            extra_instructions=extra_instructions,
        )

    @keyword("Gemini Evaluate With Screen")
    def gemini_evaluate_with_screen(
        self,
        context: str,
        evaluation: str,
        selector: str | None = None,
        filename: str | None = None,
        extra_instructions: str | None = None,
    ) -> str:
        """Take a Browser screenshot, then evaluate with context + criteria."""
        path = self._resolve_screenshot_path(filename)
        take_screenshot_to_path(path, selector=selector)
        return self._get_orchestrator().evaluate_with_image(
            context,
            evaluation,
            path,
            extra_instructions=extra_instructions,
        )

    @keyword("Gemini Evaluate With Screen And Html")
    def gemini_evaluate_with_screen_and_html(
        self,
        context: str,
        evaluation: str,
        include_html: bool = True,
        filename: str | None = None,
        extra_instructions: str | None = None,
    ) -> str:
        """Screenshot plus optional DOM HTML (truncated in client) for richer context."""
        path = self._resolve_screenshot_path(filename)
        take_screenshot_to_path(path)
        orch = self._get_orchestrator()
        if include_html:
            html = get_page_source_text()
            return orch.evaluate_with_image_and_html(
                context,
                evaluation,
                path,
                html,
                extra_instructions=extra_instructions,
            )
        return orch.evaluate_with_image(
            context,
            evaluation,
            path,
            extra_instructions=extra_instructions,
        )

    @keyword("Gemini Evaluate Text")
    def gemini_evaluate_text(
        self,
        context: str,
        evaluation: str,
        extra_instructions: str | None = None,
    ) -> str:
        """Text-only oracle from context + evaluation (no screenshot)."""
        return self._get_orchestrator().evaluate_with_text(
            context,
            evaluation,
            extra_instructions=extra_instructions,
        )

    @keyword("Gemini Evaluate Text Verdict")
    def gemini_evaluate_text_verdict(
        self,
        context: str,
        evaluation: str,
        output_instructions: str,
    ) -> str:
        """Text judge: ``output_instructions`` defines the verdict format (e.g. Sim/Não/Aviso).

        Returns raw model text. The test asserts the verdict (e.g. first line with ``Get Line``).
        """
        return self._get_orchestrator().evaluate_with_text(
            context,
            evaluation,
            extra_instructions=output_instructions,
        )

    @keyword("Gemini Evaluate Text Rating")
    def gemini_evaluate_text_rating(
        self,
        context: str,
        evaluation: str,
        extra_instructions: str | None = None,
    ) -> str:
        """Generic text judge with a 1–5 rubric (returns raw SCORE/REASON lines).

        ``context`` — any test evidence (API body, logs, UI text, file excerpt, etc.).
        ``evaluation`` — criterion to score (how well the evidence meets the test intent).
        Use ``Gemini Parse Rating`` to extract the integer score (1–5).
        ``extra_instructions`` is appended after the built-in rubric.
        """
        return self._get_orchestrator().evaluate_with_text_rating(
            context,
            evaluation,
            extra_instructions=extra_instructions,
        )

    @keyword("Gemini Parse Rating")
    def gemini_parse_rating(self, raw_response: str) -> str:
        """Extract score 1–5 from a judge response; returns raw text if parsing fails."""
        return GeminiOrchestrator.parse_rating(raw_response)

    @keyword("Gemini Generate From Prompt")
    def gemini_generate_from_prompt(self, prompt: str) -> str:
        """Send a single text prompt and return the model reply (no context/evaluation template)."""
        return self._get_orchestrator().generate_from_text(prompt)

    # --- Single-prompt shortcuts (advanced) ---

    @keyword("Gemini Screenshot And Ask")
    def gemini_screenshot_and_ask(
        self,
        prompt: str,
        selector: str | None = None,
        filename: str | None = None,
    ) -> str:
        """
        Take a screenshot with Browser library, send PNG + prompt to Gemini, return text.

        If ``filename`` is omitted, a temp PNG under the system temp dir is used.
        Prefer ``Gemini Evaluate With Screen`` with separate context and evaluation.
        """
        path = self._resolve_screenshot_path(filename)
        take_screenshot_to_path(path, selector=selector)
        return self._get_orchestrator().generate_with_image_file(prompt, path)

    @keyword("Gemini Screenshot Html And Ask")
    def gemini_screenshot_html_and_ask(self, prompt: str, filename: str | None = None) -> str:
        """Screenshot full page + current page HTML (truncated inside client)."""
        path = self._resolve_screenshot_path(filename)
        take_screenshot_to_path(path)
        html = get_page_source_text()
        return self._get_orchestrator().generate_with_image_and_html(prompt, path, html)

    @staticmethod
    def _resolve_screenshot_path(filename: str | None) -> Path:
        if filename:
            return Path(filename)
        fd, name = tempfile.mkstemp(prefix="robotframework-gemini-", suffix=".png")
        os.close(fd)
        return Path(name)


# Backward-compatible alias for suites that import BrowserGeminiLibrary.
BrowserGeminiLibrary = GeminiLibrary
