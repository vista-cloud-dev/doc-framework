# doc-framework

A tiny, project-agnostic standard for a corpus of markdown docs, plus the one tool
that keeps it honest: a **link/anchor integrity checker**.

The whole standard is one page — [`CONVENTIONS.md`](CONVENTIONS.md). In short:
kebab-case filenames, frontmatter optional, **links must resolve**, supersede by
editing and let git be the changelog.

## What's here

| Path | What it is |
|---|---|
| [`CONVENTIONS.md`](CONVENTIONS.md) | **The standard**, in one page. Read this first. |
| [`tools/link-check.py`](tools/link-check.py) | Zero-dependency markdown link + anchor checker — the only gate. |
| [`.github/workflows/validate.yml`](.github/workflows/validate.yml) | Reusable CI workflow; consumers `uses:` it (don't vendor the script by `cp`). |
| [`ci/github-actions-docs.yml`](ci/github-actions-docs.yml) | Standalone CI gate, for a repo that prefers to run the script directly. |
| [`examples/docs/`](examples/docs/) | A minimal corpus that passes the checker. |

## Use it in a project

Grow `docs/` as plain kebab-case markdown, then wire the gate. Prefer the reusable
workflow — one source of truth, no vendored copy to drift:

```yaml
# <your-repo>/.github/workflows/docs-validate.yml
name: docs-validate
on:
  push:        { paths: ["docs/**", ".github/workflows/docs-validate.yml"] }
  pull_request: { paths: ["docs/**"] }
jobs:
  validate:
    uses: vista-cloud-dev/doc-framework/.github/workflows/validate.yml@main
    with: { corpus_path: docs }   # omit to validate the whole repo
```

## Run the checker locally

```sh
python3 tools/link-check.py docs/
python3 tools/link-check.py examples/docs/
# → 0 error(s) across the corpus.  corpus is clean.
```

Exit `0` when every link/anchor resolves, `1` if any are broken, `2` on bad
invocation. Pure stdlib — no `pip install`, airgapped-friendly.
