# Expected — Eval 11

Must include:

- `/api/auth/bootstrap` and `BOOTSTRAP_*` are application/project conventions unless current official Coze evidence explicitly defines them.
- Verify production database/auth resource identity and migrations before invoking bootstrap.
- Production bootstrap must be explicitly protected with a high-entropy one-time secret or equivalent control and be idempotent/auditable.
- Do not seed or auto-create a known default production admin from `.env.local`, DEV data, or ordinary seed files.
- Verify the exact created admin identity/role.
- Restrict/disable/rotate bootstrap control after successful initialization where supported.
