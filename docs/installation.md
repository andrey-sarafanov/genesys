# Installation

[← Documentation](README.md) · [Repository home](../README.md)

## Choose a method

| Method | Best when |
|---|---|
| **Local installer** | You want to inspect the clone, choose a destination and preview changes |
| **Codex skill installer** | You want your agent to install one folder directly from GitHub |
| **Manual copy / ZIP** | You want full control or do not have Git |

## Local installer: recommended for a fresh clone

Requires Python 3.10+ and Git. The installer itself has no third-party Python dependencies and makes no network requests.

```sh
git clone https://github.com/andrey-sarafanov/genesys.git
cd genesys
python install.py --list
python install.py --dry-run
python install.py
```

`--list` shows all skills, file counts and helper paths. `--dry-run` checks the source and destination without creating files. Without `--skill`, installation selects all three skills.

Select one or several:

```sh
python install.py --skill genesys-reporting
python install.py --skill genesys-reporting --skill genesys-performance-investigator
```

Change the destination:

```sh
python install.py --dest /path/to/your/skills
```

The default is `~/.agents/skills`, the current documented user discovery directory. Clients or older installers may use another configured path, including `~/.codex/skills`; use an explicit `--dest` for that environment. Installing the same named skill in several discovered directories can produce duplicates. Consult [official skill discovery guidance](https://learn.chatgpt.com/docs/build-skills).

## Install from Codex

Paste **one** request into Codex:

```text
Use $skill-installer to install:
https://github.com/andrey-sarafanov/genesys/tree/main/skills/genesys-reporting
```

```text
Use $skill-installer to install:
https://github.com/andrey-sarafanov/genesys/tree/main/skills/genesys-cx-as-code
```

```text
Use $skill-installer to install:
https://github.com/andrey-sarafanov/genesys/tree/main/skills/genesys-performance-investigator
```

These links target actual `SKILL.md` directories. Use the directory link, not an HTML guide or ZIP URL, for repository-path installation. The built-in installer's destination and existing-folder behavior depend on the version your client supplies.

## Manual installation

1. Download the repository or the desired skill ZIP from the repository home.
2. Keep the complete folder containing `SKILL.md`, `agents/`, `references/`, and any `scripts/` or `assets/`.
3. Copy that skill folder into your configured skills directory. Do not flatten its contents or copy only `SKILL.md`.
4. Invoke the skill by name. If it does not appear after discovery, reopen the client.

Example target layout:

```text
~/.agents/skills/
  genesys-reporting/
    SKILL.md
    agents/openai.yaml
    references/...
```

## Verify the result

Confirm `<destination>/<skill-name>/SKILL.md` exists. Then ask your agent:

```text
Use $genesys-reporting to explain how you would choose between conversation aggregates and details. Do not access a tenant.
```

This validates discovery without credentials. A live API task still needs the right region, OAuth identity, roles and divisions. Flow publication requires an authorized deployment scope.

## Updates and existing installations

The local installer refuses to overwrite an existing skill folder. Before updating, review local edits and keep a backup outside the discovered skills directory. Install to a separate review directory with `--dest`, compare, then replace the intended copy yourself. Do not rerun an installer against a populated destination expecting an automatic merge.

## Runtime prerequisites

| Skill | Prerequisites for its helpers |
|---|---|
| Reporting | Instruction/reference skill; API implementation dependencies depend on your chosen SDK/client |
| CX as Code | Python; PyYAML for validation; pinned Terraform/provider for Terraform checks; channel integrations for live tests |
| Performance Investigator | Python 3.10+ and IANA timezone data; Windows may need `tzdata`; Node only for optional UI logic checks |

Installing a skill does not install these runtimes or authenticate it to Genesys.

## Troubleshooting

### Clone failed

Check `git --version`, network/proxy access and the repository URL. This repository is public. A managed environment may require network approval even for a public clone. Use GitHub's **Code → Download ZIP** if Git is unavailable. A screenshot saying only “Failed” does not establish the underlying cause; retain the actual command error for diagnosis.

### Python not found

On Windows, try `py -3`; on macOS/Linux, try `python3`. Run the same installer arguments with the available Python 3.10+ interpreter.

### Already exists

No skill is overwritten. Choose a clean review destination with `--dest`, or back up and review the existing installation first.

### Skill does not appear

Check the destination is actually searched by your client and that the skill folder contains `SKILL.md`. Avoid an extra nested `skills/skills/` level. Reopen the client if discovery has not refreshed.

### Helper fails after installation

Read the specific skill guide's prerequisites and run the helper's `--help`. Installing instructions is separate from installing Python packages, Terraform, timezone data and live integrations.
