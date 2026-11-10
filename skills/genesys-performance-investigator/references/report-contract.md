# Report files and manifest

The helper requires Python 3.10+ and IANA timezone data; it uses only the standard library. It never connects to Genesys, handles credentials or uploads data. Acquisition is performed by the invoking agent through authorized tools. Keep each run in a dedicated directory.

`plan` emits exact request candidates. `build` accepts raw aggregate envelopes plus a manifest, validates scope/overlap, computes metrics and embeds normalized data into one HTML file. No server/CDN is required. It accepts camelCase API group IDs and the MCP's preserved group keys. Invalid shapes and error envelopes surface as unavailable data; unselected entities, overlapping buckets or malformed numeric statistics stop the build.

Example manifest (replace illustrative values with actual evidence; this is not live data):

```json
{
  "title": "Selected queues: performance since Monday",
  "timezone": "Europe/London",
  "timezone_source": "Observed Analytics Workspace timezone selector, 2026-10-15T12:00:00Z",
  "interval": "2026-10-11T23:00:00Z/2026-10-15T12:00:00Z",
  "as_of": "2026-10-15T12:00:00Z",
  "entities": [{"kind":"queue","id":"user-selected-id","name":"User-selected queue"}],
  "datasets": [{
    "id":"queue-daily",
    "file":"queue-P1D.json",
    "kind":"queue",
    "granularity":"P1D",
    "slice":"base",
    "coverage":"provisional",
    "note":"Current day is incomplete; aggregate data may settle after extraction.",
    "request":{"method":"POST","path":"/api/v2/analytics/conversations/aggregates/query","body":{}}
  }],
  "limitations":["No matched historical baseline collected."],
  "findings":[]
}
```

Use the full actual request body, not the empty illustrative body above. `datasets[].interval` optionally narrows a dataset within the overall interval; comparison data outside that interval belongs in a separate manifest/report, or explicitly widen the report window and clearly name the separate baseline dataset. The UI never combines datasets.

Coverage values: `complete`, `provisional`, `partial`, `unknown`, `unavailable`. Label `complete` only after verifying requested coverage, limits and freshness; it does not certify a successful API response merely because HTTP returned 200. Overall current-day incompleteness and source freshness are distinct. Missing returned buckets are visibly flagged; sparse data is not zero-filled. If the API returns a bucket extending past the requested end, preserve the raw response and resolve its actual covered window; the builder rejects it rather than allocating a whole-bucket value to a partial interval.

Each dataset must contain only one non-overlapping time series per entity/media/additional group dimensions. Daily and intraday queries, alternative breakdowns, versions, outcome cohorts and baseline periods are separate datasets. If chunked responses contain overlapping boundary buckets, reconcile/refetch explicitly before build, not by silently dropping one.

Raw accepted shape:

```json
{"results":[{"group":{"queueId":"user-selected-id","mediaType":"voice"},"data":[
 {"interval":"2026-10-11T23:00:00Z/2026-10-12T23:00:00Z","metrics":[
   {"metric":"nOffered","stats":{"count":100}},
   {"metric":"tAnswered","stats":{"count":90,"sum":1800000}},
   {"metric":"oServiceLevel","stats":{"numerator":75,"denominator":100}}
 ]}
]}]}
```

The raw API tool envelope `{"status":200,"data":...}` is also supported. Absence of a metric remains N/A. Callback answered/abandon/SL are excluded. Service-level ratio-only individual buckets can display; pooled SL remains N/A without numerators/denominators. Complete sufficient statistics are required across every contributing row. Qualified/duplicate metrics require an explicit semantic adapter; they are rejected rather than incorrectly combined.

Flow responses use `flowId`. Additional group keys (version, outcome ID/value, destination) remain separate. Any returned additional flow metric gets a generic count and, for time metrics, average-seconds selector. The agent must explain its verified business meaning and define outcome rates before adding calculated business measures; the renderer will not invent containment or success rates.

Findings format:

```json
{
  "observation":"State an evidenced change with exact period and numbers.",
  "hypothesis":"State a plausible but unconfirmed mechanism.",
  "confidence":"low / medium / high, with rationale",
  "alternatives":["Alternative explanation"],
  "test":"Specific next evidence that could support or disprove the hypothesis.",
  "owner":"Suggested operational owner",
  "evidence":["queue-P1D.json, selected queue ID, local date, metric name"]
}
```

These entries are analyst-authored and remain scoped to their cited evidence when UI filters change. Missing findings produce an honest empty state.

For a reproducible synthetic preview, run `scripts/test_genesys_report.py --demo-dir <temporary-directory>`, then build that directory's `manifest.json`. Never use the fixture to populate a live report. The `demo:true` flag creates a persistent visible synthetic-data banner.

Run `python3 scripts/test_genesys_report.py` for aggregation, date, scope, schema and escaping checks. Optional JavaScript logic checks: `node scripts/test_report_ui.mjs <synthetic-report.html>`. This uses a minimal DOM stub, not a browser, and does not verify layout. During creation, 15 Python checks and these JS logic checks passed. Browser visual verification was blocked by the browser's local-file URL security policy; no alternate browser route was attempted. Live-tenant reconciliation has not been performed.

## Acceptance scenarios

- Three supplied queues: no other queue queried/rendered; pagination and duplicate names resolved.
- Flow-only request: no queue requirement; per-day flow counts/duration and verified outcome/version breakdowns.
- Missing selections: ask for them; do not run analytics against all entities.
- Portal timezone unavailable or inconsistent: explain missing evidence and request clarification; no computer-timezone fallback.
- Unequal queue volumes: pooled ASA/AHT/SL use sums and counts; incomplete stats yield N/A.
- 403, empty response, missing metric, missing day, current partial day: visible distinct states; no fabricated zero or trend.
- Sunday/Monday ambiguity, spring/fall DST and repeated-hour intraday data: explicit dates, offset-aware boundaries and no duplicate accumulation.
- Callback/message rows: no invented voice-style abandonment or callback success.
- Offline report: entity/media/dataset/metric filters, CSV export, printable view, readable small-screen layout, no external requests or runtime errors.
- Adversarial display names: render as text, not HTML/script; CSV protects spreadsheet-formula prefixes.
