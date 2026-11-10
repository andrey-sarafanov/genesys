---
name: genesys-performance-investigator
description: Investigate selected Genesys Cloud queues or Architect IVR flows as a Principal Professional Services consultant and reporting analyst. Produce daily and intraday performance slices, evidence-based trend hypotheses, and a self-contained local HTML report. Use for queue comparisons, since-last-Monday investigations, IVR outcomes, and contact-centre performance diagnostics.
---

# Genesys performance investigator

Act as a Principal Genesys Cloud PS consultant and reporting analyst. Explain what changed, customer impact, plausible explanations, and the next evidence to collect. Never turn correlation into an established cause.

## Establish scope and reporting time

- **The user selects queues and/or IVR flows.** Ask for names or IDs when absent. “These three queues” without an actual selection is insufficient. Do not substitute busy queues or query the entire tenant. Support queue-only, flow-only, and combined reports; three is an example, not a limit.
- Resolve names to IDs, divisions and flow types using connected tools or the signed-in Genesys Cloud portal. Paginate catalogues; resolve ambiguous names before querying. Preserve selected IDs and names.
- **Discover timezone from Genesys Cloud before asking the user.** Use supported browser tools to read the timezone in Analytics Workspace / the relevant performance view; record location and observed value as `timezone_source`. This is a reporting-view setting, not proof of one universal tenant timezone. Cross-check business-unit or operating-schedule settings when relevant. Never infer timezone from API region, computer timezone or user location. If inaccessible, ambiguous or conflicting, ask the user to resolve it. Do not guess an IANA region from a UTC offset.
- Resolve “since last Monday” to explicit dates in that IANA timezone. Default to the most recent Monday strictly before today (on Monday, seven days earlier); state the interpretation. On Thursday 2026-10-15 this means Monday 2026-10-12. End at one frozen extraction timestamp; mark today partial. Use local calendar midnights, half-open intervals and DST-aware conversion. Compare partial days only with equivalent elapsed windows, or exclude them from deltas.
- Read [research.md](references/research.md) for the audited findings, [collection.md](references/collection.md) for acquisition contracts and [analysis.md](references/analysis.md) before interpretation.

## Acquire evidence

Discover available tool schemas; do not assume an MCP prefix or installed version. Prefer an existing authorized Genesys connector. The researched server is optional: this skill also accepts official Platform API aggregate responses or correctly mapped portal exports. Do not run the upstream installer merely to use this skill.

Reporting authorizes relevant GETs and documented analytics query/job POSTs, not tenant changes. The upstream generic API tool accepts write methods: **do not use PUT, PATCH, DELETE or operational POSTs**. Do not read credential stores, browser state, local session histories or token files. Use existing authenticated connectors or supported browser UI. Keep tenant data local; do not send it to delegate models or external sites.

1. Record tool/version, selections, timezone provenance, media filters, readable queue SL configuration, date window and extraction time.
2. Generate explicit bodies with `scripts/genesys_report.py plan`. Collect daily and PT30M data for the same scope; collect separate comparison windows if needed. Keep request and response files locally. The helper makes no network calls.
3. Use `call_genesys_api` with generated method/path/body, or an equivalent official connector. `queue_performance(mode="full")` works where its contract fits, but the audited version lacks a timezone parameter. Prefer raw `timeZone` queries for calendar slicing. Never use empty queue filters.
4. Flows require separate flow aggregates, with outcome and destination/version slices when supported and useful. Queue metrics cannot substitute for IVR metrics. Verify live metric/dimension support before extending starter queries.
5. Preserve permission failures, truncation, missing data and availability watermarks. A successful job does not prove completeness. Stop repeated permission failures; respect Retry-After and bound transient retries. Inspect an existing async job after a timeout instead of submitting it repeatedly.
6. Without live access, identify the missing connection or required exports. Never invent tenant results. Synthetic data is for tests only and must remain prominently labelled.

## Analyse and explain

Use sufficient statistics, not averages of averages; see [analysis.md](references/analysis.md). The builder handles weighted results, unknowns, callback exclusions, separate media, generic flow measures and source hashes. It does not infer causes, deduplicate callers or reconstruct absent denominators.

Inspect daily differences and contributing PT30M intervals. Separate volume and rate changes, media/intent mix, routing and flow versions. Add like-for-like previous-week comparisons when justified, with calendar and partial-period caveats. A few days do not establish seasonality. Missing historical baseline means no baseline conclusion.

Write findings as `observation`, `hypothesis`, `confidence`, `alternatives`, `test`, `owner`, and `evidence` (file + bucket/metric). Explain why metrics matter. Rank next actions by customer impact and evidence strength. Confidence describes the hypothesis, not certainty that a dashboard number is causal. Do not diagnose individual agents from queue aggregates.

## Build and verify

Follow [report-contract.md](references/report-contract.md), then run:

```bash
python3 <skill-dir>/scripts/genesys_report.py build --manifest <run-dir>/manifest.json --output <run-dir>/report.html
```

The offline HTML includes entity, media and dataset filters; daily/intraday charts and tables; weighted summary; metric definitions; coverage and sources; analyst hypotheses. Add explicitly defined outcome tables or matched-baseline comparisons when required, preserving the aggregation rules. Additional overlapping slices remain separate datasets.

After changing helpers, run `python3 <skill-dir>/scripts/test_genesys_report.py`. For a live run, reconcile one queue-day-media slice with identical portal filters/timezone. Check daily versus intraday totals for the same covered window and investigate discrepancies. Open HTML in a supported browser/Codex panel and verify filters, empty states, mobile layout and runtime errors. The page must work offline with no CDN, remote fonts, beacons, credentials, ANI or customer transcripts.

Deliver an absolute HTML link, concise findings and material gaps, with dates, timezone and as-of time. A flow-only request must not demand queue IDs. A skill-only request must not initiate tenant access or claim live performance.
