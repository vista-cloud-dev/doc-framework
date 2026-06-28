#!/usr/bin/env python3
"""
link-check.py — markdown cross-reference integrity gate for a docs corpus.

Gates on the one thing that is always a real defect: **intra-repo markdown links
and section anchors must resolve.** A broken link or a broken `#anchor` is an error
(exit 1); nothing else is checked. Frontmatter is free-form and entirely optional
(see CONVENTIONS.md) — this tool neither parses nor enforces it.

Zero external dependencies (pure stdlib; airgapped-friendly).

Cross-repo links that escape the corpus root (e.g. `../../m-stdlib/...`) point at
SIBLING repos: they resolve in a full local workspace but NOT in a single-repo CI
checkout, so they are unverifiable here and are skipped. Use GitHub URLs for those.

Usage:
    python3 link-check.py docs/
    python3 link-check.py docs/ --json

Exit code: 0 if every link/anchor resolves, 1 if any are broken, 2 on bad invocation.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field

# Directories excluded from the scanned corpus. `prompts/` = session hand-offs;
# `archive/`, `retired/`, `historical/` = frozen, retired material whose internal
# links point at since-moved files; `memory/` = the auto-memory store; `modules/` =
# GENERATED reference pages drift-gated in their generating repo. None are active
# corpus docs. Inbound links INTO any of them still resolve — the checker resolves
# targets against the filesystem, not this set.
EXCLUDE_DIRS = {"prompts", "archive", "memory", "retired", "historical", "modules"}

# markdown links: [text](target)  — not images (![...]); target may carry a "title"
LINK_RE = re.compile(r"(?<!!)\[(?:[^\]]*)\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


# --------------------------------------------------------------------------- #
# Records
# --------------------------------------------------------------------------- #
@dataclass
class Finding:
    path: str
    line: int | None
    code: str
    message: str

    def fmt(self) -> str:
        loc = self.path if self.line is None else f"{self.path}:{self.line}"
        return f"  [ERROR] {loc}  ({self.code}) {self.message}"


@dataclass
class Doc:
    path: str          # absolute
    relpath: str       # relative to docs root
    headings: list[str] = field(default_factory=list)           # slugs
    links: list[tuple[str, int]] = field(default_factory=list)  # (target, line)


# --------------------------------------------------------------------------- #
# Headings & links
# --------------------------------------------------------------------------- #
def frontmatter_end(text: str) -> int:
    """Body-start line index, skipping a leading `---` frontmatter block (if any)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i + 1
    return 0  # unterminated → treat the whole file as body


def slugify(text: str) -> str:
    """GitHub-style heading slug."""
    s = text.strip().lower()
    s = s.replace("`", "")
    s = re.sub(r"\*+", "", s)       # bold/italic markers
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)  # links -> their text
    out = [ch if (ch.isalnum() or ch in (" ", "-", "_")) else "" for ch in s]
    s = "".join(out).strip()
    # GitHub maps each whitespace char to its own hyphen (no collapsing).
    return re.sub(r"\s", "-", s)


def extract_headings_and_links(text: str) -> tuple[list[str], list[tuple[str, int]]]:
    """Return (heading slugs with dedupe suffixes, [(link_target, lineno)]), skipping code fences."""
    slugs: list[str] = []
    seen: dict[str, int] = {}
    links: list[tuple[str, int]] = []
    body_start = frontmatter_end(text)
    lines = text.splitlines()
    in_fence = False
    fence_marker = ""
    for idx in range(body_start, len(lines)):
        line = lines[idx]
        lineno = idx + 1
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence, fence_marker = True, marker
            elif marker == fence_marker:
                in_fence = False
            continue
        if in_fence:
            continue
        hm = HEADING_RE.match(line)
        if hm:
            htext = hm.group(2)
            # Honor an explicit heading id `{#custom-id}` (pandoc/kramdown/mkdocs
            # attribute syntax). When present, register that id AND the auto-slug of
            # the remaining text, so both `#custom-id` and the GitHub-style slug resolve.
            explicit = None
            mid = re.search(r"\s*\{#([\w-]+)\}\s*$", htext)
            if mid:
                explicit = mid.group(1)
                htext = htext[: mid.start()]
            base = slugify(htext)
            if base in seen:
                seen[base] += 1
                slug = f"{base}-{seen[base]}"
            else:
                seen[base] = 0
                slug = base
            slugs.append(slug)
            if explicit and explicit not in slugs:
                slugs.append(explicit)
            continue
        for m in LINK_RE.finditer(line):
            target = m.group(1).strip()
            # drop an optional "title" after the url
            if " " in target and not target.startswith("<"):
                target = target.split()[0]
            links.append((target, lineno))
    return slugs, links


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def collect_docs(root: str) -> list[Doc]:
    docs: list[Doc] = []
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]  # prune excluded dirs
        for fn in files:
            if not fn.endswith(".md"):
                continue
            ap = os.path.join(dirpath, fn)
            docs.append(Doc(path=ap, relpath=os.path.relpath(ap, root)))
    return docs


def validate(root: str) -> list[Finding]:
    findings: list[Finding] = []
    docs = collect_docs(root)
    if not docs:
        return [Finding(root, None, "EMPTY", "no .md files found under this path")]

    for d in docs:
        with open(d.path, encoding="utf-8") as fh:
            d.headings, d.links = extract_headings_and_links(fh.read())

    headings_by_path = {d.path: set(d.headings) for d in docs}
    for d in docs:
        base = os.path.dirname(d.path)
        for target, lineno in d.links:
            if target.startswith(("http://", "https://", "mailto:", "#")):
                if target.startswith("#"):  # intra-doc anchor
                    anchor = target[1:]
                    if anchor and anchor not in set(d.headings):
                        findings.append(Finding(d.relpath, lineno, "ANCHOR", f"intra-doc anchor '#{anchor}' not found"))
                continue
            path_part, _, anchor = target.partition("#")
            if path_part == "":
                continue
            resolved = os.path.normpath(os.path.join(base, path_part))
            # Cross-repo links that escape the corpus root point at SIBLING repos —
            # unverifiable in a single-repo CI checkout, so skip them (see module docstring).
            if not (resolved == root or resolved.startswith(root + os.sep)):
                continue
            if not os.path.exists(resolved):
                findings.append(Finding(d.relpath, lineno, "LINK", f"link target not found: '{path_part}'"))
                continue
            if anchor and resolved.endswith(".md") and resolved in headings_by_path:
                if anchor not in headings_by_path[resolved]:
                    findings.append(Finding(d.relpath, lineno, "ANCHOR", f"anchor '#{anchor}' not in {os.path.relpath(resolved, root)}"))

    return findings


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Check markdown link + anchor integrity across a docs corpus.")
    ap.add_argument("root", help="path to the docs/ directory")
    ap.add_argument("--json", action="store_true", help="emit findings as JSON")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"error: not a directory: {args.root}", file=sys.stderr)
        return 2

    findings = validate(root)

    if args.json:
        print(json.dumps({
            "root": root,
            "errors": len(findings),
            "findings": [vars(f) for f in findings],
        }, indent=2))
    else:
        for f in sorted(findings, key=lambda x: (x.path, x.line or 0)):
            print(f.fmt())
        print(f"\n{len(findings)} error(s) across the corpus.")
        if not findings:
            print("  corpus is clean.")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
