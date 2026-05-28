---
id: widget-spec
title: Widget — Specification
type: spec
status: canonical
created: 2026-05-20
updated: 2026-05-27
tags: [widget, storage]
supersedes: widget-plan
---

# Widget — Specification

> **Status:** canonical · **Updated:** 2026-05-27 · supersedes `widget-plan`

## How to read this document

The normative contract for the Widget. Requirements use **MUST / SHOULD / MAY**.
This spec consolidated and replaced the original [`widget-plan`](historical/widget-plan.md);
the storage choice it depends on is recorded in [widget-adr §2](widget-adr.md#2-decision).

## Contents

- [1. Purpose and scope](#1-purpose-and-scope)
- [2. Goals and non-goals](#2-goals-and-non-goals)
- [3. Requirements](#3-requirements)
- [Acceptance criteria](#acceptance-criteria)
- [References](#references)

---

## 1. Purpose and scope

Specify a Widget that persists items durably and serves them by id.

### In scope

- The Widget's storage contract and its read/write API shape.

### Out of scope (guardrails)

- Deployment topology and the choice of storage engine (see [widget-adr §2](widget-adr.md#2-decision)).

## 2. Goals and non-goals

### Goals

- **Durable** — a written item MUST survive a restart.

### Non-goals

- Not a cache; eviction is out of scope.

## 3. Requirements

- **R1** — A `put(id, item)` MUST be durable before it returns.
- **R2** — A `get(id)` SHOULD return in O(1) amortized.

## Acceptance criteria

- [ ] R1 verified by a restart test.
- [ ] No statement contradicts the storage decision in [widget-adr §2](widget-adr.md#2-decision).

## References

- [widget-adr](widget-adr.md) — the storage-engine decision.
- [widget-plan](historical/widget-plan.md) — the superseded original plan.
