# API selection and requests

## Select the reporting surface

All paths are relative to the confirmed regional Platform API host. The current official [Analytics API reference](https://github.com/MyPureCloud/platform-client-sdk-python/blob/master/build/docs/AnalyticsApi.md) supplies precise schemas, permissions and status behavior.

| Question | Method and path |
|---|---|
| Historical queue/contact KPIs | POST `/api/v2/analytics/conversations/aggregates/query` |
| Narrow conversation reconstruction | POST `/api/v2/analytics/conversations/details/query` |
| Bulk conversation extraction | POST `/api/v2/analytics/conversations/details/jobs` |
| Job status | GET `/api/v2/analytics/conversations/details/jobs/{jobId}` |
| Job result pages | GET `/api/v2/analytics/conversations/details/jobs/{jobId}/results` |
| Detail data availability | GET `/api/v2/analytics/conversations/details/jobs/availability` |
| One analytics conversation | GET `/api/v2/analytics/conversations/{conversationId}/details` |
| Current queue conditions | POST `/api/v2/analytics/queues/observations/query` |
| Historical agent statistics | POST `/api/v2/analytics/users/aggregates/query` |
| Historical agent state intervals | POST `/api/v2/analytics/users/details/query` |
| Current user conditions | POST `/api/v2/analytics/users/observations/query` |
| IVR/flow statistics | POST `/api/v2/analytics/flows/aggregates/query` |

User-detail jobs and several aggregate-job families also exist. Verify their current contracts rather than assuming all families share one paging or freshness model. Inspect preview status before adopting additional bot, journey, quality, transcript, campaign or utilization APIs. Do not extrapolate an endpoint by substituting a resource noun.

Observations answer current-state questions; they do not reconstruct a historical interval. Presence, routing status, utilization, WFM schedules and adherence are related but distinct datasets. Choose the actual dataset needed for a workforce question.

## Entity discovery

Use paginated directory endpoints or an authorized connector to resolve selected entities. Common paths include GET `/api/v2/routing/queues`, `/api/v2/users`, `/api/v2/flows`, and selected `/api/v2/routing/queues/{queueId}`. Verify each resource's query parameters and permissions. Record exact ID, display name, division, and flow type/version when relevant. Match ambiguous names explicitly; do not use the first substring match. Current names/configuration are not proof of their historical values.

## Queue aggregate example

Illustrative REST body: `QUEUE_ID` must be replaced with an explicitly resolved selection. The dates and `America/New_York` are examples. This window crosses the fall DST change and spans 49 elapsed hours. Confirm metric support and filter schema before execution.

```json
{
  "interval": "2026-10-31T04:00:00Z/2026-11-02T05:00:00Z",
  "timeZone": "America/New_York",
  "granularity": "P1D",
  "groupBy": ["queueId", "mediaType"],
  "metrics": ["nOffered", "tAnswered", "tAbandon", "tHandle", "tWait", "oServiceLevel"],
  "filter": {
    "type": "and",
    "clauses": [
      {
        "type": "or",
        "predicates": [
          {"type": "dimension", "dimension": "queueId", "operator": "matches", "value": "QUEUE_ID"}
        ]
      },
      {
        "type": "or",
        "predicates": [
          {"type": "dimension", "dimension": "mediaType", "operator": "matches", "value": "voice"}
        ]
      }
    ]
  }
}
```

For more queues add predicates to the queue OR clause, retaining the AND relationship with media. A single OR across queue and media would unintentionally broaden scope. Change granularity to `PT30M` for a separate intraday dataset; do not add that dataset to the daily one. Keep `queueId` and `mediaType` in the group so interpretation preserves their populations.

Other diagnostic metrics can include `tShortAbandon`, `tTalkComplete`, `tHeldComplete`, `tAcw`, `nTransferred`. Verify support rather than treating this as an exhaustive catalogue. See [metrics.md](metrics.md).

## Conversation detail example

Details use their own filter model, not aggregate `filter`, `groupBy` or `granularity` fields. A queue filter selects conversations with matching segments; it does not mean all returned participants/segments belong to that queue.

```json
{
  "interval": "2026-11-02T05:00:00Z/2026-11-03T05:00:00Z",
  "order": "asc",
  "orderBy": "conversationStart",
  "paging": {"pageSize": 100, "pageNumber": 1},
  "segmentFilters": [
    {
      "type": "and",
      "predicates": [
        {"type": "dimension", "dimension": "queueId", "operator": "matches", "value": "QUEUE_ID"},
        {"type": "dimension", "dimension": "mediaType", "operator": "matches", "value": "voice"}
      ]
    }
  ]
}
```

This is a synchronous example. Check interval-selection semantics, page/deep-pagination limits and open-conversation behavior. Use the documented asynchronous request model for a bulk job; do not blindly pass `paging` from this example to a job request.

Preserve the nested grain: conversation → participants → sessions → segments, plus session metrics and flow/outcome fields where present. Queue attribution often lives at segment level. Flattening multiple child arrays together can multiply rows and counts. Apply queue, media, event-time and segment logic to the chosen grain before deriving measures. Do not assume the matching conversation's start date equals the date each metric was emitted.

## Flow aggregate example

```json
{
  "interval": "2026-11-02T05:00:00Z/2026-11-03T05:00:00Z",
  "timeZone": "America/New_York",
  "granularity": "P1D",
  "groupBy": ["flowId", "mediaType"],
  "metrics": ["nFlow", "tFlow", "tFlowDisconnect", "tFlowExit"],
  "filter": {
    "type": "or",
    "predicates": [
      {"type": "dimension", "dimension": "flowId", "operator": "matches", "value": "FLOW_ID"}
    ]
  }
}
```

Separate outcome slices can group by `flowOutcomeId` and `flowOutcomeValue`, using supported `nFlowOutcome`, `nFlowOutcomeFailed`, `tFlowOutcome`; version slices can use `flowVersion`. Verify current allowed combinations. Do not invent `nFlowOutcomeSuccess`, infer success from a missing failed metric, or combine overlapping outcome/version slices into base flow volume. Flow instrumentation and type determine available outcomes; in-queue flow behavior can differ.

Model references: [conversation aggregate](https://github.com/MyPureCloud/platform-client-sdk-python/blob/master/build/PureCloudPlatformClientV2/models/conversation_aggregation_query.py), [conversation detail](https://github.com/MyPureCloud/platform-client-sdk-python/blob/master/build/PureCloudPlatformClientV2/models/conversation_query.py), [flow aggregate](https://github.com/MyPureCloud/platform-client-sdk-python/blob/master/build/PureCloudPlatformClientV2/models/flow_aggregation_query.py).
