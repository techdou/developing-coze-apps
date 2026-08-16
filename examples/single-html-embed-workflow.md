# Example: Coze Web App -> Single HTML -> iframe Delivery

## User request

A Coze web app has already been deployed. The teaching platform accepts one HTML file and renders it through an iframe.

## Agent response pattern

1. Inspect whether the user has a deployed HTTPS URL or only source code.
2. Offer three schemes:
   - full-screen app;
   - app shell with title/refresh/open controls;
   - course introduction + app split layout.
3. Recommend `app-shell-iframe` for a general teaching-tool delivery unless the user explicitly wants a kiosk.
4. Confirm required capabilities such as microphone/camera before adding iframe permissions.
5. Render to `dist/index.single.html`.
6. Validate local references, secrets, viewport, URL scheme, file size, and iframe assumptions.
7. Tell the user that remote frame headers and login cookies still require browser testing.

## Example command

```bash
python scripts/single_html_tool.py render \
  --template app-shell-iframe \
  --config templates/single-html/config-examples/app-shell-iframe.json \
  --out dist/index.single.html
python scripts/single_html_tool.py validate dist/index.single.html --format md
```
