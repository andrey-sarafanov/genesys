# Research record

Reviewed 2026-10-15. Original skill/helper implementation; no upstream Python or HTML copied or bundled.

Repository: https://github.com/laggyzee/genesys-mcp
Commit: `69b18f6a9f335c6993199166ae6754be3b713811`; package version `1.24.0`.

| Finding | Evidence at pinned commit | Design consequence |
|---|---|---|
| Directory, queue analytics and generic API tools exist | `tools/directory.py`, `analytics.py`, `raw.py` | Explicit selected-ID queries |
| Queue summary drops transfer, talk, hold, ACW and short-abandon metrics | `_QUEUE_SUMMARY_METRICS` | Full mode/raw queries for diagnostics |
| Queue wrapper has no timezone argument | `queue_performance` signature/body | Raw queries with `timeZone` |
| Generic tool accepts GET/POST/PUT/PATCH/DELETE | `_ALLOWED_METHODS` in `raw.py` | Explicit operation restrictions; do not rely on “read-only” label |
| No dedicated flow analytics tool in reviewed modules | `tools/` inventory | Separate official flow aggregate endpoint |
| Daily-brief examples use empty queue lists | `skills/cc-daily-brief/SKILL.md` | Do not inherit empty/tenant-wide selection |

Pinned links: [analytics](https://github.com/laggyzee/genesys-mcp/blob/69b18f6a9f335c6993199166ae6754be3b713811/src/genesys_mcp/tools/analytics.py), [raw API](https://github.com/laggyzee/genesys-mcp/blob/69b18f6a9f335c6993199166ae6754be3b713811/src/genesys_mcp/tools/raw.py), [directory](https://github.com/laggyzee/genesys-mcp/blob/69b18f6a9f335c6993199166ae6754be3b713811/src/genesys_mcp/tools/directory.py), [daily brief](https://github.com/laggyzee/genesys-mcp/blob/69b18f6a9f335c6993199166ae6754be3b713811/skills/cc-daily-brief/SKILL.md).

The repository declares PolyForm Noncommercial 1.0.0 and separate commercial licensing. Review its [LICENSE](https://github.com/laggyzee/genesys-mcp/blob/69b18f6a9f335c6993199166ae6754be3b713811/LICENSE) before adopting that server for paid PS work. This package does not distribute or require it.

## Primary Genesys sources

- [Official API schema](https://api.mypurecloud.com/api/v2/docs/swagger): successfully retrieved after the initial slow response. The compact [api-contract.json](api-contract.json) preserves enumerated flow/conversation metric and grouping names, exact query permissions, retrieval date and full-source SHA-256. Starter and outcome/version request bodies are checked against it. Flow metrics include `nFlow`, `nFlowOutcome`, `nFlowOutcomeFailed`, `tFlow`, `tFlowDisconnect`, `tFlowExit`, `tFlowOutcome`; there is no `nFlowOutcomeSuccess` in this snapshot. Query permissions are `analytics:flowAggregate:view` and `analytics:conversationAggregate:view`, with analytics read scope; queue metadata requires `routing:queue:view` and flow metadata `architect:flow:view`. These are API permissions, distinct from the full portal-view permission set.

- [Official flow query model](https://github.com/MyPureCloud/platform-client-sdk-python/blob/master/build/PureCloudPlatformClientV2/models/flow_aggregation_query.py): verified `timeZone`, interval, granularity, groupBy and timestamp options. Its metric strings are not a catalogue of supported metrics; check live support before extending queries.
- [Official conversation query model](https://github.com/MyPureCloud/platform-client-sdk-python/blob/master/build/PureCloudPlatformClientV2/models/conversation_aggregation_query.py): filtered queue query structure.
- [Flow query guide](https://developer.genesys.cloud/analyticsdatamanagement/analytics/aggregate/flow-query): research browser returned only a JS shell; not treated as readable evidence for detailed metric semantics.
- [Flows Performance Summary](https://help.genesys.cloud/articles/flows-performance-summary-view/): reporting timezone selector, flow versions, destinations, division visibility and delayed speech/text metrics.
- [Flow Outcomes Summary](https://help.genesys.cloud/articles/flow-outcomes-summary-view/): outcomes and permissions. Missing instrumentation is not a failed business outcome.
- [Performance columns](https://help.genesys.cloud/articles/view-available-columns-in-performance-views-by-category/): configuration-dependent SL denominator and event timing.
- [Reporting FAQs](https://help.genesys.cloud/faqs/category/reports/): offered, answered and handled can land in different intervals; web messaging does not share voice abandonment semantics.
- [Add a flow outcome](https://help.genesys.cloud/?p=185383): this feature excludes in-queue flow analytics.

An independent Gemini methodology critique was reviewed. Generic weighting and attribution cautions were useful; suggested metric names, a generic SL formula and overconfident causal language were rejected as technical evidence.

No tenant or live portal was accessed. Runtime permissions, tenant instrumentation, timezone and UI reconciliation remain live-run checks. Guidance concerns Genesys Cloud, not PureConnect or Engage. API behavior may change after this review.
