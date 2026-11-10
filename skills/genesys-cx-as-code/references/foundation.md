<!-- Author: Andrey Sarafanov @ Miratech inc -->

# CX as Code foundation

The tested baseline is provider `MyPureCloud/genesyscloud` 1.87.0. Preserve an existing version unless an upgrade is needed. Pin a verified version and commit `.terraform.lock.hcl`. The official introduction's old illustrative pins are not current recommendations. [Introduction](https://developer.genesys.cloud/devapps/cx-as-code/), [releases](https://github.com/MyPureCloud/terraform-provider-genesyscloud/releases).

Authenticate with a Client Credentials OAuth client having the relevant roles/division access. Supply `GENESYSCLOUD_OAUTHCLIENT_ID`, `GENESYSCLOUD_OAUTHCLIENT_SECRET`, and `GENESYSCLOUD_REGION` through the environment/secret store. Before deployment, compare a verified read-only organization-identity result to the intended target. Do not print credentials.

In 1.87.0, flow `filepath` points to YAML, `substitutions` is a string map, `file_content_hash` is computed, and `update_trigger_hash` can express extra update dependencies. Old examples assigning `file_content_hash` fail with this schema. A name change can create a new flow ID while the old flow persists. `force_unlock` can first publish another editor's draft; `create_stubs` creates missing dependencies. [Pinned flow schema](https://github.com/MyPureCloud/terraform-provider-genesyscloud/blob/v1.87.0/docs/resources/flow.md).

YAML names alone do not establish Terraform dependencies. Use substitutions backed by resource/data-source outputs, or a justified `depends_on`. Parameterize destination divisions and names. Resolve destination IDs rather than carrying source-org GUIDs across organizations.

Export narrowly in a separate directory with `genesyscloud_tf_export`: filters, dependency resolution, HCL output, data-source replacement, and optional state export are available. Select the modern Architect exporter for YAML. Inspect permission warnings and unresolved references. Exported state belongs to its source org; flow version numbers may change on import. Exports do not preserve every secret, history, or function binary. Retain a function's source/deployment artifact separately. [Pinned export guide](https://github.com/MyPureCloud/terraform-provider-genesyscloud/blob/v1.87.0/docs/guides/export.md).

Use distinct backend/state identities and credentials for development and production, preferably separate roots sharing modules. Local state is a learning convenience; team use needs suitable locking storage. Backend reconfiguration is different from state migration: do not silently migrate dev state into production. Generate a destination-specific plan after identity/backend checks, inspect publication/activation/replacements/removals, and apply only to the authorized target. A Git revert does not undo messages, purchases, external transactions, or new GUIDs.
