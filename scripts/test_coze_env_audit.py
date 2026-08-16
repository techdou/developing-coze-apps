#!/usr/bin/env python3
"""Regression tests for coze_env_audit.py using only the standard library."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "coze_env_audit.py"


def run(root: Path, *args: str, expect: int = 0) -> dict:
    cp = subprocess.run(
        [sys.executable, str(TOOL), str(root), "--format", "json", *args],
        text=True,
        capture_output=True,
    )
    if cp.returncode != expect:
        raise AssertionError(
            f"audit failed ({cp.returncode} != {expect})\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
        )
    return json.loads(cp.stdout)


def rules(result: dict) -> set[str]:
    return {item["rule"] for item in result.get("findings", [])}


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="coze-env-good-") as td:
        root = Path(td)
        (root / ".gitignore").write_text(".env\n.env.*\n!.env.example\n", encoding="utf-8")
        (root / ".env.example").write_text(
            "# app_private\nAPI_KEY_HASH_PEPPER=\n# platform_injected\nCOZE_SUPABASE_URL=\n",
            encoding="utf-8",
        )
        (root / "docs").mkdir()
        (root / "docs" / "production-deployment.md").write_text("DEV/PROD matrix", encoding="utf-8")
        (root / "migrations").mkdir()
        good = run(root, "--strict")
        assert good["summary"]["P0"] == 0, good

    with tempfile.TemporaryDirectory(prefix="coze-env-bad-") as td:
        root = Path(td)
        (root / ".gitignore").write_text("node_modules\n", encoding="utf-8")
        (root / ".env.local").write_text(
            "BOOTSTRAP_ADMIN_EMAIL=admin@relaystudio.local\n"
            "BOOTSTRAP_ADMIN_PASSWORD=Admin123\n"
            "COZE_SUPABASE_URL=https://dev-example.supabase.co\n",
            encoding="utf-8",
        )
        (root / "scripts").mkdir()
        (root / "scripts" / "start.sh").write_text(
            "#!/bin/sh\nsource .env.local\ncurl -X POST http://localhost:5000/api/auth/bootstrap\n",
            encoding="utf-8",
        )
        (root / "src" / "components").mkdir(parents=True)
        (root / "src" / "components" / "client.tsx").write_text(
            "'use client';\nconst bad = process.env.NEXT_PUBLIC_SERVICE_ROLE_TOKEN;\n",
            encoding="utf-8",
        )
        bad = run(root, "--strict")
        found = rules(bad)
        assert {"ENV001", "ENV002", "ENV003", "AUTH001", "ENV004", "ENV006", "WEB002"} <= found, bad
        assert bad["summary"]["P0"] >= 2, bad

        # --fail-on should provide CI-friendly non-zero status.
        failed = subprocess.run(
            [sys.executable, str(TOOL), str(root), "--format", "json", "--strict", "--fail-on", "P0"],
            text=True,
            capture_output=True,
        )
        assert failed.returncode == 2, failed

    print("coze_env_audit regression tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
