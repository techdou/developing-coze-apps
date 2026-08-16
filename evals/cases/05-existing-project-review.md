# Eval Case 05 — Existing Project Review

User request:

> review 当前 Coze Coding 项目，检查资源调用和上线风险。

Expected behavior:

- Recommend running `scripts/coze_project_audit.py` if local files exist.
- Check frontend secret exposure, server-only SDK, DB filters, signed URL persistence, env vars, long tasks, deployment limits.
- Output P0/P1/P2.
