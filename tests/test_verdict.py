from robotframework_gemini.client import GeminiOrchestrator
from robotframework_gemini.library import GeminiLibrary


def test_evaluate_text_verdict_passes_output_instructions(monkeypatch):
    captured: dict = {}

    def fake_generate(prompt: str) -> str:
        captured["prompt"] = prompt
        return "Sim\nCoerente com a pergunta."

    orch = GeminiOrchestrator(api_key="k", model="m")
    monkeypatch.setattr(orch, "generate_from_text", fake_generate)

    out = orch.evaluate_with_text(
        "pergunta e resposta",
        "avalie coerência",
        extra_instructions="Responda Sim, Não ou Aviso na primeira linha.",
    )
    assert out == "Sim\nCoerente com a pergunta."
    assert "Responda Sim, Não ou Aviso" in captured["prompt"]


def test_library_gemini_evaluate_text_verdict_keyword(monkeypatch):
    captured: dict = {}

    def fake_evaluate(context, evaluation, extra_instructions=None):
        captured["context"] = context
        captured["evaluation"] = evaluation
        captured["extra"] = extra_instructions
        return "Não\nTema divergente."

    lib = GeminiLibrary(api_key="k", model="m")
    orch = GeminiOrchestrator(api_key="k", model="m")
    monkeypatch.setattr(lib, "_get_orchestrator", lambda: orch)
    monkeypatch.setattr(orch, "evaluate_with_text", fake_evaluate)

    out = lib.gemini_evaluate_text_verdict("ctx", "crit", "output fmt")
    assert out == "Não\nTema divergente."
    assert captured["extra"] == "output fmt"
