# Single-HTML Mode Selection

Use this document whenever the user asks for 单 HTML, iframe embedding, 百宝箱 delivery, a URL wrapper, or `dist/index.single.html`.

## First classify the source

| Source | Recommended mode | Why |
|---|---|---|
| Deployed Coze URL with backend/auth/database | iframe wrapper | Preserves live backend and platform resources. |
| Next.js/full-stack source | deploy first, then iframe wrapper | A single HTML cannot contain API routes, server actions, database, or auth services. |
| Vite/native static SPA | static bundle or iframe wrapper | Can be inlined if the build has no unresolved local module imports or server dependency. |
| Article/text/images | editorial template | No app runtime is required. |
| Course introduction + live app | split intro+app or cover-launch | Combines context and interaction. |
| Kiosk/exhibition display | full-screen iframe | Minimal chrome and maximum content area. |

## Option-selection contract

When the request is ambiguous, offer the best three options rather than every template:

```markdown
| 方案 | 模板 | 优点 | 依赖/限制 | 推荐度 |
```

Then recommend one. Ask the user to choose only when the visual structure materially changes the result. When the user already says “全屏 URL” or “图文型”, proceed directly.

## Recommended option sets

### A. User provides a deployed URL

1. `fullscreen-iframe` — pure full-screen display.
2. `app-shell-iframe` — title, status, refresh, open-in-new-window controls.
3. `split-intro-iframe` — course/context panel plus app.

### B. User wants an educational presentation

1. `editorial-image-text` — balanced article and image sections.
2. `course-article` — lesson objectives, reading, summary, activity entry.
3. `visual-story` — immersive large-image narrative.

### C. User wants a product/showcase page

1. `gallery-showcase` — multiple visual cards.
2. `cover-launch-iframe` — cover/intro then launch app.
3. `app-shell-iframe` — branded application frame.

### D. User wants offline single-file delivery

1. Static bundle if the project is truly static.
2. Editorial template with all local assets converted to data URIs.
3. If server dependencies exist, explain that offline parity is impossible and offer a network-dependent iframe wrapper instead.

## Output contract

- Default file: `dist/index.single.html`.
- The final `dist/` folder contains only the requested deliverable unless the user explicitly asks for reports/assets.
- Never place source templates, secrets, debug logs, or raw generated assets in `dist/`.
- Report one status:
  - `self-contained`;
  - `single-file-network-dependent`;
  - `iframe-wrapper`.
