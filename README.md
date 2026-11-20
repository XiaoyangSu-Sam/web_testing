# Skills for Daily Work

A copy-ready catalog for documents, research, planning, browser work, and everyday development. It includes 20 selections from OpenAI's public Codex Skills catalog and this repository's Web Functional Testing Skill.

## Install in a project

Copy the complete directories you want from `skills/` into `.github/skills/` for [GitHub Copilot in VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills#skill-locations) or `.agents/skills/` for [Codex](https://developers.openai.com/codex/skills). Each directory includes its `SKILL.md` and the supporting files shipped with it. If Codex already has a built-in copy of a system Skill, use that copy. Check the typical setup column for tools and connections your workspace needs.

## Web Functional Testing

[Web Functional Testing](skills/web-functional-testing/) designs, writes, and runs independent unit, integration, and browser checks from product requirements, the live UI, and fresh fixtures. See the [independent test design guide](skills/web-functional-testing/references/independent-test-design.md) for general Web scenarios and the [samples guide](skills/web-functional-testing/samples/README.md) for a file-only walkthrough and optional localhost browser demo. Python 3.10 or newer runs the local report and data helpers. Browser checks can use available browser tools or Python Playwright with Edge.

## Document, data and media

| Skill | Use it for | Typical setup | Upstream |
| --- | --- | --- | --- |
| [pdf](skills/pdf/) | Read, create and visually verify PDFs | Python PDF libraries and Poppler for rendering | [curated · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/pdf) |
| [jupyter-notebook](skills/jupyter-notebook/) | Scaffold notebooks for analysis, experiments and tutorials | Python. Jupyter for interactive use | [curated · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/jupyter-notebook) |
| [transcribe](skills/transcribe/) | Transcribe recordings and optionally identify speakers | Python and approved OpenAI Audio API access | [curated · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/transcribe) |
| [speech](skills/speech/) | Turn text into narration or a voiceover | Python and approved OpenAI Audio API access | [curated · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/speech) |
| [imagegen](skills/imagegen/) | Generate and edit images for documents or product work | Built-in image generation, or the upstream CLI when requested | [system · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.system/imagegen) |
| [screenshot](skills/screenshot/) | Capture a screen, window or region | Supported desktop OS and capture access | [curated · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/screenshot) |

## Planning and knowledge

| Skill | Use it for | Typical setup | Upstream |
| --- | --- | --- | --- |
| [define-goal](skills/define-goal/) | Convert a loose request into a measurable goal | Goal tooling for saving a goal where supported | [curated · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/define-goal) |
| [notion-meeting-intelligence](skills/notion-meeting-intelligence/) | Draft agendas and pre-reads from project context | Notion connection | [curated · MIT](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/notion-meeting-intelligence) |
| [notion-knowledge-capture](skills/notion-knowledge-capture/) | Turn notes and decisions into wiki entries or FAQs | Notion connection | [curated · MIT](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/notion-knowledge-capture) |
| [notion-research-documentation](skills/notion-research-documentation/) | Build cited briefs from multiple Notion pages | Notion connection | [curated · MIT](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/notion-research-documentation) |
| [notion-spec-to-implementation](skills/notion-spec-to-implementation/) | Turn a spec into tasks and track implementation | Notion connection | [curated · MIT](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/notion-spec-to-implementation) |
| [linear](skills/linear/) | Manage issues, projects and team workflows | Linear connection and account access | [curated · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/linear) |

## Browser and software development

| Skill | Use it for | Typical setup | Upstream |
| --- | --- | --- | --- |
| [playwright](skills/playwright/) | Navigate and inspect websites from the terminal | Node.js/npm, Playwright CLI and browser access | [curated · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/playwright) |
| [gh-address-comments](skills/gh-address-comments/) | Read PR feedback and address review comments | Authenticated GitHub CLI | [curated · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/gh-address-comments) |
| [gh-fix-ci](skills/gh-fix-ci/) | Investigate failing GitHub Actions checks | Authenticated GitHub CLI | [curated · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/gh-fix-ci) |
| [cli-creator](skills/cli-creator/) | Turn a recurring workflow or API into a reusable CLI | The project’s relevant runtime or toolchain | [curated · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/cli-creator) |

## Codex and agent customization

| Skill | Use it for | Typical setup | Upstream |
| --- | --- | --- | --- |
| [skill-creator](skills/skill-creator/) | Write and validate reusable agent skills | Python and PyYAML for bundled helpers | [system · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.system/skill-creator) |
| [skill-installer](skills/skill-installer/) | Find and install skills from the catalog or a repository | Python and GitHub access | [system · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.system/skill-installer) |
| [openai-docs](skills/openai-docs/) | Look up authoritative OpenAI or Codex guidance | Docs MCP where available. Official web fallback | [system · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.system/openai-docs) |
| [plugin-creator](skills/plugin-creator/) | Scaffold a Codex plugin and its manifest | Python for the scaffold helper | [system · Apache-2.0](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.system/plugin-creator) |

## Sources and licenses

The 20 selections are copied from the system and curated directories of [OpenAI’s Codex Skills catalog at revision `49f948f`](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431). Each copy retains its upstream license and notices. The selection favors recurring work across several roles.
