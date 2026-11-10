# Genesys Reporting

[← Documentation](README.md) · [Install](installation.md) · [Skill instructions](../skills/genesys-reporting/SKILL.md)

## What it does

Use this skill to design or troubleshoot Genesys Cloud reporting: OAuth, regional endpoints, permissions/divisions, Analytics API selection, KPI definitions, reliable extraction and reconciliation. It covers both retrieving data and understanding what the result can establish.

## When to choose it

- A token or Analytics API request fails.
- You need the correct endpoint and payload for a reporting question.
- You are building a paginated or incremental extraction.
- A portal KPI and an API result differ.
- You need channel-aware metric definitions and weighted calculations.

Use [Performance Investigator](genesys-performance-investigator.md) for a selected queue/IVR diagnostic report. Use [CX as Code](genesys-cx-as-code.md) to implement a journey change.

## Install

From this repository's clone:

```sh
python install.py --skill genesys-reporting --dry-run
python install.py --skill genesys-reporting
```

Or give `$skill-installer` this folder:

https://github.com/andrey-sarafanov/genesys/tree/main/skills/genesys-reporting

## Example request

```text
Use $genesys-reporting to design a conversation-detail extraction for these
selected queue IDs. Include OAuth prerequisites, region, cursor checkpoints,
data-availability watermarks and a strategy for late-arriving updates.
Prepare the design without accessing a tenant.
```

## Read the references

- [Authentication](../skills/genesys-reporting/references/authentication.md): grant choice, region, scopes, roles and divisions.
- [API queries](../skills/genesys-reporting/references/api-queries.md): endpoint selection and request examples.
- [Metrics](../skills/genesys-reporting/references/metrics.md): sums/counts, service level, channels and attribution.
- [Extraction](../skills/genesys-reporting/references/extraction.md): timezones, paging, jobs, retries and reconciliation.
- [Investigation](../skills/genesys-reporting/references/investigation.md): hypotheses, evidence and deliverables.
- [Sources](../skills/genesys-reporting/references/sources.md): verification dates and documentation limits.

## What is installed

Eight source files: instructions, UI metadata and six references. This skill has no bundled executable helper and does not install a network client. Dependencies depend on the SDK or connector used for the actual task.

## Limits

Missing data is not zero. Ratios without sufficient statistics cannot produce an exact pooled KPI. Current state does not establish historical staffing. A reporting request does not authorize operational configuration changes. Keep credentials outside saved evidence and reports.

[Detailed offline HTML](../index.html) · [Portable ZIP](../genesys-reporting.zip)
