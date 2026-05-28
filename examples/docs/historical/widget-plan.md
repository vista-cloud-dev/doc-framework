---
id: widget-plan
title: Widget — Plan
type: plan
status: superseded
created: 2026-05-01
updated: 2026-05-20
tags: [widget, plan]
superseded_by: widget-spec
---

# Widget — Plan

> **Superseded by [`widget-spec`](../widget-spec.md) (kept for history).**

## TL;DR

The original framing for a durable Widget. Consolidated into, and replaced by,
[`widget-spec`](../widget-spec.md).

## 1. Context

We need somewhere to persist items and read them back by id.

## 4. Phased roadmap

| Phase | Goal | Prevents | Verified by |
|---|---|---|---|
| **P0** | Pick a storage engine | thrashing the data model later | the ADR decision |
| **P1** | Implement put/get | losing data on restart | a restart test |

## 5. Open decisions

- **Q1** — which storage engine? *(Resolved in the ADR; see the current spec.)*

## References

- [`widget-spec`](../widget-spec.md) — the spec that superseded this plan.
