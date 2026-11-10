# Genesys Cloud skill library — Miratech

Detailed, self-contained HTML guides for the Genesys-specific skills installed in the reviewed environment.

| Guide | Purpose | File |
|---|---|---|
| Skill catalogue | Choose a skill and navigate the collection | [catalog.html](catalog.html) |
| Genesys Reporting | OAuth, Analytics APIs, metrics and pipelines | [index.html](index.html) |
| CX as Code | Terraform, Architect YAML, IVR, bots and messaging | [genesys-cx-as-code.html](genesys-cx-as-code.html) |
| Performance Investigator | Selected queue/IVR investigations and offline reports | [genesys-performance-investigator.html](genesys-performance-investigator.html) |

## Read the guides

Download the HTML files together and open `catalog.html` in a modern browser. GitHub displays HTML source rather than rendering the guide within its repository viewer. Each detailed guide supports section search, persistent navigation, a mobile contents menu, copyable code and print styling. No build step or external asset request is required.

## Scope and validation

Prepared November 6, 2026 from the installed skill instructions, reference documents and helper command interfaces. The two additional domain skills are `genesys-cx-as-code` and `genesys-performance-investigator`; generic BA, architecture and QA skills are not relabelled as Genesys skills.

Documentation and local checks do not prove live authentication, data completeness or deployment readiness. No live Genesys queries or flow deployments were performed for this collection. Historical provider/schema audits retain their original dates and are not current-version guarantees.

Miratech branding uses the logo from https://miratechgroup.com/. All HTML guides include links to their corresponding downloadable skill packages.

## Download the skills

Packaged November 10, 2026. Each ZIP preserves the complete skill folder, references, helpers and assets where supplied, including license notices. Bytecode caches are excluded.

- [genesys-reporting.zip](genesys-reporting.zip) — 8 files; invoke `$genesys-reporting` after placing the extracted folder in your configured skills directory.
- [genesys-cx-as-code.zip](genesys-cx-as-code.zip) — 21 files; invoke `$genesys-cx-as-code` after placing the extracted folder in your configured skills directory.
- [genesys-performance-investigator.zip](genesys-performance-investigator.zip) — 11 files; invoke `$genesys-performance-investigator` after placing the extracted folder in your configured skills directory.

See [skill-packages.json](skill-packages.json) for package sizes and SHA-256 checksums. Extract the top-level skill folder intact. Downloading a package does not execute scripts or connect to Genesys.
