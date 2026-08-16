#!/usr/bin/env python3
"""Validate structure and internal consistency of the developing-coze-apps skill."""

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
    "VERSION",
    "docs/official-evidence-map.md",
    "docs/environment-separation.md",
    "docs/environment-variables.md",
    "docs/database-storage-lifecycle.md",
    "docs/production-deployment.md",
    "docs/auth-bootstrap-patterns.md",
    "docs/single-html-mode-selection.md",
    "docs/single-html-security.md",
    "docs/static-bundling-compatibility.md",
    "docs/image-generation-for-single-html.md",
    "templates/environment-matrix.md",
    "templates/production-handoff.md",
    "templates/production-readiness-checklist.md",
    "templates/single-html/catalog.md",
    "templates/single-html/catalog.json",
    "scripts/coze_env_audit.py",
    "scripts/coze_project_audit.py",
    "scripts/check_supabase_consistency.py",
    "scripts/single_html_tool.py",
    "scripts/test_single_html_tool.py",
    "reference/Coze开发与生产环境技术参考-v2.0.md",
]
RECOMMENDED_DIRS = ["docs", "templates", "scripts", "examples", "evals", "reference"]
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
MIN_EVAL_CASES = 12


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    block = text[4:end]
    data: dict[str, str] = {}
    current_key: str | None = None
    for line in block.splitlines():
        if line.startswith("  ") and current_key:
            data[current_key] = (data.get(current_key, "") + " " + line.strip()).strip()
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            current_key = k.strip()
            data[current_key] = v.strip().strip('"').strip("'")
    return data


def collect_backtick_paths(text: str) -> set[str]:
    paths: set[str] = set()
    for token in re.findall(r"`([^`]+)`", text):
        if token.startswith(("docs/", "templates/", "scripts/", "examples/", "evals/", "reference/")):
            paths.add(token.rstrip("/.,;:"))
    return paths


def read_version(root: Path) -> str:
    p = root / "VERSION"
    return p.read_text(encoding="utf-8").strip() if p.exists() else ""


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
        if len(body) > 18000:
            warnings.append("SKILL.md body is large; move more details into docs/templates")
        for required_phrase in [
            "Do not use this skill",
            "Mandatory environment gate",
            "Production deployment workflow",
            "dist/index.single.html",
            "Single-HTML / iframe workflow",
            "Read only what the task needs",
        ]:
            if required_phrase not in text:
                errors.append(f"SKILL.md missing required workflow phrase: {required_phrase}")
        for rel in sorted(collect_backtick_paths(text)):
            if "*" not in rel and not (root / rel).exists():
                errors.append(f"SKILL.md references missing path: {rel}")

    for d in RECOMMENDED_DIRS:
        if not (root / d).exists():
            warnings.append(f"Recommended directory missing: {d}/")

    # VERSION / changelog consistency.
    version = read_version(root)
    if version and not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?", version):
        errors.append(f"VERSION is not semantic-version-like: {version}")
    changelog = root / "CHANGELOG.md"
    if version and changelog.exists():
        text = changelog.read_text(encoding="utf-8", errors="ignore")
        if not re.search(rf"(?m)^##\s+{re.escape(version)}(?:\s|$)", text):
            errors.append(f"CHANGELOG.md has no top-level entry for VERSION {version}")

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
    python_scripts = [
        "scripts/single_html_tool.py",
        "scripts/test_single_html_tool.py",
        "scripts/coze_project_audit.py",
        "scripts/coze_env_audit.py",
        "scripts/check_supabase_consistency.py",
    ]
    for rel in python_scripts:
        path = root / rel
        if path.exists():
            try:
                py_compile.compile(str(path), doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append(f"Python compile failed for {rel}: {exc.msg}")

    # Eval coverage and pair integrity.
    case_dir = root / "evals" / "cases"
    exp_dir = root / "evals" / "expected"
    cases = sorted(case_dir.glob("*.md")) if case_dir.exists() else []
    if len(cases) < MIN_EVAL_CASES:
        errors.append(f"Expected at least {MIN_EVAL_CASES} eval cases, found {len(cases)}")
    for case in cases:
        expected = exp_dir / case.name.replace(".md", ".expected.md")
        if not expected.exists():
            errors.append(f"Missing expected output criteria for eval: {case.name}")

    # v0.4 environment evals must exist explicitly.
    for prefix in ["09-", "10-", "11-", "12-"]:
        if not any(p.name.startswith(prefix) for p in cases):
            errors.append(f"Missing v0.4 environment eval case prefix: {prefix}")

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
