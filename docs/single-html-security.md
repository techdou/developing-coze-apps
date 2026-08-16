# Single-HTML iframe Security and Compatibility

A one-file wrapper does not guarantee that the target URL can be embedded. Validate these conditions before claiming success.

## Frame-policy checks

| Check | Failure symptom | Action |
|---|---|---|
| `X-Frame-Options: DENY` | Blank/refused frame | Target must change headers or use a new-window link. |
| `X-Frame-Options: SAMEORIGIN` | Cross-origin embed refused | Host wrapper and app on permitted origin, or change target policy. |
| CSP `frame-ancestors` | Browser blocks iframe | Add the parent origin to the target policy. |
| HTTP target inside HTTPS wrapper | Mixed-content block | Use HTTPS only. |
| Third-party cookies/auth | Login loop/session loss | Test browser cookie policy and SameSite settings. |
| Camera/microphone/clipboard | Feature denied | Add only required iframe `allow` permissions and test browser prompts. |
| Cross-origin downloads/popups | Action blocked | Add minimum sandbox permissions only when needed. |

## Security profiles

### `trusted` — default for a first-party Coze app

- No `sandbox` attribute.
- `allow="fullscreen"` by default.
- Add microphone/camera/clipboard only when the app actually requires them.
- Use only when the embedded URL is trusted and controlled by the project owner.

### `restricted`

```html
sandbox="allow-scripts allow-forms allow-same-origin allow-popups allow-downloads"
```

May break authentication, downloads, payment flows, camera/microphone, or cross-origin integrations. Test the full workflow.

### `strict`

```html
sandbox="allow-scripts allow-forms"
```

Use for untrusted demonstrations only. Expect many applications to stop working.

## Mandatory checks

- URL scheme is `https://` for deployed use.
- No user-controlled `javascript:` URL.
- No secret/token is placed in query parameters or HTML source.
- `referrerpolicy` defaults to `strict-origin-when-cross-origin`.
- The wrapper has a visible loading/error fallback or open-in-new-window path unless the user explicitly requests a pure kiosk page.
- The generated HTML has a viewport meta tag and mobile-safe sizing.

## Limits of offline validation

`single_html_tool.py validate` can inspect the local wrapper, but it cannot conclusively prove remote response headers, cookie behavior, or browser permissions without live browser/network testing. Report those as `needs_runtime_check`.
