<!-- Author: Andrey Sarafanov @ Miratech inc -->

# Web messaging

Use `inboundShortMessage` with the chosen bot and fallback/handoff. Web Messaging is assigned through Messenger deployment; legacy inbound chat has a different flow type. [Get started](https://help.genesys.cloud/229418/), [call a digital bot](https://help.genesys.cloud/articles/add-an-inbound-message-flow-that-calls-a-digital-bot-flow/).

Create/reference `genesyscloud_webdeployments_configuration` and `genesyscloud_webdeployments_deployment`. Bind configuration ID, its published version, and `flow_id`. Configure languages, launcher, domain allowlist, session behavior, and appearance. Use the generated `snippet`, not a guessed region CDN URL. Keep deployment inactive until activation belongs to the release. [Pinned configuration](https://github.com/MyPureCloud/terraform-provider-genesyscloud/blob/v1.87.0/docs/resources/webdeployments_configuration.md), [deployment](https://github.com/MyPureCloud/terraform-provider-genesyscloud/blob/v1.87.0/docs/resources/webdeployments_deployment.md).

Add the snippet to the requested website/test page; use supported Messenger SDK operations for custom behavior. Never embed provider OAuth credentials in browser code. Use a supported auth integration for verified identity; contact attributes alone do not authenticate customers.

Test domain restrictions, reload/resume, language selection, attachments, replies, bot escalation, queue handoff, and agent replies. Keep plain-text alternatives for bots shared with SMS. Architect's bot test does not prove website/deployment routing.
