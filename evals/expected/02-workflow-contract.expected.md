# Expected Outline

- Workflow has clear input/output JSON.
- Nodes: validate -> resume fetch/extract -> skill normalization -> match query -> LLM reason -> notify/log -> end.
- DB/storage side effects are explicit.
- Includes happy path, invalid input, downstream failure tests.
