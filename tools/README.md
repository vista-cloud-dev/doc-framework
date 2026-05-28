# tools/

## `validate_docs.py`

The corpus validator for the [framework](../FRAMEWORK.md). Zero external
dependencies — it uses PyYAML if importable, otherwise a built-in parser for the
frontmatter dialect in [FRAMEWORK.md §6](../FRAMEWORK.md#6-frontmatter-standard).

```sh
python3 validate_docs.py path/to/docs/            # validate a corpus
python3 validate_docs.py path/to/docs/ --json     # machine-readable findings
python3 validate_docs.py path/to/docs/ --strict   # warnings also fail
```

Exit code `0` when clean (no errors; no warnings under `--strict`), `1` otherwise,
`2` on bad invocation.

### What it checks

| Code | Level | Meaning |
|---|---|---|
| `FM-PARSE` | error | Missing/unterminated/invalid frontmatter. |
| `FM-REQ` | error | A required field is missing. |
| `FM-ID` | error | `id` is not kebab-case. |
| `ID-STEM` | error | `id` does not equal the filename stem. |
| `ID-DUP` | error | Two docs share an `id`. |
| `TYPE` / `STATUS` | error | Value not in the allowed enum. |
| `DATE` / `DATE-ORDER` | error | Bad ISO date, or `updated` before `created`. |
| `TAGS` | error/warn | `tags` not a list (error) or absent (warning). |
| `SUP-MISSING` | error | `superseded` status without `superseded_by`. |
| `SUP-REF` | error | `supersedes`/`superseded_by` does not resolve to a doc. |
| `SUP-BIDIR` | error | Supersession link is not declared on both sides. |
| `SUP-STATUS` | error | Has `superseded_by` but status is not superseded/deprecated. |
| `SUP-LOC` | warning | Superseded/deprecated doc not under `historical/`. |
| `LINK` | error | A relative `*.md` link target does not exist. |
| `ANCHOR` | error | A `#anchor` does not match any heading in the target. |
| `INDEX` | warning | An active doc is not linked from `docs/README.md`. |

`README.md` files are treated as navigation (no frontmatter required), but their
links are still checked.

### Editor integration

Point your editor's YAML tooling at [`../schema/frontmatter.schema.json`](../schema/frontmatter.schema.json)
for live frontmatter validation while writing.
