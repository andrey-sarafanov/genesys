---
name: genesys-reporting
description: Plan, build and troubleshoot Genesys Cloud reporting using Analytics APIs, OAuth, roles and divisions, queue/agent/flow metrics, conversation details, exports and incremental data pipelines. Use for reporting queries, authentication setup, KPI reconciliation and performance analysis. Excludes Genesys Engage/PureConnect implementation and Architect or routing changes.
---

# Genesys Cloud reporting

Turn reporting questions into correctly scoped, reproducible evidence. Cover both how to retrieve data and what it can establish. Support API design and troubleshooting without requiring a live tenant. A request to create or explain this skill does not initiate tenant access.

## Choose the relevant guidance

Read only the references needed:

- [Authentication and access](references/authentication.md): region selection, OAuth grants, SDK setup, roles, scopes, divisions and secret handling.
- [API selection and requests](references/api-queries.md): aggregate/detail/observation selection, entity discovery, filter placement and request examples.
- [Metrics and interpretation](references/metrics.md): weighted calculations, attribution, channels, service level, agent state and IVR outcomes.
- [Extraction and reconciliation](references/extraction.md): timezones, pagination, asynchronous jobs, data availability, retries, incremental loads and portal reconciliation.
- [Investigations and deliverables](references/investigation.md): comparison design, evidence, reporting outputs and troubleshooting.
- [Source register](references/sources.md): official documentation and verification limits; consult when implementing or changing technical contracts.

## Working contract

1. Establish the reporting question, Genesys product, selected entities, media, interval, reporting timezone and desired output. Resolve names to IDs and divisions. Reuse supplied scope; ask only for missing decisions that affect correctness. An explicit organization-wide report is valid; an omitted filter is not authorization for one.
2. Prefer available authorized connectors. Discover their actual schemas and versions; do not assume a tool named in a prior example exists. Use official SDK/Platform API or mapped portal exports when appropriate. Do not install a third-party server simply to run a report.
3. Establish the region independently from the reporting timezone. For tenant reporting, inspect the relevant performance-view timezone through an authorized connector or supported UI before asking. Record its provenance; it is not necessarily a universal tenant timezone. For an API-design example use an explicit illustrative timezone, labelled as such.
4. Choose the smallest dataset that answers the question. Start with aggregates for KPIs, details for conversation-level reconstruction, observations for current conditions, and user state/history for agent availability. Queue aggregates alone cannot establish staffing, occupancy or root cause.
5. Verify current endpoint method, schema, permissions, allowed dimensions/metrics, limits and preview status in official sources before live implementation. Distinguish REST camelCase from SDK snake_case and typed models. A string field in an SDK is not proof a particular metric is supported.
6. Preserve request bodies, filter and configuration provenance, extraction time and completeness. Distinguish API success, full retrieval and reconciled results. Follow [extraction.md](references/extraction.md) before treating results as complete.
7. Use sufficient statistics to pool results. Missing is not zero, a zero denominator is N/A, and average-of-averages is usually wrong. Keep observations separate from hypotheses and show material limitations beside findings.

## Authorization and data boundaries

A reporting request authorizes relevant reads and documented analytics query/job POSTs. It does not authorize routing, queue, Architect, OAuth-client, role, retention or schedule changes. Prepare any requested setup instructions or code locally; perform tenant changes only within the user's granted scope. Explain that a reporting job POST creates computation, even though it does not change routing configuration.

Use an existing authenticated connection or user-provided runtime secret binding. Never extract tokens from browser storage, credential stores or session histories. Do not request secrets in chat. Keep tokens and client secrets out of source, evidence, debug output and generated reports. Retrieve recordings, transcripts and customer identifiers only when necessary and authorized. Keep raw evidence local or in the explicitly approved destination; do not introduce external uploads or delegated processing implicitly.

## Finish the requested task

For API work, deliver the chosen endpoint, precise payload or typed SDK model, access prerequisites, pagination/completeness strategy and validation evidence. For reports, include explicit dates/timezone, as-of time, filters, metric definitions, coverage, findings and material gaps. For authentication issues, identify the failed layer and the narrow remedy. State which parts were validated locally, against documentation, and in the live tenant; never imply live success from an example or schema check.

This skill is standalone. If `genesys-performance-investigator` is available, its tested local helper and HTML workflow can support a selected queue/IVR investigation; read its contracts before use. It is optional, and its pinned third-party MCP audit is not current server documentation. Architect/Terraform changes belong to an implementation workflow when requested.
