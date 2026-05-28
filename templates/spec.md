---
id: topic-spec
title: Topic — Specification
type: spec
status: draft
created: 2026-01-01
updated: 2026-01-01
tags: [topic]
---

<!--
COPY ME to docs/<topic>-spec.md. Then:
  • set id = the filename stem (e.g. "widget-spec")
  • set created/updated = today; bump updated on every material change
  • fill the bracketed <…> placeholders and delete guidance comments
A spec is the CANONICAL contract — the single source of truth. Keep it code-free:
name commands/files/ports/config, but do not paste implementation source.
-->

# Topic — Specification

> **Status:** draft · **Updated:** 2026-01-01

## How to read this document

This is the **normative contract** for <what>. Conventions:

- Requirements use RFC-2119 keywords: **MUST / MUST NOT / SHOULD / MAY**.
- No source listings; mechanisms are named and live in <the code repo>.
- Inline semantic tags used here: **[Tag]** — <meaning>. <!-- declare any, or delete -->

## Spec at a glance

<!-- A condensed cross-walk: the components/requirements and where each is specified. -->

| Component / requirement | Specified in | Priority | Phase |
|---|---|---|---|
| <thing> | §<n> | <P0…> | <phase> |

## Contents

- [1. Purpose and scope](#1-purpose-and-scope)
- [2. Goals and non-goals](#2-goals-and-non-goals)
- [3. Glossary](#3-glossary)
- [4. <first body section>](#4-first-body-section)
- [Acceptance criteria](#acceptance-criteria)
- [Open questions](#open-questions)
- [References](#references)

---

## 1. Purpose and scope

<One paragraph: what this specifies and why.>

### In scope

- <…>

### Out of scope (guardrails)

- <…>

## 2. Goals and non-goals

### Goals

- <…>

### Non-goals

- <…>

## 3. Glossary

| Term | Meaning |
|---|---|
| <Term> | <definition> |

## 4. <first body section>

<Numbered sections give stable anchors for cross-references. Mark each normative
statement with MUST/SHOULD and, where useful, a stable requirement id (R1, R2…).>

- **R1** — <requirement>. **[Tag]**

## Acceptance criteria

The spec is satisfied when:

- [ ] Every normative statement is traceable to a source or verified against the code.
- [ ] No statement contradicts the current working code.
- [ ] <domain-specific check>.

## Open questions

- **Q1** — <open question>.

## References

- [<related doc>](<file>.md) — <why it matters>.
