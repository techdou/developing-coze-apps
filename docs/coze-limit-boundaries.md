# Coze Limit Boundaries

Use this file before making production, deployment, large-file, or high-concurrency promises.

## Limits to check

> Values below are from `coze-platform-report.pdf` (SDK 0.7.21, July 2025). Always verify in the target workspace.

| Area | Specific value / range | Why it matters |
|---|---|---|
| Sandbox CPU | 4 cores AMD EPYC | CPU-bound tasks (local inference, heavy processing) will be slow |
| Sandbox memory | 8 GB | Large media processing may OOM; use chunked/streaming approach |
| Sandbox disk | 10 GB | Heavy node_modules + media projects can exceed; clean build artifacts |
| Sandbox GPU | None (CPU only) | Cannot run local model inference; use cloud AI APIs |
| Node.js | v24.16.0 | Use compatible packages; some older packages may break |
| Python | 3.12.3 | Scripts using Python features should target <= 3.12 |
| pnpm | 9.15.9 | Do not use npm or yarn |
| Supabase DB storage | 500 MB (free plan) | Monitor table sizes; archive or partition large tables |
| Supabase Auth MAU | 50,000 (free plan) | Plan auth capacity accordingly |
| Supabase bandwidth | 5 GB/month (free plan) | CDN/static assets may consume bandwidth |
| S3 object storage | Platform-allocated quota | Monitor usage; large media files add up fast |
| Signed URL expiry | Configurable (default varies) | Persist keys, not URLs; regenerate at access time |
| TTS supported languages | Chinese + Latin-script only | Thai/Japanese/Korean/Arabic return empty audio |
| TTS voices | 15 verified (SDK 0.7.21) | npm README claims 30+; verify available voices at runtime |
| ASR audio limit | ≤ 2 hours, ≤ 100 MB | Longer audio needs chunking |
| ASR language param | None (auto-detect only) | Specific languages may be misidentified |
| Video generation duration | 5–10 seconds per clip | Long videos need segment generation + concat |
| Video resolution | 480p / 720p / 1080p | 4K not available for video generation |
| LLM models | 7 available (7/2025) | Model list changes; verify `COZE_LOOP_BASE_URL` API |
| Deployment port | 5000 (main), dynamic (worktree) | Never use port 9000 (system reserved) |
| Concurrent preview | 1 main + N worktrees | Cross-worktree file/process access is forbidden |

## Default engineering responses

- For files over the deployed upload limit: design chunk upload with small chunks and resumable state.
- For long AI/media tasks: use async task table plus polling/SSE heartbeat.
- For production data: separate migration scripts from UI code; document rollback and backup.
- For high concurrency: add queueing, caching, rate limits, and load testing before launch.
- For domain/SSL: treat as deployment preparation, not code implementation only.

## Supabase instance consistency

Re-deploying a Coze Coding project may create a **new Supabase instance** while the development terminal still references the old one. This causes:

- Password resets applied to the wrong instance (users still can't log in)
- Database writes going to the old instance (data invisible in production)
- Frontend auth connecting to one project while backend APIs connect to another

**Pre-deployment check**: always verify that the terminal's `COZE_SUPABASE_URL` matches the deployed instance's `/api/supabase-config` response.

**Automated check**: run `python scripts/check_supabase_consistency.py` before and after deployment.

**Recovery**: if instances diverge, reset passwords on the production instance (the one the frontend connects to), not the terminal's default.

## Risk language

Use:

> This is suitable for MVP and controlled pilot deployment, but production launch requires quota, domain, logging, backup, and concurrency verification in the target workspace.

Avoid:

> Coze can definitely run this at production scale without extra checks.


## Single-HTML limits

- One file does not mean offline: iframe and remote assets still require network access.
- Browser frame policies are controlled by the embedded site, not the wrapper.
- Base64 increases size and memory use; large video/3D assets can make the HTML impractical.
- Full-stack services remain remote; only the presentation wrapper is packaged.
- Camera/microphone/clipboard permissions require both iframe `allow` and browser/user approval.
