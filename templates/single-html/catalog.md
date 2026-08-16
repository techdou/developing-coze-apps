# Single-HTML Template Catalog

Read this file before offering the user design options.

| ID | Chinese name | Best for | Network dependency | Notes |
|---|---|---|---|---|
| `fullscreen-iframe` | 全屏应用嵌入 | Kiosk, pure app display, course iframe container | Embedded URL | No visual chrome; fastest. |
| `app-shell-iframe` | 应用外壳 | Branded tool with title/refresh/open controls | Embedded URL | Good general default. |
| `split-intro-iframe` | 图文介绍 + 应用分栏 | Course introduction, task brief, lab instructions | Embedded URL; optional images | Responsive stacked mobile layout. |
| `cover-launch-iframe` | 封面启动式应用 | Exhibition, immersive lesson opening | Embedded URL; cover image | Cover transitions to full app. |
| `editorial-image-text` | 图文阅读页 | Article, chapter, course reading | None if images are inlined | Alternating image/text sections. |
| `visual-story` | 沉浸式视觉叙事 | History, geography, case story, project showcase | None if images are inlined | Large visuals and scroll narrative. |
| `course-article` | 课程文章 | Objectives, reading, key points, activities | None if assets are inlined | Teaching-oriented structure. |
| `gallery-showcase` | 图库展示 | Portfolio, model references, comparison gallery | None if images are inlined | Responsive cards and captions. |

## Agent selection rules

- User says “URL 全屏” -> `fullscreen-iframe`.
- User wants title/navigation/status -> `app-shell-iframe`.
- User needs explanation beside the app -> `split-intro-iframe`.
- User wants an opening cover -> `cover-launch-iframe`.
- User wants “图文” without a live app -> offer `editorial-image-text`, `course-article`, and `visual-story`.
- User wants multiple images/reference views -> `gallery-showcase`.

## Common output

All templates must render to:

```text
dist/index.single.html
```

Use system font stacks and inline CSS/JS. Do not require external UI libraries.

## Selection decision matrix

Cross-reference **content type** (rows) against **deployment mode** (columns) to quickly narrow down the best template.

| Content type \ Mode | iframe-wrapper (deployed URL) | self-contained (offline) | network-dependent (remote assets) |
|---|---|---|---|
| Pure app display / kiosk | `fullscreen-iframe` | N/A (app needs backend) | N/A |
| Branded tool with chrome | `app-shell-iframe` | N/A | N/A |
| Intro text + live app | `split-intro-iframe` | N/A | N/A |
| Exhibition / immersive opener | `cover-launch-iframe` | N/A | N/A |
| Article / chapter reading | N/A | `editorial-image-text` | `editorial-image-text` |
| Teaching structured content | N/A | `course-article` | `course-article` |
| Scrolling visual narrative | N/A | `visual-story` | `visual-story` |
| Multi-image portfolio | N/A | `gallery-showcase` | `gallery-showcase` |

**Quick rules**:
- Has a live backend app? -> any `*-iframe` template.
- Static text + images only, want offline? -> any editorial template with inlined images.
- Static text + images, OK with network? -> any editorial template with remote image URLs.
- Need both context and a live app? -> `split-intro-iframe` or `cover-launch-iframe`.
