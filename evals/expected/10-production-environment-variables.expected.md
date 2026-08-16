# Expected — Eval 10

Must include:

- Treat observed/reserved `COZE_*` infrastructure variables as platform-owned/injected until current runtime/official evidence says otherwise.
- Do not copy the development Supabase URL/service-role key/bucket name into production as a default workflow.
- `API_KEY_HASH_PEPPER` and project-specific bootstrap/admin secrets are application-owned private variables and need independent production values.
- Private values must remain server-side.
- `NEXT_PUBLIC_*`/client-public variables are browser-visible and may be baked at build time; never place service-role/bootstrap/private secrets there.
- `.env.local` is local/DEV-only and not production source of truth.
- Verify actual production bindings before deployment.
