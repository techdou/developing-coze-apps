#!/usr/bin/env python3
"""Audit helper for Coze Coding / Vibe Coding / hybrid web projects.

This is a static heuristic checker. It does not require network access and is not
a substitute for build/typecheck/security review.

Examples:

    python scripts/coze_project_audit.py . --format md
    python scripts/coze_project_audit.py . --format json --strict --fail-on P1
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Literal

TEXT_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json", ".env", ".md", ".sql"}
CODE_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
IGNORE_DIRS = {"node_modules", ".next", "dist", "build", ".git", ".turbo", "coverage", ".vercel", ".output"}
FRONTEND_HINTS = ("components/", "app/", "pages/", "src/components/", "src/pages/")
SERVER_HINTS = ("api/", "server/", "actions", "route.ts", "route.js", "middleware", "lib/server", "src/server")
FILTER_METHODS = (".eq(", ".neq(", ".match(", ".filter(", ".in(", ".is(", ".lt(", ".lte(", ".gt(", ".gte(")

SECRET_VALUE_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"sat_[A-Za-z0-9_\-]{20,}"),
    re.compile(r"eyJ[A-Za-z0-9_\-]{30,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token|service[_-]?role)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
]

Level = Literal["P0", "P1", "P2", "INFO"]

@dataclass
class Finding:
    level: Level
    file: str
    issue: str
    suggestion: str


def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix in TEXT_EXTS or path.name.startswith(".env"):
                yield path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def is_frontend_path(r: str) -> bool:
    # Next.js app/api is server; app/* component pages can still contain client code.
    if "/api/" in r or r.startswith("app/api/"):
        return False
    return any(h in r for h in FRONTEND_HINTS) and not any(h in r for h in SERVER_HINTS)


def is_server_path(r: str) -> bool:
    return any(h in r for h in SERVER_HINTS)


def chain_has_filter(text: str, start: int) -> bool:
    snippet = text[start:start + 500]
    semi = snippet.find(";")
    if semi != -1:
        snippet = snippet[:semi]
    return any(m in snippet for m in FILTER_METHODS)


def audit_package_json(root: Path, findings: list[Finding]) -> None:
    package_json = root / "package.json"
    if not package_json.exists():
        if (root / "SKILL.md").exists():
            findings.append(Finding("INFO", "package.json", "package.json not found; root looks like a skill package, not a web project.", "Use validate_skill_package.py for skill validation."))
        else:
            findings.append(Finding("P1", "package.json", "package.json not found.", "Confirm this is a web/code project or add package metadata."))
        return
    try:
        pkg = json.loads(package_json.read_text(encoding="utf-8"))
    except Exception as exc:
        findings.append(Finding("P1", "package.json", f"Cannot parse package.json: {exc}", "Fix package.json syntax."))
        return
    scripts = pkg.get("scripts", {})
    for needed in ["dev", "build"]:
        if needed not in scripts:
            findings.append(Finding("P1", "package.json", f"Missing npm script: {needed}.", f"Add a `{needed}` script or document the alternative command."))
    if "lint" not in scripts:
        findings.append(Finding("P2", "package.json", "Missing npm script: lint.", "Add linting or document why unavailable."))
    if "typecheck" not in scripts and "tsc" not in " ".join(str(v) for v in scripts.values()):
        findings.append(Finding("P2", "package.json", "No obvious typecheck script.", "Add `typecheck` using `tsc --noEmit` for TypeScript projects."))


def audit_env_files(root: Path, findings: list[Finding]) -> None:
    for env in sorted(root.glob(".env*")):
        if env.is_file():
            findings.append(Finding("INFO", rel(env, root), "Environment file exists.", "Ensure it is ignored by git and never copied into frontend bundles."))
    gitignore = root / ".gitignore"
    if gitignore.exists():
        text = read_text(gitignore)
        if ".env" not in text:
            findings.append(Finding("P1", ".gitignore", ".env files are not clearly ignored.", "Add `.env*` with exceptions only for safe examples like `.env.example`."))


def audit_file(path: Path, root: Path, findings: list[Finding], strict: bool) -> None:
    text = read_text(path)
    r = rel(path, root)
    suffix = path.suffix

    if not text:
        return

    # Hard-coded secret-like values.
    for pat in SECRET_VALUE_PATTERNS:
        if pat.search(text):
            level: Level = "P0" if suffix != ".md" else "P1"
            findings.append(Finding(level, r, "Possible hard-coded secret/token/API key.", "Move secrets to environment variables; rotate exposed values."))
            break

    is_code = suffix in CODE_EXTS

    # SDK/model clients should be server-only.
    server_only_terms = ["coze-coding-dev-sdk", "LLMClient", "ImageGenerationClient", "VideoGenerationClient", "TTSClient", "ASRClient", "S3Storage", "SERVICE_ROLE"]
    if is_code and any(term in text for term in server_only_terms) and is_frontend_path(r):
        findings.append(Finding("P0", r, "Server-only SDK/client appears in frontend path.", "Move model/storage/database privileged calls to API routes or server actions."))

    # Browser-exposed env vars.
    if is_code and re.search(r"process\.env\.(?!NEXT_PUBLIC_)[A-Z0-9_]+", text) and is_frontend_path(r):
        findings.append(Finding("P0", r, "Private environment variable referenced in frontend path.", "Read private env vars only in server code."))
    if is_code and "NEXT_PUBLIC_" in text and re.search(r"NEXT_PUBLIC_.*(KEY|TOKEN|SECRET|SERVICE|ROLE)", text, re.I):
        findings.append(Finding("P0", r, "Potentially sensitive value exposed through NEXT_PUBLIC_*.", "Only expose non-sensitive public config to the browser."))

    # Supabase-style update/delete without chain filter.
    if is_code:
        update_delete_iter = re.finditer(r"\.(update|delete)\s*\(", text)
    else:
        update_delete_iter = []
    for match in update_delete_iter:
        if not chain_has_filter(text, match.start()):
            findings.append(Finding("P1", r, "Database update/delete may lack explicit filter in method chain.", "Add `.eq()`, `.match()`, or another filter before executing the query."))
            break

    # Signed URL persistence.
    if is_code and re.search(r"(signedUrl|signed_url|presignedUrl|presigned_url|temporaryUrl|temporary_url)", text):
        if re.search(r"(insert|upsert|create|save|persist|update)\s*\(", text, re.I):
            findings.append(Finding("P1", r, "Possible persistence of a temporary/signed URL.", "Persist storage object keys/file_key; generate signed URLs only for display/download."))

    # SSE hints for AI streaming routes.
    if is_code and is_server_path(r) and re.search(r"(ReadableStream|text/event-stream|SSE|stream\()", text):
        if "text/event-stream" not in text:
            findings.append(Finding("P1", r, "Streaming route found without explicit text/event-stream header.", "Set `Content-Type: text/event-stream`, disable caching, and handle disconnects."))
        if strict and not re.search(r"(try\s*\{|catch\s*\(|finally\s*\{)", text):
            findings.append(Finding("P1", r, "Streaming/AI route has no obvious try/catch.", "Add explicit error handling and terminal event payloads."))

    # Long-running task hints.
    if is_code and strict and re.search(r"(video|seedance|generateVideo|VideoGeneration|long[-_ ]?running)", text, re.I):
        if not re.search(r"(queued|running|succeeded|failed|cancelled|task_status|status)", text, re.I):
            findings.append(Finding("P1", r, "Video/long-running task lacks obvious async status handling.", "Use task state: queued/running/succeeded/failed/cancelled and polling/SSE heartbeat."))

    # API routes should usually have error handling.
    if is_code and strict and is_server_path(r) and re.search(r"export\s+async\s+function\s+(GET|POST|PUT|PATCH|DELETE)", text):
        if "try" not in text or "catch" not in text:
            findings.append(Finding("P1", r, "API route has no obvious try/catch.", "Add input validation, structured errors, and logging."))



def audit_single_html_output(root: Path, findings: list[Finding]) -> None:
    target = root / "dist" / "index.single.html"
    if not target.exists():
        return
    try:
        from single_html_tool import validate_single_html
        result = validate_single_html(target)
    except Exception as exc:
        findings.append(Finding("P1", "dist/index.single.html", f"Could not run single-HTML validation: {exc}", "Run `python scripts/single_html_tool.py validate dist/index.single.html --format md`."))
        return
    for item in result.get("findings", []):
        level = item.get("level", "P2")
        if level not in {"P0", "P1", "P2", "INFO"}:
            level = "P2"
        findings.append(Finding(level, "dist/index.single.html", item.get("issue", "Single-HTML validation finding"), item.get("suggestion", "Review the generated file.")))
    findings.append(Finding("INFO", "dist/index.single.html", f"Single-HTML status: {result.get('status')}; size={result.get('size_bytes', 0)} bytes.", "For iframe wrappers, still test frame headers, cookies, and browser permissions at runtime."))

def audit_supabase_consistency(root: Path, findings: list[Finding]) -> None:
    """Check that terminal env vars and deployed /api/supabase-config point to the same Supabase instance.
    
    Detects a common failure mode: after re-deployment, the platform may create a new
    Supabase instance, while the terminal session still holds env vars for the old one.
    This causes admin operations (password reset, quota changes) via the terminal to
    affect the wrong Supabase project, while the browser talks to the new one.
    """
    import urllib.request

    supabase_url = os.environ.get("COZE_SUPABASE_URL", "")
    supabase_anon = os.environ.get("COZE_SUPABASE_ANON_KEY", "")

    if not supabase_url or not supabase_anon:
        # No Supabase configured, skip check
        return

    def extract_slug(url: str) -> str:
        try:
            from urllib.parse import urlparse
            host = urlparse(url).hostname or ""
            parts = host.split(".")
            return parts[0] if parts else host
        except Exception:
            return url

    terminal_slug = extract_slug(supabase_url)

    # Check deployed API
    domain = os.environ.get("COZE_PROJECT_DOMAIN_DEFAULT", "")
    deployed_slug = ""
    deployed_anon = ""

    if domain:
        try:
            base = domain if domain.startswith("http") else f"https://{domain}"
            with urllib.request.urlopen(f"{base}/api/supabase-config", timeout=10) as resp:
                data = json.loads(resp.read().decode())
                deployed_url = data.get("url", "")
                deployed_anon = data.get("anonKey", "")
                deployed_slug = extract_slug(deployed_url)
        except Exception:
            pass

    if not deployed_slug:
        findings.append(Finding("P2", "env", "Cannot check deployed Supabase config (domain unavailable or /api/supabase-config missing)", "Ensure COZE_PROJECT_DOMAIN_DEFAULT is set and /api/supabase-config endpoint exists."))
        return

    if terminal_slug != deployed_slug:
        findings.append(Finding("P0", "env", 
            f"Terminal Supabase ({terminal_slug}) != Deployed ({deployed_slug}). "
            "Re-deployment likely created a new instance. "
            "Admin operations (password reset, quota changes) via terminal will affect the WRONG instance. ",
            "Run: python scripts/check_supabase_consistency.py --fix"))

    if deployed_anon and supabase_anon and deployed_anon != supabase_anon:
        findings.append(Finding("P0", "env",
            "Terminal and deployed Supabase anon keys differ — confirming different projects.",
            "Re-deploy or update terminal env vars to match the production instance."))


def to_markdown(root: Path, findings: list[Finding]) -> str:
    lines = [f"# Coze Project Audit", "", f"Root: `{root}`", ""]
    if not findings:
        lines.append("No findings detected by static heuristics.")
        return "\n".join(lines)
    order = {"P0": 0, "P1": 1, "P2": 2, "INFO": 3}
    for level in ["P0", "P1", "P2", "INFO"]:
        group = [f for f in findings if f.level == level]
        if not group:
            continue
        lines += [f"## {level}", ""]
        lines.append("| File | Issue | Suggestion |")
        lines.append("|---|---|---|")
        for f in sorted(group, key=lambda x: (order[x.level], x.file, x.issue)):
            lines.append(f"| `{f.file}` | {f.issue} | {f.suggestion} |")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".", help="Project root to audit")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    parser.add_argument("--strict", action="store_true", help="Enable additional heuristic checks")
    parser.add_argument("--fail-on", choices=["P0", "P1", "P2"], default="P0", help="Exit non-zero if findings at or above this level exist")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings: list[Finding] = []

    if not root.exists():
        print(f"Root not found: {root}", file=sys.stderr)
        return 2

    audit_package_json(root, findings)
    audit_env_files(root, findings)
    for path in iter_files(root):
        audit_file(path, root, findings, args.strict)
    audit_single_html_output(root, findings)
    audit_supabase_consistency(root, findings)

    if args.format == "json":
        print(json.dumps({"root": str(root), "findings": [asdict(f) for f in findings]}, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(root, findings))

    rank = {"P0": 0, "P1": 1, "P2": 2, "INFO": 3}
    threshold = rank[args.fail_on]
    return 1 if any(rank[f.level] <= threshold for f in findings if f.level != "INFO") else 0


if __name__ == "__main__":
    raise SystemExit(main())
