*** Settings ***
Documentation    Template demo: não executado pela suíte principal. Requer GEMINI_API_KEY (e opcionalmente GEMINI_MODEL).
Library    Browser
Library    GeminiLibrary

*** Variables ***
${DEMO_URL}    about:blank

*** Test Cases ***
Demo Gemini Evaluate With Screen
    [Documentation]    Exemplo mínimo com contexto + critério genéricos.
    [Tags]    demo    gemini
    Browser.New Browser    chromium    headless=True
    Browser.New Context
    Browser.New Page    url=${DEMO_URL}
    ${ctx}=    Set Variable    Página simples carregada no navegador.
    ${crit}=    Set Variable    A área visível parece predominantemente em branco ou quase vazia?
    ${text}=    Gemini Evaluate With Screen    ${ctx}    ${crit}
    Log To Console    ${text}
    [Teardown]    Browser.Close Browser
