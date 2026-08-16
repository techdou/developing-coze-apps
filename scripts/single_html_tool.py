#!/usr/bin/env python3
"""Build and validate single-HTML deliverables for Coze applications.

Commands:
- list-templates
- inspect
- render
- bundle-static
- validate

The tool intentionally fails closed when a generic static bundle still contains
relative JavaScript imports or obvious server-only dependencies.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import mimetypes
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Literal
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates" / "single-html"
CATALOG_PATH = TEMPLATE_DIR / "catalog.json"
DEFAULT_OUT = Path("dist/index.single.html")

Severity = Literal["P0", "P1", "P2", "INFO"]


@dataclass
class Finding:
    level: Severity
    issue: str
    suggestion: str


def e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Config not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Config root must be a JSON object")
    return data


def load_catalog() -> dict[str, Any]:
    return load_json(CATALOG_PATH)


def get_template_meta(template_id: str) -> dict[str, Any]:
    for item in load_catalog().get("templates", []):
        if item.get("id") == template_id:
            return item
    raise ValueError(f"Unknown template: {template_id}")


def is_remote(value: str) -> bool:
    return value.startswith("https://") or value.startswith("http://") or value.startswith("//")


def is_data_uri(value: str) -> bool:
    return value.startswith("data:")


def placeholder_svg(label: str = "Image") -> str:
    safe = html.escape(label[:80])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#172554"/><stop offset="1" stop-color="#0f766e"/></linearGradient></defs>
<rect width="1200" height="800" fill="url(#g)"/><circle cx="920" cy="180" r="150" fill="#fff" opacity=".10"/><path d="M0 650L250 430L450 570L720 300L1200 690V800H0Z" fill="#fff" opacity=".12"/><text x="60" y="720" fill="#fff" font-family="system-ui,sans-serif" font-size="54" font-weight="700">{safe}</text></svg>'''
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def file_to_data_uri(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"Asset not found: {path}")
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    raw = path.read_bytes()
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


def resolve_asset(value: Any, base_dir: Path, label: str) -> str:
    s = str(value or "").strip()
    if not s:
        return placeholder_svg(label)
    if is_data_uri(s) or is_remote(s):
        return s
    candidate = Path(unquote(s))
    if not candidate.is_absolute():
        candidate = (base_dir / candidate).resolve()
    return file_to_data_uri(candidate)


def validate_embed_url(url: str, allow_http: bool = False) -> None:
    p = urlparse(url)
    if p.scheme not in {"http", "https"}:
        raise ValueError("Embedded URL must use http:// or https://")
    if p.scheme == "http" and not allow_http and p.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Deployed iframe URLs must use HTTPS; pass --allow-http only for controlled testing")
    if not p.netloc:
        raise ValueError("Embedded URL is missing a host")


def sandbox_attr(profile: str) -> str:
    profiles = {
        "trusted": "",
        "restricted": 'sandbox="allow-scripts allow-forms allow-same-origin allow-popups allow-downloads"',
        "strict": 'sandbox="allow-scripts allow-forms"',
    }
    if profile not in profiles:
        raise ValueError(f"Unknown security_profile: {profile}")
    return profiles[profile]


def allow_attr(value: Any) -> str:
    if value is None:
        return "fullscreen"
    if isinstance(value, str):
        parts = [x.strip() for x in re.split(r"[;,]", value) if x.strip()]
    elif isinstance(value, list):
        parts = [str(x).strip() for x in value if str(x).strip()]
    else:
        raise ValueError("allow must be a string or list")
    safe_allowed = {
        "fullscreen", "microphone", "camera", "clipboard-read", "clipboard-write",
        "geolocation", "display-capture", "autoplay", "encrypted-media"
    }
    unknown = sorted(set(parts) - safe_allowed)
    if unknown:
        raise ValueError(f"Unknown/unsupported iframe permissions: {', '.join(unknown)}")
    return "; ".join(dict.fromkeys(parts or ["fullscreen"]))


def slugify(text: str, index: int) -> str:
    s = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", text).strip("-").lower()
    return s[:60] or f"section-{index}"


def build_points(points: Any) -> str:
    if not isinstance(points, list):
        return ""
    return "".join(f"<li>{e(item)}</li>" for item in points)


def build_objectives(items: Any) -> str:
    if not isinstance(items, list):
        return ""
    return "".join(f"<li>{e(item)}</li>" for item in items)


def build_sections(template_id: str, sections: Any, base_dir: Path) -> str:
    if not isinstance(sections, list):
        return ""
    chunks: list[str] = []
    for idx, item in enumerate(sections, start=1):
        if not isinstance(item, dict):
            continue
        heading = e(item.get("heading", f"Section {idx}"))
        body = e(item.get("body", ""))
        alt = e(item.get("alt", item.get("heading", f"Section {idx}")))
        image = e(resolve_asset(item.get("image"), base_dir, str(item.get("heading", f"Section {idx}"))))
        caption = e(item.get("caption", ""))
        sid = e(slugify(str(item.get("heading", "")), idx))
        if template_id == "editorial-image-text":
            cap = f'<div class="caption">{caption}</div>' if caption else ""
            chunks.append(f'<section class="section" id="{sid}"><div class="media"><img src="{image}" alt="{alt}">{cap}</div><div class="copy"><h2>{heading}</h2><p>{body}</p></div></section>')
        elif template_id == "visual-story":
            chunks.append(f'<section class="story" id="{sid}"><img src="{image}" alt="{alt}"><div><div class="index">{idx:02d}</div><h2>{heading}</h2><p>{body}</p></div></section>')
        elif template_id == "course-article":
            img_html = f'<img src="{image}" alt="{alt}">' if item.get("image") else ""
            chunks.append(f'<section id="{sid}"><h2>{heading}</h2>{img_html}<p>{body}</p></section>')
    return "".join(chunks)


def build_gallery(items: Any, base_dir: Path) -> str:
    if not isinstance(items, list):
        return ""
    chunks = []
    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        title = e(item.get("title", f"Item {idx}"))
        desc = e(item.get("description", ""))
        alt = e(item.get("alt", title))
        tag = e(item.get("tag", f"{idx:02d}"))
        image = e(resolve_asset(item.get("image"), base_dir, str(item.get("title", f"Item {idx}"))))
        chunks.append(f'<article class="card"><img src="{image}" alt="{alt}"><div class="body"><div class="tag">{tag}</div><h2>{title}</h2><p>{desc}</p></div></article>')
    return "".join(chunks)


def render_template(template_id: str, config: dict[str, Any], config_dir: Path, allow_http: bool = False) -> str:
    meta = get_template_meta(template_id)
    missing = [k for k in meta.get("required", []) if config.get(k) in (None, "", [])]
    if missing:
        raise ValueError(f"Missing required config fields for {template_id}: {', '.join(missing)}")
    tpl_path = TEMPLATE_DIR / f"{template_id}.html"
    if not tpl_path.exists():
        raise ValueError(f"Template file missing: {tpl_path}")
    template = tpl_path.read_text(encoding="utf-8")

    is_iframe = bool(meta.get("iframe"))
    url = str(config.get("url", "")).strip()
    if is_iframe:
        validate_embed_url(url, allow_http=allow_http)

    hero_image = resolve_asset(config.get("hero_image"), config_dir, str(config.get("title", "Cover")))
    values = {
        "TITLE": e(config.get("title", "Coze Application")),
        "SUBTITLE": e(config.get("subtitle", config.get("summary", ""))),
        "KICKER": e(config.get("kicker", "Coze Learning Experience")),
        "SUMMARY": e(config.get("summary", "")),
        "LEAD": e(config.get("lead", config.get("summary", ""))),
        "ACTIVITY": e(config.get("activity", "")),
        "URL": e(url),
        "ACCENT": e(config.get("accent", "#2563eb")),
        "HERO_IMAGE": e(hero_image),
        "HERO_ALT": e(config.get("hero_alt", config.get("title", "Cover image"))),
        "SANDBOX_ATTR": sandbox_attr(str(config.get("security_profile", "trusted"))),
        "ALLOW": e(allow_attr(config.get("allow"))),
        "POINTS_HTML": build_points(config.get("points", [])),
        "OBJECTIVES_HTML": build_objectives(config.get("objectives", [])),
        "SECTIONS_HTML": build_sections(template_id, config.get("sections", []), config_dir),
        "ITEMS_HTML": build_gallery(config.get("items", []), config_dir),
    }
    result = template
    for key, value in values.items():
        result = result.replace("{{" + key + "}}", value)
    unresolved = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", result)))
    if unresolved:
        raise ValueError(f"Unresolved template tokens: {', '.join(unresolved)}")
    return result


def write_output(content: str, out: Path, force: bool = False) -> None:
    out = out.resolve()
    if out.exists() and not force:
        raise ValueError(f"Output exists: {out}; pass --force to overwrite")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")


def inspect_source(source: str) -> dict[str, Any]:
    if source.startswith(("https://", "http://")):
        return {
            "source": source,
            "kind": "deployed_url",
            "server_dependent": True,
            "recommended_modes": ["app-shell-iframe", "fullscreen-iframe", "split-intro-iframe"],
            "notes": ["Frame headers, cookies, and browser permissions require runtime testing."],
        }
    root = Path(source).resolve()
    if not root.exists():
        raise ValueError(f"Source not found: {root}")
    if root.is_file():
        root = root.parent
    package = {}
    package_path = root / "package.json"
    if package_path.exists():
        try:
            package = json.loads(package_path.read_text(encoding="utf-8"))
        except Exception:
            package = {}
    deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
    files = {str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*") if p.is_file()}
    next_markers = "next" in deps or any(x.startswith("app/api/") or x.startswith("pages/api/") for x in files)
    server_markers = next_markers or any(k in deps for k in ("express", "fastify", "@nestjs/core")) or any(x in files for x in ("server.js", "server.ts", "middleware.ts", "middleware.js"))
    vite = "vite" in deps or (root / "vite.config.ts").exists() or (root / "vite.config.js").exists()
    has_index = (root / "index.html").exists()
    if next_markers:
        kind = "nextjs_fullstack_or_hybrid"
        rec = ["deploy-then-app-shell-iframe", "deploy-then-fullscreen-iframe", "static-demo-only"]
    elif server_markers:
        kind = "server_dependent_web_app"
        rec = ["deploy-then-app-shell-iframe", "deploy-then-fullscreen-iframe"]
    elif vite:
        kind = "vite_static_candidate"
        rec = ["vite-singlefile-build", "bundle-static", "iframe-wrapper"]
    elif has_index:
        kind = "native_static_candidate"
        rec = ["bundle-static", "editorial-template", "iframe-wrapper"]
    else:
        kind = "unknown_project"
        rec = ["inspect-build-output", "iframe-wrapper"]
    return {
        "source": str(root),
        "kind": kind,
        "server_dependent": bool(server_markers),
        "vite": vite,
        "index_html": has_index,
        "recommended_modes": rec,
        "notes": ["A static bundle must not contain secrets or unresolved local imports."],
    }


def safe_local_path(base: Path, ref: str, guard: Path | None = None) -> Path | None:
    ref = ref.strip().split("#", 1)[0].split("?", 1)[0]
    if not ref or ref.startswith(("data:", "http://", "https://", "//", "mailto:", "tel:", "javascript:")):
        return None
    candidate = Path(unquote(ref))
    if str(candidate).startswith("/"):
        candidate = Path(str(candidate).lstrip("/"))
    resolved = (base / candidate).resolve()
    boundary = (guard or base).resolve()
    try:
        resolved.relative_to(boundary)
    except ValueError as exc:
        raise ValueError(f"Asset escapes input directory: {ref}") from exc
    return resolved


def inline_css_assets(css: str, css_dir: Path, root: Path) -> str:
    def repl(match: re.Match[str]) -> str:
        raw = match.group(1).strip().strip('"\'')
        path = safe_local_path(css_dir, raw, guard=root)
        if path is None:
            return match.group(0)
        if not path.exists():
            raise ValueError(f"CSS asset not found: {raw}")
        return f"url('{file_to_data_uri(path)}')"
    return re.sub(r"url\(([^)]+)\)", repl, css, flags=re.I)


def bundle_static(input_dir: Path, entry: str, max_mb: float, force_modules: bool = False) -> tuple[str, list[str]]:
    root = input_dir.resolve()
    entry_path = (root / entry).resolve()
    if not entry_path.exists():
        raise ValueError(f"Entry not found: {entry_path}")
    try:
        entry_path.relative_to(root)
    except ValueError as exc:
        raise ValueError("Entry must be inside input directory") from exc
    text = entry_path.read_text(encoding="utf-8")
    warnings: list[str] = []

    # Stylesheets.
    link_re = re.compile(r'<link\b([^>]*?)href=["\']([^"\']+)["\']([^>]*)>', re.I)
    def link_repl(match: re.Match[str]) -> str:
        attrs = (match.group(1) + " " + match.group(3)).lower()
        href = match.group(2)
        local = safe_local_path(root, href)
        if "stylesheet" in attrs and local:
            if not local.exists():
                raise ValueError(f"Stylesheet not found: {href}")
            css = inline_css_assets(local.read_text(encoding="utf-8"), local.parent, root)
            return f"<style data-inlined-from=\"{e(href)}\">\n{css}\n</style>"
        if any(x in attrs for x in ("icon", "apple-touch-icon")) and local:
            if not local.exists():
                raise ValueError(f"Icon not found: {href}")
            return match.group(0).replace(href, file_to_data_uri(local))
        return match.group(0)
    text = link_re.sub(link_repl, text)

    # Scripts.
    script_re = re.compile(r'<script\b([^>]*?)src=["\']([^"\']+)["\']([^>]*)>\s*</script>', re.I | re.S)
    def script_repl(match: re.Match[str]) -> str:
        before, src, after = match.group(1), match.group(2), match.group(3)
        local = safe_local_path(root, src)
        if local is None:
            warnings.append(f"Remote script remains network-dependent: {src}")
            return match.group(0)
        if not local.exists():
            raise ValueError(f"Script not found: {src}")
        js = local.read_text(encoding="utf-8")
        if re.search(r"(?:^|[;\n])\s*(?:import|export)\s+.*?(?:from\s*)?[\"\']\.{1,2}/", js) or re.search(r"import\(\s*[\"\']\.{1,2}/", js):
            if not force_modules:
                raise ValueError(f"Unresolved relative module import remains in {src}; use a proper single-file Vite build or --force-modules for diagnostic use")
            warnings.append(f"Forced inlining with unresolved module imports: {src}")
        attrs = re.sub(r"\s*src=[\"\'][^\"\']+[\"\']", "", before + after, flags=re.I)
        return f"<script {attrs.strip()} data-inlined-from=\"{e(src)}\">\n{js}\n</script>"
    text = script_re.sub(script_repl, text)

    # Media and image attributes.
    attr_re = re.compile(r'\b(src|poster)=["\']([^"\']+)["\']', re.I)
    def attr_repl(match: re.Match[str]) -> str:
        name, value = match.group(1), match.group(2)
        local = safe_local_path(root, value)
        if local is None:
            if is_remote(value):
                warnings.append(f"Remote asset remains network-dependent: {value}")
            return match.group(0)
        if not local.exists():
            raise ValueError(f"Asset not found: {value}")
        return f'{name}="{file_to_data_uri(local)}"'
    text = attr_re.sub(attr_repl, text)

    # srcset (simple comma-separated candidates).
    srcset_re = re.compile(r'\bsrcset=["\']([^"\']+)["\']', re.I)
    def srcset_repl(match: re.Match[str]) -> str:
        candidates = []
        for part in match.group(1).split(","):
            bits = part.strip().split()
            if not bits:
                continue
            local = safe_local_path(root, bits[0])
            if local:
                if not local.exists():
                    raise ValueError(f"srcset asset not found: {bits[0]}")
                bits[0] = file_to_data_uri(local)
            candidates.append(" ".join(bits))
        return 'srcset="' + e(", ".join(candidates)) + '"'
    text = srcset_re.sub(srcset_repl, text)

    if not re.search(r"<meta\s+name=[\"']viewport[\"']", text, re.I):
        text = re.sub(r"<head([^>]*)>", r'<head\1>\n<meta name="viewport" content="width=device-width,initial-scale=1">', text, count=1, flags=re.I)
    size = len(text.encode("utf-8"))
    if size > max_mb * 1024 * 1024:
        raise ValueError(f"Output would be {size/1024/1024:.2f} MB, exceeding --max-mb {max_mb}")
    return text, sorted(set(warnings))


def validate_single_html(path: Path, max_mb: float = 25.0) -> dict[str, Any]:
    findings: list[Finding] = []
    if not path.exists():
        return {"path": str(path), "status": "missing", "findings": [asdict(Finding("P0", "File does not exist", "Generate the HTML first."))]}
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        findings.append(Finding("P0", "File is not UTF-8 HTML", "Write the file as UTF-8."))
        text = raw.decode("utf-8", errors="ignore")
    size_mb = len(raw) / 1024 / 1024
    if size_mb > max_mb:
        findings.append(Finding("P1", f"File size is {size_mb:.2f} MB", "Review large base64 assets or raise the accepted limit deliberately."))
    if not re.search(r"<!doctype\s+html", text, re.I):
        findings.append(Finding("P1", "Missing HTML5 doctype", "Add <!doctype html>."))
    if not re.search(r"<meta\s+name=[\"']viewport[\"']", text, re.I):
        findings.append(Finding("P1", "Missing viewport meta tag", "Add a mobile viewport meta tag."))
    if not re.search(r"<title>.*?</title>", text, re.I | re.S):
        findings.append(Finding("P2", "Missing document title", "Add a meaningful <title>."))
    if re.search(r"\{\{[A-Z0-9_]+\}\}", text):
        findings.append(Finding("P0", "Unresolved template token found", "Render all template placeholders."))
    secret_patterns = [
        r"sk-[A-Za-z0-9_-]{20,}", r"sat_[A-Za-z0-9_-]{20,}",
        r"(?i)(api[_-]?key|service[_-]?role[_-]?key|secret|token)\s*[:=]\s*[\"'][^\"']{12,}[\"']"
    ]
    if any(re.search(p, text) for p in secret_patterns):
        findings.append(Finding("P0", "Possible secret/token embedded in HTML", "Remove and rotate the secret; use a server-side API."))

    refs = re.findall(r'\b(?:src|href|poster)=["\']([^"\']+)["\']', text, re.I)
    local_refs, remote_refs = [], []
    for ref in refs:
        if ref.startswith(("#", "data:", "mailto:", "tel:", "javascript:")):
            continue
        if ref.startswith(("https://", "http://", "//")):
            remote_refs.append(ref)
        else:
            local_refs.append(ref)
    css_refs = []
    for ref in re.findall(r"url\(([^)]+)\)", text, re.I):
        ref = ref.strip().strip('"\'')
        if not ref.startswith(("data:", "https://", "http://", "//", "#")):
            css_refs.append(ref)
    if local_refs or css_refs:
        remaining = sorted(set(local_refs + css_refs))[:5]
        findings.append(Finding("P0", f"Local external references remain: {remaining}", "Inline local assets or correct the bundle."))

    iframe_urls = re.findall(r'<iframe\b[^>]*\bsrc=["\']([^"\']+)["\']', text, re.I)
    for url in iframe_urls:
        try:
            validate_embed_url(html.unescape(url), allow_http=False)
        except ValueError as exc:
            findings.append(Finding("P0", f"Invalid iframe URL: {exc}", "Use a deployed HTTPS URL."))
    if iframe_urls:
        if "referrerpolicy=" not in text.lower():
            findings.append(Finding("P2", "iframe has no referrerpolicy", "Use strict-origin-when-cross-origin unless the app requires otherwise."))
        findings.append(Finding("INFO", "Remote frame policy cannot be proven offline", "Test X-Frame-Options, CSP frame-ancestors, cookies, and required browser permissions."))

    if iframe_urls:
        status = "iframe-wrapper"
    elif remote_refs:
        status = "single-file-network-dependent"
    else:
        status = "self-contained"
    return {
        "path": str(path.resolve()),
        "status": status,
        "size_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "remote_dependencies": sorted(set(remote_refs)),
        "iframe_urls": iframe_urls,
        "findings": [asdict(x) for x in findings],
    }


def format_validation_md(result: dict[str, Any]) -> str:
    lines = ["# Single HTML Validation", "", f"- Path: `{result.get('path')}`", f"- Status: `{result.get('status')}`"]
    if "size_bytes" in result:
        lines.append(f"- Size: {result['size_bytes']/1024:.1f} KiB")
        lines.append(f"- SHA-256: `{result.get('sha256')}`")
    deps = result.get("remote_dependencies", [])
    if deps:
        lines += ["", "## Remote dependencies"] + [f"- {x}" for x in deps]
    findings = result.get("findings", [])
    if findings:
        lines += ["", "## Findings", "", "| Level | Issue | Suggestion |", "|---|---|---|"]
        for item in findings:
            lines.append(f"| {item['level']} | {item['issue']} | {item['suggestion']} |")
    else:
        lines += ["", "No findings detected."]
    return "\n".join(lines)


def cmd_list_templates(args: argparse.Namespace) -> int:
    catalog = load_catalog()
    if args.format == "json":
        print(json.dumps(catalog, ensure_ascii=False, indent=2))
    else:
        print("# Single-HTML Templates\n")
        print("| ID | Name | Source | Status |")
        print("|---|---|---|---|")
        for item in catalog.get("templates", []):
            print(f"| `{item['id']}` | {item['name_zh']} | {item['source_kind']} | {item['status']} |")
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    result = inspect_source(args.source)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("# Single-HTML Source Inspection\n")
        for key in ("source", "kind", "server_dependent", "vite", "index_html"):
            if key in result:
                print(f"- {key}: `{result[key]}`")
        print("\n## Recommended modes")
        for x in result["recommended_modes"]:
            print(f"- `{x}`")
        for note in result.get("notes", []):
            print(f"\n> {note}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    config_path = Path(args.config).resolve()
    config = load_json(config_path)
    content = render_template(args.template, config, config_path.parent, allow_http=args.allow_http)
    out = Path(args.out or DEFAULT_OUT)
    write_output(content, out, force=args.force)
    result = validate_single_html(out, max_mb=args.max_mb)
    if any(f["level"] == "P0" for f in result["findings"]):
        print(format_validation_md(result), file=sys.stderr)
        return 1
    print(f"Created {out.resolve()} ({result['status']}, {result['size_bytes']} bytes)")
    return 0


def cmd_bundle(args: argparse.Namespace) -> int:
    content, warnings = bundle_static(Path(args.input_dir), args.entry, args.max_mb, force_modules=args.force_modules)
    out = Path(args.out or DEFAULT_OUT)
    write_output(content, out, force=args.force)
    result = validate_single_html(out, max_mb=args.max_mb)
    if warnings:
        for warning in warnings:
            print(f"warning: {warning}", file=sys.stderr)
    if any(f["level"] == "P0" for f in result["findings"]):
        print(format_validation_md(result), file=sys.stderr)
        return 1
    print(f"Created {out.resolve()} ({result['status']}, {result['size_bytes']} bytes)")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    result = validate_single_html(Path(args.file), max_mb=args.max_mb)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_validation_md(result))
    return 1 if any(f["level"] == "P0" for f in result.get("findings", [])) else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list-templates")
    p.add_argument("--format", choices=["md", "json"], default="md")
    p.set_defaults(func=cmd_list_templates)

    p = sub.add_parser("inspect")
    p.add_argument("--source", required=True)
    p.add_argument("--format", choices=["md", "json"], default="md")
    p.set_defaults(func=cmd_inspect)

    p = sub.add_parser("render")
    p.add_argument("--template", required=True)
    p.add_argument("--config", required=True)
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--allow-http", action="store_true")
    p.add_argument("--max-mb", type=float, default=25.0)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("bundle-static")
    p.add_argument("--input-dir", required=True)
    p.add_argument("--entry", default="index.html")
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--max-mb", type=float, default=25.0)
    p.add_argument("--force-modules", action="store_true", help="Diagnostic only; may produce a broken file")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_bundle)

    p = sub.add_parser("validate")
    p.add_argument("file")
    p.add_argument("--format", choices=["md", "json"], default="md")
    p.add_argument("--max-mb", type=float, default=25.0)
    p.set_defaults(func=cmd_validate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("cancelled", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
