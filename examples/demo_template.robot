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
    ${context}=    Set Variable    Página simples carregada no navegador.
    ${evaluation}=    Set Variable    A área visível parece predominantemente em branco ou quase vazia?
    ${model_response}=    Gemini Evaluate With Screen    ${context}    ${evaluation}
    Log To Console    ${model_response}
    [Teardown]    Browser.Close Browser
