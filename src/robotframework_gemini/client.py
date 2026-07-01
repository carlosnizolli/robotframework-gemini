"""Gemini client: multimodal (image file) and text-only calls."""

from __future__ import annotations

import logging
import mimetypes
import os
from pathlib import Path

from google import genai
from google.genai import types

from robotframework_gemini.prompt_build import (
    DEFAULT_RATING_OUTPUT_INSTRUCTIONS,
    build_evaluation_prompt,
    merge_extra_instructions,
)
from robotframework_gemini.response_parse import normalize_rating

logger = logging.getLogger(__name__)

_DEFAULT_IMAGE_MIME = "image/png"


def _mime_for_path(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    return mime or _DEFAULT_IMAGE_MIME


class GeminiOrchestrator:
    """
    Thin wrapper around google-genai for test oracles.

    Environment:
    - GEMINI_API_KEY for the API key (unless ``api_key`` is passed explicitly)
    - GEMINI_MODEL for model id (e.g. gemini-2.5-flash); defaults to gemini-2.5-flash
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
    ):
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError(
                "Missing API key: set GEMINI_API_KEY (or pass api_key=...)"
            )
        self.model = model or os.environ.get("GEMINI_MODEL") or "gemini-2.5-flash"
        self._client = genai.Client(api_key=key)

    def generate_from_text(self, prompt: str) -> str:
        response = self._client.models.generate_content(model=self.model, contents=prompt)
        text = (response.text or "").strip()
        logger.debug("generate_from_text chars=%s", len(text))
        return text

    def generate_with_image_file(self, prompt: str, image_path: str | Path) -> str:
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(f"Image not found: {path}")
        data = path.read_bytes()
        mime = _mime_for_path(path)
        parts = [
            types.Part.from_text(text=prompt),
            types.Part.from_bytes(data=data, mime_type=mime),
        ]
        response = self._client.models.generate_content(
            model=self.model,
            contents=parts,
        )
        text = (response.text or "").strip()
        logger.debug("generate_with_image_file chars=%s mime=%s", len(text), mime)
        return text

    def generate_with_image_and_html(
        self,
        prompt: str,
        image_path: str | Path,
        html_text: str,
        *,
        max_html_chars: int = 120_000,
    ) -> str:
        """Multimodal image + truncated HTML as additional text part."""
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(f"Image not found: {path}")
        data = path.read_bytes()
        mime = _mime_for_path(path)
        html_snip = html_text[:max_html_chars] if html_text else ""
        combined_prompt = f"{prompt}\n\n--- HTML (truncado) ---\n{html_snip}"
        parts = [
            types.Part.from_text(text=combined_prompt),
            types.Part.from_bytes(data=data, mime_type=mime),
        ]
        response = self._client.models.generate_content(
            model=self.model,
            contents=parts,
        )
        return (response.text or "").strip()

    def evaluate_with_image(
        self,
        context: str,
        evaluation: str,
        image_path: str | Path,
        *,
        extra_instructions: str | None = None,
    ) -> str:
        prompt = build_evaluation_prompt(
            context,
            evaluation,
            extra_instructions=extra_instructions,
            include_visual_focus=True,
        )
        return self.generate_with_image_file(prompt, image_path)

    def evaluate_with_image_and_html(
        self,
        context: str,
        evaluation: str,
        image_path: str | Path,
        html_text: str,
        *,
        extra_instructions: str | None = None,
        max_html_chars: int = 120_000,
    ) -> str:
        prompt = build_evaluation_prompt(
            context,
            evaluation,
            extra_instructions=extra_instructions,
            include_visual_focus=True,
        )
        return self.generate_with_image_and_html(
            prompt, image_path, html_text, max_html_chars=max_html_chars
        )

    def evaluate_with_text(
        self,
        context: str,
        evaluation: str,
        *,
        extra_instructions: str | None = None,
    ) -> str:
        prompt = build_evaluation_prompt(
            context,
            evaluation,
            extra_instructions=extra_instructions,
            include_visual_focus=False,
        )
        return self.generate_from_text(prompt)

    def evaluate_with_text_rating(
        self,
        context: str,
        evaluation: str,
        *,
        extra_instructions: str | None = None,
    ) -> str:
        """Generic text-only judge: score how well ``context`` meets ``evaluation`` on a 1–5 scale."""
        rating_extra = merge_extra_instructions(
            DEFAULT_RATING_OUTPUT_INSTRUCTIONS,
            extra_instructions,
        )
        return self.evaluate_with_text(
            context,
            evaluation,
            extra_instructions=rating_extra,
        )

    @staticmethod
    def parse_rating(raw: str) -> str:
        return normalize_rating(raw)
