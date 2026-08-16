# Example: Vocational Training School Flexible Employment System

## Recommended Coze layer

Hybrid: Coze Coding web/admin app + database + object storage + AI model + optional workflow/agent.

## MVP

- Talent profile database: skills, portfolio, availability, expected salary, status.
- Enterprise/project database: company, role/project, duration, budget, required skills.
- Matching workflow: AI-assisted recommendation explanation; final decision by staff.
- Admin pipeline: lead -> negotiation -> contract -> settlement -> archived.
- File storage: resumes, certificates, portfolio media; store file keys.
- Basic roles: admin, staff, enterprise viewer, talent viewer.

## Coze resource routing

| Module | Resource | Notes |
|---|---|---|
| Talent/enterprise CRUD | Database + backend API | Not workflow-only. |
| Resume/certificate upload | Object storage | Store key and metadata. |
| Job matching explanation | LLM / optional workflow | AI suggests, human reviews. |
| Notifications | Workflow/plugin/API | Keep I/O contract stable. |
| Knowledge base | RAG | School policies, training courses, contract templates. |

## Do not promise first phase

- Complex financial settlement automation.
- High-concurrency public marketplace.
- Fine-grained multi-tenant billing.
- Native mobile app and mini program simultaneous release.
