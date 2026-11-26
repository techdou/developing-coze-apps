#!/usr/bin/env python3
"""Regression tests for coze_env_audit.py using only the standard library."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "coze_env_audit.py"
ENV = {
    **{key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")},
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
}


def git(root: Path, *args: str, env: dict[str, str] = ENV) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env=env)


def run(root: Path, *args: str, expect: int = 0, env: dict[str, str] = ENV) -> dict:
    cp = subprocess.run(
        [sys.executable, str(TOOL), str(root), "--format", "json", *args],
        text=True,
        capture_output=True,
        env=env,
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
        git(root, "init", "--quiet", "--template=")
        (root / ".gitignore").write_text(".env\n.env.*\n!.env.example\n", encoding="utf-8")
        (root / ".env.example").write_text(
            "# app_private\nAPI_KEY_HASH_PEPPER=\n# platform_injected\nCOZE_SUPABASE_URL=\n",
            encoding="utf-8",
        )
        (root / "docs").mkdir()
        (root / "docs" / "production-deployment.md").write_text("DEV/PROD matrix", encoding="utf-8")
        (root / "migrations").mkdir()
        good = run(root, "--strict", "--fail-on", "P1")
        assert not {"ENV001", "ENV002", "ENV007", "ENV008"} & rules(good), good
        git(root, "add", "--", ".env.example")
        assert "ENV008" not in rules(run(root, "--fail-on", "P1"))

    with tempfile.TemporaryDirectory(prefix="coze-env-bad-") as td:
        root = Path(td)
        git(root, "init", "--quiet", "--template=")
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
        run(root, "--strict", "--fail-on", "P0", expect=2)

    with tempfile.TemporaryDirectory(prefix="coze-env-ignore-") as td:
        root = Path(td)
        git(root, "init", "--quiet", "--template=")
        gi = root / ".gitignore"
        gi.write_text(".env.*\n", encoding="utf-8")
        partial = run(root, "--fail-on", "P1", expect=2)
        assert any(f["rule"] == "ENV001" and f["file"] == ".env" for f in partial["findings"]), partial
        assert "ENV002" not in rules(partial), partial
        assert "ENV007" in rules(partial), partial

        gi.write_text("/.env\n.env.*\n!.env.local\n!.env.example\n", encoding="utf-8")
        negated = run(root, "--fail-on", "P1", expect=2)
        assert "ENV002" in rules(negated), negated
        assert not {"ENV001", "ENV007"} & rules(negated), negated

        gi.write_text(".env\n.env.*\n!.env.example\n", encoding="utf-8")
        (root / ".env").write_text("MOCK_VALUE=placeholder\n", encoding="utf-8")
        git(root, "add", "--force", "--", ".env")
        tracked = run(root, "--fail-on", "P0", expect=2)
        assert any(f["rule"] == "ENV008" and f["file"] == ".env" and f["level"] == "P0"
                   for f in tracked["findings"]), tracked
        assert "placeholder" not in json.dumps(tracked), tracked

    with tempfile.TemporaryDirectory(prefix="coze-env-global-ignore-") as td:
        home = Path(td)
        root = home / "repo"
        root.mkdir()
        excludes = home / "global-ignore"
        excludes.write_text(".env\n.env.*\n", encoding="utf-8")
        env = {**ENV, "GIT_CONFIG_GLOBAL": str(home / "gitconfig")}
        git(root, "init", "--quiet", "--template=", env=env)
        git(root, "config", "--global", "core.excludesFile", str(excludes), env=env)
        for name in (".env", ".env.local"):
            git(root, "check-ignore", "--", name, env=env)

        global_only = run(root, "--fail-on", "P1", expect=2, env=env)
        warnings = {(f["rule"], f["file"]) for f in global_only["findings"] if f["level"] == "P1"}
        assert {("ENV001", ".env"), ("ENV002", ".env.local")} <= warnings, global_only
        assert "ENV007" not in rules(global_only), global_only

    with tempfile.TemporaryDirectory(prefix="coze-env-no-git-") as td:
        root = Path(td)
        # A temp directory inside the checkout must not inherit its Git worktree.
        env = {**ENV, "GIT_CEILING_DIRECTORIES": str(root.resolve().parent)}
        unverified = run(root, "--fail-on", "P1", expect=2, env=env)
        assert any(f["rule"] == "ENV001" and "Cannot verify" in f["issue"] for f in unverified["findings"])

    print("coze_env_audit regression tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
