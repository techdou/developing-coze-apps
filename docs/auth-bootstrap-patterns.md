# Auth Bootstrap / First-Admin Patterns

Many private/internal applications need a way to create the first administrator before any administrator exists. This is an **application design pattern**, not a universal Coze framework requirement.

## 1. Terminology

"Bootstrap" here means initial system provisioning/self-start. It is unrelated to the Bootstrap CSS framework.

Variable names such as:

- `BOOTSTRAP_TOKEN`
- `BOOTSTRAP_ADMIN_EMAIL`
- `BOOTSTRAP_ADMIN_PASSWORD`
- `INIT_ADMIN_SECRET`

are project conventions unless current platform documentation explicitly defines them.

## 2. When bootstrap is appropriate

Use a first-admin bootstrap when:

- public self-registration is disabled;
- admin users can create other users;
- a fresh production database/auth tenant begins with no privileged user;
- there is no safer managed administrative provisioning flow already available.

Do not add a bootstrap endpoint merely because another project had one.

## 3. Production requirements

A production bootstrap should be:

- **explicit** — not triggered by an accidental page view;
- **protected** — high-entropy token, trusted control plane, or equivalent;
- **idempotent** — repeated calls cannot create unlimited admins;
- **environment-aware** — production requires stronger controls than DEV;
- **auditable** — log result/actor metadata without logging secret values;
- **short-lived/restrictable** — disable or rotate the bootstrap path/secret after success where practical.

## 4. Forbidden patterns

Do not:

- commit a default production admin password;
- create `admin@example.local / Admin@123` during PROD startup;
- load DEV `.env.local` and use its admin values in PROD;
- seed an auth admin account through ordinary reference-data seed files;
- expose bootstrap secrets via `NEXT_PUBLIC_*` or browser code;
- leave an unauthenticated repeatable `create-admin` endpoint open;
- silently bootstrap against whichever database happens to be in shell variables.

## 5. Recommended lifecycle

```text
production infrastructure ready
        |
production migrations complete
        |
verify PROD DB/Auth identity
        |
configure project-specific bootstrap inputs
        |
invoke one-time bootstrap
        |
verify exact admin identity + role
        |
restrict/rotate bootstrap control
        |
normal admin user-management takes over
```

## 6. Example endpoint pattern

Illustrative only:

```ts
export async function POST(req: Request) {
  if (process.env.COZE_PROJECT_ENV === 'PROD') {
    const expected = process.env.BOOTSTRAP_TOKEN;
    const provided = req.headers.get('x-bootstrap-token');
    if (!expected || provided !== expected) {
      return Response.json({ error: 'forbidden' }, { status: 403 });
    }
  }

  // 1. verify target DB/Auth resource
  // 2. check whether a valid admin already exists
  // 3. require production admin email/password from private runtime config
  // 4. create admin atomically/idempotently
  // 5. write audit event without secret values
}
```

Production code should use constant-time secret comparison where appropriate and should rate-limit/protect the endpoint based on the threat model.

## 7. Existing-admin behavior

"Admin already exists" must not automatically mean "bootstrap succeeded correctly".

Verify:

- the existing account is in the production Auth tenant;
- its email/identity is intended;
- it did not arrive from DEV data sync/default seed;
- its role record is correct;
- it can authenticate with known production-managed credentials.

If an unexpected DEV admin exists in PROD, investigate data sync/startup/env leakage first.

## 8. Bootstrap values

For project-owned bootstrap variables:

- email: production owner's/admin's real intended address;
- password: strong unique production password or managed onboarding flow;
- token: cryptographically random/high-entropy value, not a memorable example string;
- never document/paste real values in repository files.

Generate secrets with an appropriate password/secret manager or cryptographic generator.

## 9. Agent response contract

When a user asks "怎么创建第一个账号" the Agent must first inspect the project's auth/bootstrap code/documentation.

Then state:

1. whether the project actually implements bootstrap;
2. which variables are project-specific;
3. which environment must receive them;
4. whether production database/auth is fresh and migrated;
5. exact invocation only after the above is verified;
6. post-bootstrap hardening action.

Never present a project-specific `/api/auth/bootstrap` route as a Coze platform standard.
