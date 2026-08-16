#!/usr/bin/env python3
"""Regression tests for single_html_tool.py using only the standard library."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "single_html_tool.py"
EXAMPLES = ROOT / "templates" / "single-html" / "config-examples"
TEMPLATES = [
    "fullscreen-iframe",
    "app-shell-iframe",
    "split-intro-iframe",
    "cover-launch-iframe",
    "editorial-image-text",
    "visual-story",
    "course-article",
    "gallery-showcase",
]


def run(*args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run([sys.executable, str(TOOL), *args], text=True, capture_output=True)
    if cp.returncode != expect:
        raise AssertionError(
            f"command failed ({cp.returncode} != {expect}): {' '.join(args)}\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
        )
    return cp


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="single-html-test-") as td:
        tmp = Path(td)

        # Catalog must contain all expected templates.
        cp = run("list-templates", "--format", "json")
        catalog = json.loads(cp.stdout)
        ids = {x["id"] for x in catalog["templates"]}
        assert set(TEMPLATES) <= ids

        # Every template renders and validates.
        for template in TEMPLATES:
            out = tmp / f"{template}.html"
            run(
                "render", "--template", template,
                "--config", str(EXAMPLES / f"{template}.json"),
                "--out", str(out), "--force",
            )
            cp = run("validate", str(out), "--format", "json")
            result = json.loads(cp.stdout)
            assert not any(x["level"] == "P0" for x in result["findings"]), result
            assert result["status"] in {"self-contained", "iframe-wrapper", "single-file-network-dependent"}

        # Simple static bundle: local CSS/JS/image must be inlined.
        static = tmp / "static"
        static.mkdir()
        (static / "css").mkdir()
        (static / "css" / "style.css").write_text("body{background:url('../dot.png')}\n", encoding="utf-8")
        (static / "app.js").write_text("document.body.dataset.ready='1';\n", encoding="utf-8")
        (static / "dot.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        (static / "index.html").write_text(
            '<!doctype html><html><head><title>T</title><link rel="stylesheet" href="css/style.css"></head>'
            '<body><img src="dot.png" alt="dot"><script src="app.js"></script></body></html>',
            encoding="utf-8",
        )
        bundled = tmp / "bundled.html"
        run("bundle-static", "--input-dir", str(static), "--out", str(bundled), "--force")
        result = json.loads(run("validate", str(bundled), "--format", "json").stdout)
        assert result["status"] == "self-contained", result
        body = bundled.read_text(encoding="utf-8")
        assert "data:image/png;base64" in body
        assert "data-inlined-from" in body

        # Relative ESM imports must fail closed.
        modules = tmp / "modules"
        modules.mkdir()
        (modules / "dep.js").write_text("export const x=1;", encoding="utf-8")
        (modules / "main.js").write_text("import {x} from './dep.js'; console.log(x);", encoding="utf-8")
        (modules / "index.html").write_text(
            '<!doctype html><html><head><title>M</title></head><body><script type="module" src="main.js"></script></body></html>',
            encoding="utf-8",
        )
        run("bundle-static", "--input-dir", str(modules), "--out", str(tmp / "bad.html"), expect=2)

        # Next.js project inspection must recommend deployment + iframe.
        nextp = tmp / "next"
        (nextp / "app" / "api" / "hello").mkdir(parents=True)
        (nextp / "package.json").write_text(json.dumps({"dependencies": {"next": "16.0.0"}}), encoding="utf-8")
        (nextp / "app" / "api" / "hello" / "route.ts").write_text("export async function GET(){}", encoding="utf-8")
        inspected = json.loads(run("inspect", "--source", str(nextp), "--format", "json").stdout)
        assert inspected["server_dependent"] is True
        assert inspected["kind"] == "nextjs_fullstack_or_hybrid"

    print("All single-HTML tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
