# Genesys skills · Miratech

Read the documentation, inspect the source, then install the skills you need.

**[Start here](docs/README.md)** · **[Install](docs/installation.md)** · **[Browse skill source](skills/)** · **[Troubleshooting](docs/installation.md#troubleshooting)**

## Choose a skill

| Skill | Use it for | Read the guide | Inspect instructions |
|---|---|---|---|
| **Genesys Reporting** | OAuth, Analytics APIs, metrics and extraction pipelines | [Documentation](docs/genesys-reporting.md) | [SKILL.md](skills/genesys-reporting/SKILL.md) |
| **CX as Code** | IVR, voicebots, Web Messaging, SMS and WhatsApp | [Documentation](docs/genesys-cx-as-code.md) | [SKILL.md](skills/genesys-cx-as-code/SKILL.md) |
| **Performance Investigator** | Selected queue/IVR investigations and offline reports | [Documentation](docs/genesys-performance-investigator.md) | [SKILL.md](skills/genesys-performance-investigator/SKILL.md) |

## Quick install

Requires Git and Python 3.10 or newer. Run these commands in your terminal:

```sh
git clone https://github.com/andrey-sarafanov/genesys.git
cd genesys
python install.py --list
python install.py --dry-run
python install.py
```

On Windows, use `py -3` if `python` is not available; on macOS/Linux, `python3` may be the command name. The installer copies all three skill folders to `~/.agents/skills`. It does not overwrite existing installations, run skill helpers or contact Genesys. Use `--skill` to select one skill and `--dest` for a different configured directory.

```sh
python install.py --skill genesys-reporting
```

Prefer asking your agent to install? Paste this into Codex:

```text
Use $skill-installer to install the skill from:
https://github.com/andrey-sarafanov/genesys/tree/main/skills/genesys-reporting
```

See [installation options](docs/installation.md) for all three links, manual installation, alternate directories and updates. Installation is separate from OAuth setup and live deployment.

## Read in GitHub or in a browser

The Markdown guides above render directly on GitHub. The detailed HTML versions retain Miratech branding, search, navigation, copyable examples and print styling:

- [HTML catalogue](catalog.html)
- [Reporting HTML](index.html)
- [CX as Code HTML](genesys-cx-as-code.html)
- [Performance Investigator HTML](genesys-performance-investigator.html)

GitHub shows HTML source in its file viewer. For the rendered version, clone/download the repository, then open `catalog.html` locally. No web server or build is needed. For the fastest reading experience inside GitHub, start with the Markdown documentation.

## Repository layout

```text
README.md                 Start here
install.py                List, preview and install local skills
skills/<skill>/           Complete, browsable skill source
  SKILL.md                Skill instructions and trigger description
  agents/                 UI metadata
  references/             Task-specific reference material
  scripts/                Helpers where supplied
  assets/                 Templates and license notices where supplied
docs/                     Reading guides and installation help
*.html                    Detailed offline HTML guides
*.zip                     Portable skill packages
skill-packages.json       Archive sizes and SHA-256 checksums
```

## Scope and licenses

These skills concern **Genesys Cloud**. Runtime prerequisites vary by task; see each guide. They do not include tenant credentials or customer data. Reading/installing does not authorize live queries, routing changes or flow publication.

Retain the notices in [CX as Code assets](skills/genesys-cx-as-code/assets/). Do not assume one blanket license applies to all third-party material. The optional server discussed in the Performance Investigator research has its own licensing; it is not bundled or required.

Skill source is the maintained, readable form. ZIPs are portable copies of those same folders. See [official OpenAI skill documentation](https://learn.chatgpt.com/docs/build-skills) for current discovery locations and client behavior.
