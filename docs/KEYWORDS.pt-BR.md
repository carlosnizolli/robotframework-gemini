# Keywords do Robot Framework (`GeminiLibrary`)

Referência da biblioteca `robotframework_gemini.library.GeminiLibrary` (atalho: `Library    GeminiLibrary` após `pip install`).

## Pré-requisitos

- `Library    GeminiLibrary` (ou `Library    robotframework_gemini.library.GeminiLibrary`)
- Para keywords de screenshot: `Library    Browser` (instale com `pip install "robotframework-gemini[browser]"`)
- Variáveis de ambiente: `GEMINI_API_KEY` e opcionalmente `GEMINI_MODEL`

## Convenção de retorno

- Keywords de avaliação retornam **texto bruto do modelo**.
- **Vereditos** (Sim/Não, Sim/Não/Aviso, etc.): defina o formato em `extra_instructions` ou em `output_instructions` (`Gemini Evaluate Text Verdict`); extraia a primeira linha no teste com `Get Line` / `Strip String` (biblioteca `String`).
- **Notas 1–5**: use `Gemini Evaluate Text Rating` + `Gemini Parse Rating` (ou a atalho `Gemini Evaluate Text Rating Score`). Ver [Notas 1–5: três keywords](#notas-15-três-keywords-quando-usar).

## Notas 1–5: três keywords, quando usar

Três keywords cobrem o fluxo de **pontuação 1–5**. Duas etapas separam **julgar** (LLM, não determinístico) de **extrair a nota** (código local, determinístico) — o mesmo padrão de `Gemini Evaluate Text Verdict` + `Get Line` para vereditos.

| Keyword | Chama API? | Retorno | Quando usar |
|---------|------------|---------|-------------|
| `Gemini Evaluate Text Rating` | Sim | Texto bruto (`SCORE:` + `REASON:`) | Precisa auditar a resposta completa, logar justificativa ou tratar parse manualmente |
| `Gemini Parse Rating` | Não | `"1"`–`"5"` ou texto original se falhar | Já tem resposta do modelo (desta lib ou de outra fonte) e quer extrair a nota |
| `Gemini Evaluate Text Rating Score` | Sim | Só `"1"`–`"5"` (atalho) | Assertiva simples (`>= 4`) sem precisar do texto bruto |

**Fluxo em duas etapas** (recomendado para debug):

```robot
${model_response}=    Gemini Evaluate Text Rating    ${context}    ${evaluation}
Log    ${model_response}
${rating_score}=    Gemini Parse Rating    ${model_response}
Should Be True    ${rating_score} >= 4
```

**Atalho em uma etapa** (smoke tests, critério claro):

```robot
${rating_score}=    Gemini Evaluate Text Rating Score    ${context}    ${evaluation}
Should Be True    ${rating_score} >= 4
```

**Por que não uma keyword só?** A lib mantém keywords de avaliação sempre retornando texto bruto para transparência e reuso do parser. A composta existe para quem só precisa do número.

## Reference

### `Gemini Evaluate With Image File`

**Assinatura**

```robot
${model_response}=    Gemini Evaluate With Image File    ${context}    ${evaluation}    ${image_path}    extra_instructions=${extra_instructions}
```

**Descrição**
Avalia uma imagem já existente (multimodal: texto + imagem em bytes).

---

### `Gemini Evaluate With Screen`

**Assinatura**

```robot
${model_response}=    Gemini Evaluate With Screen    ${context}    ${evaluation}    selector=${selector}    filename=${screenshot_filename}    extra_instructions=${extra_instructions}
```

**Descrição**
Tira screenshot com a `Browser` e avalia via Gemini.

- `selector` (opcional): captura apenas um elemento.
- `filename` (opcional): caminho para salvar a imagem.

---

### `Gemini Evaluate With Screen And Html`

**Assinatura**

```robot
${model_response}=    Gemini Evaluate With Screen And Html    ${context}    ${evaluation}    include_html=${True}    filename=${screenshot_filename}    extra_instructions=${extra_instructions}
```

**Descrição**
Captura screenshot e, opcionalmente, inclui HTML da página no prompt.

---

### `Gemini Evaluate Text`

**Assinatura**

```robot
${model_response}=    Gemini Evaluate Text    ${context}    ${evaluation}    extra_instructions=${extra_instructions}
```

**Descrição**
Avaliação somente textual (sem imagem).

---

### `Gemini Evaluate Text Verdict`

**Assinatura**

```robot
${model_response}=    Gemini Evaluate Text Verdict    ${context}    ${evaluation}    ${output_instructions}
```

**Descrição**
Juiz textual com formato de veredito definido pelo teste (`output_instructions`, ex.: Sim/Não/Aviso na primeira linha). Retorna texto bruto; o teste extrai o veredito (ex.: primeira linha com `Get Line`).

---

### `Gemini Evaluate Text Rating`

**Assinatura**

```robot
${model_response}=    Gemini Evaluate Text Rating    ${context}    ${evaluation}    extra_instructions=${extra_instructions}
```

**Descrição**
Juiz textual com rubrica 1–5 embutida. **Chama a API** e retorna texto bruto no formato `SCORE:` + `REASON:`. Use com `Gemini Parse Rating` ou prefira `Gemini Evaluate Text Rating Score` se só precisar da nota.

---

### `Gemini Parse Rating`

**Assinatura**

```robot
${rating_score}=    Gemini Parse Rating    ${model_response}
```

**Descrição**
**Não chama a API** — extrai nota `1`–`5` localmente de respostas `SCORE:`/`NOTA:`. Se não reconhecer o formato, devolve o texto original (útil para debug quando o modelo não seguiu a rubrica).

---

### `Gemini Evaluate Text Rating Score`

**Assinatura**

```robot
${rating_score}=    Gemini Evaluate Text Rating Score    ${context}    ${evaluation}    extra_instructions=${extra_instructions}
```

**Descrição**
Atalho: executa `Gemini Evaluate Text Rating` e em seguida `Gemini Parse Rating`. Retorna **apenas** a nota (`"1"`–`"5"`). Use o fluxo em duas etapas quando precisar logar ou inspecionar a linha `REASON:`.

---

### `Gemini Generate From Prompt`

**Assinatura**

```robot
${model_response}=    Gemini Generate From Prompt    ${prompt}
```

**Descrição**
Envia prompt textual direto (sem template contexto/avaliação).

---

### `Gemini Screenshot And Ask`

**Assinatura**

```robot
${model_response}=    Gemini Screenshot And Ask    ${prompt}    selector=${selector}    filename=${screenshot_filename}
```

**Descrição**
Atalho avançado: screenshot + prompt único.

---

### `Gemini Screenshot Html And Ask`

**Assinatura**

```robot
${model_response}=    Gemini Screenshot Html And Ask    ${prompt}    filename=${screenshot_filename}
```

**Descrição**
Atalho avançado: screenshot + HTML + prompt único.

## Exemplos de uso

> **Nota:** os exemplos usam `Set Variable` e `Catenate` em vez da keyword `VAR` (Robot Framework 7.0+) para manter retrocompatibilidade com versões anteriores do Robot Framework.

Boas práticas usadas nos exemplos: **contexto factual** (o que o teste observou), **critério objetivo** (o que julgar), **formato de saída** explícito no prompt, e **assertiva** sobre a primeira linha (veredito) ou `Gemini Parse Rating` (nota).

### Seções do contexto — o que colocar em cada bloco

Ao montar `${context}` com `Catenate`, estes títulos organizam a evidência para o modelo. Substitua `${ARTIFACT}`, `${SCENARIO_INTENT}` e `${EXPECTED_REFERENCE}` pelo conteúdo real do seu teste.

#### `## Evidência do teste`

Material **observado ou capturado** durante a execução — o “dado bruto” que o juiz deve analisar.

| Tipo | Exemplo |
|------|---------|
| Resposta de API | `{"status": 200, "pedido": {"id": 8842, "situacao": "confirmado"}}` |
| Log / stderr | `[WARN] Retentativa 2/3 — serviço de frete indisponível` |
| Texto de UI | `Get Text` → `"3 resultados para filtro Status=Ativo"` |
| Resposta de chatbot | `"O prazo de entrega é de 5 a 7 dias úteis para sua região."` |
| Arquivo / relatório | Trecho de CSV, markdown gerado, e-mail renderizado como texto |
| HTML (com screenshot) | DOM truncado junto à captura de tela |

#### `## Intenção do cenário`

**Por que** o teste rodou e **o que** se esperava alcançar — enquadramento funcional, sem repetir o critério de avaliação.

| Tipo | Exemplo |
|------|---------|
| Objetivo do caso | `Validar criação de pedido com endereço válido após login de cliente PJ.` |
| Pré-condição | `Usuário autenticado; carrinho com 2 itens; cupom "FRETEGRATIS" aplicado.` |
| Ação executada | `POST /api/v1/pedidos enviado com payload de smoke da suíte de checkout.` |
| Resultado esperado (alto nível) | `Sistema deve confirmar pedido e exibir resumo com valor final e prazo.` |

#### `## Referência esperada`

**Contrato ou referência externa** contra a qual a evidência será comparada — útil quando há resposta “correta”, spec ou regra de negócio explícita.

| Tipo | Exemplo |
|------|---------|
| Pergunta original | `"Qual o prazo de entrega para o CEP 01310-100?"` |
| Regra de negócio | `Pedidos acima de R$ 299,00 têm frete grátis na região Sudeste.` |
| Trecho de documentação | `Manual v2.3: status "confirmado" exige pagamento aprovado e estoque reservado.` |
| Exemplo gold | Resposta aprovada por QA: `"Seu pedido foi confirmado. Entrega em até 7 dias úteis."` |
| Contrato / OpenAPI | `200 OK — body.pedido.situacao enum: [confirmado, pendente, cancelado]` |

> Nos exemplos 1 e 4 abaixo, comentários `#` indicam onde cada variável se encaixa nessas seções.

### 1) Juiz genérico com nota 1–5 (texto)

```robot
*** Keywords ***
Avaliar artefato do teste
    [Documentation]    Juiz reutilizável: evidência + critério + rubrica embutida na lib.
    ${context}=    Catenate    SEPARATOR=\n
    ...    ## Evidência do teste
    ...    # ${ARTIFACT} = dado capturado (JSON de API, log, texto de UI, resposta de LLM, etc.)
    ...    ${ARTIFACT}
    ...    
    ...    ## Intenção do cenário
    ...    # ${SCENARIO_INTENT} = objetivo do teste, pré-condições e ação executada
    ...    ${SCENARIO_INTENT}
    ${evaluation}=    Set Variable
    ...    Quão bem a evidência cumpre a intenção do cenário?
    ...    Considere: completude, consistência interna e ausência de sinais de erro ou placeholder.
    ${model_response}=    Gemini Evaluate Text Rating    ${context}    ${evaluation}
    ${rating_score}=    Gemini Parse Rating    ${model_response}
    Log    rating_score=${rating_score} | model_response=${model_response}
    ${rating_score_as_integer}=    Convert To Integer    ${rating_score}
    Should Be True    ${rating_score_as_integer} >= 4    msg=Nota abaixo do mínimo (${rating_score})
    # Atalho equivalente (sem log da linha REASON:):
    # ${rating_score}=    Gemini Evaluate Text Rating Score    ${context}    ${evaluation}
```

### 2) Avaliação visual de tela + Sim/Não

```robot
*** Settings ***
Library    String

*** Keywords ***
Validar consistência da tela
    [Documentation]    Contexto descreve estado; critério é binário e verificável na imagem.
    ${context}=    Catenate    SEPARATOR=\n
    ...    ## Estado da UI
    ...    Listagem com filtro "${FILTER_LABEL}"="${FILTER_VALUE}" aplicado.
    ...    Apenas itens visíveis na viewport atual devem ser considerados.
    ${evaluation}=    Set Variable
    ...    Todos os registros visíveis exibem o valor "${FILTER_VALUE}" no campo "${FILTER_LABEL}"?
    ${output_instructions}=    Set Variable
    ...    Responda com exatamente uma palavra na primeira linha: Sim ou Não.
    ...    Se Não, uma frase curta na linha seguinte.
    ${model_response}=    Gemini Evaluate With Screen    ${context}    ${evaluation}    extra_instructions=${output_instructions}
    ${verdict}=    Get Line    ${model_response}    0
    ${verdict}=    Strip String    ${verdict}
    Should Be Equal As Strings    ${verdict}    Sim
```

### 3) Screenshot salvo (imagem existente)

```robot
*** Keywords ***
Avaliar imagem completa
    [Documentation]    Multimodal com arquivo já capturado; critério foca em sinais visíveis de falha.
    Take Screenshot    ${OUTPUT_DIR}/page_full.png    fullPage=True
    ${context}=    Set Variable    Captura full-page após navegação concluída e rede ociosa.
    ${evaluation}=    Set Variable
    ...    Há placeholders de loading, skeletons, mensagens de erro ou layout claramente quebrado?
    ...    Ignore diferenças cosméticas menores (fonte, espaçamento) se o conteúdo principal estiver legível.
    ${model_response}=    Gemini Evaluate With Image File
    ...    ${context}
    ...    ${evaluation}
    ...    ${OUTPUT_DIR}/page_full.png
    ...    extra_instructions=Responda com exatamente uma palavra na primeira linha: Sim ou Não. Sim = página carregada e utilizável; Não = problema evidente.
    ${verdict}=    Get Line    ${model_response}    0
    ${verdict}=    Strip String    ${verdict}
    Should Be Equal As Strings    ${verdict}    Sim
```

### 4) Juiz textual com três estados (Sim / Não / Aviso)

```robot
*** Settings ***
Library    String

*** Keywords ***
Validar artefato com veredito ternário
    [Documentation]    Aviso quando faltam dados; não confundir ausência de evidência com falha do critério.
    ${context}=    Catenate    SEPARATOR=\n
    ...    ## Evidência
    ...    # ${ARTIFACT} = o que o teste produziu ou observou (resposta, log, texto extraído)
    ...    ${ARTIFACT}
    ...    
    ...    ## Referência esperada
    ...    # ${EXPECTED_REFERENCE} = pergunta, regra de negócio, spec ou exemplo gold
    ...    ${EXPECTED_REFERENCE}
    ${evaluation}=    Set Variable
    ...    Checklist:
    ...    1) A evidência responde ao que a referência esperada pede.
    ...    2) Não há contradição explícita entre evidência e referência.
    ...    3) Se a evidência declarar indisponibilidade ou ausência de dados, classifique como Aviso, não como Não.
    ${output_instructions}=    Set Variable
    ...    Responda com exatamente uma palavra na primeira linha: Sim, Não ou Aviso.
    ${model_response}=    Gemini Evaluate Text Verdict    ${context}    ${evaluation}    ${output_instructions}
    ${verdict}=    Get Line    ${model_response}    0
    ${verdict}=    Strip String    ${verdict}
    Log    Veredito=${verdict} | Resposta=${model_response}
    Should Be Equal As Strings    ${verdict}    Sim
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
    ${generated_question}=    Gemini Generate From Prompt    ${prompt}
    Log    ${generated_question}
```
