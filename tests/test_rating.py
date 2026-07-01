from robotframework_gemini.client import GeminiOrchestrator
from robotframework_gemini.library import GeminiLibrary
from robotframework_gemini.prompt_build import (
    DEFAULT_RATING_OUTPUT_INSTRUCTIONS,
    build_evaluation_prompt,
    merge_extra_instructions,
)
from robotframework_gemini.response_parse import normalize_rating


def test_merge_extra_instructions_appends_caller_text():
    merged = merge_extra_instructions("Base rubric.", "Treat missing data as score 1.")
    assert "Base rubric." in merged
    assert "Treat missing data as score 1." in merged


def test_build_evaluation_prompt_with_rating_extra():
    extra = merge_extra_instructions(DEFAULT_RATING_OUTPUT_INSTRUCTIONS)
    prompt = build_evaluation_prompt("Ctx", "Crit", extra_instructions=extra)
    assert "SCORE:" in prompt
    assert "Rubrica" in prompt
    assert "não presuma formato de pergunta" in prompt
    assert "## Contexto" in prompt


def test_normalize_rating_score_line():
    raw = "SCORE: 4\nREASON: Clear and mostly complete."
    assert normalize_rating(raw) == "4"


def test_normalize_rating_nota_line():
    assert normalize_rating("NOTA: 2\nRAZÃO: lacunas.") == "2"


def test_normalize_rating_fraction_and_standalone():
    assert normalize_rating("Overall 3/5 for partial match.") == "3"
    assert normalize_rating("5") == "5"


def test_normalize_rating_returns_raw_when_unparseable():
    raw = "Unable to judge from the provided text."
    assert normalize_rating(raw) == raw


def test_evaluate_with_text_rating_uses_rubric(monkeypatch):
    captured: dict = {}

    def fake_generate(prompt: str) -> str:
        captured["prompt"] = prompt
        return "SCORE: 5\nREASON: ok"

    orch = GeminiOrchestrator(api_key="k", model="m")
    monkeypatch.setattr(orch, "generate_from_text", fake_generate)

    out = orch.evaluate_with_text_rating("API payload excerpt", "Is the structure consistent and complete?")
    assert out == "SCORE: 5\nREASON: ok"
    assert "SCORE:" in captured["prompt"]
    assert "Is the structure consistent and complete?" in captured["prompt"]
    assert orch.parse_rating(out) == "5"


def test_library_gemini_evaluate_text_rating_score_keyword(monkeypatch):
    lib = GeminiLibrary(api_key="k", model="m")

    def fake_rating(context, evaluation, extra_instructions=None):
        return "SCORE: 4\nREASON: Mostly complete."

    monkeypatch.setattr(lib, "gemini_evaluate_text_rating", fake_rating)

    score = lib.gemini_evaluate_text_rating_score("context", "evaluation")
    assert score == "4"
