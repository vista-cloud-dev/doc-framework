---
id: framework
title: Technical Documentation Framework
type: spec
status: canonical
created: 2026-05-27
updated: 2026-05-27
tags: [meta, documentation, framework, standard]
---

# Technical Documentation Framework

A naming, tagging, structuring, and lifecycle standard for an evolving corpus of
**technical** project documents — from first ideation through to a final,
cross-validated specification — designed so that (a) every document stays in sync
with the others, and (b) the whole corpus is machine-tractable: linkable,
linted, and reviewable by a tool or an LLM.

> This document **is itself** an instance of the framework (it dogfoods the
> conventions below). Read it once end-to-end; thereafter use it as reference and
> copy from `templates/` to start new documents.

## How to read this document

This is the **normative standard**. Conventions:

- **Normative** keywords follow RFC 2119: **MUST / MUST NOT / SHOULD / SHOULD NOT
  / MAY**. A *MUST* is checked by the validator (`tools/validate_docs.py`) where
  mechanically possible; a *SHOULD* is a convention the validator may warn about.
- File and field names appear `in code font`. Cross-references use the inline-link
  convention defined in [§9](#9-cross-referencing-and-keeping-docs-in-sync).
- "The corpus" = all the documents under a project's `docs/` tree. "A doc" = one
  markdown file with valid frontmatter.

## Contents

- [1. Purpose and scope](#1-purpose-and-scope)
- [2. Quickstart](#2-quickstart)
- [3. The document lifecycle](#3-the-document-lifecycle)
- [4. Document taxonomy](#4-document-taxonomy)
- [5. Naming and file organization](#5-naming-and-file-organization)
- [6. Frontmatter standard](#6-frontmatter-standard)
- [7. Structural conventions](#7-structural-conventions)
- [8. Semantic conventions](#8-semantic-conventions)
- [9. Cross-referencing and keeping docs in sync](#9-cross-referencing-and-keeping-docs-in-sync)
- [10. Status and supersession lifecycle](#10-status-and-supersession-lifecycle)
- [11. Validation and CI](#11-validation-and-ci)
- [12. Working with Claude to evolve a spec](#12-working-with-claude-to-evolve-a-spec)
- [13. Glossary](#13-glossary)
- [14. Appendix: the type-to-sections matrix](#14-appendix-the-type-to-sections-matrix)

---

## 1. Purpose and scope

### In scope

- A **moderate** YAML frontmatter schema every doc carries ([§6](#6-frontmatter-standard)).
- A fixed **document taxonomy** (eight types) and the **lifecycle** that moves an
  idea from ideation to a canonical spec ([§3](#3-the-document-lifecycle), [§4](#4-document-taxonomy)).
- **Naming**, **structure**, **semantic markup**, and **cross-reference**
  conventions ([§5](#5-naming-and-file-organization)–[§9](#9-cross-referencing-and-keeping-docs-in-sync)).
- A **single-source-of-truth** discipline + **supersession protocol** that keep
  documents from drifting out of sync ([§9](#9-cross-referencing-and-keeping-docs-in-sync), [§10](#10-status-and-supersession-lifecycle)).
- A zero-dependency **validator** + a **CI** gate ([§11](#11-validation-and-ci)).
- **Claude best-practices** for turning ad-hoc spec evolution into a repeatable,
  approval-gated process ([§12](#12-working-with-claude-to-evolve-a-spec)).

### Out of scope (guardrails)

- **Creative / marketing / end-user prose.** This is a standard for *technical*
  documents (specs, decisions, research, plans).
- **Prescribing your prose style.** The framework constrains *structure and
  metadata*, not voice.
- **A heavyweight metadata graph.** Cross-document dependencies stay as **inline
  links** (validated), not duplicated into frontmatter. Only the **supersession**
  relationship is machine-encoded, because the lifecycle depends on it.
- **Modifying any existing corpus.** This scaffold is greenfield: copy it into a
  new project and grow `docs/` from the templates.

---

## 2. Quickstart

**Start a new project's docs:**

1. Copy this `doc-framework/` directory into the new repo (it can live beside
   `docs/`; it changes rarely and is the standard + tooling).
2. Create `docs/` and `docs/README.md` from `templates/index.md`.
3. Wire the CI gate from `ci/github-actions-docs.yml`.

**Add a document:**

1. Pick the type ([§4](#4-document-taxonomy)) and copy the matching
   `templates/<type>.md` into `docs/`.
2. Fill the frontmatter ([§6](#6-frontmatter-standard)); set `id` = the filename
   stem, `created`/`updated` = today.
3. Write the body using the type's section spine ([§7](#7-structural-conventions),
   [§14](#14-appendix-the-type-to-sections-matrix)).
4. Run the validator: `python3 doc-framework/tools/validate_docs.py docs/`.

**Evolve a document:** edit it, bump `updated`, keep `created` fixed. Let git be
the changelog. When a doc replaces another, follow the supersession protocol
([§10](#10-status-and-supersession-lifecycle)).

---

## 3. The document lifecycle

A technical idea matures along a predictable path. The framework names the
**stages** and maps each to the document **type** that carries it. The same idea
typically produces several documents over time; the goal is that exactly **one**
is canonical for each fact at any moment.

```
 ideation        exploration / discovery        decision           consolidation        steady state
    │                     │                         │                     │                  │
    ▼                     ▼                         ▼                     ▼                  ▼
  PLAN ───────────►  RESEARCH / INVESTIGATION ──► ADR ──────────►  SPEC (canonical) ──►  GUIDE
 (the goal,          (survey the landscape;      (record the       (reconcile all       (how to use
  framing,            probe a specific           decision +         supporting docs       the result)
  open questions)     question; "Finding:")      alternatives)      into one source       LOG / MAP
                                                                     of truth)            (history / graph)
```

- **Ideation** → a `plan` frames the goal, the constraints, and the open
  questions. It is allowed to be speculative and is expected to change.
- **Exploration / discovery** → `research` surveys an external landscape (tools,
  prior art); `investigation` probes one specific question and ends in a
  **Finding**.
- **Decision** → an `adr` records a single decision, the alternatives considered,
  and the consequences. ADRs are append-only in spirit: you supersede, not edit
  away, a decision.
- **Consolidation** → a `spec` is the **canonical** contract. When several
  overlapping sources exist (an older spec, a log, the working code), a
  *consolidation pass* reconciles them into one spec and supersedes the rest
  ([§12](#12-working-with-claude-to-evolve-a-spec)).
- **Steady state** → a `guide` explains how to use the result; a `log` preserves
  the chronological "why"; a `map` holds the dependency/integration graph.

The lifecycle is reflected in two frontmatter fields: `type` (which kind of doc)
and `status` (where it is in its own maturity arc — [§10](#10-status-and-supersession-lifecycle)).

---

## 4. Document taxonomy

Exactly **eight** types. The `type` field MUST be one of these. Pick by intent,
not by topic.

| `type` | Purpose | Ends with / hallmark | Typical `status` arc |
|---|---|---|---|
| `spec` | The normative contract: what MUST be true. The source of truth. | Acceptance criteria; normative MUST/SHOULD language. | `draft → proposed → canonical → superseded` |
| `adr` | One architecture/technology **decision** + alternatives + consequences. | A dated "Decision" statement. | `proposed → accepted → superseded` |
| `investigation` | Probe **one** question; reduce uncertainty. | A clearly labelled **Finding**. | `draft → accepted` (then feeds a spec/ADR) |
| `research` | Survey an external landscape (tools, prior art, options). | A comparison table + recommendation. | `draft → accepted` |
| `plan` | Frame a goal: context, strategy, phasing, open questions. | A phased roadmap + open decisions. | `draft → proposed → superseded` (by a spec) |
| `map` | The dependency / integration graph across components. | A graph + an ordered implementation sequence. | `draft → canonical` |
| `guide` | How to *use* the built thing (onboarding, how-to). | Step-by-step, runnable instructions. | `draft → canonical` |
| `log` | Chronological narrative: decisions, discoveries, errors, remedies. | Numbered ledgers (D#, E#, …) + a re-implementation blueprint. | `draft → accepted` (append-only) |

Rules:

- A doc has **exactly one** `type`. If it is doing two jobs (e.g. an ADR *and* a
  tool design), the **primary** intent wins; name the secondary in the title and
  body (e.g. *"language decision (ADR) + tool design"*).
- Only a `spec` (or a `map` for graph facts) is allowed to be **canonical**. A
  `plan`/`research`/`investigation` feeds a spec but is not itself the contract.
- When a `plan` has been fully absorbed into a `spec`, mark the plan
  `superseded_by` the spec ([§10](#10-status-and-supersession-lifecycle)).

---

## 5. Naming and file organization

### File names

- **`kebab-case.md`**, all lowercase, ASCII. The name describes the *topic*, not
  the type (type lives in frontmatter): `iris-source-materialization.md`,
  `host-side-go-toolchain.md`.
- A **type suffix** SHOULD be appended only when it disambiguates a topic that has
  several docs: `-adr`, `-spec`, `-investigation`, `-map`, `-guide`. Example:
  `liberation-binary-design.md` (design note) vs a hypothetical
  `liberation-binary-adr.md`.
- A **variant suffix** distinguishes parallel bindings of one contract:
  `<topic>-spec.md` (core) with `<topic>-spec-<variant>.md` profiles
  (`-public`, `-va`). The core and each variant are **separate docs**, never mixed.
- **Versioning:** prefer `status` + supersession over version-in-filename. Use a
  `-vN` suffix **only** when you deliberately want the version visible in the path
  (e.g. a spec that is re-cut wholesale); the superseded `-v{N-1}` then moves to
  `historical/` ([§10](#10-status-and-supersession-lifecycle)).

### `id`

- `id` MUST equal the filename stem (the name without `.md`). This makes the
  filename the stable handle used in `supersedes` / `superseded_by` and in human
  references. Renaming a file means updating its `id` and every reference — the
  validator flags the mismatch.

### Directory layout

```
docs/
  README.md                  ← the index (from templates/index.md); lists every active doc
  <topic>.md                 ← active docs at the root, or…
  <component>/<topic>.md      ← …grouped into a subdirectory per component when the corpus grows
  historical/                ← superseded / deprecated docs (kept for history)
    <topic>-v1.md
  prompts/                   ← session hand-off / kickoff docs (NOT validated)
```

- Group into component subdirectories once a flat `docs/` exceeds ~12 files.
- **`prompts/` is excluded from validation** (`EXCLUDE_DIRS` in `validate_docs.py`).
  Kickoff / session-handoff docs are working notes with their own lightweight
  frontmatter, not part of the validated corpus; the frontmatter dialect and
  type/status enums do not apply to them.
- **Superseded** and **deprecated** docs MUST live under `historical/` and carry a
  supersession banner ([§10](#10-status-and-supersession-lifecycle)). Never delete a
  superseded doc; git history is not a substitute for a discoverable, banner-topped
  archive.

---

## 6. Frontmatter standard

Every doc MUST begin with a YAML frontmatter block delimited by `---` on its own
line, before any other content. The schema is **moderate**: enough for machine
indexing and lifecycle checks, no heavier. The authoritative schema is
[`schema/frontmatter.schema.json`](schema/frontmatter.schema.json) (usable by
editors for live validation).

```yaml
---
id: iris-source-materialization        # REQUIRED — stable; equals the filename stem
title: IRIS Source Materialization      # REQUIRED — human title (≈ the H1)
type: plan                              # REQUIRED — one of the eight (§4)
status: proposed                        # REQUIRED — one of the seven (§10)
created: 2026-05-22                     # REQUIRED — ISO date, never changes
updated: 2026-05-22                     # REQUIRED — ISO date, bump on material edit
tags: [iris, source, m-cli]             # RECOMMENDED — flat list of kebab-case topics
supersedes: iris-source-plan-v1         # OPTIONAL — id of the doc this replaces
superseded_by: ""                       # OPTIONAL — id of the doc that replaced this
---
```

| Field | Req. | Type | Rule |
|---|:--:|---|---|
| `id` | MUST | string | kebab-case; **equals filename stem**; unique across the corpus. |
| `title` | MUST | string | Human-readable; SHOULD match the H1. |
| `type` | MUST | enum | One of the eight types ([§4](#4-document-taxonomy)). |
| `status` | MUST | enum | One of the seven statuses ([§10](#10-status-and-supersession-lifecycle)). |
| `created` | MUST | date | `YYYY-MM-DD`; set once, never changed. |
| `updated` | MUST | date | `YYYY-MM-DD`; `>= created`; bump on material change. |
| `tags` | SHOULD | list | Flat list of kebab-case strings. Inline form `[a, b]` or block form. |
| `supersedes` | MAY | string | `id` of the doc this one replaces (see [§10](#10-status-and-supersession-lifecycle)). |
| `superseded_by` | MAY | string | `id` of the doc that replaced this one. |

**Frontmatter dialect (so the validator is dependency-free):** keep values to
**scalars** and **flat lists**. Do not nest maps. Strings need quotes only when
they contain `:` or start with a special character. This subset parses with or
without PyYAML.

**Why frontmatter and not the inline `**Status:** …` header block?** The corpus
this framework grew from used a bold header line. Frontmatter is strictly better
for machine review: it is unambiguous to parse, schema-checkable, and ignored by
markdown renderers. You MAY *also* keep a one-line human status banner just under
the H1 (see templates) — but the frontmatter is authoritative.

---

## 7. Structural conventions

Every doc shares a **section spine**; each type adds or drops sections (the full
matrix is [§14](#14-appendix-the-type-to-sections-matrix)). The templates encode
this — start from them.

The common spine, in order:

1. **Frontmatter** ([§6](#6-frontmatter-standard)).
2. **`# H1 title`** — matches `title`.
3. **Status banner** *(optional, one line)* — e.g.
   `> **Status:** proposed · **Updated:** 2026-05-27 · supersedes \`old-id\``.
   Human convenience; the frontmatter is authoritative.
4. **"How to read this document"** — what this is, who it is for, and a
   **Conventions** sub-block declaring normative language and any inline semantic
   tags ([§8](#8-semantic-conventions)). Required for `spec` and `adr`; recommended
   elsewhere.
5. **TL;DR / "At a glance"** — a short abstract or a summary table. Required for
   any doc over ~150 lines.
6. **Contents** — a TOC with anchor links, for any doc with more than ~6 sections.
7. **Body** — **numbered** `## N. Section` headings (`### N.M` for subsections).
   Numbering gives every section a stable handle for cross-references
   ([§9](#9-cross-referencing-and-keeping-docs-in-sync)).
8. **Open questions** — explicit, ID'd (`Q1`, `Q2`) where a doc is still maturing.
9. **References** — the doc's external and internal sources, last.
10. **Appendices** — "Key facts", matrices, ledgers.

Recurring section idioms (use the exact names so the corpus is uniform):

- **In scope / Out of scope (guardrails)** — bound the doc explicitly.
- **Goals and Non-Goals** — for specs and plans.
- **Glossary** — a term table; required once a doc introduces ≥5 domain terms.
- **Decision** — for ADRs: a dated, one-paragraph statement, then **Alternatives
  considered** and **Consequences**.
- **Phased roadmap** — ordered phases; each phase SHOULD name *the failure it
  prevents* and *how it is verified* (a pattern that makes plans testable).
- **Acceptance criteria** — for specs: "this is done when…", as a checklist.

---

## 8. Semantic conventions

These make the *meaning* inside a doc machine-addressable.

### 8.1 Normative language

Normative docs (`spec`, `adr`) MUST use RFC-2119 keywords (**MUST / MUST NOT /
SHOULD / SHOULD NOT / MAY**) and declare so in their Conventions block. Avoid
normative weasel words ("ideally", "try to") in a requirement.

### 8.2 Inline semantic tags

A project MAY define a small set of **inline tags** — single bracketed words —
to classify statements that recur across the corpus, and MUST declare them in a
legend. The framework defines the *mechanism*; each project defines its *tags*.

Example legend (from a real corpus):

> - **[Parity]** — MUST be identical across environments.
> - **[Profile]** — a value supplied by an environment profile.
> - **[Instance]** — a value discovered from the target system.

A tagged line then reads: *"The developer's command set is identical **[Parity]**."*
Tags are greppable, so "show me everything that must stay in parity" is one search.

### 8.3 Stable IDs for ledger items

Things that get **referenced from other docs** MUST carry a stable ID prefix so
references survive edits and re-ordering:

| Prefix | Meaning | Example reference |
|---|---|---|
| `R#` | Requirement | "satisfies **R8**" |
| `D#` | Decision / Discovery | "per **D14**" |
| `E#` | Error + remedy (in a `log`) | "the **E16** late-failure" |
| `Q#` | Open question | "blocked on **Q3**" |

IDs are assigned once and never renumbered; a withdrawn item is struck through,
not deleted, so the numbering stays stable.

### 8.4 Reconciliation vocabulary

When a consolidation pass reconciles documents against ground truth (usually the
working **code**), tag each claim with one of: **CONFIRMED** (matches code) /
**CONTRADICTED** (code differs — record the code's actual value) / **STALE** (no
longer applies) / **UNVERIFIABLE**. The rule: *when docs and code disagree, the
code wins*, and the discrepancy is footnoted. See
[§12](#12-working-with-claude-to-evolve-a-spec).

---

## 9. Cross-referencing and keeping docs in sync

### 9.1 The single-source-of-truth principle

Each fact is **owned by exactly one doc**. Every other doc that needs it
**links** to the owner instead of restating it. Restating a fact in two places is
how corpora drift; a link cannot drift (and the validator catches it if the target
moves). When you must summarize a linked fact for flow, keep the summary to one
sentence and link to the authority for the detail.

### 9.2 Inline link convention

Cross-references are **inline markdown links**, never duplicated into frontmatter.
Use a short **alias + section** so the link reads naturally and points precisely:

```
[core §6.5](vista-iris-dev-bridge-spec.md#65-round-trip-mechanics)
[`liberation-binary-design.md`](liberation-binary-design.md)
[R8](iris-tooling-dependency-map.md#6-m-dev-tools-requirements-for-iris)
```

- **Same-repo links use *relative* paths** (relative to the linking file). Links to
  `historical/` are fine.
- A link to a section MUST include the `#anchor`; the validator resolves anchors
  against the target file's headings (GitHub slug rules).
- An external link (http/https) is not anchor-checked but SHOULD live in the
  **References** section if it is a primary source.

#### Cross-repo links — use a GitHub URL, never a `../../` filesystem path

In a multi-repo project (sibling repos in one workspace), it is tempting to link a doc
in another repo with a relative path like `../../m-stdlib/docs/foo.md` or `../../CLAUDE.md`.
**Don't.** Such a path resolves *only* in a full local checkout of every sibling repo; it
is **broken** in:
- **CI**, which checks out a single repo (the link target doesn't exist there), and
- the **GitHub web view** (relative paths can't escape the repo).

**Rule:** a link whose target lives in **another repo** MUST be a **full GitHub URL**:

```
[m-stdlib S3 design](https://github.com/vista-cloud-dev/m-stdlib/blob/main/docs/plans/m-stdlib-s3-design.md)
[the org increment protocol](https://github.com/vista-cloud-dev/.github/blob/main/CLAUDE.md)
```

The validator enforces this *negatively*: it **does not error** on a link that escapes the
corpus root (it cannot verify a sibling repo it can't see), so a stray `../../` won't fail
CI — but it also won't be checked, so it silently rots. A GitHub URL renders and resolves
everywhere. Keep **relative** paths for **intra-repo** links (those *are* validated).

### 9.3 Section anchors

Anchors follow GitHub's slug algorithm: lowercase, strip markdown/punctuation,
spaces → hyphens. Numbered headings (`## 6.5 Round-trip mechanics`) give stable,
human-meaningful anchors (`#65-round-trip-mechanics`). This is the main reason the
spine uses numbered sections ([§7](#7-structural-conventions)).

### 9.4 Keeping in sync — the mechanics

1. **Own each fact once** (§9.1); link, don't copy.
2. **Bump `updated`** on the owning doc when the fact changes; let git hold the
   diff. Optionally add a one-line *"Recent significant changes"* note near the top
   that points to `git log` rather than maintaining an in-doc changelog.
3. **Run the validator** ([§11](#11-validation-and-ci)) — it fails on a moved
   target, a dead anchor, a duplicate `id`, or a broken supersession link, which is
   exactly how desync manifests mechanically.
4. **Supersede, don't fork** — when a doc is replaced, follow §10 so the old one
   self-declares as stale.

---

## 10. Status and supersession lifecycle

### 10.1 The `status` values

| `status` | Meaning | Constraints |
|---|---|---|
| `draft` | In progress, not yet circulated. | — |
| `proposed` | Circulated for review/decision. | — |
| `accepted` | Agreed; the decision/finding stands (esp. `adr`, `investigation`, `research`, `log`). | — |
| `canonical` | The current source of truth (only `spec` / `map`). | At most one canonical doc per topic. |
| `superseded` | Replaced by another doc. | MUST set `superseded_by`; MUST live in `historical/`; MUST carry the banner. |
| `deprecated` | No longer relevant, not replaced. | SHOULD live in `historical/`; SHOULD carry the banner. |
| `idea` | A captured thought not yet worked (optional early state). | — |

### 10.2 The supersession protocol

When document **B** replaces document **A**:

1. In **B**'s frontmatter: `supersedes: A`.
2. In **A**'s frontmatter: `superseded_by: B`, `status: superseded`.
3. Move **A** into `historical/` and add a top banner directly under its H1 (the
   literal markdown to paste, with `B` = the replacing doc's id):

   ```markdown
   > **Superseded by [`B`](../B.md) (kept for history).**
   ```

4. Update `docs/README.md` (the index) to point at **B**.
5. Run the validator — it checks the link is **bidirectional** (A↔B), that A's
   status is `superseded`/`deprecated`, and that B exists.

This is the single most important rule for a corpus that stays coherent: there is
always exactly one live document for each contract, and every dead one points
forward to its replacement.

---

## 11. Validation and CI

### 11.1 The validator

`tools/validate_docs.py` is a **zero-dependency** Python 3 script (uses PyYAML if
present, otherwise a built-in parser for the frontmatter dialect in §6). Run it
against a docs tree:

```
python3 doc-framework/tools/validate_docs.py docs/
python3 doc-framework/tools/validate_docs.py docs/ --json     # machine-readable
python3 doc-framework/tools/validate_docs.py docs/ --strict   # warnings become errors
```

**Slimmed (2026-06-23).** The validator gates on **cross-reference integrity only** —
the one class of finding that is always a real defect — and treats everything else as
**advisory**. It is also **dialect-agnostic**: the corpus uses two frontmatter dialects
(framework `id/type/updated`, proposal `doc_type/last_modified`) and the validator
enforces neither; it only *notices* the common core. The former ceremony (type/status
enums, `id`↔filename, the supersession protocol, index coverage, tags) was **removed** —
the corpus never adopted that dialect, so those checks produced noise, not signal.

It checks:

- **Link + anchor integrity (ERROR — the gate):** every relative same-repo `*.md` link
  resolves to a file; every `#anchor` resolves to a heading in the target (GitHub slug
  rules). **Cross-repo links** (targets escaping the corpus root) are **skipped, not
  errored** — they're unverifiable in a single-repo CI checkout; use a GitHub URL for
  those (§9.2).
- **Basic frontmatter (WARNING — advisory):** frontmatter present + parseable; the
  common core (`title`/`status`/`created`) present; `created`/`updated`/`last_modified`
  are ISO `YYYY-MM-DD`. None of these fail the build (the corpus legitimately includes
  frontmatter-less working notes).
- Excluded from validation entirely: `prompts/`, `archive/`, `memory/`, `retired/`.

Exit code is non-zero if any **error** (broken link/anchor) is found — or, with
`--strict`, on any warning too.

### 11.2 CI — call the reusable workflow (don't vendor by `cp`)

Consumers reference the framework's **reusable workflow** instead of copying the
validator into each repo (which drifts). In `<repo>/.github/workflows/docs-validate.yml`:

```yaml
name: docs-validate
on:
  push:         { paths: ["**/*.md", ".github/workflows/docs-validate.yml"] }
  pull_request: { paths: ["**/*.md"] }
jobs:
  validate:
    uses: vista-cloud-dev/doc-framework/.github/workflows/validate.yml@main
    # with: { corpus_path: docs }   # only if docs live in a subdir
```

The reusable workflow (`.github/workflows/validate.yml`) checks out the caller corpus and
this framework separately and runs the slim validator against the corpus — one source of
truth, no vendored copy to re-sync. (The old `cp ci/github-actions-docs.yml …` /
`cp tools/validate_docs.py …` vendoring is deprecated; the template in `ci/` remains for
air-gapped consumers that cannot reference a reusable workflow.)

---

## 12. Working with Claude to evolve a spec

The aim is to turn ad-hoc, conversational spec-writing into a **repeatable,
approval-gated** process. These practices are distilled from how the framework's
source corpus was actually built, plus common patterns for LLM-assisted spec work.

### 12.1 Plan first, write on approval

For any non-trivial doc change, instruct Claude to **work in plan mode first**:
read all inputs, present a proposed table of contents and the findings/decisions,
and **wait for approval** before writing the document. This catches scope and
structure problems before they are baked into prose.

### 12.2 The consolidation pass (the core move)

The recurring problem is **several overlapping sources of truth** (an old spec, a
log, the working code) that partly disagree. Resolve it with a consolidation pass:

1. **Read every input fully**, plus the ground truth (the **code**).
2. Build a **reconciliation table**: for each material claim, tag it CONFIRMED /
   CONTRADICTED / STALE / UNVERIFIABLE against the code ([§8.4](#8-semantic-conventions)).
   **When docs and code disagree, the code wins** and the conflict is footnoted.
3. **Present the TOC + reconciliation findings; wait for approval.**
4. Write **one** canonical doc; **supersede** the inputs ([§10](#10-status-and-supersession-lifecycle)).
5. Print the discrepancies found, so a human can sanity-check.

### 12.3 Write good acceptance criteria

A spec is not done until it says *how you know it is done*. Make Claude include an
**Acceptance criteria** checklist: every normative statement traceable to a source
or verified against code; no statement contradicting the code; the doc
self-contained and (for technical specs) **code-free** — name commands, files,
ports, config keys, but do not paste implementation source.

### 12.4 The reusable prompt shape

The most effective evolution prompts share a fixed anatomy. Reuse it (the
`templates/` headers mirror it):

```
ROLE & GOAL          — one paragraph: what you are producing and why.
INPUTS               — every file to read fully, named, incl. the ground-truth code.
WHAT IT IS           — the normative scope of the output.
WHAT IT IS NOT       — explicit guardrails ("not a redesign", "no source listings").
METHOD               — "plan mode first; do not write until approved"; the steps.
PROPOSED STRUCTURE   — the target TOC (adjust only with justification).
DELIVERABLES         — exact files to create/modify, banners to add, links to update.
ACCEPTANCE CRITERIA  — the done-when checklist.
"Begin by reading the inputs and presenting the plan. Do not write until I approve."
```

### 12.5 Hygiene that keeps the machine (and the human) happy

- **Reference by stable ID** (`R8`, `D14`, `§6.5`) so Claude and reviewers point
  precisely and references survive edits ([§8.3](#8-semantic-conventions)).
- **One concern per commit**; keep behavior-preserving moves separate from new
  content, so review is tractable.
- **Bump `updated`; let git be the changelog** — do not have Claude maintain an
  in-doc revision log beyond a one-line pointer.
- **Run the validator before declaring a doc synced** — treat a red validator like
  a failing test.
- **Be honest about verification** — if a build/check was not actually run, the
  doc (or the final message) must say so and give a manual checklist. Never let
  "done" outrun "verified".

---

## 13. Glossary

| Term | Meaning |
|---|---|
| **Corpus** | All documents under a project's `docs/` tree. |
| **Canonical** | The single live source of truth for a topic (`status: canonical`). |
| **Consolidation pass** | A reconciliation of overlapping sources into one canonical doc ([§12.2](#12-working-with-claude-to-evolve-a-spec)). |
| **Frontmatter** | The YAML metadata block at the top of every doc ([§6](#6-frontmatter-standard)). |
| **Ground truth** | The authority a doc is reconciled against — usually the working code. |
| **Ledger item** | A stably-ID'd requirement/decision/error/question ([§8.3](#8-semantic-conventions)). |
| **Supersession** | The protocol by which a new doc replaces an old one ([§10.2](#10-status-and-supersession-lifecycle)). |

---

## 14. Appendix: the type-to-sections matrix

`●` required · `○` recommended · `–` not typical. All types carry frontmatter +
H1 + References.

| Section | spec | adr | investigation | research | plan | map | guide | log |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| How to read / Conventions | ● | ● | ○ | ○ | ○ | ○ | ○ | ○ |
| TL;DR / At a glance | ● | ○ | ● | ● | ● | ● | ○ | ● |
| Contents (TOC) | ● | ○ | ○ | ○ | ● | ● | ○ | ● |
| In / Out of scope | ● | ○ | ● | ○ | ● | ○ | ○ | – |
| Goals and Non-Goals | ● | – | – | – | ● | – | – | – |
| Glossary | ● | ○ | ○ | ○ | ○ | ● | ○ | ○ |
| Decision + Alternatives | – | ● | – | – | – | – | – | ○ |
| Finding | – | – | ● | ○ | – | – | – | – |
| Comparison table | ○ | ○ | ○ | ● | ○ | ● | – | – |
| Phased roadmap | ○ | ○ | – | – | ● | ● | ○ | ● |
| Numbered ledgers (R/D/E) | ○ | ○ | ○ | – | ○ | ○ | – | ● |
| Acceptance criteria | ● | ○ | – | – | ○ | ○ | ○ | – |
| Open questions | ● | ● | ● | ○ | ● | ● | – | ● |
| Key-facts appendix | ○ | – | ○ | ○ | ○ | ● | – | ● |

## References

- [`schema/frontmatter.schema.json`](schema/frontmatter.schema.json) — the frontmatter JSON Schema.
- [`templates/`](templates/) — per-type document skeletons.
- [`tools/validate_docs.py`](tools/validate_docs.py) — the corpus validator.
- [`README.md`](README.md) — how to bootstrap a project from this scaffold.
- RFC 2119 — keywords for requirement levels (MUST/SHOULD/MAY).
- Architecture Decision Records — M. Nygard, the ADR pattern.
