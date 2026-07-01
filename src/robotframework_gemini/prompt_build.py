"""Compose neutral Portuguese prompts from context + evaluation criteria."""

DEFAULT_RATING_OUTPUT_INSTRUCTIONS = """\
Atribua uma nota inteira de 1 a 5 julgando o contexto fornecido apenas pelos critérios acima.
O contexto pode ser qualquer evidência de teste (resposta de API, trecho de log, texto de UI, \
transcrição, JSON, markdown, etc.) — não presuma formato de pergunta e resposta.

Formato obrigatório da resposta (exatamente duas linhas):
SCORE: <1|2|3|4|5>
REASON: <uma frase curta justificando a nota>

Rubrica (quão bem o contexto atende ao critério em ## O que avaliar):
1 — Não atende: falha grave ou critério central ausente.
2 — Atende minimamente: lacunas importantes ou incoerências relevantes.
3 — Atende parcialmente: cumpre parte do critério, com ressalvas claras.
4 — Atende bem: cumpre o critério com pequenas imperfeições.
5 — Atende plenamente: cumpre o critério de forma clara e completa.

Regras:
- Use somente inteiros de 1 a 5 em SCORE (sem decimais, sem escala 0–10).
- Não inclua texto antes da linha SCORE.
- Baseie-se apenas nas evidências presentes no contexto; não invente fatos."""


def merge_extra_instructions(
    base: str,
    extra_instructions: str | None = None,
) -> str:
    """Append caller overrides after structured base instructions."""
    parts = [base.strip()]
    if extra_instructions and extra_instructions.strip():
        parts.append(extra_instructions.strip())
    return "\n\n".join(parts)


def build_evaluation_prompt(
    context: str,
    evaluation: str,
    *,
    extra_instructions: str | None = None,
    include_visual_focus: bool = False,
) -> str:
    """
    Build a single prompt from caller-supplied context and what to judge.

    When ``include_visual_focus`` is True (screenshot/multimodal), remind the model
    to rely only on what is visibly rendered.
    """
    parts: list[str] = []

    if include_visual_focus:
        parts.append(
            "Uma captura de tela acompanha esta mensagem. Baseie-se apenas no que está "
            "claramente visível na imagem (textos, números, cores e layout renderizado). "
            "Não invente detalhes que não apareçam na captura."
        )

    parts.extend(
        [
            "## Contexto",
            context.strip(),
            "",
            "## O que avaliar",
            evaluation.strip(),
        ]
    )

    if extra_instructions and extra_instructions.strip():
        parts.extend(["", "## Instruções adicionais de resposta", extra_instructions.strip()])

    return "\n".join(parts)
