<!-- Author: Andrey Sarafanov @ Miratech inc -->

# IVR and voicebots

Use `inboundCall` menus for DTMF and tasks for business logic. Bind E.164 numbers, hours/holiday flows, and schedules with `genesyscloud_architect_ivr`. Flow creation and number routing are separate resources; telephony availability is another prerequisite. [Pinned IVR schema](https://github.com/MyPureCloud/terraform-provider-genesyscloud/blob/v1.87.0/docs/resources/architect_ivr.md).

Implement requested choices, repeat/return paths, bounded retries, prompts/languages, hours, data-action failures, and useful agent handoff attributes. The bundled IVR seed only exits a menu; replace it with the requested behavior. For a voicebot, call a supported native or selected external bot action and handle its returned intent/slots, failures, and escalation.

Native voicebots use `botFlow`. The bundled intent seed adapts an official Genesys blueprint and collects intent before exiting; implement the requested business action and handoff in the bot or caller. Recognition followed by disconnection is not a completed service bot. [Official bot blueprint](https://github.com/GenesysCloudBlueprints/deploy-webmessaging-chatbot-with-lambda-blueprint), [Call Bot Flow](https://help.genesys.cloud/articles/call-bot-flow-action/).

Author representative utterances, entities, slots, validation/confirmation, and return values. Configure voice endpointing, barge-in, no-input timing, and reprompts. Use current schemas or exports rather than digital-menu fields. Test silence, noise, interruption, ambiguity, invalid/corrected slots, explicit agent requests, backend timeouts, and transfers over the actual telephony path.
