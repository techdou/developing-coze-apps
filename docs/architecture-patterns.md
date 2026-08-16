# Architecture Patterns

## Pattern A: Coze Coding Web/Admin App

Use for business systems, dashboards, education tools, and SaaS prototypes.

```text
Frontend pages/components
  -> API routes / server actions
    -> database for structured data
    -> object storage for files/media
    -> AI model endpoints for generation/analysis
    -> workflow/API calls for orchestration
```

Key checks:

- Server-only model/storage/database clients.
- CRUD filters and role checks.
- Loading/error/empty states.
- Production env variables and database sync strategy.

## Pattern B: Agent + Knowledge + Database

Use for learning assistants, sales assistants, support agents, and memory/stateful assistants.

```text
User chat
  -> Agent prompt
    -> knowledge retrieval for source-grounded content
    -> database for user progress/state
    -> plugins/API for external actions
```

Key checks:

- Separate factual grounding from user state.
- Store progress and audit records in database.
- Provide citations or source snippets.

## Pattern C: Workflow as Reusable Pipeline

Use for form extraction, review pipelines, notification chains, document processing, and multi-step automations.

```text
Start input
  -> validate
  -> fetch/search/extract/model call
  -> database/storage write
  -> format result
  -> end output
```

Key checks:

- Input/output schema.
- Node-level error handling.
- Retry/degradation path.
- Test cases with sample payloads.

## Pattern D: Interactive Teaching HTML / 百宝箱

Use for lightweight learning tools with rich UI, diagrams, 3D, or simulations.

```text
Static/interactive frontend
  -> assets in repo or object storage
  -> optional AI explanation route
  -> optional knowledge/RAG for course references
```

Key checks:

- Mobile responsive UI.
- Offline/static fallback where possible.
- Asset size and storage strategy.
- No heavy server dependency unless necessary.

## Pattern E: Media Generation App

Use for image/video/audio generation, editing, storyboard, and creative tools.

```text
Prompt/reference input
  -> task API
  -> model generation job
  -> object storage persistence
  -> task status polling/SSE
  -> gallery/history table
```

Key checks:

- Async task state.
- Generated media persisted immediately.
- User-friendly failures and retry.
- Quota and timeout handling.


## Pattern F: Single-HTML Delivery

```text
source classification
  -> choose iframe wrapper / static bundle / editorial template
  -> generate or collect assets
  -> render dist/index.single.html
  -> validate single-file status and frame/security assumptions
```

Key checks:

- Do not package server-side capabilities as client HTML.
- Keep images local/data-URI for offline delivery.
- Check iframe frame policy and permissions.
- Validate mobile viewport, local references, secret leakage, and file size.
