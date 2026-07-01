"""Unit tests without calling the real Gemini API."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from robotframework_gemini.client import GeminiOrchestrator


@pytest.fixture()
def png_file(tmp_path: Path) -> Path:
    p = tmp_path / "shot.png"
    p.write_bytes(b"\x89PNG\r\n\x1a\n\x00fake")
    return p


@patch.dict(
    "os.environ",
    {"GEMINI_API_KEY": "x", "GEMINI_MODEL": "gemini-2.0-flash-test"},
    clear=False,
)
@patch("robotframework_gemini.client.genai.Client")
def test_generate_with_image_file_uses_parts(mock_client_cls, png_file: Path):
    mock_response = MagicMock()
    mock_response.text = "  Sim.\nMotivo compatível."

    inner = MagicMock()
    inner.generate_content.return_value = mock_response
    models = MagicMock()
    models.generate_content = inner.generate_content
    client_inst = MagicMock()
    client_inst.models = models
    mock_client_cls.return_value = client_inst

    g = GeminiOrchestrator(api_key="k", model="m")
    out = g.generate_with_image_file("Olhe a UI", png_file)

    inner.generate_content.assert_called_once()
    call_kw = inner.generate_content.call_args.kwargs
    assert call_kw["model"] == "m"
    contents = call_kw["contents"]
    assert isinstance(contents, list)
    assert len(contents) >= 2
    assert out == "Sim.\nMotivo compatível."


@patch.dict(
    "os.environ",
    {"GEMINI_API_KEY": "x"},
    clear=False,
)
@patch("robotframework_gemini.client.genai.Client")
def test_evaluate_with_image_embeds_context_and_evaluation(mock_client_cls, png_file: Path):
    mock_response = MagicMock()
    mock_response.text = "ok"

    inner = MagicMock()
    inner.generate_content.return_value = mock_response
    models = MagicMock()
    models.generate_content = inner.generate_content
    client_inst = MagicMock()
    client_inst.models = models
    mock_client_cls.return_value = client_inst

    g = GeminiOrchestrator(api_key="k", model="m")
    g.evaluate_with_image("CTX_MARKER", "EVAL_MARKER", png_file)

    parts = inner.generate_content.call_args.kwargs["contents"]
    text_part = parts[0]
    prompt_text = text_part.text
    assert "CTX_MARKER" in prompt_text
    assert "EVAL_MARKER" in prompt_text
    assert "## Contexto" in prompt_text
    assert "## O que avaliar" in prompt_text


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        GeminiOrchestrator(api_key=None)
