<!--
COPY ME to docs/README.md. This is the corpus INDEX: every active doc is listed
here (the validator warns about active docs that are missing). Update it whenever
you add a doc or supersede one. This file needs no frontmatter.
-->

# <Project> documentation

<One paragraph: what this project is and what the docs cover. Start with the
canonical spec.>

## Specifications (canonical)

- [`<topic>-spec.md`](<topic>-spec.md) — <one-line description>.

## Decisions (ADRs)

- [`<topic>-adr.md`](<topic>-adr.md) — <the decision>.

## Plans, research, investigations

- [`<topic>-plan.md`](<topic>-plan.md) — <…>.
- [`<topic>-research.md`](<topic>-research.md) — <…>.
- [`<topic>-investigation.md`](<topic>-investigation.md) — <…>.

## Maps, guides, logs

- [`<topic>-map.md`](<topic>-map.md) — <…>.
- [`<topic>-guide.md`](<topic>-guide.md) — <…>.
- [`<topic>-log.md`](<topic>-log.md) — <…>.

## Historical (superseded — kept for history)

- [`historical/<topic>-v1.md`](historical/<topic>-v1.md) — superseded by <current>.

---

### Status legend

`idea` → `draft` → `proposed` → `accepted`/`canonical`; terminal: `superseded`, `deprecated`.
The authoritative status of each doc is its frontmatter; this index is the human map.
Run `python3 doc-framework/tools/validate_docs.py docs/` before pushing.
