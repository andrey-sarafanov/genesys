# CX as Code

[← Documentation](README.md) · [Install](installation.md) · [Skill instructions](../skills/genesys-cx-as-code/SKILL.md)

## What it does

Use this skill to implement Genesys Cloud IVR, voicebots, Web Messaging, SMS and WhatsApp journeys with Terraform and Architect YAML. It covers dependencies, channel wiring, business API calls, verification and release effects.

## Install

```sh
python install.py --skill genesys-cx-as-code --dry-run
python install.py --skill genesys-cx-as-code
```

Repository folder for `$skill-installer`:

https://github.com/andrey-sarafanov/genesys/tree/main/skills/genesys-cx-as-code

## Example request

```text
Use $genesys-cx-as-code to implement an English/French support IVR with
billing and technical-support choices, holiday routing and agent handoff.
Start with this exported inboundCall flow. Prepare the local implementation
and development plan; do not deploy until the target scope is authorized.
```

## Helpers

The installed skill folder contains two Python helpers:

```sh
python skills/genesys-cx-as-code/scripts/scaffold.py --help
python skills/genesys-cx-as-code/scripts/validate_project.py --help
```

These paths run from the repository clone. After installing, run the helper at its path inside the installed skill folder.

`scaffold.py` creates a new local project and refuses a nonempty output directory. Adapt its seeds to the requested behavior. `validate_project.py` checks structure and optional initialized Terraform schema/formatting; it requires PyYAML. Neither helper applies Terraform.

## Read the channel notes

- [Foundation](../skills/genesys-cx-as-code/references/foundation.md): provider baseline, OAuth, state and dependency handling.
- [Voice](../skills/genesys-cx-as-code/references/voice.md): inbound IVR and voicebot behavior.
- [Web Messaging](../skills/genesys-cx-as-code/references/webmessaging.md): configuration, deployment and website entry point.
- [SMS](../skills/genesys-cx-as-code/references/sms.md) and [WhatsApp](../skills/genesys-cx-as-code/references/whatsapp.md): routing and channel constraints.
- [Bots and backend APIs](../skills/genesys-cx-as-code/references/bots.md): intents, slots, failure handling and contracts.
- [Verification](../skills/genesys-cx-as-code/references/verification.md): local/development/live evidence and rollback.
- [Sources](../skills/genesys-cx-as-code/references/sources.md): baseline dates and licensing.

## Important deployment behavior

Applying a flow resource publishes it and can change live traffic. Scaffolding is not a completed journey. A bot recognizing an intent is not proof its business action succeeded. Native, digital and external engines have different schemas and runtime requirements.

Keep Terraform state, secrets and plan files protected. Preserve the [bundled asset license notices](../skills/genesys-cx-as-code/assets/).

[Detailed offline HTML](../genesys-cx-as-code.html) · [Portable ZIP](../genesys-cx-as-code.zip)
