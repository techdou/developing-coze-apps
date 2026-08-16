# developing-coze-apps

一个面向 Agent 的 Coze Coding（扣子编程）工程 Skill：从架构规划、开发、审查到生产部署与单 HTML / iframe 交付。重点覆盖 **DEV/PROD 环境隔离、数据库/Auth/对象存储生命周期、环境变量治理、生产迁移与初始化**，避免“开发环境能跑、生产环境混乱”的常见问题。

## 核心能力

- **平台分层判断**：区分 Coze Coding / 普通 Coze Agent / Workflow / Plugin / Knowledge/RAG / 项目代码边界。
- **DEV/PROD 环境设计**：数据库、Auth、对象存储、Secret、Domain、第三方 API 分环境建模；先建立 Environment Matrix，再写持久化业务。
- **数据库生命周期**：Schema 通过 versioned migrations 推进；普通 DEV 测试数据默认不进入 PROD；Seed 与 Business Data 分离。
- **对象存储生命周期**：数据库持久化 object key，不持久化临时签名 URL；DEV key 不等于 PROD 文件存在；支持显式 Asset Promotion。
- **环境变量治理**：区分 `platform_injected`、`app_private`、`client_public`、`local_only`；禁止 `.env.local` 成为生产配置源。
- **生产部署**：Production preflight → resource verification → migration → deploy → smoke test → project-specific bootstrap → handoff。
- **项目审查**：密钥泄漏、客户端 service-role、DEV/PROD 串库、默认管理员、自动 bootstrap、匿名凭据降级、临时 URL 持久化等。
- **单 HTML / iframe**：支持静态内联、部署 URL wrapper、课程/图文/画廊等模板，输出 `dist/index.single.html`。

## 安装

```bash
# Claude Code
~/.claude/skills/developing-coze-apps/

# Codex / 通用 Agent Skills
~/.agents/skills/developing-coze-apps/
```

或：

```bash
git clone https://github.com/techdou/developing-coze-apps.git ~/.agents/skills/developing-coze-apps
```

## 推荐使用方式

### 1. 新建 Coze 全栈项目

```text
使用 developing-coze-apps skill 设计并开发这个 Coze Coding 项目。
如果项目需要数据库、Auth、对象存储或环境变量，先建立 DEV/PROD Environment Matrix，明确哪些由平台注入、哪些是项目私密变量、哪些会暴露给浏览器。Schema 使用 migrations，默认不要把开发业务数据同步到生产。完成后给出生产部署和 handoff 流程。
```

### 2. 部署生产环境

```text
使用 developing-coze-apps skill 帮我部署当前 Coze 项目到生产。
先核对当前 Coze CLI/官方行为，执行项目审计和环境审计；确认生产 DB/Auth/Bucket 与环境变量；默认关闭 DEV 业务数据同步，用 migrations 推进 schema；部署后完成 auth、CRUD、storage、AI、runtime config smoke test。如果项目有 first-admin/bootstrap，再按项目代码完成一次性初始化。
```

### 3. 排查 DEV 正常、PROD 异常

```text
使用 developing-coze-apps skill 排查为什么开发环境正常但生产异常。
重点检查 .env.local、平台注入变量、NEXT_PUBLIC/build-time 配置、生产数据库/对象存储绑定、迁移版本、默认管理员/bootstrap，以及本地终端是否仍指向旧资源。
```

### 4. 单 HTML / iframe

```text
使用 developing-coze-apps skill，把我已部署的 Coze Web 应用封装为适合外部平台嵌入的单 HTML。先判断应该静态内联还是 iframe wrapper，并验证 frame policy、cookies、HTTPS 和移动端。
```

## 关键文档

- `docs/environment-separation.md` — DEV/PROD 边界原则
- `docs/environment-variables.md` — 环境变量四分类、build-time/runtime
- `docs/database-storage-lifecycle.md` — DB/Auth/Object Storage 生命周期
- `docs/production-deployment.md` — 生产部署 playbook
- `docs/auth-bootstrap-patterns.md` — 首位管理员/bootstrap 安全模式
- `docs/official-evidence-map.md` — 官方/CLI/实测/项目证据分层
- `examples/relay-studio-dev-prod-hardening.md` — Relay Studio 实战复盘

## 模板

- `templates/architecture-blueprint.md`
- `templates/environment-matrix.md`
- `templates/production-readiness-checklist.md`
- `templates/production-handoff.md`
- `templates/coze-build-prompts.md`
- `templates/single-html/`

## 审计工具

```bash
# 通用 Coze 项目静态审计
python scripts/coze_project_audit.py . --format md --strict

# DEV/PROD / env / bootstrap / storage 边界审计
python scripts/coze_env_audit.py . --format md --strict

# Supabase-style 项目：本地/终端与部署实例一致性检查
python scripts/check_supabase_consistency.py

# Skill 包结构/引用校验
python scripts/validate_skill_package.py .
```

`coze_env_audit.py` 重点检测：

- `.env.local` / env 文件生产污染；
- `COZE_*` 等平台变量被错误固化为 DEV 值；
- `NEXT_PUBLIC_*` 暴露 service-role/secret/token；
- startup 自动调用 privileged bootstrap；
- DEV/default admin 凭据；
- privileged credential → anonymous/public 静默降级；
- DEV→PROD 自动全量同步；
- signed URL 持久化；
- DB 项目缺少明确 migration posture。

## 目录结构

```text
developing-coze-apps/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── VERSION
├── docs/
├── templates/
├── scripts/
├── evals/
├── examples/
└── reference/          # 可发布的 Coze 开发/生产参考资料
```

## 工程原则

1. **同一套代码，不等于同一套数据。**
2. **Schema promotion ≠ business-data sync。**
3. **DEV key/URL/secret 不能默认成为 PROD 配置。**
4. **平台注入变量先验证，不手工复制 DEV 值。**
5. **生产缺少 privileged config 时 fail fast，不静默降级。**
6. **Bootstrap 是项目机制，除非官方明确规定，否则不要包装成 Coze 通用规则。**
7. **精确 CLI/模型/配额属于易变信息，执行前用当前官方资料和 `--help` 再核对。**
