# Robot Framework Keywords (`GeminiLibrary`)

Reference for `robotframework_gemini.library.GeminiLibrary` (short name: `Library    GeminiLibrary` after pip install).

## Prerequisites

- `Library    GeminiLibrary` (or `Library    robotframework_gemini.library.GeminiLibrary`)
- For screenshot keywords: `Library    Browser` (install with `pip install "robotframework-gemini[browser]"`)
- Environment variables: `GEMINI_API_KEY` and optionally `GEMINI_MODEL`

## Return behavior

- Evaluation keywords return the **raw model text**.
- **Verdicts** (Yes/No, three-way labels, localized Sim/Não/Aviso, etc.): define the format in `extra_instructions` or `output_instructions` (`Gemini Evaluate Text Verdict`); extract the first line in the test with `Get Line` / `Strip String` (`String` library).
- **Scores 1–5**: use `Gemini Evaluate Text Rating` + `Gemini Parse Rating` when the model follows the `SCORE`/`NOTA` format.

## Reference

### `Gemini Evaluate With Image File`

**Signature**

```robot
${raw}=    Gemini Evaluate With Image File    ${context}    ${evaluation}    ${image_path}    extra_instructions=${extra}
```

**Description**
Evaluates an existing image file (multimodal: text + image bytes).

---

### `Gemini Evaluate With Screen`

**Signature**

```robot
${raw}=    Gemini Evaluate With Screen    ${context}    ${evaluation}    selector=${selector}    filename=${file}    extra_instructions=${extra}
```

**Description**
Takes a screenshot with `Browser` and evaluates it with Gemini.

- `selector` (optional): capture only one element.
- `filename` (optional): output image path.

---

### `Gemini Evaluate With Screen And Html`

**Signature**

```robot
${raw}=    Gemini Evaluate With Screen And Html    ${context}    ${evaluation}    include_html=${True}    filename=${file}    extra_instructions=${extra}
```

**Description**
Captures screenshot and optionally includes page HTML in the prompt.

---

### `Gemini Evaluate Text`

**Signature**

```robot
${raw}=    Gemini Evaluate Text    ${context}    ${evaluation}    extra_instructions=${extra}
```

**Description**
Text-only evaluation (no screenshot).

---

### `Gemini Evaluate Text Verdict`

**Signature**

```robot
${raw}=    Gemini Evaluate Text Verdict    ${context}    ${evaluation}    ${output_instructions}
```

**Description**
Text judge with verdict format defined by the test (`output_instructions`, e.g. one word on the first line). Returns raw text; the test extracts the verdict (e.g. first line with `Get Line`).

---

### `Gemini Evaluate Text Rating`

**Signature**

```robot
${raw}=    Gemini Evaluate Text Rating    ${context}    ${evaluation}    extra_instructions=${extra}
```

**Description**
Generic text judge with a 1–5 rubric (`SCORE` + `REASON`). `context` = test evidence; `evaluation` = criterion to score. Returns raw text; use `Gemini Parse Rating` to extract the score.

---

### `Gemini Parse Rating`

**Signature**

```robot
${score}=    Gemini Parse Rating    ${raw}
```

**Description**
Extracts integer `1`–`5` from `SCORE:`/`NOTA:` lines; returns the original text when parsing fails.

---

### `Gemini Generate From Prompt`

**Signature**

```robot
${text}=    Gemini Generate From Prompt    ${prompt}
```

**Description**
Sends a direct text prompt (no context/evaluation template).

---

### `Gemini Screenshot And Ask`

**Signature**

```robot
${text}=    Gemini Screenshot And Ask    ${prompt}    selector=${selector}    filename=${file}
```

**Description**
Advanced shortcut: screenshot + single prompt.

---

### `Gemini Screenshot Html And Ask`

**Signature**

```robot
${text}=    Gemini Screenshot Html And Ask    ${prompt}    filename=${file}
```

**Description**
Advanced shortcut: screenshot + HTML + single prompt.

## Usage examples

Examples follow prompt-engineering basics: **factual context** (what the test observed), **objective criteria** (what to judge), **output format** in `extra_instructions` when needed, and a **parser** separate from raw model text.

### 1) Generic judge with 1–5 score (text)

```robot
*** Keywords ***
Rate test artifact
    [Documentation]    Reusable judge: evidence + criterion + rubric built into the library.
    ${ctx}=    Catenate    SEPARATOR=\n
    ...    ## Test evidence
    ...    ${ARTIFACT}
    ...    
    ...    ## Scenario intent
    ...    ${SCENARIO_INTENT}
    ${crit}=    Set Variable
    ...    How well does the evidence fulfill the scenario intent?
    ...    Consider: completeness, internal consistency, and absence of errors or placeholders.
    ${raw}=    Gemini Evaluate Text Rating    ${ctx}    ${crit}
    ${score}=    Gemini Parse Rating    ${raw}
    Log    score=${score} | raw=${raw}
    ${score_int}=    Convert To Integer    ${score}
    Should Be True    ${score_int} >= 4    msg=Score below minimum (${score})
```

### 2) Screen evaluation + Yes/No

```robot
*** Settings ***
Library    String

*** Keywords ***
Validate screen consistency
    [Documentation]    Context describes UI state; criterion is binary and visible in the screenshot.
    ${ctx}=    Catenate    SEPARATOR=\n
    ...    ## UI state
    ...    Listing with filter "${FILTER_LABEL}"="${FILTER_VALUE}" applied.
    ...    Consider only rows visible in the current viewport.
    ${crit}=    Set Variable
    ...    Do all visible rows show "${FILTER_VALUE}" in field "${FILTER_LABEL}"?
    ${output}=    Set Variable
    ...    Reply with exactly one word on the first line: Yes or No.
    ...    If No, one short reason on the next line.
    ${raw}=    Gemini Evaluate With Screen    ${ctx}    ${crit}    extra_instructions=${output}
    ${v}=    Get Line    ${raw}    0
    ${v}=    Strip String    ${v}
    Should Be Equal As Strings    ${v}    Yes
```

### 3) Existing screenshot file (saved image)

```robot
*** Keywords ***
Evaluate full image
    [Documentation]    Multimodal with a saved file; criteria target visible failure signals.
    Take Screenshot    ${OUTPUT_DIR}/page_full.png    fullPage=True
    ${ctx}=    Set Variable    Full-page capture after navigation finished and network idle.
    ${crit}=    Set Variable
    ...    Are there loading placeholders, skeletons, error messages, or clearly broken layout?
    ...    Ignore minor cosmetic differences if main content is readable.
    ${raw}=    Gemini Evaluate With Image File
    ...    ${ctx}
    ...    ${crit}
    ...    ${OUTPUT_DIR}/page_full.png
    ...    extra_instructions=Reply with exactly one word on the first line: Yes or No. Yes = page looks loaded and usable; No = obvious problem.
    ${v}=    Get Line    ${raw}    0
    ${v}=    Strip String    ${v}
    Should Be Equal As Strings    ${v}    Yes
```

### 4) Text judge with three outcomes (Yes / No / Warn)

```robot
*** Settings ***
Library    String

*** Keywords ***
Validate artifact with three-way verdict
    [Documentation]    Warn when data is missing; do not treat missing evidence as criterion failure.
    ${ctx}=    Catenate    SEPARATOR=\n
    ...    ## Evidence
    ...    ${ARTIFACT}
    ...    
    ...    ## Expected reference
    ...    ${EXPECTED_REFERENCE}
    ${crit}=    Set Variable
    ...    Checklist:
    ...    1) Evidence addresses what the expected reference requires.
    ...    2) No explicit contradiction between evidence and reference.
    ...    3) If evidence states unavailability or missing data, classify as Warn, not No.
    ${output}=    Set Variable
    ...    Reply with exactly one word on the first line: Yes, No, or Warn.
    ${raw}=    Gemini Evaluate Text Verdict    ${ctx}    ${crit}    ${output}
    ${v}=    Get Line    ${raw}    0
    ${v}=    Strip String    ${v}
    Log    Verdict=${v} | Raw=${raw}
    Should Be Equal As Strings    ${v}    Yes
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
    ${q}=    Gemini Generate From Prompt    ${prompt}
    Log    ${q}
```
