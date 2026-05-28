# Widget documentation (example corpus)

A minimal, **valid** corpus that demonstrates the framework: a canonical spec, an
accepted ADR it relies on, and a superseded plan kept in `historical/`. Run the
validator against this directory to see a clean pass:

```
python3 ../../tools/validate_docs.py .
```

## Specifications (canonical)

- [`widget-spec.md`](widget-spec.md) — the normative Widget contract.

## Decisions (ADRs)

- [`widget-adr.md`](widget-adr.md) — storage-engine decision for the Widget.

## Historical (superseded — kept for history)

- [`historical/widget-plan.md`](historical/widget-plan.md) — the original plan, superseded by the spec.

---

### Status legend

`idea` → `draft` → `proposed` → `accepted`/`canonical`; terminal: `superseded`, `deprecated`.
