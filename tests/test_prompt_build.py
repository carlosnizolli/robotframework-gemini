from robotframework_gemini.prompt_build import build_evaluation_prompt


def test_build_evaluation_prompt_sections():
    p = build_evaluation_prompt("Alpha context", "Beta evaluation")
    assert "Alpha context" in p
    assert "Beta evaluation" in p
    assert "## Contexto" in p
    assert "## O que avaliar" in p


def test_build_evaluation_prompt_visual_focus():
    p = build_evaluation_prompt("c", "e", include_visual_focus=True)
    assert "captura de tela" in p.lower()


def test_build_evaluation_prompt_extra():
    p = build_evaluation_prompt("c", "e", extra_instructions="Say maybe.")
    assert "## Instruções adicionais de resposta" in p
    assert "Say maybe." in p
