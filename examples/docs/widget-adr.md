---
id: widget-adr
title: Widget — Storage Engine Decision (ADR)
type: adr
status: accepted
created: 2026-05-22
updated: 2026-05-22
tags: [widget, storage, decision]
---

# Widget — Storage Engine Decision (ADR)

> **Status:** accepted · **Updated:** 2026-05-22

## 1. Context

The Widget MUST be durable (see [widget-spec §3](widget-spec.md#3-requirements)).
The deployment is single-node with modest write volume.

## 2. Decision

**On 2026-05-22 we decided: use an embedded key-value store (single file, no server).**

It satisfies the durability requirement without operating a separate database
process, matching the single-node deployment.

## 3. Alternatives considered

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **Embedded KV** | No server; durable; simple | Single-node only | **Chosen** |
| Client/server SQL | Scales out | Extra process to operate | Rejected — premature |

## 4. Consequences

- **Positive:** zero operational surface beyond the app process.
- **Negative:** a future multi-node need would require a new ADR superseding this.

## References

- [widget-spec](widget-spec.md) — the contract this decision serves.
