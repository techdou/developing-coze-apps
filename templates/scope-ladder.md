# Scope Ladder Template

Use this to prevent over-promising and to produce realistic MVP plans.

## MVP — must ship first

| Feature | Why must ship | Simplest implementation | Acceptance test |
|---|---|---|---|

## V1 — strong next iteration

| Feature | Value | Dependency | Risk |
|---|---|---|---|

## Later — useful but not first phase

| Feature | Reason to delay | What to validate first |
|---|---|---|

## Do not promise before testing

| Item | Risk | Required verification |
|---|---|---|
| High concurrency | Plan/resource limits | Load test and deployment resource check |
| Large media files | Upload/storage/timeouts | Chunk upload and storage quota test |
| Long video generation | Timeout/quota/asynchronous state | Model access and task status test |
| Complex finance settlement | Audit/security/compliance | Data model, audit log, manual review |
| Fine-grained multi-tenant RBAC | Security complexity | Permission matrix and backend enforcement |
| Exact model/version access | Workspace/model availability | Check current model list and quotas |

## Recommended answer language

Use:

> 首期做 MVP，先跑通核心闭环；V1 再加自动化、智能推荐和数据看板；涉及高并发、复杂财务、长视频、大文件和精细 RBAC 的部分需要单独实测和评估。
