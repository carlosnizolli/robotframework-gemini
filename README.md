# robotframework-gemini

**English** | [Português (Brasil)](https://github.com/carlosnizolli/robotframework-gemini/blob/main/README.pt-BR.md)

Robot Framework **keyword library** for **Google Gemini** oracles: **text-only** evaluation (API payloads, logs, JSON, etc.) or **multimodal** checks with an image (PNG file or a **Robot Framework Browser** screenshot).

- **Multimodal**: sends prompt text and the capture as a byte `Part` (`google-genai`).
- **Recommended flow**: two inputs — **context** (test framing) and **evaluation** (criterion or yes/no question).
- **Browser optional**: screenshot keywords need `Library    Browser`; text keywords work without a browser.

## Installation

```bash
pip install robotframework-gemini
```

With Robot Framework Browser (Playwright) screenshot support:

```bash
pip install "robotframework-gemini[browser]"
python -m pip install robotframework
```

Local development:

```bash
python -m pip install -e ".[dev]"
```

## Environment variables and Library import

| Variable / argument | Purpose |
|---------------------|---------|
| `GEMINI_API_KEY` | Gemini API key (required unless you pass `api_key` on the Library) |
| `GEMINI_MODEL` | Model id (e.g. `gemini-2.5-flash`). If omitted, defaults to `gemini-2.5-flash`. |
| `api_key` (import) | Overrides `GEMINI_API_KEY` at Library import |
| `model` (import) | Overrides `GEMINI_MODEL` at Library import |

By default the Library reads key and model from the environment. You can also pass them on import (useful in CI or suites that keep credentials in Robot variables):

```robot
*** Variables ***
${GEMINI_API_KEY}    %{GEMINI_API_KEY}
${GEMINI_MODEL}      gemini-2.5-flash

*** Settings ***
Library    GeminiLibrary    api_key=${GEMINI_API_KEY}    model=${GEMINI_MODEL}
```

Model only (key still comes from the environment):

```robot
Library    GeminiLibrary    model=gemini-2.5-flash
```

Explicit package import (equivalent):

```robot
Library    robotframework_gemini.library.GeminiLibrary    api_key=${GEMINI_API_KEY}    model=${GEMINI_MODEL}
```

> Do not commit a literal API key; prefer `%{GEMINI_API_KEY}` or CI secrets.

## Keyword documentation

- English: [docs/KEYWORDS.en.md](https://github.com/carlosnizolli/robotframework-gemini/blob/main/docs/KEYWORDS.en.md)
- Português: [docs/KEYWORDS.pt-BR.md](https://github.com/carlosnizolli/robotframework-gemini/blob/main/docs/KEYWORDS.pt-BR.md)

## Usage in Robot Framework

> **Note:** examples use `Set Variable` and `Catenate` instead of the `VAR` keyword (Robot Framework 7.0+) to stay compatible with older Robot Framework versions.

### Text only (no Browser)

```robot
*** Settings ***
Library    GeminiLibrary

*** Keywords ***
Validate API response
    ${context}=       Set Variable    {"status": "ok", "items": 3}
    ${evaluation}=    Set Variable    Does the payload indicate success with items?
    ${model_response}=    Gemini Evaluate Text    ${context}    ${evaluation}
    Log    ${model_response}
```

### With a screenshot (Browser)

Import **Browser** before **Gemini**:

```robot
*** Settings ***
Library    Browser
Library    GeminiLibrary

*** Keywords ***
Check screen against a neutral criterion
    ${context}=       Set Variable    List filtered by Active status.
    ${evaluation}=    Set Variable    Do all visible items show Active status?
    ${model_response}=    Gemini Evaluate With Screen    ${context}    ${evaluation}
    Log    ${model_response}
```

Recommended import (RobotCode, runtime, and PyPI):

```robot
Library    GeminiLibrary    api_key=${GEMINI_API_KEY}    model=${GEMINI_MODEL}
```

Explicit package path (IDEs that prefer a full Python path):

```robot
Library    robotframework_gemini.library.GeminiLibrary    api_key=${GEMINI_API_KEY}    model=${GEMINI_MODEL}
```

### IDE and RobotCode

| Import form | Resolved by |
|-------------|-------------|
| `Library    GeminiLibrary` | Top-level `GeminiLibrary.py` module (installed in the wheel or via `src/` in a clone) |
| `Library    robotframework_gemini.library.GeminiLibrary` | Standard Python package path |

In a **repository clone**, without installing:

- [`robot.toml`](robot.toml) — `python-path = ["src"]` for RobotCode/LSP
- [`.vscode/settings.json`](.vscode/settings.json) — `extraPaths` for Pylance/Cursor

With a local venv: `pip install -e ".[dev]"`, then reload the IDE window after changes.

With an image file already saved:

```robot
Browser.Take Screenshot    ${OUTPUT_DIR}/screen.png
${model_response}=    Gemini Evaluate With Image File    ${context}    ${evaluation}    ${OUTPUT_DIR}/screen.png
```

Verdict via prompt (first line) and 1–5 score:

```robot
${model_response}=    Gemini Evaluate With Screen    ${context}    ${evaluation}
...    extra_instructions=Reply with one word on the first line: Yes or No.
${verdict}=    Get Line    ${model_response}    0
Should Be Equal As Strings    ${verdict}    Yes

# Score 1–5: two steps (log the reason) or one-line shortcut
${model_response}=    Gemini Evaluate Text Rating    ${context}    ${evaluation}
${rating_score}=    Gemini Parse Rating    ${model_response}

${rating_score}=    Gemini Evaluate Text Rating Score    ${context}    ${evaluation}
```

Details for the three rating keywords: [Scores 1–5 (EN)](https://github.com/carlosnizolli/robotframework-gemini/blob/main/docs/KEYWORDS.en.md#scores-15-three-keywords-when-to-use).

See also [examples/demo_template.robot](https://github.com/carlosnizolli/robotframework-gemini/blob/main/examples/demo_template.robot).

## Tests

```bash
pytest
```

Tests mock `generate_content`; there are no real API calls.

## License

MIT.
