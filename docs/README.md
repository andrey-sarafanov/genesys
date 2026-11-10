# Documentation

[Repository home](../README.md) · [Installation](installation.md) · [Skill source](../skills/)

## Start with your task

- **Access data or build a reporting integration:** [Genesys Reporting](genesys-reporting.md).
- **Implement a customer journey:** [CX as Code](genesys-cx-as-code.md).
- **Explain queue or IVR performance:** [Performance Investigator](genesys-performance-investigator.md).

Each guide below links to the actual instructions, reference files and helpers. The Markdown pages render directly in GitHub, so no download is needed to read them.

## Install and try

Read [installation](installation.md), then run `python install.py --list` from the clone. You can select one skill, preview the target location with `--dry-run`, and install without overwriting an existing folder.

A useful first request is a plan-only task with explicit scope. Installation alone does not set up OAuth, run Analytics queries or authorize routing changes.

## Detailed HTML guides

For searchable, branded offline reading, download/clone the repository and open [catalog.html](../catalog.html). HTML files appear as source in GitHub's viewer; use the Markdown guides for reading directly on this page.

## How the material is organized

- `docs/`: a reading guide and installation instructions for people.
- `skills/<name>/SKILL.md`: the agent's instructions and trigger description.
- `skills/<name>/references/`: detailed contracts and channel/API notes, loaded when needed.
- `scripts/` and `assets/` within a skill: executable helpers and reusable templates where present.
- Root HTML guides and ZIPs: portable reading and installation copies.

Historical API/provider baselines retain their original dates. Local validation does not establish live tenant permissions, completeness or production readiness.
