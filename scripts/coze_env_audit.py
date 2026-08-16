#!/usr/bin/env python3
"""Audit DEV/PROD environment separation for Coze Coding projects.

Static heuristic checker. It intentionally does not mutate Coze resources and does
not assume a specific managed database/storage implementation.

Examples:
  python scripts/coze_env_audit.py . --format md
  python scripts/coze_env_audit.py . --format json --strict --fail-on P1
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Literal

Level = Literal["P0", "P1", "P2", "INFO"]

IGNORE_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", "coverage", ".turbo",
    ".vercel", ".output", "vendor", "target", "__pycache__",
}
TEXT_EXTS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".sh", ".bash",
    ".json", ".yaml", ".yml", ".toml", ".md", ".sql", ".env", ".txt",
}
CODE_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".sh", ".bash"}
CLIENT_HINTS = (
    "components/", "src/components/", "src/pages/", "app/", "pages/", "client/",
)
SERVER_EXCLUSIONS = ("/api/", "app/api/", "server/", "src/server/", "route.ts", "route.js")

PLATFORM_PREFIXES = ("COZE_",)
PRIVILEGED_NAMES = (
    "SERVICE_ROLE", "SERVICE_ROLE_KEY", "BOOTSTRAP_TOKEN", "PRIVATE_KEY",
    "SECRET_KEY", "API_SECRET", "DATABASE_PASSWORD", "DB_PASSWORD",
)

SECRET_VALUE_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sat_[A-Za-z0-9_-]{20,}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    re.compile(r"(?i)(token|secret|password|service[_-]?role|api[_-]?key)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
]

DEFAULT_ADMIN_PATTERNS = [
    re.compile(r"admin@(?:localhost|[^\s'\"]+\.local)\b", re.I),
    re.compile(r"(?i)BOOTSTRAP_ADMIN_PASSWORD\s*=\s*(Admin@?\d+|password|changeme|admin123)\b"),
    re.compile(r"(?i)(default|demo|test)[_-]?admin.*password"),
]


@dataclass
class Finding:
    level: Level
    rule: str
    file: str
    issue: str
    suggestion: str


def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() in TEXT_EXTS or p.name.startswith(".env"):
                yield p


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


def is_client_path(r: str) -> bool:
    if any(x in r for x in SERVER_EXCLUSIONS):
        return False
    return any(x in r for x in CLIENT_HINTS)


def add(findings: list[Finding], level: Level, rule: str, file: str, issue: str, suggestion: str) -> None:
    key = (level, rule, file, issue)
    if any((f.level, f.rule, f.file, f.issue) == key for f in findings):
        return
    findings.append(Finding(level, rule, file, issue, suggestion))


def audit_gitignore(root: Path, findings: list[Finding]) -> None:
    gi = root / ".gitignore"
    if not gi.exists():
        add(findings, "P1", "ENV001", ".gitignore", ".gitignore is missing.",
            "Ignore `.env`, `.env.*`, and especially `.env.local`; allowlist only safe examples.")
        return
    text = read_text(gi)
    if not re.search(r"(?m)^\.env(?:\.\*|\*)?\s*$", text) and ".env*" not in text:
        add(findings, "P1", "ENV001", ".gitignore", "Environment files are not broadly ignored.",
            "Add `.env` and `.env.*`/`.env*`, then explicitly allow safe `.env.example` if needed.")
    if ".env.local" not in text and ".env*" not in text and ".env.*" not in text:
        add(findings, "P1", "ENV002", ".gitignore", "`.env.local` is not clearly ignored.",
            "Treat `.env.local` as local/DEV-only and exclude it from version control/deployment source.")


def audit_env_files(root: Path, findings: list[Finding], strict: bool) -> None:
    for p in root.glob(".env*"):
        if not p.is_file():
            continue
        r = rel(p, root)
        text = read_text(p)
        is_example = p.name in {".env.example", ".env.sample", ".env.template"}
        if p.name == ".env.local":
            add(findings, "P1", "ENV003", r, "`.env.local` exists in project root.",
                "Keep it DEV-only, ensure git ignores it, and verify production build/start scripts cannot load/copy it.")
        if not is_example:
            for pat in SECRET_VALUE_PATTERNS:
                if pat.search(text):
                    add(findings, "P0", "SEC001", r, "Possible real secret/token is stored in an environment file present in the project tree.",
                        "Remove it from deploy/source artifacts and rotate it if it was committed or exposed.")
                    break
        for pat in DEFAULT_ADMIN_PATTERNS:
            if pat.search(text):
                add(findings, "P0" if strict and not is_example else "P1", "AUTH001", r,
                    "Default/demo administrator credential appears in environment configuration.",
                    "Do not use known DEV/default admin credentials in PROD; use a project-specific protected bootstrap/onboarding flow.")
                break
        # Real values under platform-owned names are suspicious outside examples.
        if not is_example:
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key.startswith(PLATFORM_PREFIXES) and value.strip():
                    add(findings, "P1", "ENV004", r,
                        f"Platform-prefixed variable `{key}` has a concrete value in a project env file.",
                        "Verify this is not a copied DEV platform value. Prefer the current Coze runtime-injected PROD value where applicable.")


def audit_source_file(path: Path, root: Path, findings: list[Finding], strict: bool) -> None:
    text = read_text(path)
    if not text:
        return
    r = rel(path, root)
    lower = text.lower()
    suffix = path.suffix.lower()
    is_code = suffix in CODE_EXTS

    # Secrets/client exposure.
    if is_code and is_client_path(r):
        for name in PRIVILEGED_NAMES:
            if name in text:
                add(findings, "P0", "WEB001", r,
                    f"Privileged configuration name `{name}` appears in a client/frontend path.",
                    "Move privileged configuration and calls to server/BFF code; expose only an allowlisted client-safe subset.")
                break
        if re.search(r"NEXT_PUBLIC_[A-Z0-9_]*(SERVICE|ROLE|SECRET|PASSWORD|TOKEN|PRIVATE)", text, re.I):
            add(findings, "P0", "WEB002", r,
                "Potential private credential is exposed through a client-public environment variable.",
                "Remove it from `NEXT_PUBLIC_*`; browser-public variables must contain only intentionally public values.")

    # Hard-coded dev/local endpoints in production-capable code.
    if is_code and re.search(r"https?://(?:localhost|127\.0\.0\.1|[^/\s'\"]+\.dev\.coze\.site)", text, re.I):
        if not re.search(r"(?i)(test|mock|example|fixture)", r):
            add(findings, "P1", "ENV005", r,
                "Hard-coded local/DEV URL appears in application code.",
                "Move environment-specific origins to classified config and verify the production value/build bundle.")

    # Startup explicitly loading local env.
    if (suffix in {".sh", ".bash", ".js", ".mjs", ".cjs", ".py"} or "start" in r.lower() or "deploy" in r.lower()):
        if re.search(r"(?i)(dotenv[^\n]*\.env\.local|source\s+\.env\.local|loadenv[^\n]*\.env\.local|\.env\.local)", text):
            add(findings, "P0" if strict else "P1", "ENV006", r,
                "Build/start/deploy logic references `.env.local`.",
                "Remove production dependence on local env files; use runtime production configuration.")

    # Automatic privileged bootstrap during startup.
    if re.search(r"(?i)(bootstrap|init[-_ ]?admin|first[-_ ]?admin)", text) and re.search(r"(?i)(start|startup|entrypoint|listen|next start|node .*server)", text):
        if re.search(r"(?i)(curl|fetch|request|post).*bootstrap", text, re.S):
            add(findings, "P1", "AUTH002", r,
                "Startup logic appears to invoke an admin/bootstrap endpoint automatically.",
                "Prefer explicit one-time production bootstrap after DB/Auth identity and migrations are verified; never use DEV defaults.")

    # Privileged -> anon/public fallback heuristic.
    if re.search(r"(?i)(SERVICE_ROLE|serviceRole).{0,160}(ANON|anonKey|anonymous)", text, re.S):
        if re.search(r"\|\||\?\?|fallback|else", text, re.I):
            add(findings, "P0" if strict else "P1", "SEC002", r,
                "Privileged credential may fall back to anonymous/public credentials.",
                "In production, fail fast when privileged credentials are required instead of silently downgrading.")

    # Public config endpoint leaking service/admin key.
    if re.search(r"(?i)(supabase-config|runtime-config|public-config)", r + "\n" + text):
        if re.search(r"(?i)(SERVICE_ROLE|BOOTSTRAP_TOKEN|PRIVATE_KEY|API_SECRET)", text):
            add(findings, "P0", "WEB003", r,
                "Runtime/public config code references privileged secret material.",
                "Return only explicitly client-safe fields; never expose service-role/bootstrap/private secrets.")

    # Signed URL persistence heuristic.
    if is_code and re.search(r"(?i)(presigned|signed[_-]?url|temporary[_-]?url)", text):
        if re.search(r"(?i)(insert|upsert|update|create|save|persist)", text):
            add(findings, "P1", "STORAGE001", r,
                "Code may persist a temporary/signed URL.",
                "Persist the object key/ID and generate the current access URL at read/display time.")

    # Seed/default admin.
    if suffix == ".sql" or "seed" in r.lower():
        if re.search(r"(?i)(admin@|role.{0,40}admin|BOOTSTRAP_ADMIN)", text):
            add(findings, "P1", "AUTH003", r,
                "Seed/migration content appears to create or encode an administrator.",
                "Separate production-safe reference seeds from privileged first-admin provisioning.")

    # Full dev->prod language in automation/docs can be dangerous; only flag automation code.
    if is_code and re.search(r"(?i)(sync|copy|clone).{0,80}(dev|development).{0,80}(prod|production)", text, re.S):
        if not re.search(r"(?i)(allowlist|dry[-_ ]?run|confirm|explicit)", text):
            add(findings, "P1", "DB001", r,
                "Automation appears to copy/sync DEV data to PROD without an obvious allowlist/confirmation.",
                "Default ordinary DEV business data sync to off; promote schema via migrations and explicitly approve data/assets.")


def audit_migration_posture(root: Path, findings: list[Finding]) -> None:
    candidates = [root / "supabase" / "migrations", root / "migrations", root / "db" / "migrations"]
    has_db_code = False
    for p in iter_files(root):
        t = read_text(p)
        if re.search(r"(?i)(supabase|postgres|database|drizzle|prisma|pgdatabase)", t):
            has_db_code = True
            break
    if has_db_code and not any(p.exists() and p.is_dir() for p in candidates):
        add(findings, "P2", "DB002", "migrations/",
            "Database usage detected but no common migration directory was found.",
            "Document the schema-migration mechanism; production schema should be versioned and reproducible.")


def audit_docs(root: Path, findings: list[Finding]) -> None:
    # Helpful informational signal: environment matrix/handoff docs in application repos.
    names = {p.name.lower() for p in root.rglob("*.md") if not any(part in IGNORE_DIRS for part in p.parts)}
    if not any("environment" in n or "deployment" in n or "production" in n for n in names):
        add(findings, "INFO", "DOC001", "docs/",
            "No obvious environment/production runbook was found.",
            "For persistent apps, document DEV/PROD bindings, migration/data policy, bootstrap, smoke tests, and rollback.")


def to_markdown(root: Path, findings: list[Finding]) -> str:
    lines = ["# Coze Environment Audit", "", f"Root: `{root}`", ""]
    if not findings:
        return "\n".join(lines + ["No findings detected by static heuristics."])
    for level in ("P0", "P1", "P2", "INFO"):
        group = [f for f in findings if f.level == level]
        if not group:
            continue
        lines += [f"## {level}", "", "| Rule | File | Issue | Suggestion |", "|---|---|---|---|"]
        for f in sorted(group, key=lambda x: (x.rule, x.file, x.issue)):
            issue = f.issue.replace("|", "\\|").replace("\n", " ")
            suggestion = f.suggestion.replace("|", "\\|").replace("\n", " ")
            lines.append(f"| `{f.rule}` | `{f.file}` | {issue} | {suggestion} |")
        lines.append("")
    return "\n".join(lines)


def threshold_failed(findings: list[Finding], fail_on: str) -> bool:
    rank = {"P0": 0, "P1": 1, "P2": 2, "INFO": 3}
    threshold = rank[fail_on]
    return any(rank[f.level] <= threshold for f in findings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Project root")
    parser.add_argument("--format", choices=["json", "md"], default="md")
    parser.add_argument("--strict", action="store_true", help="Escalate production-risk heuristics")
    parser.add_argument("--fail-on", choices=["P0", "P1", "P2"], default=None,
                        help="Exit 2 if findings at or above this severity exist")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings: list[Finding] = []

    audit_gitignore(root, findings)
    audit_env_files(root, findings, args.strict)
    for path in iter_files(root):
        audit_source_file(path, root, findings, args.strict)
    audit_migration_posture(root, findings)
    audit_docs(root, findings)

    if args.format == "json":
        print(json.dumps({
            "root": str(root),
            "summary": {level: sum(1 for f in findings if f.level == level) for level in ("P0", "P1", "P2", "INFO")},
            "findings": [asdict(f) for f in findings],
        }, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(root, findings))

    if args.fail_on and threshold_failed(findings, args.fail_on):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
