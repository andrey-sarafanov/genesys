---
name: genesys-cx-as-code
description: Build, modify, troubleshoot, and validate Genesys Cloud IVR, voicebot, web messaging, SMS, and WhatsApp flows and bots using CX as Code, Terraform, and Architect flow YAML. Use for Genesys conversation applications and their channel integrations, including existing flow exports. Excludes Genesys reporting and non-Genesys chatbot projects.
---

<!-- Author: Andrey Sarafanov @ Miratech inc -->
# Build Genesys conversations with CX as Code

Turn the requested journey into working Architect YAML, Terraform configuration, channel wiring, and acceptance scenarios. Continue through implementation and available validation. A scaffold or a description of a flow is not a completed build.

## Select the implementation

Use Terraform for supported resources, Architect YAML for conversation logic, and application code only for required runtime services. The current provider publishes YAML through Architect jobs APIs; a separate Archy CLI installation is optional for authoring, exports, and schema tooling.

| Request | YAML flow roots | Channel wiring |
|---|---|---|
| IVR | `inboundCall`, optionally `inqueueCall` | `genesyscloud_architect_ivr`, numbers, hours, prompts, queues |
| Voicebot | `botFlow` called by `inboundCall` | Native or selected external engine, speech behavior, ACD fallback |
| Web messaging | `inboundShortMessage`, usually `digitalBot` | Messenger configuration/version, deployment, website snippet |
| SMS | `inboundShortMessage`, supported bot | Provisioned number, Message Routing; outbound API/campaign if requested |
| WhatsApp | `inboundShortMessage`, supported bot | WhatsApp integration, Message Routing, approved templates when required |

Read [foundation.md](references/foundation.md) for a new project, migration, or provider upgrade. Load only relevant channel references: [voice.md](references/voice.md), [webmessaging.md](references/webmessaging.md), [sms.md](references/sms.md), [whatsapp.md](references/whatsapp.md). For bots/backend calls, also read [bots.md](references/bots.md). Use [verification.md](references/verification.md) before delivery or deployment; [sources.md](references/sources.md) identifies authoritative sources.

## Establish the journey and target

Inspect repository instructions, lockfile, YAML exports, backend/state configuration, and supplied requirements. Identify entry points, languages, intents/menu choices, slots, API calls, hours, handoff, no-input/no-match behavior, and acceptance criteria. Keep unrelated tenant resources outside the build.

Use existing flow exports as the strongest starting point. Without exports, adapt the bundled seeds and consult current Architect schema/action documentation. Do not convert `digitalBot` into `botFlow` by renaming its root. Ask for missing information only when it materially changes design or prevents a required next step; continue independent implementation.

Preserve the requested bot engine. Codex authors the application; it is not automatically the runtime bot. Do not introduce OpenAI, Lex, Dialogflow, or another hosted service merely because the user asks to vibecode.

## Implement locally

The standard-library helper creates a new project with provider configuration, flow resources, entry wiring, a journey manifest, and scenario files:

```text
python scripts/scaffold.py --output <new-directory> --name support --channels ivr voicebot webmessaging sms whatsapp
```

Run from this skill directory or use absolute script paths. `--seed-dir` supplies replacements matching the generated manifest filenames; `--provider-version` changes the tested baseline. `--bot-engine whatsapp=native` (or digital, external, none on messaging channels) preserves a chosen engine; voicebot supports native/external. External mode creates an entry seed and records the connector/runtime work to implement, rather than silently replacing the engine. It refuses a nonempty destination, performs no network calls, and never applies Terraform. Its manifest starts with `implementation_complete: false`; complete the requested journey before changing that status.

The seeds demonstrate minimal menus/intent recognition and handoff. Implement the user's business logic, slots, messages, failures, and channel adaptations. Complete every requested channel. If the pinned provider lacks SMS/WhatsApp route attachment, implement a verified API/SDK operation or the documented admin action; missing Terraform coverage does not remove that channel from scope.

Consult the pinned provider docs and `terraform providers schema -json` before adding resources/fields. Use current API Explorer for operations outside provider coverage. Record versions used; the research baseline is not a permanent latest-version claim. Bind substitutions to Terraform resources/data sources or environment inputs, making ordering explicit. Create dependencies before calling flows and channel entry points. Use data sources for deliberately unmanaged resources; import only when taking management is requested.

For a missing provider operation, build a small helper from the verified request schema. Include target lookup, current-state comparison, bounded asynchronous-job polling, and readback. Reconcile uncertain outcomes before retrying mutations. Do not invent endpoints, payloads, commands, or resources.

## Validate and deliver

```text
python scripts/validate_project.py <project-directory>
python scripts/validate_project.py <project-directory> --terraform <terraform-executable>
```

Use the available Python interpreter; on Codex desktop, `load_workspace_dependencies` can locate a bundled interpreter when Python is absent from PATH. The local checker requires PyYAML (`python -m pip install PyYAML` for that interpreter if absent). It checks required flow files, YAML shape, startup references, duplicate reference IDs, substitutions, channels, and scenarios. The second command adds Terraform formatting/schema checks after `terraform init -backend=false`. Neither authenticates to Genesys or proves live conversation behavior. `--readiness` rejects missing implementation/setup/test evidence; it does not independently prove the evidence is true.

For an authorized development deployment, publish in the named org, inspect the flows in Architect, exercise each channel, and record outcomes. Parser and Terraform checks cannot certify Architect expressions, NLU training, permissions, integrations, or live routing. Finish the locally buildable application even when credentials/onboarding prevent connected tests, and identify exact pending connected steps without claiming they succeeded.

Deliver implemented files, a journey diagram when useful, environment inputs, commands, scoped test results, remaining setup, and rollback instructions. Distinguish local validation, development-org validation, and production readiness.

## Deployment boundaries

A skill/local build does not authorize flow publication, phone purchases, account onboarding, campaigns, or messages. Respect prior authorization for a named environment without asking again. When an external action is not authorized, first finish the reviewable implementation/plan, then request that specific authorization.

Applying `genesyscloud_flow` publishes. An update can immediately change a routed customer journey; a saved Terraform plan applies without another Terraform prompt. Check org, region, and backend before an authorized apply. Protect secrets, state, and plan files; keep OAuth secrets and WhatsApp tokens out of source/logs. Leave `force_unlock` and `create_stubs` false unless their actual effects are needed and authorized.
