# Authentication and access

## Select region and identity

Confirm the organization region from its known sign-in URL, connected configuration or administrator-provided region. Select the matching official SDK region host before constructing the API client. Login and API hosts must belong to that environment. Never infer region from user geography, or reporting timezone from region. Example commercial hosts `login.mypurecloud.com` and `api.mypurecloud.com` are US East examples, not global defaults. Check current mappings for newer regions and sovereign environments.

Choose client credentials for a service acting as itself; choose authorization code with PKCE for a user-facing application acting with user context. Public clients cannot keep a client secret. Preserve the organization's approved SSO/delegated flow when one exists. Do not design new integrations around legacy implicit grants. Confirm currently supported grant configuration and token behavior from the OAuth client documentation.

Client credentials obtain application authority from assigned roles and divisions, with no human user context. An endpoint requiring a logged-in user can reject that grant even when permissions look sufficient. Do not use `/users/me` as a universal authentication probe. Test a narrow read appropriate to the actual reporting task.

## OAuth wire contract

For client credentials, POST to the confirmed regional login host at `/oauth/token` over HTTPS. Send `Content-Type: application/x-www-form-urlencoded`, HTTP Basic authentication using client ID and secret, and body `grant_type=client_credentials`. Basic encoding is not encryption. Read `access_token`, `token_type` and `expires_in`; retain the token only in the protected runtime and renew shortly before expiration. Client credentials acquire a new token with the same grant, rather than assuming a refresh token.

Platform API requests use `Authorization: Bearer <runtime-token>` and JSON payloads where the endpoint expects JSON. Do not send a JSON object in place of the token endpoint's form body. Do not send client secrets to an API resource endpoint or place tokens in URLs.

For authorization code/PKCE, validate state, bind verifier/challenge correctly, use the exact registered redirect URI, and exchange the code at the correct regional token endpoint. Consult the current grant guide for refresh and revocation support. Never automate password entry as a replacement for OAuth.

## Official Python SDK pattern

Illustrative setup, not executed during skill creation. Dependency: an approved, pinned `PureCloudPlatformClientV2` version. The named environment variables are runtime bindings; their values must not be printed.

```python
import os
import PureCloudPlatformClientV2 as gc

# Example only: replace with the confirmed organization region.
region = gc.PureCloudRegionHosts.us_east_1
gc.configuration.host = region.get_api_host()
client = gc.api_client.ApiClient().get_client_credentials_token(
    os.environ["GENESYS_CLOUD_CLIENT_ID"],
    os.environ["GENESYS_CLOUD_CLIENT_SECRET"],
)
analytics = gc.AnalyticsApi(client)
# Build the endpoint's typed query model before calling it.
# Keep HTTP debugging disabled where headers/bodies could contain secrets or PII.
```

Pass the authenticated client to each API class. Do not construct a second unauthenticated client accidentally. Review SDK serialization and automatic token/retry behavior for the installed version before adding duplicate renewal/retry logic. Do not assume a raw dictionary is accepted by a typed SDK method; populate its documented model or use an explicitly supported REST client.

## Permission model

Authentication proves identity; access also depends on grant compatibility, endpoint permissions, applicable scopes, role/division grants, licensing and data visibility. OAuth scopes and platform role permissions are different controls. Do not invent scope names from permission names or solve a 403 by assigning blanket administrator access.

Starting permission examples, to verify against the selected endpoint:

| Need | Typical platform permission |
|---|---|
| Conversation aggregates | `analytics:conversationAggregate:view` |
| Conversation details | `analytics:conversationDetail:view` |
| Flow aggregates | `analytics:flowAggregate:view` |
| User aggregates | `analytics:userAggregate:view` |
| User details | `analytics:userDetail:view` |
| Queue metadata | `routing:queue:view` |
| Architect flow metadata | `architect:flow:view` |

Some endpoints offer alternative permissions with different visibility, such as agent-specific conversation details. Inspect the endpoint's ANY/ALL requirements. Portal views can need additional permissions beyond the API query. Match the requested divisions; a successful response can still omit inaccessible entities.

For authorized OAuth setup, define the grant, region, minimum roles/divisions, redirect URIs and runtime secret destination concretely before creation. Grant role/division changes through the approved administrator process. Do not embed an organization's client ID, secret or token in this reusable skill.

## Diagnose the failed layer

- Token 400/401: verify form encoding, client type, client authentication, region and configured grant. Avoid logging the request's Authorization header.
- API 401: check expiry, bearer format, region and which client actually made the call. Reacquire once when justified; stop repeated failures.
- API 403: check exact permissions, divisions, scope, grant/user-context compatibility and any configured IP restrictions. A different token does not fix missing grants.
- Empty data: confirm entity IDs, interval, filters and division visibility before concluding there is no activity.

Official references: [OAuth client setup](https://help.genesys.cloud/articles/create-an-oauth-client/), [client credentials guide](https://developer.genesys.cloud/authorization/platform-auth/use-client-credentials), [SDK authentication and regions](https://github.com/MyPureCloud/platform-client-sdk-python/blob/master/README.md), [SDK token implementation](https://github.com/MyPureCloud/platform-client-sdk-python/blob/master/build/PureCloudPlatformClientV2/api_client.py).
