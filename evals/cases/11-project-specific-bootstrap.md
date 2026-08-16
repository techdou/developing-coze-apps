# Eval 11 — Project-specific bootstrap

## User request

我部署了一个 Coze Web 应用，项目里有 `/api/auth/bootstrap`、`BOOTSTRAP_TOKEN`、`BOOTSTRAP_ADMIN_EMAIL`。这是 Coze 官方规定的吗？生产环境应该怎么安全初始化第一个管理员？

## Evaluate

The response should inspect/describe bootstrap as project-specific unless official evidence says otherwise, verify PROD DB/Auth first, require protected/idempotent one-time initialization, forbid DEV/default credentials, and include post-bootstrap hardening.
