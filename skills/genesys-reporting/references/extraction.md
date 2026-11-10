# Extraction and reconciliation

## Time contract

Record the reporting IANA timezone and its provenance separately from API region and extraction timestamp. Inspect the relevant performance-view setting when available. An offset such as UTC-5 is insufficient to identify a DST-aware region. If sources conflict, resolve the ambiguity with the user; do not guess from computer location.

Resolve relative language into explicit local dates and state the interpretation. For “since last Monday” use an established user convention; absent one, state an interpretation before calculating. The existing investigation convention is the most recent Monday strictly before today, including seven days earlier when today is Monday.

Convert local calendar boundaries with timezone-aware code, using half-open windows `[start,end)`. Freeze one as-of instant for the run and label the current date partial. A local day can be 23 or 25 hours; add calendar dates in the local timezone instead of assuming a fixed 24-hour UTC duration. Retain offset-aware timestamps for repeated fall-back hours. Use the aggregate query's supported `timeZone`; detail queries use explicit absolute bounds and their own model. Timestamp/alternate-time-dimension choices must match across comparisons.

For local wall times that can be ambiguous or nonexistent, require an explicit offset/fold rule or choose validated calendar boundaries. Python `zoneinfo` requires installed IANA timezone data; a Windows runtime may require the `tzdata` package. Do not silently fall back to the machine timezone.

Compare partial days only with equivalent elapsed windows or exclude them from headline deltas. Daily and intraday reconciliation must cover the same instants. Avoid assuming UTC days match the portal's local dates.

## Collection manifest

Keep per-run metadata next to immutable raw responses and request bodies. Include only fields relevant to the run:

- Organization alias/region and connector or SDK version; no secrets.
- Entity IDs/names/divisions, media/direction, timezone and timezone source.
- Exact UTC interval and local labels, as-of time, granularity and timestamp convention.
- Metric names/units, configuration provenance and comparison scope.
- Requests, job IDs, cursors/checkpoints, response status and correlation IDs when available.
- Availability watermark, rows/pages retrieved, known gaps, exclusions and completion status.

Use explicit states such as planned, submitted, completed, fully fetched and reconciled. They represent different guarantees. Keep sensitive response bodies out of public reports and exception logs.

## Paging and asynchronous jobs

Directory pagination, synchronous detail paging and asynchronous result cursors are different contracts. Verify the endpoint's termination conditions and limits. Do not use an aggregate response `limit` as if it were a page cursor. A successful capped query may require splitting scope or time to obtain all groups.

For an asynchronous detail extraction:

1. Check `/api/v2/analytics/conversations/details/jobs/availability` and document what the current response says is available. A finished computation does not guarantee the most recent interactions were available to it.
2. Submit the documented async query model; persist the job ID and request metadata without secrets.
3. Poll that existing job with bounded backoff until a documented terminal state. Respect deadline, failure and expiration states; do not create replacement jobs simply because polling timed out.
4. Fetch every result page using the returned cursor. Detect repeated cursors and preserve the last durable checkpoint.
5. Verify fetch completion, scope and coverage before publishing. Record any interval beyond the available watermark as provisional or deferred.

If job submission times out before an ID returns, the outcome is uncertain. Reconcile using connector/job-discovery capabilities when available. Otherwise disclose uncertainty and avoid unbounded duplicate submissions. A correlation ID is useful for support, not proof the request is safely idempotent.

Do not hardcode one lookback, retention window, maximum interval, job lifetime, page limit or rate limit for every API family. Verify current documentation and applicable organization settings. Data absent outside a retention window is not zero activity.

## Retries and query size

Start conservatively, for example with two concurrent analytics queries; increase only with evidence that the tenant and endpoint permit it. Honor `Retry-After` on 429s, supporting either a delay or HTTP date when returned. Use bounded exponential backoff with jitter for transient network/5xx failures; three retries is a useful starting budget, not a platform guarantee. Coordinate with SDK retry behavior.

Do not retry invalid-schema 400s or permission 403s unchanged. For 401, renew once when expiry is the reason. Reduce interval, dimensions or selected-entity batch on query-size errors. Preserve successful partitions and explicit gaps. Split at nonoverlapping absolute bounds with consistent metric semantics; deduplicate overlapping detail results where the API's interval selection returns the same conversation more than once.

## Incremental data and storage

Use a watermark based on verified data availability rather than just wall-clock now. Advance the durable checkpoint after all pages and storage commits succeed. Re-query a documented overlap to capture late-arriving metrics and updated conversations, then upsert at the actual grain. A conversation can change after it first appears; append-only conversationStart extraction can miss updates or completions.

Choose stable keys supported by the payload. Conversation ID is suitable for a current conversation snapshot; it is not a unique key for participants, sessions, segments or metric events. Segments may require a documented composite key or snapshot replacement. Preserve raw JSON and schema/version provenance so transformations can be corrected. Do not invent a segment ID that the payload does not provide.

Keep queue, user, flow and division mappings separately, preserving historical versions when needed. Current directory labels and current membership cannot retrospectively reconstruct historical state. Confirm retention, access and approved destination for the user's requested pipeline; do not upload raw tenant data to a new service implicitly.

## Reconcile against the portal

Select one queue-day-media slice and match IDs, timezone, dates, media/direction, filters, service-level configuration, timestamp convention and as-of timing. Record the portal view and export units. Compare primitive counts and duration sums before derived averages or rates.

Investigate differences in order: scope/filters → local/UTC boundaries and DST → metric definitions and event timing → permissions/divisions → pagination/caps → delayed data/open interactions → rounding/export transformation. Do not force equality by changing a formula without evidence. Daily and intraday totals should reconcile only where the metric is additive and the populations, coverage and semantics match.

Portal fallback is valid when APIs are inaccessible. Preserve export provenance and map columns explicitly. Missing denominators, sums or numerator counts remain unavailable; do not backfill invented sufficient statistics from rounded averages.
