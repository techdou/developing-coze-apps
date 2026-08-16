# Example: Interactive Teaching HTML / 百宝箱

## Recommended Coze layer

Coze Coding web app or static frontend-first app. Use ordinary Coze/Workflow only for optional explanation or content generation.

## MVP

- Rich interactive HTML page.
- Responsive layout for PC/mobile.
- Three.js/D3/Mermaid/SVG where useful.
- Externalized large assets where possible.
- Optional AI explanation panel, called through server API.

## Resource routing

| Need | Resource |
|---|---|
| 3D simulation/rendering | Frontend Three.js/WebGL |
| Large STL/GLB/audio/video | Object storage or external assets |
| Teaching explanation | AI API route or Agent |
| Course reference grounding | Knowledge/RAG |
| Export packaged file | Build script / object storage |

## Key prompts

- Ask Coze Coding to first build a static prototype with mock data.
- Add assets and interaction in a second pass.
- Add AI explanation only after the core teaching interaction works.
- Check mobile layout and asset loading at the end.
