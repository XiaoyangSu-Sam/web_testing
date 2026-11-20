# Copilot Skills

Each directory in [`skills/`](skills/) is a complete Skill. Copy the whole directory when installing one.

| Skill | What it does |
| --- | --- |
| [Web Functional Testing](skills/web-functional-testing/) | Turns a web application's README, source and test URL into unit, integration and browser checks with a coverage report. |

## Install in a project

Copy `skills/web-functional-testing/` from this repository into the target project's `.github/skills/`. To install the whole collection, copy `skills/` into the project's `.github/` directory and merge it with any existing skills. Open the target project in VS Code and invoke `/web-functional-testing` in Copilot Chat. See [VS Code Skill locations](https://code.visualstudio.com/docs/agent-customization/agent-skills#skill-locations).

```text
skills/
  web-functional-testing/
    SKILL.md                   Copilot entry point and testing workflow
    references/                Detailed workflows, report schema and prompt example
    scripts/                   Testing and reporting helpers
    samples/                   Synthetic requirements and report input
    requirements-browser.lock  Optional Playwright dependency pins
```

The report renderer and fixture generator use Python 3.10 or newer. Browser helpers can use an existing approved Python Playwright and Microsoft Edge setup. The Skill can also use browser tools available to Copilot. The [samples guide](skills/web-functional-testing/samples/README.md) includes a file-only walkthrough and an optional loopback browser demo.
