<!-- Author: Andrey Sarafanov @ Miratech inc -->

# Verification and release

The helper checks manifest/YAML structure; it does not implement the entire Architect grammar. With initialized Terraform, it adds formatting/schema validation against the pinned provider. Test any runtime service with appropriate application tests too.

For stronger offline YAML validation, use current Archy JSON schemas/editor tooling. Confirm commands with `archy --help` and per-command help; do not assume `archy validate` exists or that `archy create` is read-only. [Commands](https://developer.genesys.cloud/devapps/archy/commandOverview), [schema refresh](https://developer.genesys.cloud/devapps/archy/commandRefresh).

Check substitutions, startup/cross-flow references, resource lookups, unexplained source-org GUIDs, and requested behavior. Capture licensing/integration dependencies. Before an authorized development apply, verify org/region, permissions/divisions, and backend. Inspect the plan; flow apply publishes and may immediately change routed traffic. Read back IDs, versions/status, dependencies, and channel mappings; inspect Architect.

Exercise every channel: success, handoff, no-input/no-match, invalid input, hours where applicable, backend failure, and channel-specific cases. Record actual results, environment, and evidence such as redacted transcripts/conversation IDs/readbacks. Do not record unperformed tests as passed.

`--readiness` checks for missing implementation/setup/scenario evidence but cannot judge whether that evidence is true. Use it after real tests, not as independent runtime certification.

For production, build a destination-specific plan and retain prior code/YAML, state/version references, and route mappings. Rollback restores/re-publishes a known-good flow and mappings, followed by entry-point tests. Reverting Git alone does not recover GUIDs or reverse external side effects. [Publication behavior](https://help.genesys.cloud/articles/publish-an-architect-flow/).
