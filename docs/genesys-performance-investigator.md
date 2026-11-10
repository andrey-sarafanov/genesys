# Performance Investigator

[← Documentation](README.md) · [Install](installation.md) · [Skill instructions](../skills/genesys-performance-investigator/SKILL.md)

## What it does

Use this skill to investigate selected Genesys Cloud queues and/or IVR flows. It preserves reporting scope and timezone provenance, collects daily and intraday evidence, computes weighted metrics and creates a self-contained HTML report.

## Install

```sh
python install.py --skill genesys-performance-investigator --dry-run
python install.py --skill genesys-performance-investigator
```

Repository folder for `$skill-installer`:

https://github.com/andrey-sarafanov/genesys/tree/main/skills/genesys-performance-investigator

## Example request

```text
Use $genesys-performance-investigator to investigate these selected queues
since last Monday. Discover the reporting-view timezone, separate media,
show the 30-minute intervals driving the daily change, and distinguish
observations from hypotheses. Build an offline HTML report.
```

Flow-only requests are valid. Do not substitute a tenant-wide scan for missing selected IDs.

## Helpers

From the repository clone:

```sh
python skills/genesys-performance-investigator/scripts/genesys_report.py --help
python skills/genesys-performance-investigator/scripts/genesys_report.py plan --help
python skills/genesys-performance-investigator/scripts/genesys_report.py build --help
```

After installation, use the same paths relative to the installed skill folder. The planner and builder require Python 3.10+ and IANA timezone data. They use the standard library, do not authenticate, and do not collect data from Genesys. Acquisition uses a separately authorized connection.

The `plan` command emits candidate requests. The `build` command consumes raw aggregate evidence and a manifest. Preserve daily, intraday, baseline and outcome/version data as separate datasets.

## Read the contracts

- [Collection](../skills/genesys-performance-investigator/references/collection.md): selection, requests, pagination and acquisition.
- [Analysis](../skills/genesys-performance-investigator/references/analysis.md): weighted measures, attribution and hypotheses.
- [Report contract](../skills/genesys-performance-investigator/references/report-contract.md): manifest examples, coverage states and accepted raw envelopes.
- [Research](../skills/genesys-performance-investigator/references/research.md): pinned API/server audit and licensing limitations.
- [API snapshot](../skills/genesys-performance-investigator/references/api-contract.json): historical checked schema, not a current tenant guarantee.

## Report limits

A finished job does not prove complete retrieval. Missing metrics remain unavailable. Do not pool percentages without sufficient statistics or infer successful self-service from a disconnect. Queue totals describe workload, not deduplicated people or individual-agent productivity.

For live work, reconcile a representative portal/API slice and exercise the generated report's controls. Synthetic fixtures must retain their visible demo banner.

[Detailed offline HTML](../genesys-performance-investigator.html) · [Portable ZIP](../genesys-performance-investigator.zip)
