# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| Latest release on [PyPI](https://pypi.org/project/robotframework-gemini/) | Yes |
| Older releases | Best effort only |

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security problems (credential leaks, RCE, dependency exploits, etc.).

Prefer one of these channels:

1. **[GitHub Security Advisories](https://github.com/carlosnizolli/robotframework-gemini/security/advisories/new)** for this repository (private report to the maintainer).
2. Email the maintainer listed on [PyPI](https://pypi.org/project/robotframework-gemini/) / GitHub profile if Advisories are unavailable.

Include:

- Description of the issue and impact
- Steps to reproduce (PoC if possible)
- Affected versions / commit SHA
- Whether you plan to disclose publicly and on what timeline

You should receive an acknowledgement when possible. Please allow reasonable time for a fix or coordinated disclosure before public discussion.

## What is out of scope

- Abuse of **your own** Gemini API key or quota
- Social engineering / phishing unrelated to this codebase
- Issues that require compromised local CI secrets outside this project

## Safe usage notes

- Never commit `GEMINI_API_KEY`, tokens, or `.env` files.
- Prefer environment variables or CI secrets; examples in the docs use `%{GEMINI_API_KEY}` on purpose.
- Treat model output as untrusted text in assertions and logs.
