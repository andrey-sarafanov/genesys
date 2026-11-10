# Metrics and interpretation

## Grain, units and pooling

Retain metric name, group dimensions, interval, statistics and configuration provenance. Raw analytics duration statistics are generally milliseconds; verify the source and convert once. Portal exports may already be seconds or formatted durations. A metric omitted from a sparse response is not automatically zero.

For disjoint compatible slices, pool additive numerators and denominators first. Do not average averages or percentages. Rows missing required sufficient statistics cannot silently drop out of a pooled measure. A zero denominator is N/A, not 0%. Never sum daily and intraday results, base data and drilldowns, or overlapping partitions.

| Measure | Working definition |
|---|---|
| Offered | `nOffered.count`; queue offers, not distinct callers |
| Answered | `tAnswered.count`; do not replace with connected or handled |
| Abandoned | `tAbandon.count`, with channel-specific semantics |
| Handled | `tHandle.count`; its event timing and population differ from answered |
| ASA in seconds | sum of `tAnswered.sum` / sum of `tAnswered.count` / 1000 |
| AHT in seconds | sum of `tHandle.sum` / sum of `tHandle.count` / 1000 |
| Average wait/abandon | own duration sum / own count / 1000 |
| Talk/hold/ACW averages | own `tTalkComplete`, `tHeldComplete`, `tAcw` sum / own count / 1000 |
| Short abandons | `tShortAbandon.count`; obtain the configured threshold |
| Transfers | `nTransferred.count`; declare a denominator for any rate |
| Service level | `oServiceLevel`; preserve returned sufficient statistics and configuration |
| Flow execution volume | verified `nFlow.count`; not unique customers |
| Average flow duration | `tFlow.sum` / `tFlow.count` / 1000 |

Worked weighting: one bucket has 10 handles totaling 100 seconds; another has 90 totaling 1,800 seconds. Pooled AHT is 1,900/100 = 19 seconds, rather than the unweighted 15 seconds. A ratio-only export cannot recover an exact pooled rate without its denominator.

Talk, hold and ACW metrics may have different observation populations and boundaries; their averages need not sum to AHT. Counts from event metrics often use `stats.count`; do not assume `sum` is an event count or that a metric prefix is a full semantic specification. Preserve actual response statistics.

## Service level

Use the API's service-level metric and returned numerator/denominator when available. Confirm response shape and scale before calculating or displaying percentages. Pool sufficient statistics only when threshold and inclusion settings are comparable. If only ratios are available, report the scope-specific ratios or mark pooling unavailable.

Service-level configuration can include/exclude abandons, short abandons and flow-outs, with channel/callback-specific options. Read the relevant organization/queue configuration and reporting-view definition. If unavailable, disclose it; do not substitute a universal formula. Configuration changes can invalidate historical comparisons, and today's setting does not establish last month's setting.

Source for configuration dependence: [Queues Activity Detail view](https://help.genesys.cloud/?p=185887). This documentation changes as callback behavior evolves; recheck before implementing callback SL.

## Attribution and channel differences

A conversation can traverse several queues, agents, media legs and flows. Adding queue offers measures workload, not deduplicated people or journeys. Answered, offered and handled events can fall in different buckets. Short-interval answered/offered ratios are event ratios rather than same-cohort conversion probabilities; a ratio above 100% can reflect timing rather than a bug.

Callbacks must be separated from voice legs. Customer-first and agent-first lifecycles can attribute events differently. Offered/answered/SL alone do not establish reach, bridge success or customer waiting experience; inspect the relevant lifecycle details. Web messaging, email and asynchronous channels do not inherit voice abandon and duration assumptions. Open/reopened interactions and concurrency affect interpretation.

Define both numerator and population before transfer rate, repeat-contact rate, first-contact resolution, containment, deflection or self-service success. Linked repeat contact needs an explicit identity rule and follow-up horizon. A disconnect is not proof of successful containment; a flow outcome is evidence of its instrumented definition, not an assumed business result. Multiple outcomes per execution are not mutually exclusive.

## Agent and workforce reporting

Presence, routing status, on-queue time, utilization, handling work, schedules, adherence and paid staffing are different concepts. Current presence or queue membership cannot establish historical staffing. Use historical user state/detail or the appropriate workforce dataset for the interval, including state definitions, effective membership and reporting eligibility.

Before computing occupancy/utilization, state the exact numerator and eligible-time denominator, media treatment and concurrency model. Adding overlapping digital handle durations can exceed wall-clock time. Do not divide queue handle time by an assumed headcount or treat offered volume as agent productivity. Queue-level SL cannot establish an individual agent's performance.

## Trend reasoning

Separate demand, effective capacity, workload, mix, routing and measurement changes. Compare the same local hours, operating calendar, media and definitions. Show absolute volume changes and rate changes in percentage points. Percentage change needs a nonzero baseline. Segment mix can worsen an overall KPI even when each segment improves.

A few days support descriptive findings, not established seasonality or causality. Do not invent targets, confidence intervals or significance from incomplete observations. Distinguish low volume, no returned rows, confirmed zero, unavailable metrics and permission-filtered data.

Definition references: [performance columns](https://help.genesys.cloud/articles/view-available-columns-in-performance-views-by-category/), [reporting FAQs](https://help.genesys.cloud/faqs/category/reports/), [Flow Outcomes Summary](https://help.genesys.cloud/articles/flow-outcomes-summary-view/).
