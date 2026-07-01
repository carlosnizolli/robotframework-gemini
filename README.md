# robotframework-gemini

Biblioteca **Python** e **keywords do Robot Framework** para oráculos com **Google Gemini**: avaliação **só texto** (API, logs, JSON, etc.) ou **multimodal** com imagem (arquivo PNG ou captura do **Robot Framework Browser**).

- **Multimodal**: envia o texto do prompt e a captura como `Part` em bytes (`google-genai`).
- **Fluxo recomendado**: duas entradas — **contexto** (enquadramento do teste) e **avaliação** (critério ou pergunta objetiva).
- **Browser opcional**: keywords de screenshot exigem `Library    Browser`; keywords de texto funcionam sem navegador.

## Instalação

```bash
pip install robotframework-gemini
```

Com suporte a captura via Robot Framework Browser (Playwright):

```bash
pip install "robotframework-gemini[browser]"
python -m pip install robotframework
```

Desenvolvimento local:

```bash
python -m pip install -e ".[dev]"
```

## Variáveis de ambiente e importação da Library

| Variável / argumento | Função |
|----------------------|--------|
| `GEMINI_API_KEY` | Chave da API Gemini (obrigatória se não passar `api_key` na Library) |
| `GEMINI_MODEL` | Modelo (ex.: `gemini-2.5-flash`). Se omitido, usa `gemini-2.5-flash`. |
| `api_key` (import) | Sobrescreve `GEMINI_API_KEY` na importação da Library |
| `model` (import) | Sobrescreve `GEMINI_MODEL` na importação da Library |

Por padrão, a Library lê chave e modelo das variáveis de ambiente. Você também pode passá-los na importação (útil em CI ou suítes com credenciais em variáveis Robot):

```robot
*** Variables ***
${GEMINI_API_KEY}    %{GEMINI_API_KEY}
${GEMINI_MODEL}      gemini-2.5-flash

*** Settings ***
Library    GeminiLibrary    api_key=${GEMINI_API_KEY}    model=${GEMINI_MODEL}
```

Só o modelo (chave continua vinda do ambiente):

```robot
Library    GeminiLibrary    model=gemini-2.5-flash
```

Import explícito (equivalente):

```robot
Library    robotframework_gemini.library.GeminiLibrary    api_key=${GEMINI_API_KEY}    model=${GEMINI_MODEL}
```

> Evite commitar a chave literal no repositório; prefira `%{GEMINI_API_KEY}` ou secrets do CI.

## Uso em Python (`GeminiOrchestrator`)

```python
from pathlib import Path
from robotframework_gemini import GeminiOrchestrator

orchestrator = GeminiOrchestrator()
# ou explicitamente:
# orchestrator = GeminiOrchestrator(api_key="...", model="gemini-2.5-flash")
context = "Web dashboard with the 'Active' category filter applied."
evaluation = "Do the visible list items match the selected category?"
model_response = orchestrator.evaluate_with_image(context, evaluation, Path("screen.png"))
```

Para formato de saída restrito (ex.: Yes/No), use `extra_instructions`:

```python
model_response = orchestrator.evaluate_with_text(
    context,
    evaluation,
    extra_instructions="Reply with one word only: Yes or No.",
)
```

## Uso no Robot Framework

> **Nota:** os exemplos usam `Set Variable` e `Catenate` em vez da keyword `VAR` (Robot Framework 7.0+) para manter retrocompatibilidade com versões anteriores do Robot Framework.

### Só texto (sem Browser)

```robot
*** Settings ***
Library    GeminiLibrary

*** Keywords ***
Validar resposta da API
    ${context}=       Set Variable    {"status": "ok", "items": 3}
    ${evaluation}=    Set Variable    O payload indica sucesso com itens?
    ${model_response}=    Gemini Evaluate Text    ${context}    ${evaluation}
    Log    ${model_response}
```

### Com captura de tela (Browser)

Declare a biblioteca **Browser** antes de **Gemini**:

```robot
*** Settings ***
Library    Browser
Library    GeminiLibrary

*** Keywords ***
Checar tela por critério neutro
    ${context}=       Set Variable    Lista filtrada por status Ativo.
    ${evaluation}=    Set Variable    Todos os itens visíveis mostram status Ativo?
    ${model_response}=    Gemini Evaluate With Screen    ${context}    ${evaluation}
    Log    ${model_response}
```

Import recomendado (RobotCode, runtime e PyPI):

```robot
Library    GeminiLibrary    api_key=${GEMINI_API_KEY}    model=${GEMINI_MODEL}
```

Import explícito do pacote (Python / IDEs que preferem o caminho completo):

```robot
Library    robotframework_gemini.library.GeminiLibrary    api_key=${GEMINI_API_KEY}    model=${GEMINI_MODEL}
```

### IDE e RobotCode

| Forma de import | Quem resolve |
|-----------------|--------------|
| `Library    GeminiLibrary` | Módulo top-level `GeminiLibrary.py` (instalado no wheel ou via `src/` no clone) |
| `Library    robotframework_gemini.library.GeminiLibrary` | Pacote Python padrão |

No **clone do repositório**, sem instalar:

- [`robot.toml`](robot.toml) — `python-path = ["src"]` para RobotCode/LSP
- [`.vscode/settings.json`](.vscode/settings.json) — `extraPaths` para Pylance/Cursor

Com venv local: `pip install -e ".[dev]"` e recarregue a janela do IDE após mudanças.

Com arquivo já salvo:

```robot
Browser.Take Screenshot    ${OUTPUT_DIR}/tela.png
${model_response}=    Gemini Evaluate With Image File    ${context}    ${evaluation}    ${OUTPUT_DIR}/tela.png
```

Veredito via prompt (primeira linha) e nota 1–5:

```robot
${model_response}=    Gemini Evaluate With Screen    ${context}    ${evaluation}
...    extra_instructions=Responda com uma palavra na primeira linha: Sim ou Não.
${verdict}=    Get Line    ${model_response}    0
Should Be Equal As Strings    ${verdict}    Sim

# Nota 1–5: duas etapas (log da justificativa) ou atalho em uma linha
${model_response}=    Gemini Evaluate Text Rating    ${context}    ${evaluation}
${rating_score}=    Gemini Parse Rating    ${model_response}

${rating_score}=    Gemini Evaluate Text Rating Score    ${context}    ${evaluation}
```

Detalhes das três keywords de nota: [`docs/KEYWORDS.pt-BR.md#notas-15-três-keywords-quando-usar`](docs/KEYWORDS.pt-BR.md#notas-15-três-keywords-quando-usar).

Consulte também [`examples/demo_template.robot`](examples/demo_template.robot).

## Documentação de Keywords

- Português: [`docs/KEYWORDS.pt-BR.md`](docs/KEYWORDS.pt-BR.md)
- English: [`docs/KEYWORDS.en.md`](docs/KEYWORDS.en.md)

## Compatibilidade

- `BrowserGeminiLibrary` permanece como alias de `GeminiLibrary` para suítes existentes.
- Variáveis legadas (`LLM_API_KEY`, `LLM_API_KEY_LIA`, `LLM_LIA_MODEL`) são mapeadas para `GEMINI_*` ao importar o pacote.

## Testes

```bash
pytest
```

Os testes usam mocks de `generate_content`; não há chamadas reais à API.

## Licença

MIT.
