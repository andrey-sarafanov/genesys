# Source register and maintenance

Prepared 2026-11-06. This is reusable Genesys Cloud guidance, not an exhaustive catalogue of every licensed feature. No live organization was accessed and no credentials were discovered. Product/API behavior, limits and licensing can change; record current verification when executing a task.

## Primary sources

- [OAuth client configuration](https://help.genesys.cloud/articles/create-an-oauth-client/) — readable during authoring; grant choices, role/division setup and client configuration.
- [Official Python SDK README](https://github.com/MyPureCloud/platform-client-sdk-python/blob/master/README.md) — official runtime authentication and regional configuration examples; raw source readable during authoring. Installed SDK version remains the runtime contract.
- [Official API client source](https://github.com/MyPureCloud/platform-client-sdk-python/blob/master/build/PureCloudPlatformClientV2/api_client.py) — token request implementation, readable during authoring.
- [Official Analytics API reference](https://github.com/MyPureCloud/platform-client-sdk-python/blob/master/build/docs/AnalyticsApi.md) — raw source readable during authoring; paths, permissions, async job/status/results and availability operations.
- [Conversation aggregate query model](https://github.com/MyPureCloud/platform-client-sdk-python/blob/master/build/PureCloudPlatformClientV2/models/conversation_aggregation_query.py) and [detail query model](https://github.com/MyPureCloud/platform-client-sdk-python/blob/master/build/PureCloudPlatformClientV2/models/conversation_query.py) — raw source readable during authoring; separate filter/paging models and REST field mappings.
- [Flow aggregate query model](https://github.com/MyPureCloud/platform-client-sdk-python/blob/master/build/PureCloudPlatformClientV2/models/flow_aggregation_query.py) — maintained official model; verify current metric/dimension support separately.
- [API Explorer](https://developer.genesys.cloud/devapps/api-explorer) and [US East OpenAPI schema](https://api.mypurecloud.com/api/v2/docs/swagger) — runtime verification resources. The schema link is a documentation source, not this skill's selected tenant host. No fresh full-schema download was performed for this skill.
- [Client credentials](https://developer.genesys.cloud/authorization/platform-auth/use-client-credentials) — Developer Center returned a JavaScript shell during authoring; detailed authentication checks instead used readable official SDK/client sources.
- [Queues Activity Detail](https://help.genesys.cloud/?p=185887) — readable during authoring; configuration-dependent service level including callback options.
- [Performance columns](https://help.genesys.cloud/articles/view-available-columns-in-performance-views-by-category/), [reporting FAQs](https://help.genesys.cloud/faqs/category/reports/), [Flows Performance Summary](https://help.genesys.cloud/articles/flows-performance-summary-view/), [Flow Outcomes Summary](https://help.genesys.cloud/articles/flow-outcomes-summary-view/) — official metric/view references inherited from the existing reporting research; reread relevant current sections when needed. These were not all freshly retrieved during authoring.

## Existing local knowledge incorporated

The installed `genesys-performance-investigator` provided prior researched metric definitions, timezone/evidence contracts and collection patterns. Its 2026-10-15 schema research verified starter flow/conversation metrics and permissions. This new skill makes that guidance usable without requiring the older skill, its helper, or a particular MCP implementation.

The existing `genesys-cx-as-code` skill informed the reporting-versus-configuration boundary. Neither existing skill was modified. No upstream third-party server code or installer is bundled. Prior third-party server version/permission audits should not be treated as current API or tool contracts.

## Updating this skill

Recheck exact schemas and allowed metric/dimension combinations before changing request examples. Confirm examples against current official sources, then validate JSON and the time/filter logic locally. When possible reconcile a scoped live slice, explicitly recording its tenant access and completeness limits. Mark unavailable sources as unavailable instead of presenting a JavaScript shell, SDK free-form string or community post as detailed contract evidence.

Keep tenant-specific IDs, tokens, secrets, raw conversations, organization assumptions and temporary incident workarounds out of the reusable package. Put genuinely reusable lessons in the relevant reference, preserving concise routing in SKILL.md.
