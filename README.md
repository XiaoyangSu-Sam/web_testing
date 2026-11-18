# Web Functional Testing Skill

A GitHub Copilot Skill for testing a web application from its README, source code, and test URL. Copilot maps documented behavior to test cases, authors and runs them, and reports what passed, what failed, and how to verify a fix.

- Start with a smoke test, then cover business logic with unit, integration, and browser tests.
- Track asynchronous jobs by ID and confirm terminal status and actual output before passing a test.
- Measure file and result-set capacity after the small functional baseline passes.
- Produce a report with requirement coverage, reproduction steps, evidence, and recommended fixes.

[Skill definition](.github/skills/web-functional-testing/SKILL.md) · [Copilot prompt](COPILOT_WEB_FUNCTIONAL_TESTING.md) · [Example report](samples/async-demo/report.md) · [Validation](VALIDATION.md)

## Use the Skill in Copilot

Copy `.github/skills/web-functional-testing/` into the same path in your testing workspace, or open this repository as your workspace. In VS Code Copilot Agent, invoke `/web-functional-testing` when available. You can also ask Copilot to read the linked Skill definition and paste the included prompt. Provide the target repository or checkout, test URL, and available test roles.

Use the existing Python testing kit environment if one is already configured. For a fresh setup on Windows x64 with Python 3.12, uv and Microsoft Edge installed, run the following from the repository root:

```powershell
uv venv --python 3.12 --no-python-downloads
uv pip sync --require-hashes requirements.lock
```

For offline setup, point uv at the matching Windows x64, Python 3.12 wheels from the Python testing kit:

```powershell
uv venv --python 3.12 --no-python-downloads --offline
uv pip sync --offline --no-index --find-links offline/wheels --require-hashes requirements.lock
```

The scripts use installed Edge. The setup requires no npm commands or separate browser download. Source-level unit tests for a target application use that project's available test runner.

## Run the sample locally

```powershell
.\.venv\Scripts\python.exe .github/skills/web-functional-testing/scripts/run_async_demo.py
```

The sample starts a synthetic localhost service, exercises background jobs in Edge, and checks bounded local CSV reads. Intentional fixture failures illustrate diagnosis and remediation in the report. New reports are written to `reports/exploration/`.
