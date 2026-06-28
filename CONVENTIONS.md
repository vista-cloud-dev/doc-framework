# Doc conventions

The whole standard, in one page. A docs corpus is just markdown under a `docs/`
tree; keep it coherent with four rules and one gate.

## The rules

1. **Kebab-case filenames.** `rpc-tap-scalable.md`, not `RPC_Tap_Scalable.md`.
   Lowercase, words joined by `-`, `.md` extension. One file = one topic.
2. **Frontmatter is optional.** Add a `---` YAML block if it helps you or a tool;
   leave it off for working notes. No required fields, no enforced dialect — the
   gate does not read it. (If you do add dates, ISO `YYYY-MM-DD`.)
3. **Links must resolve.** Every relative markdown link and every `#anchor` must
   point at something real. This is the **only** gate (see below). Reference a
   **sibling repo** by GitHub URL, not a `../../other-repo/...` path — those are
   unverifiable in a single-repo CI checkout.
4. **Supersede by editing; let git be the changelog.** One canonical doc per fact.
   When something changes, edit the doc in place — do not fork a `-v2` or keep an
   in-doc revision log. git history *is* the record. Retire a doc by `git mv`-ing
   it into `archive/` (or `historical/`), never by leaving a stale copy live.

## The gate

```sh
python3 tools/link-check.py docs/        # 0 broken links/anchors → exit 0
```

Pure stdlib, zero dependencies, airgapped-friendly. Wire it into CI by calling the
reusable workflow (`.github/workflows/validate.yml`) — see `README.md`. Treat a red
link-check like a failing test: fix it before declaring docs synced.

The checker skips these directories (frozen / generated / own-convention):
`prompts/ archive/ retired/ historical/ memory/ modules/`. Inbound links *into*
them still resolve.

## Folder layout (vista-cloud-dev house standard)

`README.md` (the one index) · `guides/` (how-to) · `modules/` (generated reference,
stdlib repos only) · `design/` (this repo's design notes) · `memory/` (auto-memory)
· `archive/` (retired docs, `git mv`'d). Live-work trackers sit in `docs/` root as
`<effort>-tracker.md` and move to `archive/` when the effort lands. Don't invent
bespoke folders. Full rationale: the org docs repo's
`proposals/docs-organization-remediation-plan.md`.

---

## Appendix: the consolidation pass

The recurring documentation problem is **several overlapping sources of truth** (an
old spec, a log, the working code) that partly disagree. Resolve it with one move:

1. **Read every input fully**, plus the ground truth — the **code**.
2. Build a **reconciliation table**: tag each material claim CONFIRMED /
   CONTRADICTED / STALE / UNVERIFIABLE against the code. **When docs and code
   disagree, the code wins**, and the conflict is footnoted.
3. **Present the table of contents + findings; wait for approval** before writing.
4. Write **one** canonical doc; supersede (edit/retire) the inputs.
5. Print the discrepancies found, so a human can sanity-check.

Keep specs **code-free**: name commands, files, ports, and config keys, but do not
paste implementation source. A spec is not done until it says *how you know it is
done* — an acceptance checklist whose every claim is traceable to a source or
verified against the code. **Be honest about verification:** if a build or check
was not actually run, say so. Never let "done" outrun "verified".
