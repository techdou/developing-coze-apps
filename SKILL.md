---
name: developing-coze-apps
description: >-
  Plan, build, review, or package Coze Coding (扣子编程) applications.
  Covers full-stack web apps, agents, workflows, RAG, media generation,
  and single-HTML/iframe packaging (dist/index.single.html).
  Triggers: Coze app, architecture routing, resource plan, single HTML, iframe embed.
---

# Developing Coze Apps

Turn a Coze requirement into a scoped architecture, correct resource-routing plan, staged implementation prompts, tested deliverables, and—when requested—a validated single-HTML package.

## Use this skill for

适用于以下场景 / Use this skill for:

- Coze Coding / 扣子编程 web apps, admin systems, SaaS prototypes, teaching tools, agents, workflows, plugins, knowledge/RAG, and media-generation apps.
- Deciding whether logic belongs in Coze Coding, ordinary Coze Agent, Workflow, Plugin, Skill, backend code, database, object storage, or knowledge/RAG.
- Reviewing an existing Coze project for resource misuse, security, quotas, deployment, and production readiness.
- Packaging a deployed URL or static web project as `dist/index.single.html` for iframe embedding.
- Designing image-text, course-reading, visual-story, gallery, kiosk, and application-wrapper single-HTML pages.

## Do not use this skill for

不适用场景 / Do not use this skill for:

- A short general explanation of what Coze is.
- Generic React/Next.js/Vue debugging with no Coze-specific resource or packaging requirement.
- Pure prompt rewriting unrelated to Coze application/agent/workflow development.
- Product ideation where Coze is not the target platform.

## First decision: identify the Coze layer

首先确定目标 Coze 层 / First, identify the target Coze layer:

Do not collapse these into one surface:

1. **Ordinary Coze / Coze Studio**: agents, workflows, plugins, knowledge bases, prompts, OpenAPI/SDK integration, publishing.
2. **Coze Coding / 扣子编程**: cloud AI programming for web apps, agents, workflows, skills, mini programs, mobile prototypes, and full-stack AI applications.
3. **Project-specific wrappers**: `coze-coding-dev-sdk`, Supabase-style helpers, S3-style helpers, runner scripts, and template commands. Treat exact APIs/model IDs as environment-specific until verified.

State the selected layer in every architecture answer.

## Core routing workflow

核心路由工作流 / Core routing workflow:

1. Classify the deliverable: web/admin app, agent, workflow, skill, mini program, mobile app, single HTML, or hybrid.
2. Classify the workload: display, tool, business system, media generation, RAG, automation, or embed/package.
3. Route resources:
   - UI/state -> frontend.
   - Transactions, RBAC, validation, complex CRUD -> backend code + database.
   - Files/media/exports -> object storage; persist object keys, not temporary signed URLs.
   - Reasoning/generation -> LLM or specialized model.
   - Document-grounded answers -> knowledge/RAG with source metadata.
   - Reusable orchestration -> Workflow with explicit I/O contract.
4. Verify environment-specific claims before coding: package version, model list, quotas, domains, storage, auth, runtime limits.
5. Build in stages and validate each stage before moving on.

## Single-HTML / iframe workflow

Trigger this workflow when the user mentions 单 HTML, single HTML, iframe, 百宝箱, 外部应用嵌入, URL 全屏展示, 图文页, or `dist/index.single.html`.

1. Read `docs/single-html-mode-selection.md` and `templates/single-html/catalog.md`.
2. Inspect the source:
   - deployed URL -> iframe-wrapper modes;
   - native/static/Vite build -> static bundle may be possible;
   - Next.js/full-stack/auth/database/API routes -> keep the app deployed and wrap its URL; do not pretend the backend can be packed into one file;
   - content + images -> editorial templates.
3. Present the best 3 options with fit, dependency, limitation, and recommendation. If the user already specified a style, skip unnecessary choice prompts.
4. Generate images through the current Coze Coding built-in image-generation integration by default. A user-selected Coze image skill/prompt standard may override only the image-generation step. Do not hard-code a model ID unless verified in the current environment.
5. Generate or package the HTML with `scripts/single_html_tool.py`.
6. Write the final deliverable to `dist/index.single.html` unless the user specifies another path.
7. Validate the file and report whether it is:
   - `self-contained` (offline assets inlined),
   - `single-file-network-dependent` (remote URL/assets required), or
   - `iframe-wrapper` (depends on the embedded app and its frame policy).
8. Run iframe/security checks from `docs/single-html-security.md` and static compatibility checks from `docs/static-bundling-compatibility.md`.

## Read only what the task needs

| User task | Read these files |
|---|---|
| Platform feasibility | `docs/capability-map.md`, `docs/official-evidence-map.md`, `docs/coze-limit-boundaries.md` |
| Architecture/MVP | `templates/architecture-blueprint.md`, `templates/scope-ladder.md`, `docs/architecture-patterns.md` |
| Staged Coze prompts | `templates/coze-build-prompts.md` |
| Workflow design | `templates/workflow-contract.md`, `docs/agent-routing-rules.md` |
| Single HTML / iframe | `docs/single-html-mode-selection.md`, `templates/single-html/catalog.md`, `docs/single-html-security.md` |
| Static app to one HTML | `docs/static-bundling-compatibility.md`, `scripts/single_html_tool.py` |
| Image-text HTML | `docs/image-generation-for-single-html.md`, `templates/single-html/catalog.md` |
| Project review | `templates/production-readiness-checklist.md`, `scripts/coze_project_audit.py` |
| Supabase 一致性检查 | `scripts/check_supabase_consistency.py`, `docs/coze-limit-boundaries.md` (Supabase 一致性章节) |
| Skill validation/evals | `scripts/validate_skill_package.py`, `evals/cases/` |

## Required output for planning tasks

```markdown
## 结论
<能做 / 部分能做 / 不建议这样做>

## 应采用的 Coze 层
<Coze Coding / ordinary Coze Agent / Workflow / Skill / Hybrid>

## 资源调用设计
| 模块 | 资源 | 所在层 | 风险/验证 |

## MVP 范围
<Must-have / Should-have / Later / Not first phase>

## 分阶段 Prompt
<每阶段可直接粘贴>

## 验收清单
<build, CRUD, auth, storage, AI, workflow, packaging, deployment>
```

## Required output for single-HTML tasks

```markdown
## 推荐方案
| 方案 | 适合场景 | 是否离线 | 关键限制 |

## 选定模板与资源
<template id, source URL/build dir, image slots, iframe permissions>

## 构建方式
<command or staged prompt>

## 输出
`dist/index.single.html`

## 验证结果
<single-file status, local references, iframe policy, mobile layout, file size>
```

## Guardrails

- Do not claim ordinary Coze Bot alone can replace a full business system.
- Do not expose model/storage/service-role clients in frontend code.
- Do not persist temporary signed URLs as permanent records.
- Do not promise exact CPU/RAM/disk/model access without checking the target workspace.
- Do not describe project-specific Supabase/S3 wrappers as universal platform guarantees.
- Do not pack a server-rendered/full-stack app into one HTML and claim its backend still works.
- Do not use `iframe srcdoc` for an entire third-party app when a normal `src` wrapper is more reliable.
- Do not assume a URL can be framed: verify `X-Frame-Options`, CSP `frame-ancestors`, authentication cookies, HTTPS, and required permissions.
- Do not embed secrets, service tokens, or private API endpoints in the generated HTML.
- Do not assume local terminal env vars and deployed runtime env vars point to the same Supabase project; run `scripts/check_supabase_consistency.py` after re-deployment.

### BFF proxy pattern (代码级实现参考 / Code-level reference)

All AI/SDK calls must go through a Backend-for-Frontend (BFF) API route. Never import `coze-coding-dev-sdk` in client components.

```typescript
// app/api/llm/stream/route.ts  — Server-side BFF pattern
import { LLMClient, Config, HeaderUtils } from 'coze-coding-dev-sdk';

export async function POST(request: Request) {
  const { messages } = await request.json();

  // Config auto-reads env vars — no hardcoded keys
  const config = new Config();
  const customHeaders = HeaderUtils.extractForwardHeaders(request.headers);
  const client = new LLMClient(config, customHeaders);

  const stream = client.stream(messages, {
    model: 'doubao-seed-2-0-lite-260215',
    thinking: 'enabled',
    caching: 'enabled',
  });

  const encoder = new TextEncoder();
  const readable = new ReadableStream({
    async start(controller) {
      for await (const chunk of stream) {
        if (chunk.content) {
          controller.enqueue(
            encoder.encode(`data: ${JSON.stringify({ content: chunk.content.toString() })}\n\n`)
          );
        }
      }
      controller.enqueue(encoder.encode(`data: ${JSON.stringify({ done: true })}\n\n`));
      controller.close();
    },
  });

  return new Response(readable, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
```

```typescript
// S3 storage pattern — persist key, not URL
import { S3Storage } from 'coze-coding-dev-sdk';

const storage = new S3Storage({
  endpointUrl: process.env.COZE_BUCKET_ENDPOINT_URL!,
  accessKey: '',
  secretKey: '',
  bucketName: process.env.COZE_BUCKET_NAME!,
  region: 'cn-beijing',
});

// Upload — use returned key (SDK adds UUID prefix), NOT your fileName
const key = await storage.uploadFile({
  fileContent: buffer,
  fileName: 'images/photo.jpg',
  contentType: 'image/jpeg',
});

// Persist key in database, NOT the URL
await db.photo.create({ imageKey: key });

// Generate signed URL only when the frontend needs to display it
const url = await storage.generatePresignedUrl({ key, expireTime: 86400 });
```
