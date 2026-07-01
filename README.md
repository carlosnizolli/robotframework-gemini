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

## Variáveis de ambiente

| Variável          | Função                                      |
|-------------------|---------------------------------------------|
| `GEMINI_API_KEY`  | Chave da API Gemini (obrigatória se não passar `api_key` na Library) |
| `GEMINI_MODEL`    | Modelo (ex.: `gemini-2.0-flash`). Se omitido, usa `gemini-2.0-flash`. |

## Uso em Python (`GeminiOrchestrator`)

```python
from pathlib import Path
from robotframework_gemini import GeminiOrchestrator

orc = GeminiOrchestrator()
ctx = "Web dashboard with the 'Active' category filter applied."
crit = "Do the visible list items match the selected category?"
raw = orc.evaluate_with_image(ctx, crit, Path("screen.png"))
```

Para formato de saída restrito (ex.: Yes/No), use `extra_instructions`:

```python
raw = orc.evaluate_with_text(
    ctx,
    crit,
    extra_instructions="Reply with one word only: Yes or No.",
)
```

## Uso no Robot Framework

### Só texto (sem Browser)

```robot
*** Settings ***
Library    GeminiLibrary

*** Keywords ***
Validar resposta da API
    ${ctx}=       Set Variable    {"status": "ok", "items": 3}
    ${crit}=      Set Variable    O payload indica sucesso com itens?
    ${raw}=       Gemini Evaluate Text    ${ctx}    ${crit}
    Log    ${raw}
```

### Com captura de tela (Browser)

Declare a biblioteca **Browser** antes de **Gemini**:

```robot
*** Settings ***
Library    Browser
Library    GeminiLibrary

*** Keywords ***
Checar tela por critério neutro
    ${ctx}=       Set Variable    Lista filtrada por status Ativo.
    ${crit}=      Set Variable    Todos os itens visíveis mostram status Ativo?
    ${raw}=       Gemini Evaluate With Screen    ${ctx}    ${crit}
    Log    ${raw}
```

Import explícito (equivalente):

```robot
Library    robotframework_gemini.library.GeminiLibrary
```

Com arquivo já salvo:

```robot
Browser.Take Screenshot    ${OUTPUT_DIR}/tela.png
${raw}=    Gemini Evaluate With Image File    ${ctx}    ${crit}    ${OUTPUT_DIR}/tela.png
```

Veredito via prompt (primeira linha) e nota 1–5:

```robot
${raw}=    Gemini Evaluate With Screen    ${ctx}    ${crit}
...    extra_instructions=Responda com uma palavra na primeira linha: Sim ou Não.
${v}=    Get Line    ${raw}    0
Should Be Equal As Strings    ${v}    Sim

${raw}=    Gemini Evaluate Text Rating    ${ctx}    ${criterion}
${score}=    Gemini Parse Rating    ${raw}
```

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
