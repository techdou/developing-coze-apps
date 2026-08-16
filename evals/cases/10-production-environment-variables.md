# Eval 10 — Production environment variables

## User request

开发环境已经有 `COZE_SUPABASE_URL`、`COZE_SUPABASE_SERVICE_ROLE_KEY`、`COZE_BUCKET_NAME`，上线时生产环境变量里我要不要把这些值全部复制过去？另外我自己的 `API_KEY_HASH_PEPPER` 和管理员初始化密码应该怎么处理？

## Evaluate

The response should classify platform-injected vs app-private vs client-public vs local-only variables, avoid copying DEV managed-resource values into PROD, require independent production app secrets, and warn that client-public/build-time variables are browser-visible.
