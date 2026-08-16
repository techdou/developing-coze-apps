# Expected — Eval 09

Must include:

- Do not recommend blanket DEV→PROD data sync by default.
- Schema should be promoted through versioned migrations.
- Test users/auth sessions and ordinary DEV rows should remain out of PROD unless explicitly approved.
- Object storage is a separate environment concern; DEV keys are not assumed to exist in PROD.
- Required curated assets should use an explicit allowlist/manifest and verification.
- First verify the actual production DB/Auth/Bucket bindings in the current Coze workspace.
- If exact Coze UI/CLI behavior is stated, require current official/runtime verification.
