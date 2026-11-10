# Metric and interpretation contract

Durations in raw aggregates are milliseconds. Convert once to seconds. Missing is not zero; a zero denominator is N/A. Missing sufficient statistics invalidate a pooled measure rather than silently shrinking its population.

| Measure | Calculation / interpretation |
|---|---|
| Offered | `nOffered.count`; queue offers, not distinct callers |
| Answered | `tAnswered.count`, not `nConnected` |
| Abandoned | `tAbandon.count`; do not impose voice semantics on web messaging |
| Handled | `tHandle.count`; differs from answered |
| ASA | sum `tAnswered.sum` / sum `tAnswered.count` / 1000 |
| AHT | sum `tHandle.sum` / sum `tHandle.count` / 1000 |
| Average wait/abandon time | respective `tWait` / `tAbandon` sum divided by its own count / 1000 |
| Talk/hold/ACW averages | respective `tTalkComplete`, `tHeldComplete`, `tAcw` sum / own count / 1000; different populations mean averages need not sum to AHT |
| Answer/abandon ratio | respective event count / offered; short-bucket event ratios are not same-cohort conversion rates |
| Service level | `oServiceLevel`; pool numerator/denominator, never average percentages. Ratio-only rows cannot establish pooled SL |
| Short abandons | `tShortAbandon.count` when returned; source the configured threshold |
| Transfers | `nTransferred.count`; document denominator for any rate |
| Flow volume/duration | verified count metric (starter `nFlow.count`), and `tFlow.sum / tFlow.count / 1000`; executions, not unique customers |
| Outcomes | retain ID/value; define eligible attempts before success rate. Multiple outcomes/versions/milestones are not additive total flow volume |

Combine only disjoint rows with matching semantics, filters, granularity and timestamp convention. Never add daily and intraday queries. Selected-queue totals are workload, not deduplicated contacts: transfers/requeues and repeated flow visits count again. Do not invent a customer funnel by joining independent aggregates.

Callback aggregates are separate. Customer-first callback results may book on voice legs; callback offered/answered/abandoned/SL do not measure reach/bridge success. Use validated callback details and availability for outcomes. For message/email, use applicable metrics only. Missing abandon does not mean success. Queue metrics cannot establish agent occupancy, concurrency, productivity or historical staffing.

## Investigation

1. Check coverage, open interactions, provisional data, missing buckets, permissions and detail watermarks. Sparse results do not establish zero activity without verified omission semantics.
2. Describe each entity/media separately. Show absolute volume change and percentage-point rate change; percentage change needs nonzero baseline.
3. Find PT30M intervals driving daily differences. Compare like hours and operating calendars. Keep partial dates and DST offsets visible.
4. Separate demand, effective capacity, handling workload, contact mix, transfers/routing and measurement changes. A weighted aggregate can worsen purely because mix changed.
5. Test competing explanations with narrow additional evidence. A few days are descriptive variation, not established seasonality. Do not invent significance, control limits or business targets. SL configuration changes can invalidate comparisons.

| Observed pattern | Candidate explanation | Needed evidence / alternative |
|---|---|---|
| Volume and delay rise | Demand pressure | Same-hour baseline and staffing; handling workload could also rise |
| Stable volume, delay worsens | Capacity or routing reach | Historical routing statuses, staffing, eligibility and schedules; arrivals may have shifted within the day |
| AHT rise concentrated in ACW | Workflow change | Wrap-up/contact mix and process history; complexity is an alternative |
| One queue grows, another shrinks | Routing/transfer shift | Flow changes and linked transfer evidence; independent demand is possible |
| Flow disconnects rise, queue offers fall | Journey/technical change | Exit reason, outcome, flow version and technical evidence; successful self-service is also possible |
| Outcome success drops after new version | Regression or audience change | Matched version/intent cohorts and outcome instrumentation |

Disconnect is not proof of containment. Self-service success requires an explicit business outcome, eligible population and any follow-up horizon. In their absence, report unavailable. Label findings with observation, hypothesis, confidence, alternatives, next test, owner and exact evidence references.
