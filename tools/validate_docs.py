#!/usr/bin/env python3
"""
validate_docs.py — corpus validator for the Technical Documentation Framework.

Checks frontmatter, the type/status enums, id/filename agreement, supersession
integrity, and cross-document link + anchor integrity across a docs/ tree.

Zero external dependencies: uses PyYAML if importable, otherwise a built-in
parser for the constrained frontmatter dialect described in FRAMEWORK.md §6.

Usage:
    python3 validate_docs.py docs/
    python3 validate_docs.py docs/ --json
    python3 validate_docs.py docs/ --strict      # warnings count as failures

Exit code: 0 if clean (no errors; no warnings under --strict), 1 otherwise.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any

VALID_TYPES = {"spec", "adr", "investigation", "research", "plan", "map", "guide", "log"}
VALID_STATUS = {"idea", "draft", "proposed", "accepted", "canonical", "superseded", "deprecated"}
REQUIRED_FIELDS = ["id", "title", "type", "status", "created", "updated"]
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# markdown links: [text](target)  — not images (![...]); target may carry a "title"
LINK_RE = re.compile(r"(?<!!)\[(?:[^\]]*)\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")

try:  # optional dependency
    import yaml  # type: ignore

    _HAS_YAML = True
except Exception:  # pragma: no cover
    _HAS_YAML = False


# --------------------------------------------------------------------------- #
# Finding records
# --------------------------------------------------------------------------- #
@dataclass
class Finding:
    level: str  # "error" | "warning"
    path: str
    line: int | None
    code: str
    message: str

    def fmt(self) -> str:
        loc = self.path if self.line is None else f"{self.path}:{self.line}"
        return f"  [{self.level.upper():7}] {loc}  ({self.code}) {self.message}"


@dataclass
class Doc:
    path: str          # absolute
    relpath: str       # relative to docs root
    stem: str          # filename without .md
    meta: dict[str, Any] = field(default_factory=dict)
    fm_ok: bool = False
    headings: list[str] = field(default_factory=list)  # slugs
    links: list[tuple[str, int]] = field(default_factory=list)  # (target, line)
    in_historical: bool = False
    is_index: bool = False  # README.md files are navigation, not corpus docs


# --------------------------------------------------------------------------- #
# Frontmatter parsing
# --------------------------------------------------------------------------- #
def split_frontmatter(text: str) -> tuple[str | None, int]:
    """Return (frontmatter_block, body_start_line). frontmatter_block is None if absent."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), i + 1
    return None, 0  # unterminated


def _strip_quotes(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    return v


def _fallback_parse(block: str) -> dict[str, Any]:
    """Parse the constrained frontmatter dialect (scalars + flat lists)."""
    data: dict[str, Any] = {}
    key: str | None = None
    pending_list: list[str] | None = None
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        # block-list item belonging to the previous key
        if line.lstrip().startswith("- ") and pending_list is not None:
            pending_list.append(_strip_quotes(line.lstrip()[2:]))
            continue
        if ":" not in line:
            continue
        # close any open block list
        if pending_list is not None and key is not None:
            data[key] = pending_list
            pending_list = None
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        # strip trailing comment when unquoted
        if val and val[0] not in ("'", '"') and " #" in val and not val.startswith("["):
            val = val.split(" #", 1)[0].strip()
        if val == "":
            pending_list = []  # may be a block list, resolved on next lines
            data[key] = ""      # tentative; overwritten if list items follow
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [_strip_quotes(x) for x in inner.split(",") if x.strip()] if inner else []
        else:
            data[key] = _strip_quotes(val)
    if pending_list is not None and key is not None and pending_list:
        data[key] = pending_list
    return data


def parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str | None]:
    block, _ = split_frontmatter(text)
    if block is None:
        return None, "missing or unterminated frontmatter (must start at line 1 with '---')"
    if _HAS_YAML:
        try:
            data = yaml.safe_load(block) or {}
            if not isinstance(data, dict):
                return None, "frontmatter is not a mapping"
            # normalise dates to ISO strings for uniform checks
            for k, v in list(data.items()):
                if isinstance(v, (_dt.date, _dt.datetime)):
                    data[k] = v.isoformat()[:10]
            return data, None
        except Exception as e:  # pragma: no cover
            return None, f"YAML parse error: {e}"
    return _fallback_parse(block), None


# --------------------------------------------------------------------------- #
# Headings & links
# --------------------------------------------------------------------------- #
def slugify(text: str) -> str:
    """GitHub-style heading slug."""
    s = text.strip().lower()
    s = s.replace("`", "")
    s = re.sub(r"\*+", "", s)       # bold/italic markers
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)  # links -> their text
    out = [ch if (ch.isalnum() or ch in (" ", "-", "_")) else "" for ch in s]
    s = "".join(out).strip()
    return re.sub(r"\s+", "-", s)


def extract_headings_and_links(text: str) -> tuple[list[str], list[tuple[str, int]]]:
    """Return (heading slugs with dedupe suffixes, [(link_target, lineno)]), skipping code fences."""
    slugs: list[str] = []
    seen: dict[str, int] = {}
    links: list[tuple[str, int]] = []
    _, body_start = split_frontmatter(text)
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
            base = slugify(hm.group(2))
            if base in seen:
                seen[base] += 1
                slug = f"{base}-{seen[base]}"
            else:
                seen[base] = 0
                slug = base
            slugs.append(slug)
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
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            ap = os.path.join(dirpath, fn)
            rel = os.path.relpath(ap, root)
            docs.append(
                Doc(
                    path=ap,
                    relpath=rel,
                    stem=fn[:-3],
                    in_historical="historical" in rel.split(os.sep),
                    is_index=fn.lower() == "readme.md",
                )
            )
    return docs


def validate(root: str) -> list[Finding]:
    findings: list[Finding] = []
    docs = collect_docs(root)
    if not docs:
        return [Finding("error", root, None, "EMPTY", "no .md files found under this path")]

    texts: dict[str, str] = {}
    for d in docs:
        with open(d.path, encoding="utf-8") as fh:
            texts[d.path] = fh.read()
        d.headings, d.links = extract_headings_and_links(texts[d.path])
        if d.is_index:
            continue  # navigation file: no frontmatter required, but links are still checked
        meta, err = parse_frontmatter(texts[d.path])
        if err:
            findings.append(Finding("error", d.relpath, 1, "FM-PARSE", err))
            d.meta = {}
        else:
            d.meta = meta
            d.fm_ok = True

    # ---- per-doc field checks ----
    id_to_doc: dict[str, Doc] = {}
    for d in docs:
        m = d.meta
        if not d.fm_ok:
            continue
        for fldname in REQUIRED_FIELDS:
            if fldname not in m or m[fldname] in (None, ""):
                findings.append(Finding("error", d.relpath, None, "FM-REQ", f"missing required field '{fldname}'"))

        doc_id = m.get("id")
        if doc_id:
            if not ID_RE.match(str(doc_id)):
                findings.append(Finding("error", d.relpath, None, "FM-ID", f"id '{doc_id}' is not kebab-case"))
            if str(doc_id) != d.stem:
                findings.append(Finding("error", d.relpath, None, "ID-STEM", f"id '{doc_id}' != filename stem '{d.stem}'"))
            if doc_id in id_to_doc:
                findings.append(Finding("error", d.relpath, None, "ID-DUP", f"duplicate id '{doc_id}' (also in {id_to_doc[doc_id].relpath})"))
            else:
                id_to_doc[doc_id] = d

        t = m.get("type")
        if t and t not in VALID_TYPES:
            findings.append(Finding("error", d.relpath, None, "TYPE", f"invalid type '{t}' (allowed: {sorted(VALID_TYPES)})"))
        st = m.get("status")
        if st and st not in VALID_STATUS:
            findings.append(Finding("error", d.relpath, None, "STATUS", f"invalid status '{st}' (allowed: {sorted(VALID_STATUS)})"))

        created, updated = m.get("created"), m.get("updated")
        cd = ud = None
        for label, val in (("created", created), ("updated", updated)):
            if val and not DATE_RE.match(str(val)):
                findings.append(Finding("error", d.relpath, None, "DATE", f"{label} '{val}' is not ISO YYYY-MM-DD"))
        try:
            if created and DATE_RE.match(str(created)):
                cd = _dt.date.fromisoformat(str(created))
            if updated and DATE_RE.match(str(updated)):
                ud = _dt.date.fromisoformat(str(updated))
            if cd and ud and ud < cd:
                findings.append(Finding("error", d.relpath, None, "DATE-ORDER", f"updated ({updated}) is before created ({created})"))
        except ValueError as e:
            findings.append(Finding("error", d.relpath, None, "DATE", f"invalid date: {e}"))

        if "tags" not in m:
            findings.append(Finding("warning", d.relpath, None, "TAGS", "no tags (recommended)"))
        elif not isinstance(m.get("tags"), list):
            findings.append(Finding("error", d.relpath, None, "TAGS", "tags must be a flat list"))

    # ---- supersession integrity ----
    for d in docs:
        if not d.fm_ok:
            continue
        m = d.meta
        st = m.get("status")
        sup = (m.get("supersedes") or "").strip() if isinstance(m.get("supersedes"), str) else m.get("supersedes")
        supby = (m.get("superseded_by") or "").strip() if isinstance(m.get("superseded_by"), str) else m.get("superseded_by")

        if st == "superseded" and not supby:
            findings.append(Finding("error", d.relpath, None, "SUP-MISSING", "status 'superseded' requires 'superseded_by'"))
        if supby:
            other = id_to_doc.get(supby)
            if not other:
                findings.append(Finding("error", d.relpath, None, "SUP-REF", f"superseded_by '{supby}' does not resolve to a doc"))
            else:
                if (other.meta.get("supersedes") or "") != m.get("id"):
                    findings.append(Finding("error", d.relpath, None, "SUP-BIDIR", f"'{supby}' does not declare supersedes: {m.get('id')}"))
                if st not in ("superseded", "deprecated"):
                    findings.append(Finding("error", d.relpath, None, "SUP-STATUS", f"has superseded_by but status is '{st}', not superseded/deprecated"))
            if not d.in_historical:
                findings.append(Finding("warning", d.relpath, None, "SUP-LOC", "superseded/deprecated docs should live under historical/"))
        if sup:
            other = id_to_doc.get(sup)
            if not other:
                findings.append(Finding("error", d.relpath, None, "SUP-REF", f"supersedes '{sup}' does not resolve to a doc"))
            elif (other.meta.get("superseded_by") or "") != m.get("id"):
                findings.append(Finding("error", d.relpath, None, "SUP-BIDIR", f"'{sup}' does not declare superseded_by: {m.get('id')}"))

    # ---- link + anchor integrity ----
    headings_by_path = {d.path: set(d.headings) for d in docs}
    for d in docs:
        base = os.path.dirname(d.path)
        for target, lineno in d.links:
            if target.startswith(("http://", "https://", "mailto:", "#")):
                if target.startswith("#"):  # intra-doc anchor
                    anchor = target[1:]
                    if anchor and anchor not in set(d.headings):
                        findings.append(Finding("error", d.relpath, lineno, "ANCHOR", f"intra-doc anchor '#{anchor}' not found"))
                continue
            path_part, _, anchor = target.partition("#")
            if path_part == "":
                continue
            resolved = os.path.normpath(os.path.join(base, path_part))
            if not os.path.exists(resolved):
                findings.append(Finding("error", d.relpath, lineno, "LINK", f"link target not found: '{path_part}'"))
                continue
            if anchor and resolved.endswith(".md"):
                if resolved in headings_by_path:
                    if anchor not in headings_by_path[resolved]:
                        findings.append(Finding("error", d.relpath, lineno, "ANCHOR", f"anchor '#{anchor}' not in {os.path.relpath(resolved, root)}"))

    # ---- index coverage (warning) ----
    index_path = os.path.join(root, "README.md")
    if os.path.exists(index_path):
        idx_doc = next((d for d in docs if d.path == index_path), None)
        linked = set()
        if idx_doc:
            for target, _ in idx_doc.links:
                p = target.partition("#")[0]
                if p.endswith(".md"):
                    linked.add(os.path.normpath(os.path.join(root, p)))
        for d in docs:
            if d.path == index_path or d.in_historical:
                continue
            if d.fm_ok and d.meta.get("status") in ("superseded", "deprecated"):
                continue
            if d.path not in linked:
                findings.append(Finding("warning", d.relpath, None, "INDEX", "active doc not linked from docs/README.md"))
    else:
        findings.append(Finding("warning", root, None, "INDEX", "no docs/README.md index found"))

    return findings


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate a documentation corpus against the framework.")
    ap.add_argument("root", help="path to the docs/ directory")
    ap.add_argument("--json", action="store_true", help="emit findings as JSON")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"error: not a directory: {args.root}", file=sys.stderr)
        return 2

    findings = validate(root)
    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]

    if args.json:
        print(json.dumps({
            "root": root,
            "errors": len(errors),
            "warnings": len(warnings),
            "findings": [vars(f) for f in findings],
        }, indent=2))
    else:
        if findings:
            for f in sorted(findings, key=lambda x: (x.level != "error", x.path, x.line or 0)):
                print(f.fmt())
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) across the corpus.")
        if not findings:
            print("  corpus is clean.")

    failed = bool(errors) or (args.strict and bool(warnings))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
