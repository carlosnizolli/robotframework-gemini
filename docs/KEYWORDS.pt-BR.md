# Keywords do Robot Framework (`GeminiLibrary`)

Referência da biblioteca `robotframework_gemini.library.GeminiLibrary` (atalho: `Library    GeminiLibrary` após `pip install`).

## Pré-requisitos

- `Library    GeminiLibrary` (ou `Library    robotframework_gemini.library.GeminiLibrary`)
- Para keywords de screenshot: `Library    Browser` (instale com `pip install "robotframework-gemini[browser]"`)
- Variáveis de ambiente: `GEMINI_API_KEY` e opcionalmente `GEMINI_MODEL`

## Convenção de retorno

- Keywords de avaliação retornam **texto bruto do modelo**.
- **Vereditos** (Sim/Não, Sim/Não/Aviso, etc.): defina o formato em `extra_instructions` ou em `output_instructions` (`Gemini Evaluate Text Verdict`); extraia a primeira linha no teste com `Get Line` / `Strip String` (biblioteca `String`).
- **Notas 1–5**: use `Gemini Evaluate Text Rating` + `Gemini Parse Rating` quando o modelo seguir o formato `SCORE`/`NOTA`.

## Reference

### `Gemini Evaluate With Image File`

**Assinatura**

```robot
${raw}=    Gemini Evaluate With Image File    ${context}    ${evaluation}    ${image_path}    extra_instructions=${extra}
```

**Descrição**
Avalia uma imagem já existente (multimodal: texto + imagem em bytes).

---

### `Gemini Evaluate With Screen`

**Assinatura**

```robot
${raw}=    Gemini Evaluate With Screen    ${context}    ${evaluation}    selector=${selector}    filename=${file}    extra_instructions=${extra}
```

**Descrição**
Tira screenshot com a `Browser` e avalia via Gemini.

- `selector` (opcional): captura apenas um elemento.
- `filename` (opcional): caminho para salvar a imagem.

---

### `Gemini Evaluate With Screen And Html`

**Assinatura**

```robot
${raw}=    Gemini Evaluate With Screen And Html    ${context}    ${evaluation}    include_html=${True}    filename=${file}    extra_instructions=${extra}
```

**Descrição**
Captura screenshot e, opcionalmente, inclui HTML da página no prompt.

---

### `Gemini Evaluate Text`

**Assinatura**

```robot
${raw}=    Gemini Evaluate Text    ${context}    ${evaluation}    extra_instructions=${extra}
```

**Descrição**
Avaliação somente textual (sem imagem).

---

### `Gemini Evaluate Text Verdict`

**Assinatura**

```robot
${raw}=    Gemini Evaluate Text Verdict    ${context}    ${evaluation}    ${output_instructions}
```

**Descrição**
Juiz textual com formato de veredito definido pelo teste (`output_instructions`, ex.: Sim/Não/Aviso na primeira linha). Retorna texto bruto; o teste extrai o veredito (ex.: primeira linha com `Get Line`).

---

### `Gemini Evaluate Text Rating`

**Assinatura**

```robot
${raw}=    Gemini Evaluate Text Rating    ${context}    ${evaluation}    extra_instructions=${extra}
```

**Descrição**
Juiz textual genérico com rubrica 1–5 (formato `SCORE` + `REASON`). `context` = evidência do teste; `evaluation` = critério a pontuar. Retorna texto bruto; use `Gemini Parse Rating` para extrair a nota.

---

### `Gemini Parse Rating`

**Assinatura**

```robot
${score}=    Gemini Parse Rating    ${raw}
```

**Descrição**
Extrai nota inteira `1`–`5` de respostas no formato `SCORE:`/`NOTA:`; se não reconhecer, devolve o texto original.

---

### `Gemini Generate From Prompt`

**Assinatura**

```robot
${text}=    Gemini Generate From Prompt    ${prompt}
```

**Descrição**
Envia prompt textual direto (sem template contexto/avaliação).

---

### `Gemini Screenshot And Ask`

**Assinatura**

```robot
${text}=    Gemini Screenshot And Ask    ${prompt}    selector=${selector}    filename=${file}
```

**Descrição**
Atalho avançado: screenshot + prompt único.

---

### `Gemini Screenshot Html And Ask`

**Assinatura**

```robot
${text}=    Gemini Screenshot Html And Ask    ${prompt}    filename=${file}
```

**Descrição**
Atalho avançado: screenshot + HTML + prompt único.

## Exemplos de uso

Boas práticas usadas nos exemplos: **contexto factual** (o que o teste observou), **critério objetivo** (o que julgar), **formato de saída** explícito no prompt, e **assertiva** sobre a primeira linha (veredito) ou `Gemini Parse Rating` (nota).

### 1) Juiz genérico com nota 1–5 (texto)

```robot
*** Keywords ***
Avaliar artefato do teste
    [Documentation]    Juiz reutilizável: evidência + critério + rubrica embutida na lib.
    ${ctx}=    Catenate    SEPARATOR=\n
    ...    ## Evidência do teste
    ...    ${ARTIFACT}
    ...    
    ...    ## Intenção do cenário
    ...    ${SCENARIO_INTENT}
    ${crit}=    Set Variable
    ...    Quão bem a evidência cumpre a intenção do cenário?
    ...    Considere: completude, consistência interna e ausência de sinais de erro ou placeholder.
    ${raw}=    Gemini Evaluate Text Rating    ${ctx}    ${crit}
    ${score}=    Gemini Parse Rating    ${raw}
    Log    score=${score} | raw=${raw}
    ${score_int}=    Convert To Integer    ${score}
    Should Be True    ${score_int} >= 4    msg=Nota abaixo do mínimo (${score})
```

### 2) Avaliação visual de tela + Sim/Não

```robot
*** Settings ***
Library    String

*** Keywords ***
Validar consistência da tela
    [Documentation]    Contexto descreve estado; critério é binário e verificável na imagem.
    ${ctx}=    Catenate    SEPARATOR=\n
    ...    ## Estado da UI
    ...    Listagem com filtro "${FILTER_LABEL}"="${FILTER_VALUE}" aplicado.
    ...    Apenas itens visíveis na viewport atual devem ser considerados.
    ${crit}=    Set Variable
    ...    Todos os registros visíveis exibem o valor "${FILTER_VALUE}" no campo "${FILTER_LABEL}"?
    ${output}=    Set Variable
    ...    Responda com exatamente uma palavra na primeira linha: Sim ou Não.
    ...    Se Não, uma frase curta na linha seguinte.
    ${raw}=    Gemini Evaluate With Screen    ${ctx}    ${crit}    extra_instructions=${output}
    ${v}=    Get Line    ${raw}    0
    ${v}=    Strip String    ${v}
    Should Be Equal As Strings    ${v}    Sim
```

### 3) Screenshot salvo (imagem existente)

```robot
*** Keywords ***
Avaliar imagem completa
    [Documentation]    Multimodal com arquivo já capturado; critério foca em sinais visíveis de falha.
    Take Screenshot    ${OUTPUT_DIR}/page_full.png    fullPage=True
    ${ctx}=    Set Variable    Captura full-page após navegação concluída e rede ociosa.
    ${crit}=    Set Variable
    ...    Há placeholders de loading, skeletons, mensagens de erro ou layout claramente quebrado?
    ...    Ignore diferenças cosméticas menores (fonte, espaçamento) se o conteúdo principal estiver legível.
    ${raw}=    Gemini Evaluate With Image File
    ...    ${ctx}
    ...    ${crit}
    ...    ${OUTPUT_DIR}/page_full.png
    ...    extra_instructions=Responda com exatamente uma palavra na primeira linha: Sim ou Não. Sim = página carregada e utilizável; Não = problema evidente.
    ${v}=    Get Line    ${raw}    0
    ${v}=    Strip String    ${v}
    Should Be Equal As Strings    ${v}    Sim
```

### 4) Juiz textual com três estados (Sim / Não / Aviso)

```robot
*** Settings ***
Library    String

*** Keywords ***
Validar artefato com veredito ternário
    [Documentation]    Aviso quando faltam dados; não confundir ausência de evidência com falha do critério.
    ${ctx}=    Catenate    SEPARATOR=\n
    ...    ## Evidência
    ...    ${ARTIFACT}
    ...    
    ...    ## Referência esperada
    ...    ${EXPECTED_REFERENCE}
    ${crit}=    Set Variable
    ...    Checklist:
    ...    1) A evidência responde ao que a referência esperada pede.
    ...    2) Não há contradição explícita entre evidência e referência.
    ...    3) Se a evidência declarar indisponibilidade ou ausência de dados, classifique como Aviso, não como Não.
    ${output}=    Set Variable
    ...    Responda com exatamente uma palavra na primeira linha: Sim, Não ou Aviso.
    ${raw}=    Gemini Evaluate Text Verdict    ${ctx}    ${crit}    ${output}
    ${v}=    Get Line    ${raw}    0
    ${v}=    Strip String    ${v}
    Log    Veredito=${v} | Raw=${raw}
    Should Be Equal As Strings    ${v}    Sim
```

### 5) Geração de texto livre (exemplo didático)

```robot
*** Keywords ***
Gerar texto com restrições
    [Documentation]    Prompt único: papel, formato e limites explícitos (sem template contexto/avaliação).
    ${prompt}=    Catenate    SEPARATOR=\n
    ...    Gere uma pergunta curta sobre um tema genérico (ex.: clima, história ou ciência).
    ...    
    ...    Regras:
    ...    - Uma única frase, terminando com "?".
    ...    - Máximo 20 palavras.
    ...    - Sem prefácio ("Claro", "Aqui está", etc.).
    ...    - Idioma: português.
    ${q}=    Gemini Generate From Prompt    ${prompt}
    Log    ${q}
```
