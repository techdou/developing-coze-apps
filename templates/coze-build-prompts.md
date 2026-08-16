# Staged Coze Coding Prompt Templates

Prefer staged prompts. Fill placeholders before use.

## Phase 0 — Requirements alignment

```text
你是 Coze Coding / 扣子编程项目架构师。请先不要写代码，先帮我把需求拆清楚。

项目：【项目名称】
目标用户：【用户】
业务目标：【一句话目标】
必须包含：【功能列表】
可能用到的资源：【数据库/对象存储/大模型/知识库/工作流/插件/搜索/生图/视频/语音】

请输出：
1. 应采用的 Coze 层：Coze Coding / Agent / Workflow / Hybrid
2. MVP 范围、V1 增强、暂不承诺
3. 页面路由
4. 数据表草案
5. AI/Workflow/Storage 资源调用图
6. 风险和需要实测的点
```

## Phase 1 — App skeleton

```text
基于上一轮确认的方案，先实现项目骨架，不要一次性实现全部复杂逻辑。

要求：
- 创建清晰的页面路由和布局
- 搭建导航、列表页、详情页、表单页、空状态、错误状态
- 使用响应式布局，兼顾 PC 和移动端
- 先用 mock 数据跑通 UI
- 不要在前端写任何 API Key 或模型调用

输出后请说明已创建/修改的文件和下一步需要接入的数据接口。
```

## Phase 2 — Database and CRUD

```text
现在接入数据库能力，实现结构化数据持久化。

要求：
- 根据确认的数据模型创建表，字段使用 snake_case
- 每张表包含 id、created_at、updated_at
- 实现列表、创建、编辑、详情、软删除/状态变更
- update/delete 必须带明确过滤条件
- API 返回统一错误格式
- 前端展示 loading、empty、error 状态
- 如涉及权限，请预留 role 字段和后端校验逻辑

完成后请给出数据库表结构、CRUD API 列表和烟测步骤。
```

## Phase 3 — Storage

```text
现在接入对象存储能力，用于上传和展示【图片/文档/音频/视频/导出文件】。

要求：
- 上传后数据库只保存 file_key/object_key 和元数据，不保存临时 signed URL
- 展示/下载时由服务端生成临时访问 URL
- 增加文件类型、大小、失败重试提示
- 如果文件可能超过平台上传限制，设计分片上传方案

完成后请说明存储 key 命名规则、数据库字段和测试方法。
```

## Phase 4 — AI/RAG integration

```text
现在添加 AI 能力：【AI 功能描述】。

要求：
- 模型调用必须放在服务端/API Route，不允许出现在前端组件
- 输入参数要做校验
- 输出支持流式/SSE 或异步任务状态，按场景选择
- 如果使用 RAG/知识库，必须保留 source_title、source_url、chunk_id、updated_at 等元数据，并在 UI 展示引用来源
- 添加模型失败、超时、额度不足的降级提示

完成后请给出 AI API 契约、Prompt 策略、错误处理和验证用例。
```

## Phase 5 — Workflow / Agent / Plugin assets

```text
现在将以下逻辑拆成可复用 Coze Workflow/Agent/Plugin 调用：【流程描述】。

要求：
- 先定义输入 JSON Schema 和输出 JSON Schema
- 每个节点说明职责、输入、输出、失败处理
- 明确哪些逻辑留在后端代码，哪些放到 Workflow
- 生成至少 3 个测试 payload
- 在 Web 应用中封装调用接口，并处理超时、失败、重试

完成后请输出工作流契约、节点清单、测试用例和接入代码位置。
```

## Phase 6 — Production readiness

```text
请对当前项目做上线前检查。

重点检查：
1. 前端是否暴露密钥或服务端 SDK
2. 数据库 update/delete 是否有 filter
3. 对象存储是否只保存 key 而不是临时 URL
4. AI 接口是否有错误处理、超时、额度提示
5. 长任务是否有 async state 或 heartbeat
6. 日志、备份、权限、部署环境变量是否说明清楚
7. 移动端适配、空状态、错误状态、可访问性是否合格

按 P0/P1/P2 输出问题清单和修复 Prompt。
```

## Phase 7 — Single-HTML / iframe delivery

Use only when the user needs one HTML file or an iframe-compatible teaching container.

```text
现在为当前项目设计单 HTML 交付物，默认输出 dist/index.single.html。

先判断：
- 当前项目是已部署 URL、静态/Vite 项目，还是依赖 Next.js API、数据库、鉴权、对象存储和服务端模型调用的全栈项目？
- 如果依赖服务端能力，不要错误地把它打成离线 HTML；应使用已部署 URL 的 iframe wrapper。

若用户尚未指定样式，请只给最合适的 3 款方案，并说明优点、网络依赖、iframe 限制和推荐度：
- fullscreen-iframe
- app-shell-iframe
- split-intro-iframe
- cover-launch-iframe
- editorial-image-text
- visual-story
- course-article
- gallery-showcase

图片要求：
- 默认通过当前 Coze Coding 环境内置生图能力生成；如用户指定其他 Coze 生图 skill 或 prompt 规范，则把图片槽位要求交给该能力执行。
- 先输出图片槽位、比例、最低尺寸、内容和 alt 文本，再生成图片。
- 离线单 HTML 必须把最终图片内嵌为 data URI；不要把临时 signed URL 当作长期资源。

构建完成后：
1. 输出 dist/index.single.html
2. 检查本地相对资源引用是否清零
3. 检查密钥泄露、viewport、移动端布局和文件大小
4. iframe 模式说明 X-Frame-Options、CSP frame-ancestors、登录 Cookie、HTTPS 和麦克风/摄像头权限仍需浏览器实测
5. 标记为 self-contained、single-file-network-dependent 或 iframe-wrapper
```
