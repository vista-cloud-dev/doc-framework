# doc-framework

A portable, project-agnostic **scaffold** for a corpus of technical documents that
evolves from first ideation to a final, cross-validated specification — and stays
in sync and machine-reviewable the whole way.

Drop this directory into any new project, grow `docs/` from the templates, and let
the validator keep the corpus coherent.

## What's here

| Path | What it is |
|---|---|
| [`FRAMEWORK.md`](FRAMEWORK.md) | **The standard.** Naming, tagging, structure, semantics, frontmatter, lifecycle, cross-referencing, and Claude best-practices. Read this first. |
| [`templates/`](templates/) | One copy-and-fill skeleton per document type: `spec`, `adr`, `investigation`, `research`, `plan`, `map`, `guide`, `log`, plus `index.md` for `docs/README.md`. |
| [`schema/frontmatter.schema.json`](schema/frontmatter.schema.json) | JSON Schema for the frontmatter — wire it into your editor for live validation. |
| [`tools/validate_docs.py`](tools/validate_docs.py) | Zero-dependency corpus validator (frontmatter, enums, links, anchors, supersession). |
| [`ci/github-actions-docs.yml`](ci/github-actions-docs.yml) | A CI gate that runs the validator on PRs touching `docs/`. |
| [`examples/docs/`](examples/docs/) | A minimal valid corpus (spec + ADR + superseded plan) that passes the validator. |

## Bootstrap a new project

```sh
# 1. Copy the scaffold in beside your code.
cp -R doc-framework/ /path/to/new-project/doc-framework/

# 2. Create the docs tree and its index.
mkdir -p /path/to/new-project/docs
cp doc-framework/templates/index.md /path/to/new-project/docs/README.md

# 3. Wire the CI gate.
mkdir -p /path/to/new-project/.github/workflows
cp doc-framework/ci/github-actions-docs.yml /path/to/new-project/.github/workflows/docs-validate.yml
```

## Add a document

1. Pick the type ([taxonomy](FRAMEWORK.md#4-document-taxonomy)) and copy
   `templates/<type>.md` to `docs/<topic>-<type>.md`.
2. Fill the frontmatter: set `id` = the filename stem, dates = today.
3. Write the body from the type's section spine.
4. Validate:

```sh
python3 doc-framework/tools/validate_docs.py docs/
```

## The lifecycle in one line

`plan` (ideate) → `research` / `investigation` (explore) → `adr` (decide) →
**`spec`** (consolidate into the canonical contract) → `guide` / `map` / `log`
(use, relate, remember). Supersede, never fork; one canonical doc per fact.
See [FRAMEWORK.md §3](FRAMEWORK.md#3-the-document-lifecycle).

## Try the validator now

```sh
python3 tools/validate_docs.py examples/docs/
# → 0 error(s), 0 warning(s) across the corpus.  corpus is clean.
```
