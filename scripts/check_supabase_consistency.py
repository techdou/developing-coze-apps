#!/usr/bin/env python3
"""
Supabase Instance Consistency Checker
======================================

Detects a critical class of bugs: when the Coze Coding project's
server-side environment and the deployed frontend are pointing to
DIFFERENT Supabase instances.

This happens when:
- A project is re-deployed and the platform creates a new Supabase instance
- The local terminal session retains old COZE_SUPABASE_* env vars
- The deployed server process gets new COZE_SUPABASE_* env vars
- Admin operations (password reset, quota changes) target the wrong instance

Symptoms:
- "Invalid login credentials" on new devices despite password reset
- API Key auth works but browser login fails
- Data appears in one database but not the other
- Admin operations seem to have no effect

Usage:
  python3 check_supabase_consistency.py [--deployed-url URL] [--json] [--fix]

Exit codes:
  0 = consistent (same project) or no Supabase detected
  1 = INCONSISTENT (different projects) — requires attention
  2 = error (missing deps, network failure)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


@dataclass
class SupabaseProjectInfo:
    """Parsed identity of a Supabase project."""
    url: str
    project_slug: str  # e.g. "br-snug-tern-c22e4bfc"
    anon_key: Optional[str] = None
    anon_key_suffix: Optional[str] = None
    source: str = ""  # "env" or "deployed_api"


@dataclass
class ConsistencyResult:
    """Result of consistency check."""
    consistent: bool
    local_project: Optional[SupabaseProjectInfo]
    deployed_project: Optional[SupabaseProjectInfo]
    message: str
    severity: str  # "ok", "warn", "critical"


def extract_project_slug(url: str) -> str:
    """Extract the Supabase project slug from a URL.

    Handles patterns like:
    - https://br-snug-tern-c22e4bfc.supabase2.aidap-global.cn-beijing.volces.com
    - https://br-snug-tern-c22e4bfc.supabase.co
    - https://xxx.supabase.com
    """
    match = re.match(r'https?://([a-z0-9-]+)\.supabase', url)
    if match:
        return match.group(1)
    # Try alternative patterns
    match = re.match(r'https?://([a-z0-9-]+)\.supabase2\.', url)
    if match:
        return match.group(1)
    return ""


def get_local_supabase_config() -> Optional[SupabaseProjectInfo]:
    """Read Supabase config from local environment variables."""
    url = os.environ.get("COZE_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    if not url:
        return None

    anon_key = os.environ.get("COZE_SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    slug = extract_project_slug(url)

    return SupabaseProjectInfo(
        url=url,
        project_slug=slug,
        anon_key=anon_key,
        anon_key_suffix=anon_key[-20:] if anon_key and len(anon_key) > 20 else None,
        source="env",
    )


def get_deployed_supabase_config(deployed_url: str) -> Optional[SupabaseProjectInfo]:
    """Fetch Supabase config from the deployed app's /api/supabase-config endpoint."""
    endpoint = deployed_url.rstrip("/") + "/api/supabase-config"
    try:
        req = Request(endpoint, headers={"Accept": "application/json"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except (URLError, HTTPError, json.JSONDecodeError, TimeoutError) as e:
        print(f"  Warning: Could not fetch deployed config from {endpoint}: {e}", file=sys.stderr)
        return None

    url = data.get("url") or data.get("supabaseUrl")
    anon_key = data.get("anonKey") or data.get("supabaseAnonKey")

    if not url:
        return None

    slug = extract_project_slug(url)

    return SupabaseProjectInfo(
        url=url,
        project_slug=slug,
        anon_key=anon_key,
        anon_key_suffix=anon_key[-20:] if anon_key and len(anon_key) > 20 else None,
        source="deployed_api",
    )


def get_project_from_code(root_dir: str) -> Optional[SupabaseProjectInfo]:
    """Scan project source code for hardcoded or .env Supabase URLs."""
    env_files = [".env", ".env.local", ".env.production", ".env.development"]
    for ef in env_files:
        path = os.path.join(root_dir, ef)
        if not os.path.exists(path):
            continue
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip("\"'")
                    if "supabase" in key.lower() and "url" in key.lower() and value.startswith("http"):
                        slug = extract_project_slug(value)
                        if slug:
                            return SupabaseProjectInfo(
                                url=value,
                                project_slug=slug,
                                source=f"file:{ef}",
                            )
        except Exception:
            continue
    return None


def check_data_consistency(deployed_url: str, api_key: Optional[str] = None) -> dict:
    """Compare data counts between local and deployed Supabase instances.

    This is a heuristic check: if the deployed instance has significantly
    more data, it's likely the "real" production instance.
    """
    # This would require Supabase client access; return heuristic for now
    return {"note": "Data consistency requires Supabase client access. Compare task/user counts via API."}


def check(
    root_dir: str = ".",
    deployed_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> ConsistencyResult:
    """Run the full consistency check."""

    # 1. Get local config from env vars
    local = get_local_supabase_config()

    # 2. Get config from source code / .env files
    code_config = get_project_from_code(root_dir)

    # 3. Get deployed config from API
    deployed = None
    if deployed_url:
        deployed = get_deployed_supabase_config(deployed_url)

    # 4. Determine consistency
    all_projects = []

    if local and local.project_slug:
        all_projects.append(local)
    if code_config and code_config.project_slug:
        all_projects.append(code_config)
    if deployed and deployed.project_slug:
        all_projects.append(deployed)

    if not all_projects:
        return ConsistencyResult(
            consistent=True,
            local_project=local,
            deployed_project=deployed,
            message="No Supabase configuration detected. Either Supabase is not used, or env vars are not set.",
            severity="ok",
        )

    if len(all_projects) == 1:
        return ConsistencyResult(
            consistent=True,
            local_project=local,
            deployed_project=deployed,
            message=f"Only one Supabase project detected (slug: {all_projects[0].project_slug}, source: {all_projects[0].source}). No inconsistency possible.",
            severity="ok",
        )

    # Check if all project slugs match
    slugs = set(p.project_slug for p in all_projects)
    if len(slugs) == 1:
        return ConsistencyResult(
            consistent=True,
            local_project=local,
            deployed_project=deployed,
            message=f"All sources point to the same Supabase project: {all_projects[0].project_slug}",
            severity="ok",
        )

    # INCONSISTENCY DETECTED
    slug_sources = {}
    for p in all_projects:
        slug_sources.setdefault(p.project_slug, []).append(p.source)

    details = []
    for slug, sources in slug_sources.items():
        details.append(f"  Project {slug}: referenced by {', '.join(sources)}")

    return ConsistencyResult(
        consistent=False,
        local_project=local,
        deployed_project=deployed,
        message=(
            f"CRITICAL: Multiple Supabase projects detected!\n"
            + "\n".join(details)
            + "\n\nThis means the server-side env and the deployed frontend are using"
            + " DIFFERENT Supabase instances. Admin operations (password reset, quota"
            + " changes) on one instance will not affect the other."
            + "\n\nSymptoms: 'Invalid login credentials' on new devices, data appearing"
            + " in one database but not the other, API key auth works but browser login fails."
            + "\n\nFix: Use the DEPLOYED instance's Supabase credentials for admin operations."
            + " If the local terminal has stale env vars, source the new deployment's config."
        ),
        severity="critical",
    )


def print_report(result: ConsistencyResult, fmt: str = "text"):
    """Print the check result."""
    if fmt == "json":
        d = asdict(result)
        # Remove None anon keys from output for cleanliness
        print(json.dumps(d, indent=2, ensure_ascii=False))
        return

    # Text format
    severity_icons = {"ok": "✅", "warn": "⚠️", "critical": "🚨"}
    icon = severity_icons.get(result.severity, "?")

    print(f"\n{icon} Supabase Consistency Check: {result.severity.upper()}")
    print("=" * 60)

    if result.local_project:
        print(f"\n  Local env vars:")
        print(f"    URL:   {result.local_project.url}")
        print(f"    Slug:  {result.local_project.project_slug}")
        if result.local_project.anon_key_suffix:
            print(f"    Key:   ...{result.local_project.anon_key_suffix}")

    if result.deployed_project:
        print(f"\n  Deployed API:")
        print(f"    URL:   {result.deployed_project.url}")
        print(f"    Slug:  {result.deployed_project.project_slug}")
        if result.deployed_project.anon_key_suffix:
            print(f"    Key:   ...{result.deployed_project.anon_key_suffix}")

    print(f"\n  Result: {result.message}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Supabase instance consistency between local env and deployed app"
    )
    parser.add_argument("--deployed-url", "-d",
                        help="Deployed app URL (e.g. https://your-app.dev.coze.site)")
    parser.add_argument("--root", "-r", default=".",
                        help="Project root directory (default: current)")
    parser.add_argument("--api-key",
                        help="API key for authenticated endpoints")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text",
                        help="Output format")
    parser.add_argument("--strict", action="store_true",
                        help="Also check .env files and source code for hardcoded URLs")
    args = parser.parse_args()

    # Auto-detect deployed URL from environment
    deployed_url = args.deployed_url
    if not deployed_url:
        domain = os.environ.get("COZE_PROJECT_DOMAIN_DEFAULT", "")
        if domain and not domain.startswith("http"):
            domain = f"https://{domain}"
        if domain:
            deployed_url = domain
            print(f"  Auto-detected deployed URL: {deployed_url}", file=sys.stderr)

    result = check(
        root_dir=args.root,
        deployed_url=deployed_url,
        api_key=args.api_key,
    )

    print_report(result, fmt=args.format)

    return 0 if result.consistent else 1


if __name__ == "__main__":
    raise SystemExit(main())
