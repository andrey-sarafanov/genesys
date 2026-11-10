<!-- Author: Andrey Sarafanov @ Miratech inc -->

# Bots and backend integration

For each intent, implement utterances, slots, validation, confirmation, business action, outcome, handoff attributes, and failure handling. A digital menu satisfies a menu request; it does not constitute a trained conversational intent bot. Keep return contracts consistent with the calling flow.

For a conversational prototype with no engine specified, the bundled native intent/slot seed can serve voice, Web Messaging, SMS, and WhatsApp through Call Bot Flow; use the corresponding native engine options. The digital seed demonstrates a menu. A selected Digital Bot Flow that needs intent/slot collection requires authoring those actions against its current schema or export; do not copy voice-specific fields into a digital flow or present the menu as equivalent.

Native `botFlow` and `digitalBot` settings/actions differ. Use current Architect/Archy schemas or a fresh export. Implement no-input/no-match, correction, retries, exit, escalation, and timeout behavior. Transfer in the bot where supported or in the caller; inspect actual failure/exit outputs before wiring them. [Archy schemas](https://developer.genesys.cloud/devapps/archy/commandRefresh), [substitutions](https://developer.genesys.cloud/devapps/archy/flowAuthoring/lesson_07_substitutions).

Use supported integrations/data actions for business APIs. Define request/response contracts and timeouts. Mock locally; test auth, bad responses, missing records, permission failures, rate limits, and retries in development. Do not retry non-idempotent operations without an idempotency key or verified outcome. [Pinned data actions](https://github.com/MyPureCloud/terraform-provider-genesyscloud/blob/v1.87.0/docs/resources/integration_action.md).

For a selected external engine, version/deploy its bot or runtime separately from the Genesys connector, and map its intent/entity/session/escalation contract. Connector provisioning does not train the third-party bot. Verify transport/signatures. [Supported message actions](https://help.genesys.cloud/articles/inbound-message-flows/).

For requested generative behavior, use the chosen runtime, permitted knowledge, business-tool boundaries, fallbacks, and evaluation conversations. Keep Codex authoring separate from runtime. A generated statement cannot prove a business action succeeded.

Reuse business/intent contracts across channels, while keeping speech, presentation, rich-content limits, session timing, and outbound constraints specific to each channel. Test each independently.
