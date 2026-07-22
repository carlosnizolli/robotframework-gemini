# Robot Framework Keywords (`GeminiLibrary`)

Reference for `robotframework_gemini.library.GeminiLibrary` (short name: `Library    GeminiLibrary` after pip install).

## Prerequisites

- `Library    GeminiLibrary` — recommended (top-level module; RobotCode and runtime)
- `Library    robotframework_gemini.library.GeminiLibrary` — explicit Python package path
- `Library    BrowserGeminiLibrary` — legacy alias (same class)
- Optional import arguments: `api_key=${GEMINI_API_KEY}` and `model=${GEMINI_MODEL}` (override env; default model: `gemini-flash-latest`)
- For screenshot keywords: `Library    Browser` (install with `pip install "robotframework-gemini[browser]"`)
- Environment variables: `GEMINI_API_KEY` and optionally `GEMINI_MODEL`

```robot
*** Settings ***
Library    GeminiLibrary    api_key=${GEMINI_API_KEY}    model=gemini-flash-latest
```

## Return behavior

- Evaluation keywords return the **raw model text**.
- **Verdicts** (Yes/No, three-way labels, localized Sim/Não/Aviso, etc.): define the format in `extra_instructions` or `output_instructions` (`Gemini Evaluate Text Verdict`); extract the first line in the test with `Get Line` / `Strip String` (`String` library).
- **Scores 1–5**: use `Gemini Evaluate Text Rating` + `Gemini Parse Rating`, or the shortcut `Gemini Evaluate Text Rating Score`. See [Scores 1–5: three keywords](#scores-15-three-keywords-when-to-use).

## Scores 1–5: three keywords, when to use

Three keywords cover the **1–5 scoring** flow. The two-step pattern separates **judging** (LLM, non-deterministic) from **extracting the score** (local code, deterministic) — same idea as `Gemini Evaluate Text Verdict` + `Get Line` for verdicts.

| Keyword | Calls API? | Returns | When to use |
|---------|------------|---------|-------------|
| `Gemini Evaluate Text Rating` | Yes | Raw text (`SCORE:` + `REASON:`) | You need the full response for audit, logging the reason, or custom parsing |
| `Gemini Parse Rating` | No | `"1"`–`"5"` or original text on failure | You already have model output (from this lib or elsewhere) and want the score |
| `Gemini Evaluate Text Rating Score` | Yes | Only `"1"`–`"5"` (shortcut) | Simple assertion (`>= 4`) without needing raw text |

**Two-step flow** (recommended for debugging):

```robot
${model_response}=    Gemini Evaluate Text Rating    ${context}    ${evaluation}
Log    ${model_response}
${rating_score}=    Gemini Parse Rating    ${model_response}
Should Be True    ${rating_score} >= 4
```

**One-step shortcut** (smoke tests, clear criteria):

```robot
${rating_score}=    Gemini Evaluate Text Rating Score    ${context}    ${evaluation}
Should Be True    ${rating_score} >= 4
```

**Why not a single keyword?** Evaluation keywords return raw text for transparency and parser reuse. The composite exists when you only need the number.

## Reference

### `Gemini Evaluate With Image File`

**Signature**

```robot
${model_response}=    Gemini Evaluate With Image File    ${context}    ${evaluation}    ${image_path}    extra_instructions=${extra_instructions}
```

**Description**
Evaluates an existing image file (multimodal: text + image bytes).

---

### `Gemini Evaluate With Screen`

**Signature**

```robot
${model_response}=    Gemini Evaluate With Screen    ${context}    ${evaluation}    selector=${selector}    filename=${screenshot_filename}    extra_instructions=${extra_instructions}
```

**Description**
Takes a screenshot with `Browser` and evaluates it with Gemini.

- `selector` (optional): capture only one element.
- `filename` (optional): output image path.

---

### `Gemini Evaluate With Screen And Html`

**Signature**

```robot
${model_response}=    Gemini Evaluate With Screen And Html    ${context}    ${evaluation}    include_html=${True}    filename=${screenshot_filename}    extra_instructions=${extra_instructions}
```

**Description**
Captures screenshot and optionally includes page HTML in the prompt.

---

### `Gemini Evaluate Text`

**Signature**

```robot
${model_response}=    Gemini Evaluate Text    ${context}    ${evaluation}    extra_instructions=${extra_instructions}
```

**Description**
Text-only evaluation (no screenshot).

---

### `Gemini Evaluate Text Verdict`

**Signature**

```robot
${model_response}=    Gemini Evaluate Text Verdict    ${context}    ${evaluation}    ${output_instructions}
```

**Description**
Text judge with verdict format defined by the test (`output_instructions`, e.g. one word on the first line). Returns raw text; the test extracts the verdict (e.g. first line with `Get Line`).

---

### `Gemini Evaluate Text Rating`

**Signature**

```robot
${model_response}=    Gemini Evaluate Text Rating    ${context}    ${evaluation}    extra_instructions=${extra_instructions}
```

**Description**
Text judge with built-in 1–5 rubric. **Calls the API** and returns raw `SCORE:` + `REASON:` text. Pair with `Gemini Parse Rating`, or use `Gemini Evaluate Text Rating Score` when you only need the score.

---

### `Gemini Parse Rating`

**Signature**

```robot
${rating_score}=    Gemini Parse Rating    ${model_response}
```

**Description**
**Does not call the API** — locally extracts `1`–`5` from `SCORE:`/`NOTA:` responses. Returns the original text when parsing fails (helps debug when the model ignored the rubric).

---

### `Gemini Evaluate Text Rating Score`

**Signature**

```robot
${rating_score}=    Gemini Evaluate Text Rating Score    ${context}    ${evaluation}    extra_instructions=${extra_instructions}
```

**Description**
Shortcut: runs `Gemini Evaluate Text Rating` then `Gemini Parse Rating`. Returns **only** the score (`"1"`–`"5"`). Use the two-step flow when you need to log or inspect the `REASON:` line.

---

### `Gemini Generate From Prompt`

**Signature**

```robot
${model_response}=    Gemini Generate From Prompt    ${prompt}
```

**Description**
Sends a direct text prompt (no context/evaluation template).

---

### `Gemini Screenshot And Ask`

**Signature**

```robot
${model_response}=    Gemini Screenshot And Ask    ${prompt}    selector=${selector}    filename=${screenshot_filename}
```

**Description**
Advanced shortcut: screenshot + single prompt.

---

### `Gemini Screenshot Html And Ask`

**Signature**

```robot
${model_response}=    Gemini Screenshot Html And Ask    ${prompt}    filename=${screenshot_filename}
```

**Description**
Advanced shortcut: screenshot + HTML + single prompt.

## Usage examples

> **Note:** examples use `Set Variable` and `Catenate` instead of the `VAR` keyword (Robot Framework 7.0+) to stay compatible with older Robot Framework versions.

Examples follow prompt-engineering basics: **factual context** (what the test observed), **objective criteria** (what to judge), **output format** in `extra_instructions` when needed, and a **parser** separate from raw model text.

### Context sections — what to put in each block

When building `${context}` with `Catenate`, these headings organize evidence for the model. Replace `${ARTIFACT}`, `${SCENARIO_INTENT}`, and `${EXPECTED_REFERENCE}` with your test’s actual content.

#### `## Test evidence`

Material **observed or captured** during the run — the raw input the judge must analyze.

| Type | Example |
|------|---------|
| API response | `{"status": 200, "order": {"id": 8842, "state": "confirmed"}}` |
| Log / stderr | `[WARN] Retry 2/3 — shipping service unavailable` |
| UI text | `Get Text` → `"3 results for filter Status=Active"` |
| Chatbot reply | `"Delivery time is 5 to 7 business days for your region."` |
| File / report | CSV excerpt, generated markdown, rendered email as text |
| HTML (with screenshot) | Truncated DOM together with a screen capture |

#### `## Scenario intent`

**Why** the test ran and **what** it aimed to achieve — functional framing, without repeating the evaluation criterion.

| Type | Example |
|------|---------|
| Test objective | `Validate order creation with a valid address after B2B customer login.` |
| Precondition | `Authenticated user; cart with 2 items; coupon "FREESHIP" applied.` |
| Action performed | `POST /api/v1/orders sent with checkout smoke payload.` |
| Expected outcome (high level) | `System should confirm the order and show summary with total and delivery ETA.` |

#### `## Expected reference`

**Contract or external reference** to compare evidence against — useful when there is a “correct” answer, spec, or explicit business rule.

| Type | Example |
|------|---------|
| Original question | `"What is the delivery time for ZIP 10001?"` |
| Business rule | `Orders over $299 get free shipping in the Northeast region.` |
| Documentation excerpt | `Manual v2.3: status "confirmed" requires approved payment and reserved stock.` |
| Gold example | QA-approved reply: `"Your order was confirmed. Delivery within 7 business days."` |
| Contract / OpenAPI | `200 OK — body.order.state enum: [confirmed, pending, cancelled]` |

> In examples 1 and 4 below, `#` comments show where each variable fits in these sections.

### 1) Generic judge with 1–5 score (text)

```robot
*** Keywords ***
Rate test artifact
    [Documentation]    Reusable judge: evidence + criterion + rubric built into the library.
    ${context}=    Catenate    SEPARATOR=\n
    ...    ## Test evidence
    ...    # ${ARTIFACT} = captured data (API JSON, log, UI text, LLM reply, etc.)
    ...    ${ARTIFACT}
    ...    
    ...    ## Scenario intent
    ...    # ${SCENARIO_INTENT} = test goal, preconditions, and action performed
    ...    ${SCENARIO_INTENT}
    ${evaluation}=    Set Variable
    ...    How well does the evidence fulfill the scenario intent?
    ...    Consider: completeness, internal consistency, and absence of errors or placeholders.
    ${model_response}=    Gemini Evaluate Text Rating    ${context}    ${evaluation}
    ${rating_score}=    Gemini Parse Rating    ${model_response}
    Log    rating_score=${rating_score} | model_response=${model_response}
    ${rating_score_as_integer}=    Convert To Integer    ${rating_score}
    Should Be True    ${rating_score_as_integer} >= 4    msg=Score below minimum (${rating_score})
    # Equivalent shortcut (no REASON line in log):
    # ${rating_score}=    Gemini Evaluate Text Rating Score    ${context}    ${evaluation}
```

### 2) Screen evaluation + Yes/No

```robot
*** Settings ***
Library    String

*** Keywords ***
Validate screen consistency
    [Documentation]    Context describes UI state; criterion is binary and visible in the screenshot.
    ${context}=    Catenate    SEPARATOR=\n
    ...    ## UI state
    ...    Listing with filter "${FILTER_LABEL}"="${FILTER_VALUE}" applied.
    ...    Consider only rows visible in the current viewport.
    ${evaluation}=    Set Variable
    ...    Do all visible rows show "${FILTER_VALUE}" in field "${FILTER_LABEL}"?
    ${output_instructions}=    Set Variable
    ...    Reply with exactly one word on the first line: Yes or No.
    ...    If No, one short reason on the next line.
    ${model_response}=    Gemini Evaluate With Screen    ${context}    ${evaluation}    extra_instructions=${output_instructions}
    ${verdict}=    Get Line    ${model_response}    0
    ${verdict}=    Strip String    ${verdict}
    Should Be Equal As Strings    ${verdict}    Yes
```

### 3) Existing screenshot file (saved image)

```robot
*** Keywords ***
Evaluate full image
    [Documentation]    Multimodal with a saved file; criteria target visible failure signals.
    Take Screenshot    ${OUTPUT_DIR}/page_full.png    fullPage=True
    ${context}=    Set Variable    Full-page capture after navigation finished and network idle.
    ${evaluation}=    Set Variable
    ...    Are there loading placeholders, skeletons, error messages, or clearly broken layout?
    ...    Ignore minor cosmetic differences if main content is readable.
    ${model_response}=    Gemini Evaluate With Image File
    ...    ${context}
    ...    ${evaluation}
    ...    ${OUTPUT_DIR}/page_full.png
    ...    extra_instructions=Reply with exactly one word on the first line: Yes or No. Yes = page looks loaded and usable; No = obvious problem.
    ${verdict}=    Get Line    ${model_response}    0
    ${verdict}=    Strip String    ${verdict}
    Should Be Equal As Strings    ${verdict}    Yes
```

### 4) Text judge with three outcomes (Yes / No / Warn)

```robot
*** Settings ***
Library    String

*** Keywords ***
Validate artifact with three-way verdict
    [Documentation]    Warn when data is missing; do not treat missing evidence as criterion failure.
    ${context}=    Catenate    SEPARATOR=\n
    ...    ## Evidence
    ...    # ${ARTIFACT} = what the test produced or observed (reply, log, extracted text)
    ...    ${ARTIFACT}
    ...    
    ...    ## Expected reference
    ...    # ${EXPECTED_REFERENCE} = question, business rule, spec, or gold example
    ...    ${EXPECTED_REFERENCE}
    ${evaluation}=    Set Variable
    ...    Checklist:
    ...    1) Evidence addresses what the expected reference requires.
    ...    2) No explicit contradiction between evidence and reference.
    ...    3) If evidence states unavailability or missing data, classify as Warn, not No.
    ${output_instructions}=    Set Variable
    ...    Reply with exactly one word on the first line: Yes, No, or Warn.
    ${model_response}=    Gemini Evaluate Text Verdict    ${context}    ${evaluation}    ${output_instructions}
    ${verdict}=    Get Line    ${model_response}    0
    ${verdict}=    Strip String    ${verdict}
    Log    Verdict=${verdict} | Response=${model_response}
    Should Be Equal As Strings    ${verdict}    Yes
```

### 5) Free-form generation (tutorial example)

```robot
*** Keywords ***
Generate text with constraints
    [Documentation]    Single prompt: explicit role, format, and limits (no context/evaluation template).
    ${prompt}=    Catenate    SEPARATOR=\n
    ...    Generate a short question about a generic topic (e.g. weather, history, or science).
    ...    
    ...    Rules:
    ...    - One sentence only, ending with "?".
    ...    - Maximum 20 words.
    ...    - No preamble ("Sure", "Here is", etc.).
    ...    - Language: English.
    ${generated_question}=    Gemini Generate From Prompt    ${prompt}
    Log    ${generated_question}
```
