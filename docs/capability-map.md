# Coze Capability Map

> **SDK baseline**: `coze-coding-dev-sdk@0.7.24` (latest verified). Model IDs, method signatures, and environment variables may differ across versions — always verify at runtime with `npx coze-coding-ai --version` or check `process.env` in your sandbox.

Use this file when deciding which Coze resource should handle a requirement.

## Platform surfaces

| Surface | Best for | Do not use as |
|---|---|---|
| Ordinary Coze / Coze Studio | Agent, workflow, plugin, knowledge base, prompt, API/SDK publishing | Full business-system backend by itself |
| Coze Coding / 扣子编程 | Web apps, admin systems, full-stack AI apps, agents, workflows, skills, mini programs, app prototypes | Unlimited cloud server or general-purpose production platform without limits |
| Project wrappers / SDKs | Environment-specific helpers such as model clients, storage helpers, runner scripts | Official guarantees before local verification |

## Resource routing matrix

| Requirement | Preferred resource | Why | Verification |
|---|---|---|---|
| CRUD business data | Database / backend code (`SupabaseClient`, `@supabase/supabase-js`) | Querying, filtering, pagination, relations | Schema, filters, migrations, prod sync |
| Files, images, audio, video, exports | Object storage (`S3Storage` from SDK) | Persist large/non-structured assets | Store object key; signed URL only for access |
| Chat, analysis, text generation | LLM (`LLMClient`, SDK 0.7.21+) | Natural-language reasoning/generation | Model availability, rate, error handling |
| Document-grounded Q&A | Knowledge/RAG (`KnowledgeClient`, `EmbeddingClient`) | Source-grounded retrieval | Chunking, metadata, citations, update path |
| Latest public facts | Search/fetch (`SearchClient`, `FetchClient`) | Current information | Fetch failure, unsupported pages, citations |
| Image generation | Image model (`ImageGenerationClient`, SeeDream) + storage | Generated visuals | Persist outputs; usage quota |
| Video generation/editing | Video model (`VideoGenerationClient`, `VideoEditClient` 0.7.24+) + async state | Long-running media tasks | queued/running/succeeded/failed state |
| Speech input/output | ASR/TTS (`ASRClient`, `TTSClient`) + storage | Voice features | Format, latency, storage, playback |
| Repeatable multi-step process | Workflow | Orchestration and non-dev inspectability | I/O contract, node tests, retries |
| Transactions/RBAC/complex validation | Backend code (Next.js API Routes) | Maintainability and security | Unit tests, filters, permissions |
| Third-party service | Plugin/API/backend integration | External tool calls | Auth, retries, rate limits |

## Default architecture choices

1. **Web/admin system**: Coze Coding + database + backend API + object storage + optional workflow/AI.
2. **Pure conversational agent**: ordinary Coze Agent + knowledge + plugins + optional database.
3. **Reusable pipeline**: Workflow with clear inputs/outputs, plus database/storage if stateful.
4. **Teaching demo / 百宝箱**: frontend-first, static assets or object storage, optional AI explanation endpoint.
5. **Media generation app**: frontend UI + backend task API + model service + storage + async polling.

## Capability confidence labels

Use these labels in answers:

- **Officially documented**: confirmed in official Coze docs or SDK README.
- **Environment-specific**: mentioned in project notes or available in a current sandbox/SDK, but not universal.
- **Needs live verification**: model IDs, quotas, exact resource specs, permissions, or package versions may vary.
- **Not recommended first phase**: technically possible but high-risk for MVP.


## Single-HTML capability routing

| Requirement | Preferred mode | Confidence |
|---|---|---|
| Embed a deployed Coze app URL in one HTML | iframe wrapper template | Supported by standard browser HTML; target framing policy needs runtime check. |
| Native/static app to one HTML | static bundling | Environment/project dependent; validate unresolved imports and server dependencies. |
| Full-stack Coze app to offline one HTML | Not equivalent | Use deployed URL + iframe; backend cannot be embedded. |
| Image-text course page | self-contained editorial template | Supported; images may be generated via current Coze image integration and inlined. |
