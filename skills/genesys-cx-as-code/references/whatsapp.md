<!-- Author: Andrey Sarafanov @ Miratech inc -->

# WhatsApp flows and bots

Reference an existing business integration or use authorized Genesys Embedded Signup, then attach its address to `inboundShortMessage` through Message Routing. Meta onboarding/number verification is separate from bot YAML. Keep interactive account-owner steps with the authorized owner. [Embedded Signup](https://help.genesys.cloud/articles/whatsapp-embedded-signup-self-service-onboarding-overview/), [ACD setup](https://help.genesys.cloud/?p=403970).

Provider 1.87.0 exposes `genesyscloud_conversations_messaging_integrations_whatsapp`: creation requires `name` and `embedded_signup_access_token`; optional `activate_whatsapp` holds `phone_number` and `pin`. The resource does not attach an inbound message route. Use its data source for an existing integration instead of recreating it to build a bot. Treat tokens/PINs as secrets; sensitive variables hide presentation but not state storage. [Pinned schema](https://github.com/MyPureCloud/terraform-provider-genesyscloud/blob/v1.87.0/docs/resources/conversations_messaging_integrations_whatsapp.md).

Use native/digital/external bots with channel-supported messages and text fallback. Recheck current service-window, opt-in, and template requirements for proactive/out-of-window messages. Do not assume Messenger widgets or unrestricted free-form outbound text work here. [Template use](https://help.genesys.cloud/articles/use-a-whatsapp-template-message/), [template setup](https://help.genesys.cloud/?p=220588).

Test inbound routing, media/menus, languages, template/parameter matching, expired-window handling, errors, escalation, and agent replies with an authorized test account. Deliver pending Meta approvals as concrete setup steps, not a claimed completed deployment.
