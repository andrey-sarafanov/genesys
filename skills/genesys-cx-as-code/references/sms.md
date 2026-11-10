<!-- Author: Andrey Sarafanov @ Miratech inc -->

# SMS applications

Use a provisioned number or supported BYO SMS integration, Message Routing, and an `inboundShortMessage` flow with a supported bot/queue. Messenger deployment is for Web Messaging. [Message Routing](https://help.genesys.cloud/articles/about-message-routing/), [SMS overview](https://help.genesys.cloud/articles/about-sms-messaging/).

`genesyscloud_routing_sms_address` represents a postal address, not an SMS number or a flow binding. Check pinned provider coverage for numbers and route attachment. If absent, implement a verified API/SDK operation or documented admin action, retaining address/flow IDs, prior mapping, and readback. Do not invent `genesyscloud_routing_message_route`. [Postal-address schema](https://github.com/MyPureCloud/terraform-provider-genesyscloud/blob/v1.87.0/docs/resources/routing_sms_address.md), [attach route](https://help.genesys.cloud/152364/).

Design for plain text, typos, numeric/keyword choices, delayed replies, duplicates, threading, and short messages. Adapt digital quick-reply sample menus to supported SMS input rather than assuming buttons exist. For outbound requests, choose the verified agentless API or messaging campaign as appropriate; implement applicable sender, opt-in/opt-out rules and designated test recipients. Recheck current regional/channel requirements.

Test Unicode/segmentation, STOP, delayed replies, delivery failure, duplicates, fallback, and agent replies. Add a custom backend only for runtime needs native flows cannot meet; use server-side secrets, verified webhook authentication, and idempotency for business side effects.
