# Acquisition recipes

Runtime tool schemas take precedence over these audited examples. Keep local per-run requests/responses immutable; record timestamps and never save credentials with evidence.

## Discovery

- `list_queues(name_contains=...,page_size=100,page_number=1)` returns `queues,total,page_number,page_size`. Paginate; match exact ID/division, not first substring.
- Relevant GETs: `/api/v2/routing/queues/{queueId}` for selected settings; `/api/v2/flows` for paginated discovery; `/api/v2/flows/{flowId}` for metadata. Verify current API Explorer parameters/permissions before use.
- `mcp_health_check` if exposed establishes server version/readiness, not every permission.
- Portal: inspect Analytics Workspace timezone using supported browser UI without changing settings. A fixed offset alone does not identify a DST-aware IANA region. Record visible evidence, not browser storage.

## Planner

Python 3.10+ with IANA zoneinfo data, no third-party dependencies:

```bash
python3 <skill-dir>/scripts/genesys_report.py plan \
  --timezone '<discovered-IANA-zone>' --queue-id '<id-1>' --queue-id '<id-2>' --queue-id '<id-3>' \
  --output <run-dir>/plan.json
```

Use `--flow-id` instead of/alongside queues. Add `--flow-outcomes` and/or `--flow-versions` for separate breakdown datasets. Optional `--start YYYY-MM-DD`, `--as-of <offset-aware-ISO-timestamp>`, repeated `--media voice`. Defaults are last Monday through now, daily and PT30M. Plan does not execute requests.

Pass each `requests[].request` object to `call_genesys_api`: `path,method,body`. Save responses including envelope. Raw tool success is `{"status":200,"data":{"results":[...]}}`; queue wrapper has root `results`. Check transport and semantic errors.

Queues: POST `/api/v2/analytics/conversations/aggregates/query`, group `queueId,mediaType`, explicit nonempty queue OR filter AND media filter, plus `interval,timeZone,granularity`. Starter metrics retain counts, sums, SL and diagnostic components.

Flows: POST `/api/v2/analytics/flows/aggregates/query`, group `flowId,mediaType`, selected flow filter. Verified starter metrics are `nFlow,tFlow,tFlowDisconnect,tFlowExit`. Outcome option adds a separate dataset grouped by `flowOutcomeId,flowOutcomeValue` with `nFlowOutcome,nFlowOutcomeFailed,tFlowOutcome`; version option adds `flowVersion`. These match the official schema snapshot in [api-contract.json](api-contract.json). Recheck live schema on incompatibility; tenant instrumentation determines available values. Define outcome populations before deriving success rates; do not guess `nFlowOutcomeSuccess`. Extend exits/destinations/language in distinct slices if needed. In-queue flows may lack the requested outcome analytics.

Do not pass hypothetical fields or a flowId filter to the conversation aggregate endpoint without schema verification. The official query model accepting a string is not evidence the backend supports that metric.

## Comparisons, detail and export fallback

Previous-week baselines need explicit matched local dates/hours and filters. Save baseline as a distinct slice; never include it in headline totals. Expanded direction/language/skill/wrap-up slices can multiply observations, so keep them separate from base queries.

For causal tests, fetch narrowly scoped conversation details through documented query/job endpoints. Follow pagination/cursors, record sampling/truncation and availability watermarks, and exclude customer details from HTML. Do not infer historical staffing from current snapshots.

Portal CSV must retain timezone, filters, units and denominators. Normalize to the documented aggregate envelope. If only averages/percentages were exported, leave missing sums/counts/numerators absent; pooled results remain N/A. Never manufacture sufficient statistics.

Start with two concurrent analytics queries. Respect 429 Retry-After; cap transient retries at three. Split size-limited queries into non-overlapping windows, preserving successes and explicit gaps. Poll existing async jobs after ambiguous timeouts. No unbounded organization-wide scans or credential refresh loops.
