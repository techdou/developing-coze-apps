# Agent Routing Rules

路由决策树 / Routing decision tree. Use this file to decide where each function belongs.

## Decision flowchart

```mermaid
graph TD
    A[需求输入] --> B{可视化应用或管理系统?}
    B -->|是| C[Coze Coding Web App<br/>前端 + 后端 API Routes]
    B -->|否| D{主要是对话助手?}
    D -->|是| E[Coze Agent<br/>+ 知识库/插件/数据库]
    D -->|否| F{可复用的流水线<br/>有明确输入输出?}
    F -->|是| G[Workflow 工作流]
    F -->|否| H{可复用的开发指令包?}
    H -->|是| I[Skill 技能包]
    H -->|否| J{需要事务/RBAC/复杂CRUD?}
    J -->|是| K[后端代码 + 数据库<br/>Workflow 仅做编排]
    J -->|否| L{处理文档或知识?}
    L -->|是| M[Knowledge/RAG<br/>+ 向量数据库]
    L -->|否| N{生成媒体?}
    N -->|是| O[模型集成 + 对象存储<br/>+ 异步状态轮询]
    N -->|否| P[评估具体需求<br/>参考资源路由矩阵]

    style C fill:#4f46e5,color:#fff
    style E fill:#059669,color:#fff
    style G fill:#d97706,color:#fff
    style I fill:#7c3aed,color:#fff
```

## Decision tree (text version)

1. **Is the deliverable a visual app or admin system?**
   - Yes -> Coze Coding web app / frontend + backend routes.
   - No -> continue.
2. **Is it mainly a conversational assistant?**
   - Yes -> ordinary Coze Agent, plus knowledge/plugins/database as needed.
3. **Is it a repeatable pipeline with clear inputs and outputs?**
   - Yes -> Workflow.
4. **Is it a reusable developer instruction package?**
   - Yes -> Skill.
5. **Does it need transactions, RBAC, or complex CRUD?**
   - Use backend code + database, with workflow only as orchestration.
6. **Does it process documents or knowledge?**
   - Use Knowledge/RAG or vector DB; preserve metadata.
7. **Does it generate media?**
   - Use model integration + storage + async state.

## Backend code vs workflow

Use backend code when:

- Multiple tables must be updated atomically.
- Permissions and row-level rules matter.
- Inputs need strict validation.
- Business logic needs tests.
- The workflow graph would be hard to maintain.

Use workflow when:

- A non-developer should inspect/adjust the steps.
- Steps call independent tools/APIs.
- Inputs and outputs are stable.
- The process is reusable across apps/agents.

## Agent vs web app

Use an Agent when the user experience is conversational. Use a web app when the user needs dashboards, CRUD tables, file management, charting, role-based pages, or complex UI state.

## Knowledge/RAG vs database

Use database for structured business state. Use RAG for source-grounded text/document retrieval. Use both when documents have metadata and business lifecycle state.


## Single HTML routing

- Deployed full-stack URL -> iframe wrapper.
- Static/Vite client-only build -> inspect, then single-file bundle.
- Course text/images -> editorial template.
- Need both context and app -> split or cover-launch wrapper.
- Need offline parity with backend -> explain impossibility; offer static demo or network-dependent wrapper.
