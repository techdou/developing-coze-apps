# Workflow Contract Template

Use before asking Coze to generate or modify a workflow.

## Workflow name

- Name:
- Purpose:
- Trigger: manual / API / scheduled / app button / agent call
- Owner:

## Why this belongs in workflow

- Reusable process:
- Clear I/O:
- Inspectable by non-developers:
- External integrations:

## Input schema

```json
{
  "type": "object",
  "required": [],
  "properties": {}
}
```

## Output schema

```json
{
  "type": "object",
  "required": ["status"],
  "properties": {
    "status": { "type": "string", "enum": ["success", "partial", "failed"] },
    "data": { "type": "object" },
    "errors": { "type": "array", "items": { "type": "string" } }
  }
}
```

## Node plan

| Node | Responsibility | Input | Output | Failure handling |
|---|---|---|---|---|
| Start | Validate trigger input |  |  | Return schema error |
|  |  |  |  |  |
| End | Return normalized output |  |  |  |

## Data/storage side effects

| Step | Writes to DB/storage? | Idempotency key | Rollback/cleanup |
|---|---|---|---|

## Test payloads

### Happy path

```json
{}
```

### Missing/invalid input

```json
{}
```

### Downstream failure

```json
{}
```

## Web app integration

- API route:
- Auth required:
- Timeout/retry policy:
- UI states: idle / running / success / partial / failed
