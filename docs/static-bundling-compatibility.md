# Static Bundling Compatibility

Use this before converting a built web application into one HTML file.

## Supported well

- Native HTML/CSS/JS projects.
- Static Vite output whose JavaScript bundle has no unresolved relative imports.
- Local images/audio/small media that can be converted to data URIs.
- Client-only SPAs that call public remote APIs at runtime.

## Not preservable inside one file

- Next.js API routes, server actions, SSR, middleware, or server components.
- Database, object-storage, authentication, workflow, or model services themselves.
- Secret-bearing backend calls.
- Node/Python server processes.
- Private environment variables.

For these, deploy the app and use an iframe wrapper.

## Preferred Vite route

When modifying a Vite project is allowed, use a single-file build plugin and keep the generic inliner as a verification/fallback tool. A config template is provided at `templates/single-html/vite.config.singlefile.ts`.

## Generic inliner rules

`scripts/single_html_tool.py bundle-static`:

- inlines local CSS and local script files;
- converts local image/icon/source references to data URIs;
- converts local CSS `url(...)` assets;
- leaves remote HTTP(S) resources as network dependencies;
- fails by default when bundled JavaScript still contains unresolved relative `import` statements;
- validates that no local file references remain;
- enforces a configurable maximum output size.

## Size guidance

Base64 adds roughly one-third overhead. Keep large video/GLB/STL outside the single HTML unless strict offline delivery is more important than file size. For large interactive teaching assets, offer:

1. one HTML + remote stable assets;
2. one HTML + deployed app iframe;
3. truly offline single HTML with an explicit size warning.

## Build decision

```text
static and client-only -> bundle-static
full-stack/server-dependent -> deploy + iframe wrapper
content-first -> editorial template
```
