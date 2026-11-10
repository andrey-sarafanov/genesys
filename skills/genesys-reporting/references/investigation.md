# Investigations and deliverables

## Evidence-driven investigation

Start with the user's selected queues, flows, agents or explicit organization scope. Preserve those IDs throughout comparisons. Queue-only, flow-only and combined investigations are valid; never require queue IDs for flow-only work. Freeze extraction time and compare like local windows.

Obtain daily and intraday aggregates for the same population. Keep baseline, media, flow-version, outcome and other drilldowns as separate datasets. Identify the intervals and segments driving a change before collecting narrow details. Check missing buckets, open conversations, provisional data and permission coverage before interpreting trends.

| Pattern | Plausible hypothesis | Evidence needed / competing explanation |
|---|---|---|
| Volume and delay rise | Demand pressure | Matched hours and staffing; handle workload may also rise |
| Volume stable, delay worsens | Capacity or routing eligibility | Historical state, schedules, eligibility; arrivals may have shifted within buckets |
| AHT grows mainly in ACW | Workflow or case-mix change | Wrap-up/contact mix and process history |
| One queue rises while another falls | Routing or transfer change | Linked journeys and configuration history; independent demand is possible |
| Flow disconnects rise | Technical failure or self-service change | Outcome, exit, version and error evidence; disconnect alone proves neither |
| Outcome success declines after release | Regression or audience change | Matched version/intent populations and unchanged instrumentation |

Each material finding should distinguish the observed fact, interpretation, confidence, alternatives and next test. Link to exact local evidence or supplied source identifiers. “Associated with” is appropriate for correlation. State cause only when the evidence supports that stronger claim. Do not collect broad conversation/customer data when a smaller slice can test the hypothesis.

## Deliver the format requested

A concise answer may be sufficient. For a file/report, include explicit date range, timezone, as-of time, selected entities/media, coverage, KPI definitions, comparison windows, findings and material gaps. Preserve reusable raw/request evidence locally without embedding it all in the report.

For an offline HTML report: embed required CSS/JS, avoid CDNs/fonts/beacons, and exclude credentials, ANI, transcripts and unnecessary user/customer identifiers. Escape inserted strings and use safe JSON embedding for labels that could contain markup. Show empty/unavailable/provisional states distinctly. Verify it in a supported browser, including filtering and responsive layout. Do not claim visual QA if it was not opened.

For CSV/spreadsheet outputs: preserve numeric duration units and time offsets, identify row grain, distinguish blank from zero, and neutralize formula-like untrusted labels in cells. For a pipeline deliver the actual requested implementation plus checkpoint, paging and late-data strategy; a suggested architecture alone does not complete an implementation request.

## Troubleshooting map

| Symptom | First checks |
|---|---|
| Token acquisition fails | Regional login host, grant type, form encoding and client authentication |
| API 401 | Expiry, bearer header, region and actual client instance |
| API 403 | Endpoint ANY/ALL permissions, role/division grants, scopes, user context and applicable IP controls |
| 400 query error | Correct endpoint model, exact field casing, supported metric/dimension, filter nesting and limits |
| Empty or unexpectedly small results | Selected IDs, interval, media, division visibility, sparse response and availability |
| 429 or repeated timeout | Retry-After, shared client load, SDK retry multiplication and query size |
| Async complete but missing data | Availability watermark, all result cursors, gaps, open/late conversations and retention |
| Portal/API mismatch | Match scope, timezone, event timing, metric definitions, configuration and as-of timestamp |
| Duplicated totals after flattening | Nested join multiplication, overlapping datasets, repeat queue/flow visits and detail upsert key |
| Occupancy above 100% | Concurrent handling overlap, mixed populations and denominator definition |

Preserve safe error status, endpoint, timestamp, connector version and correlation ID for diagnosis. Redact secrets, headers and sensitive body values before sharing. Avoid treating every API problem as an authentication failure.

## Practical validation cases

Use these to review implementation decisions; tenant access is not required for design work:

- Unequal bucket volumes: pooled AHT uses duration sums/counts and gives 19 seconds for the example in metrics.md.
- New York DST window in api-queries.md: two local dates span 49 elapsed hours; repeated local hours retain distinct offsets.
- Flow-only request: uses flow metrics and selected flow IDs, without substituting queue activity.
- Restricted division: a 200 with missing entities is a coverage limitation until visibility is verified.
- Timed-out job poll: resume the existing job; do not resubmit it blindly.
- Ratio-only export: exact pooled service level remains unavailable.
- Authenticated app with no human context: do not use a user-only endpoint as the token validity test.

For live work, reconcile a small representative slice before broad extraction. Local JSON/schema checks establish structure, not permission, completeness or live metric semantics.
