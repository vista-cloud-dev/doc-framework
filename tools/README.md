# tools/

## `link-check.py`

The corpus link/anchor integrity checker — the one doc gate (see
[`../CONVENTIONS.md`](../CONVENTIONS.md)). Zero external dependencies (pure stdlib,
airgapped-friendly).

```sh
python3 link-check.py path/to/docs/            # check a corpus
python3 link-check.py path/to/docs/ --json     # machine-readable findings
```

Exit code `0` when every link/anchor resolves, `1` if any are broken, `2` on bad
invocation.

### What it checks

| Code | Meaning |
|---|---|
| `LINK`   | A relative `*.md` link target does not exist. |
| `ANCHOR` | A `#anchor` does not match any heading in the target (or, intra-doc, in this file). |
| `EMPTY`  | No `.md` files found under the given path. |

Frontmatter is **not** parsed or enforced — it is free-form and optional. Links to
sibling repos that escape the corpus root are skipped (unverifiable in a single-repo
CI checkout; use GitHub URLs). These directories are skipped entirely:
`prompts/ archive/ retired/ historical/ memory/ modules/` — inbound links into them
still resolve.
