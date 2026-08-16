# Environment Variables: Ownership, Build-Time, and Production Safety

Environment variables in a Coze Coding project must be classified by **ownership** and **exposure**, not copied wholesale between environments.

## 1. Four classes

### A. `platform_injected`

Runtime values owned/injected by Coze or the current managed integration.

Examples observed in Coze Coding environments include names such as:

- `COZE_PROJECT_ENV`
- `COZE_SUPABASE_URL`
- `COZE_SUPABASE_ANON_KEY`
- `COZE_SUPABASE_SERVICE_ROLE_KEY`
- `COZE_BUCKET_ENDPOINT_URL`
- `COZE_BUCKET_NAME`
- deployment/runtime port/domain variables

These names are environment-specific evidence, not permission to create them manually. If the platform reserves a prefix such as `COZE_`, do not instruct the user to create conflicting custom variables.

Rule: **inspect current runtime/UI/CLI first**. Use the production-injected value in production rather than copying the development value.

### B. `app_private`

Project-owned server-side secrets/configuration.

Examples:

- application encryption/hash pepper;
- third-party API secret;
- webhook verification secret;
- project-specific bootstrap token;
- private admin bootstrap password;
- internal signing key.

Create independent production values. Never expose to browser code.

### C. `client_public`

Values intentionally visible to browser JavaScript.

Examples:

- public application origin;
- public analytics ID;
- a deliberately public/anonymous SDK key if the architecture and access policies allow it.

`NEXT_PUBLIC_*` in Next.js belongs here. The prefix does **not** make a secret safe; it makes the value browser-visible.

### D. `local_only`

Developer-machine or sandbox convenience.

Examples:

- `.env.local` values;
- local mock endpoints;
- test admin credentials;
- smoke-test keys.

Never use as PROD source of truth.

## 2. Variable registry

Every production project should maintain a names-only registry:

| Variable | Class | DEV source | PROD source | Browser-visible | Required |
|---|---|---|---|---|---|
| `EXAMPLE_PRIVATE_KEY` | app_private | local secret | PROD env | no | yes |
| `NEXT_PUBLIC_APP_ORIGIN` | client_public | DEV URL | PROD URL | yes | yes |
| managed DB URL | platform_injected | runtime | runtime | server by default | yes |

Do not store secret values in documentation, issue bodies, screenshots, or handoff reports.

## 3. `.env` file policy

Recommended repository policy:

```gitignore
.env
.env.*
!.env.example
```

If the framework/tooling requires another safe example file, explicitly allowlist that file only.

`.env.example` should contain:

- variable names;
- empty/placeholders;
- ownership classification comments;
- whether client-visible;
- whether production user action is required.

It should not contain real DEV or PROD secrets.

## 4. Build-time vs runtime

### Build-time client config

Frameworks may inline public variables during build. A production runtime environment variable cannot necessarily change code already bundled into the browser.

Risks:

- production client still points at DEV database/API;
- CSP contains only DEV origins;
- redeploy changes server config but stale client bundle still uses old value.

### Runtime server config

Server code can normally read current process/runtime variables. Prefer this for secrets and platform-bound infrastructure.

### Runtime public-config endpoint

When the browser needs safe platform-bound config that should follow the deployed runtime, consider an allowlisted BFF endpoint:

```ts
// example only; never return service-role/private keys
export async function GET() {
  return Response.json({
    publicUrl: process.env.COZE_SUPABASE_URL,
    anonKey: process.env.COZE_SUPABASE_ANON_KEY,
  });
}
```

Only use this if those fields are intentionally client-safe in the project architecture and access policy. The endpoint must never expose service-role/admin secrets.

## 5. Reserved-prefix rule

If the platform warns that a key/prefix is reserved:

1. stop creating that variable;
2. determine whether it is platform-injected;
3. inspect current production variable list/runtime docs;
4. create only the project-owned alias if genuinely needed.

Do not work around a reserved prefix by hiding the same production secret under a public/client prefix.

## 6. Production validation

Before deploy verify:

- app-private values are present in PROD;
- platform-injected variables are not manually copied from DEV;
- no production secret is in `NEXT_PUBLIC_*` or frontend source;
- `.env.local` is absent from git/deploy source;
- startup scripts do not force-load DEV env files in PROD;
- browser bundle/runtime config uses production-safe values;
- `COZE_PROJECT_ENV` or equivalent observed environment marker matches the intended target when available.

## 7. Rotation

Rotate a production secret when:

- it was committed or pasted publicly;
- it was copied into a client bundle;
- a DEV secret was reused in PROD and should be separated;
- a bootstrap token has fulfilled its one-time purpose and the design allows rotation/removal;
- access ownership changes.

## 8. Agent rules

Never answer "把开发环境变量全部同步到生产" with a blanket yes.

Instead classify each variable and produce:

- **platform-injected** -> verify production injection;
- **app-private** -> create/enter independent PROD value;
- **client-public** -> confirm build/runtime exposure and production value;
- **local-only** -> do not promote.
