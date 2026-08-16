#!/usr/bin/env python3
"""Validate the structure and internal consistency of this Anthropic-style skill."""

from __future__ import annotations

import argparse
import json
import py_compile
import re
from pathlib import Path

REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "CHANGELOG.md",
    "docs/official-evidence-map.md",
    "docs/single-html-mode-selection.md",
    "docs/single-html-security.md",
    "docs/static-bundling-compatibility.md",
    "docs/image-generation-for-single-html.md",
    "templates/single-html/catalog.md",
    "templates/single-html/catalog.json",
    "scripts/single_html_tool.py",
    "scripts/test_single_html_tool.py",
]
RECOMMENDED_DIRS = ["docs", "templates", "scripts", "examples", "evals"]
EXPECTED_TEMPLATE_IDS = {
    "fullscreen-iframe",
    "app-shell-iframe",
    "split-intro-iframe",
    "cover-launch-iframe",
    "editorial-image-text",
    "visual-story",
    "course-article",
    "gallery-showcase",
}


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    block = text[4:end]
    data: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def collect_backtick_paths(text: str) -> set[str]:
    paths: set[str] = set()
    for token in re.findall(r"`([^`]+)`", text):
        if token.startswith(("docs/", "templates/", "scripts/", "examples/", "evals/")):
            paths.add(token.rstrip("/.,;:"))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"Missing required file: {rel}")

    skill = root / "SKILL.md"
    if skill.exists():
        text = skill.read_text(encoding="utf-8", errors="ignore")
        fm = parse_frontmatter(text)
        for key in ["name", "description"]:
            if not fm.get(key):
                errors.append(f"SKILL.md frontmatter missing `{key}`")
        name = fm.get("name", "")
        if name and not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,62}", name):
            errors.append("Skill name should be lowercase kebab-case, 2-63 chars")
        desc = fm.get("description", "")
        if len(desc) < 80:
            warnings.append("Description may be too short to trigger reliably")
        if len(desc) > 1024:
            errors.append("Description exceeds 1024 characters; sharpen trigger scope")
        body = text.split("\n---", 2)[-1]
        if len(body) > 14000:
            warnings.append("SKILL.md body is large; move more details into docs/templates")
        if "Do not use this skill" not in text:
            warnings.append("Negative trigger conditions are missing")
        for required_phrase in ["dist/index.single.html", "Single-HTML / iframe workflow", "Read only what the task needs"]:
            if required_phrase not in text:
                errors.append(f"SKILL.md missing required workflow phrase: {required_phrase}")
        for rel in sorted(collect_backtick_paths(text)):
            if "*" not in rel and not (root / rel).exists():
                errors.append(f"SKILL.md references missing path: {rel}")

    for d in RECOMMENDED_DIRS:
        if not (root / d).exists():
            warnings.append(f"Recommended directory missing: {d}/")

    # Validate template catalog and files.
    catalog_path = root / "templates" / "single-html" / "catalog.json"
    if catalog_path.exists():
        try:
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"Cannot parse catalog.json: {exc}")
            catalog = {}
        ids = {x.get("id") for x in catalog.get("templates", []) if isinstance(x, dict)}
        missing_ids = EXPECTED_TEMPLATE_IDS - ids
        extra_ids = ids - EXPECTED_TEMPLATE_IDS
        if missing_ids:
            errors.append(f"Template catalog missing IDs: {sorted(missing_ids)}")
        if extra_ids:
            warnings.append(f"Template catalog has undocumented extra IDs: {sorted(extra_ids)}")
        for tid in sorted(ids):
            if not (root / "templates" / "single-html" / f"{tid}.html").exists():
                errors.append(f"Template file missing for catalog ID: {tid}")
            if not (root / "templates" / "single-html" / "config-examples" / f"{tid}.json").exists():
                errors.append(f"Config example missing for template ID: {tid}")

    # Python syntax checks.
    for rel in ["scripts/single_html_tool.py", "scripts/test_single_html_tool.py", "scripts/coze_project_audit.py"]:
        path = root / rel
        if path.exists():
            try:
                py_compile.compile(str(path), doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append(f"Python compile failed for {rel}: {exc.msg}")

    # Eval coverage.
    case_dir = root / "evals" / "cases"
    exp_dir = root / "evals" / "expected"
    cases = sorted(case_dir.glob("*.md")) if case_dir.exists() else []
    if len(cases) < 8:
        warnings.append("Fewer than 8 eval cases found")
    for case in cases:
        expected = exp_dir / case.name.replace(".md", ".expected.md")
        if not expected.exists():
            errors.append(f"Missing expected output criteria for eval: {case.name}")

    print("# Skill Package Validation\n")
    if errors:
        print("## Errors")
        for item in errors:
            print(f"- {item}")
    else:
        print("No structural errors detected.")
    if warnings:
        print("\n## Warnings")
        for item in warnings:
            print(f"- {item}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
