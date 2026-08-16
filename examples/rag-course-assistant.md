# Example: RAG Course Assistant

## Recommended Coze layer

Coze Agent or Coze Coding app + Knowledge/RAG + database.

## MVP

- Upload/import course documents.
- Chunk and index documents.
- Ask questions with source-grounded answers.
- Show citations/source snippets.
- Store user questions and feedback.

## Resource routing

| Module | Resource |
|---|---|
| Course documents | Knowledge/RAG or vector DB |
| Source files | Object storage |
| User progress/feedback | Database |
| Answer generation | LLM |
| Frontend UI | Coze Coding web app if visual UX is needed |

## Guardrails

- Do not answer as if document-grounded unless retrieval succeeded.
- Preserve source metadata.
- Provide fallback when fetch/import fails.
