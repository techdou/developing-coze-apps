# Example: Media Generation Agent/App

## Recommended Coze layer

Hybrid: Coze Coding frontend + backend task API + image/video/audio model integration + object storage + optional workflow.

## MVP

- Prompt/reference upload.
- Generate image or short media asset.
- Persist generated result to object storage.
- Store history in database.
- Display task state and retry failed jobs.

## Resource routing

| Module | Resource |
|---|---|
| Prompt UI/history | Coze Coding web app + database |
| Reference files | Object storage |
| Image generation | Image model |
| Video generation/editing | Video model/editing tools + async task state |
| TTS/ASR | Speech model |
| Multi-step pipeline | Workflow if reusable |

## Long-task state

Use:

```text
queued -> running -> succeeded | failed | cancelled
```

For long HTTP connections, design heartbeat or polling instead of assuming one blocking request will stay open.
