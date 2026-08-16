# Coze 开发与生产环境技术参考 v2.0

> developing-coze-apps 配套参考资料  
> Review baseline: 2026-08-17  
> 适用：Coze Coding / 扣子编程全栈项目的开发、部署与维护

## 1. 这版资料解决什么问题

Coze Coding 项目在开发阶段通常能快速获得数据库、认证、对象存储和 AI 能力，但真正上线后，最容易出问题的不是页面，而是**环境边界**：开发数据库和生产数据库是否混用、开发账号是否进入生产、对象存储 key 是否跨环境失效、`.env.local` 是否污染生产、浏览器 build-time 配置是否仍指向开发资源。

v2.0 的核心原则是：

> 同一套应用代码可以在 DEV 与 PROD 运行，但数据库/Auth/对象存储/Secret/业务数据默认按环境隔离。跨环境推进的是代码、Schema migration 和显式批准的数据/资产，而不是整个开发环境状态。

## 2. 双环境架构

```text
                    Application Source
                           |
                   Versioned Migrations
                           |
             +-------------+-------------+
             |                           |
        Development                    Production
             |                           |
        DEV Database                  PROD Database
        DEV Auth                      PROD Auth
        DEV Object Storage            PROD Object Storage
        DEV App Secrets               PROD App Secrets
        Test/Demo Data                Real Business Data
```

必须通过当前 Coze workspace/UI/CLI/runtime 核实资源实际绑定，不能仅凭变量名推断隔离关系。

## 3. 环境变量四分类

### 3.1 platform_injected

由 Coze 或当前 managed integration 提供/注入的运行时配置。在已测试的 Coze Coding 环境中曾观察到：

- `COZE_PROJECT_ENV`
- `COZE_SUPABASE_URL`
- `COZE_SUPABASE_ANON_KEY`
- `COZE_SUPABASE_SERVICE_ROLE_KEY`
- `COZE_BUCKET_ENDPOINT_URL`
- `COZE_BUCKET_NAME`
- runtime domain/port 等变量

这些变量名属于环境实测证据。部署时应先确认平台是否在 PROD 自动注入对应生产值，而不是复制 DEV 值。平台如果提示 `COZE_` 等前缀保留，不要创建冲突的用户变量。

### 3.2 app_private

项目自己拥有的服务端私密配置，例如：

- 第三方 API Key/Secret
- `API_KEY_HASH_PEPPER`
- 项目自定义 Bootstrap Token
- 内部签名密钥
- 生产初始化密码

DEV 与 PROD 应分别配置，不复用开发值作为默认做法。

### 3.3 client_public

主动暴露给浏览器的非敏感配置，例如 `NEXT_PUBLIC_*`。

关键点：`NEXT_PUBLIC_` 的含义是“会进入浏览器”，不是“安全”。绝不能放 Service Role、Bootstrap Token、Private Key 或其他服务端 Secret。

### 3.4 local_only

本地/开发便利配置，例如 `.env.local`、mock endpoint、测试管理员。

`.env.local` 必须视为 DEV-only，不能成为生产环境 source of truth。

## 4. Build-time 与 Runtime

Next.js 等框架可能把 client-public 变量在构建时写入浏览器 bundle。因此：

- PROD runtime 变量正确，不代表浏览器 bundle 一定正确；
- Server 可以已经连接 PROD，但 Browser 仍可能连接 DEV；
- 修改运行时变量后，已构建前端可能需要重新构建/部署；
- CSP `connect-src` 等配置也需要同时核验。

对于平台绑定基础设施，如果浏览器确实需要公开配置，可以采用 server runtime -> allowlisted runtime-config/BFF -> browser 的方式，但只返回明确 client-safe 的字段。

## 5. 数据库开发与生产策略

### 5.1 开发数据库

用于：

- Schema 迭代
- 测试账号
- Demo/Mock 数据
- 迁移演练
- 破坏性测试

### 5.2 生产数据库

生产数据库承载真实用户数据。默认不复制开发环境业务数据。

推荐：

```text
Code        -> same reviewed release
Schema      -> versioned migrations
Reference   -> reviewed idempotent seed/import
Business    -> no DEV sync by default
Auth users  -> no DEV sync by default
```

如果部署页面存在“同步开发环境数据至生产环境”，它只是技术能力，不代表应该开启。需要先区分用户到底要同步 Schema、字典数据、部分业务数据还是整个 DEV 状态。

## 6. Migration 与 Seed

Schema 变更应该进入版本控制：

- Migration 与依赖该 Schema 的代码一起提交；
- 生产执行前确认目标 DB identity；
- destructive migration 前备份；
- 记录 migration ID 与结果；
- migration 和大规模数据导入分开；
- reference seed 尽量幂等。

Seed 建议分类：

- reference：状态字典、公开分类，可审核后进入 PROD；
- demo：示例任务、假用户，不进入 PROD；
- privileged：默认管理员，不应普通 seed；
- migration-support：配合 Schema 的 backfill，显式执行；
- business：真实/测试业务记录，默认不从 DEV 推进。

## 7. Auth 与首位管理员

Auth 用户、session、测试 OAuth identity 都属于环境数据。

`BOOTSTRAP_TOKEN`、`BOOTSTRAP_ADMIN_EMAIL`、`/api/auth/bootstrap` 之类通常是**项目自定义机制**，不是 Coze 通用规范。

安全的生产初始化顺序：

```text
确认 PROD DB/Auth
 -> 执行 production migrations
 -> 配置项目自有 bootstrap secret
 -> 显式调用一次初始化
 -> 验证管理员 identity/role
 -> 限制/关闭/轮换 bootstrap 控制
```

禁止：

- `.env.local` 内固定的 DEV 管理员进入 PROD；
- production startup 自动使用默认管理员密码；
- 未验证目标数据库就执行 privileged bootstrap；
- Bootstrap endpoint 无保护且可重复创建管理员。

## 8. 对象存储

适合存放：图片、视频、音频、文档、导出文件。

推荐持久化模式：

```text
Upload -> Object Storage returns key -> DB stores key
Read   -> Generate current signed/public URL when needed
```

数据库不要把临时 signed URL 当永久字段。

### 8.1 DEV key 不等于 PROD object

例如 DEV DB 中有：

```text
users/123/images/a.png
```

把这行数据库记录迁移到 PROD，不会自动把二进制文件复制到 PROD bucket。

### 8.2 Asset Promotion

需要上线的封面、模板图、课程素材等，应建立 allowlist/manifest：

- logical name
- DEV source key/path
- PROD target key
- content type
- expected size/checksum

上传/复制完成后验证目标 object，再写入生产引用。

## 9. Coze CLI 与官方资料

Coze CLI 演进较快，Skill 不应该把某一版命令永久写死。

执行前至少运行：

```bash
coze --version
coze code --help
coze code env --help
coze code db --help
```

当前官方 `@coze/cli` 文档已经提供 `coze code ...` 的项目、环境变量、数据库等命令体系，并区分开发/生产环境变量查询能力。最终以**当前安装版本的 `--help` + 当前官方文档**为准。

Canonical references：

- https://docs.coze.cn/guides_vibe_coding_overview
- https://docs.coze.cn/guides_internal_integrations
- https://docs.coze.cn/guides_integrate_database
- https://docs.coze.cn/guides_integrate_storage
- https://docs.coze.cn/guides_environment_variables
- https://docs.coze.cn/guides_integrate_authentication
- https://www.npmjs.com/package/@coze/cli

## 10. 推荐生产部署流程

```text
1. Freeze release commit
2. Source audit
3. DEV/PROD Environment Matrix
4. Verify/create/bind PROD DB/Auth/Storage
5. Configure app-private PROD secrets
6. Backup if required
7. Apply migrations
8. Deploy reviewed commit
9. Smoke test production runtime
10. Project-specific bootstrap/first admin
11. Harden bootstrap
12. Production handoff + rollback notes
```

审计命令：

```bash
python scripts/coze_project_audit.py . --format md --strict
python scripts/coze_env_audit.py . --format md --strict
```

Supabase-style 项目在 redeploy/resource 变化后可运行：

```bash
python scripts/check_supabase_consistency.py
```

## 11. Production Smoke Test

最低测试集：

- 页面/health 正常；
- 登录、退出、session 正常；
- RBAC 拒绝未授权操作；
- 创建/读取/更新/删除一条 disposable record；
- 上传/读取/删除一个 disposable object；
- AI route 正常调用；
- AI failure/timeout/empty response 被正确处理；
- runtime public config 不暴露 Secret；
- CSP/connect-src/frame policy 正确；
- 日志不泄漏 Secret；
- 不存在意外 DEV/default admin。

## 12. Relay Studio 复盘

Relay Studio 的生产加固过程说明了几个可复用问题：

1. 开发默认账号/`.env.local` 不能进入生产初始化链路；
2. Server runtime 与 browser build-time 配置可能不一致；
3. redeploy 后本地 terminal 可能仍指向旧数据库；
4. 数据库 object key 不会自动复制对象存储文件；
5. privileged config 缺失时应 fail fast，而不是匿名凭据降级；
6. Bootstrap 是应用自定义能力，不能包装成 Coze 官方通用流程。

Reference project: https://github.com/douknowai/relay-studio

## 13. 生产交付原则

最终 handoff 需要记录：

- release commit/tag；
- production URL/project；
- DB/Auth/Bucket 安全标识；
- variable names + ownership（不写值）；
- migration version；
- backup/rollback；
- bootstrap 状态；
- smoke test；
- known risks；
- Secret rotation/operation owner。

## 14. 最终原则

1. 同一套代码，不等于同一套数据。
2. Schema migration，不等于 DEV business-data sync。
3. DEV object key，不等于 PROD object 已存在。
4. `.env.local` 不属于生产环境。
5. `NEXT_PUBLIC_*` 不可以放 Secret。
6. 平台注入变量先核验，不复制 DEV 值。
7. Privileged production config 缺失时 fail fast。
8. Bootstrap 先看项目代码，不能假设 Coze 通用机制。
9. 精确模型、CLI、配额、变量和平台行为执行前重新查证。
10. 生产修改前先确认“我现在操作的究竟是哪一个环境/资源”。
