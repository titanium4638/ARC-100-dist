---
name: arc-100-documentation-skill
description: Engage for ALL <PROJECT>-100 architecture-documentation work — translating, authoring, migrating, relocating, porting, folding-in, conforming, or revising existing documentation (anything under the project's existing/legacy documentation — a `docs/` tree, design docs, prior architecture/security write-ups, scattered notes) or verified code reality into chapters of the <PROJECT>-100 ARC-100 books-chapter system at `<PROJECT>-100/docs/`. Engage EVEN WHEN the source already LOOKS like a finished ARC-100 chapter or seems to merely need moving: there are NO bare file moves — every source runs the full loop (placement → verification against current code/DB reality → cross-reference reconciliation → change-manifest → human gate), because a polished-looking or dated doc can be stale and MUST be re-proven against the live application before it is trusted. Triggers on any request to migrate / move / port / relocate / fold / conform / document X into <PROJECT>-100, for one doc, a folder, a multi-chapter split, or a batch campaign — including the verbatim shape "migrate existing documentation at <path> into <PROJECT>-100/". ORCHESTRATOR: coordinates `arc-100-librarian` (placement, index, status, ULIDs), `arc-100-chapter-author` (chapter bodies verified against reality), and `likec4-author` (diagrams), with human gates for intent. Do NOT use it to edit the ARC-100 standard (Book 00, read-only) or to run a code change — it owns documentation translation only.
---

# arc-100-documentation-skill

The connective tissue for building out <PROJECT>-100 from the project's existing
documentation and code. `arc-100-librarian` knows *where* a chapter goes; `arc-100-chapter-author`
knows *how* to write one; `likec4-author` draws the diagrams. None of them can
call each other (subagents cannot dispatch subagents). **This skill is the
agent that holds the loop** — it routes between them, enforces the division of
labor, supplies the ARC-100 conventions, and surfaces the human-judgment gates.

## Absolute rules (bind every actor in this loop)

1. **Source documentation is read-only to this system.** No agent, command, or
   skill alters, moves, renames, or deletes a source doc as a side effect of
   translation. The fate of a translated source doc — keep / add a pointer /
   remove — is **always** a human-gated decision (Step 7), never automatic. This
   binds any ARC-100 agent, command, or skill that touches source documentation.
2. **Diagrams are `likec4-author`'s sole domain.** No other agent authors or
   edits a `.c4` model or a diagram; the chapter author only drops a `likec4-view`
   fence for a view that already exists and requests new views via its return.
3. **The index (`01-01`) is the librarian's sole write target.** The ULID lives
   only there (`arc_100_ulid`), minted once by the librarian — for inherited AND
   project-local (`arc_100: false`) chapters. Chapter files carry `arc_100_id`
   (the `BB-CC` join key) and never the ULID or the lineage flag.
4. **No shortcuts — never a bare file move or copy.** Source material that
   already looks like a finished ARC-100 chapter still runs the full loop:
   placement ruling → **re-verification of every current-state claim against the
   live code/DB** → cross-reference reconciliation to real <PROJECT>-100 ids → scope
   check → change-manifest → status gate. A polished or dated source is an
   *unproven* source until the author re-derives it against current reality;
   relocating or copying content as-is is forbidden. **The closer a doc looks to
   "done", the more important it is to confirm it is not stale** — good
   documentation can be an almost-perfect ARC-100 fit and still describe a
   reality the code has since moved past.

## When to engage

| Trigger | Action |
|---|---|
| "Translate / migrate / move `<doc>` into <PROJECT>-100" | Run the loop on that doc. |
| "Author / fill in <PROJECT>-100 chapter `BB-CC`" | Skip intake placement (id known); go to author. |
| "Build out <PROJECT>-100 from the existing docs" / a migration campaign | Run the loop per doc; maintain the ledger; resume from it. |
| Coding in the project and a subsystem's documentation should land in <PROJECT>-100 | Engage to place + author it. |
| The user asks where existing docs live or should live | Ground via the librarian (no authoring). |

Do **not** engage to edit Book 00 (`<PROJECT>-100/docs/00/` — upstream read-only) or
to make code/test changes. This skill translates documentation; it is not a
code workflow.

## Division of labor (who owns what)

| Actor | Owns | Never |
|---|---|---|
| **`arc-100-librarian`** (agent) | Placement rulings (existing / new chapter / new book); the working index `01-01`; ULID minting; flipping a chapter `placeholder→active`/`draft`. Sole writer of the index. | Authoring chapter bodies. |
| **`arc-100-chapter-author`** (agent) | One chapter `.md` body under `<PROJECT>-100/docs/<book>/`, verified against reality; the out-of-scope manifest. | Writing the index; allocating numbers/ULIDs; editing Book 00 / `mkdocs.yml` / master. |
| **`likec4-author`** (agent) | The `.c4` model + views the chapters embed via `likec4-view` fences. | Chapter prose. |
| **Human** (via this skill) | Intent calls: ONE-vs-MANY chapter splits, any `new_book`, draft→active promotion, the fate of the legacy source doc. | — |
| **This skill** (orchestrator) | The loop: routing, manifest recursion, the ledger, gates. | Doing any of the above agents' writes itself. |

**Key rule (load-bearing):** the **author writes the body file; the librarian
writes the index** — two facts owned by two actors, and they must agree. The
documentation hook renders any chapter **whose body file exists** as a live link
in the index tree *regardless of status* — a `draft` is navigable, carrying its
status as a badge — and only file-less `placeholder` rows render inert (§00-03;
the mkdocs sidebar-nav leaf is `active`-only, but the index-tree link is
file-exists-gated). So the instant an author writes a body, the librarian must
move the index row off `placeholder` to the **authored status**: `placeholder →
draft` on authoring-for-review, `draft → active` on promotion (Step 6). A body
file paired with a `placeholder` row is a contradiction (§00-00.6: `placeholder`
= *no file exists yet*) — never leave an authored chapter at `placeholder`.
Nobody edits `mkdocs.yml`: nav is generated by
`<PROJECT>-100/_hooks/arc100_master_index.py`, so a chapter surfaces automatically
once its file exists and its row carries a non-`placeholder` status.

## The loop

### Step 1 — Intake

Identify the source: a legacy doc path (wherever the project keeps existing
documentation — a `docs/` tree, design docs, prior write-ups), a set of docs, or
"the documentation for subsystem X" (then the source is the code + any scattered notes). Read it enough to know its topics. If this is a
resumed campaign, read the ledger (Step 8) first and skip already-migrated docs.

### Step 2 — Ground + place (librarian)

Dispatch `arc-100-librarian` with the doc's topic(s): *"Where in <PROJECT>-100 does
this belong — existing chapter, new chapter, or new book?"* It returns a ruling
per topic. Decisions you carry from its return:

- **`existing_chapter` / `new_chapter`** → proceed. For `new_chapter` the
  librarian allocates the slot + ULID and commits the `placeholder` index row.
- **`new_book` (STOP)** → **human gate.** Never let a book be allocated
  autonomously. Present the librarian's `new_book` ruling to the user; proceed
  only on approval.
- **One-doc-spans-many-chapters** → **human gate** if it's an intent call
  ("should this be ONE chapter or THREE?"). The librarian escalates intent; you
  ask the user, then place per their answer.

### Step 3 — Author each target chapter (chapter-author)

For each placed chapter, dispatch `arc-100-chapter-author` with:

- the **chapter id** `BB-CC`,
- the **source material** (the slice of the legacy doc + permission to verify
  against the live codebase/DB),
- **mode** (`author` new, or `revise` an existing `active`/`draft` chapter),
- **target status** — default **`draft`** (author for human review, then promote)
  unless the translation is high-confidence and the user wants `active` directly.

Dispatch independent chapters in parallel (one message, multiple authors). Each
author reads its scope from the index `01-01`, writes its one file, verifies
current-state claims with cites, marks planning as planning, and returns its
manifest + any diagram requests + any `LIBRARIAN_REQUIRED` escalations.

### Step 4 — Drain the out-of-scope manifests (recursion)

This is the engine that builds <PROJECT>-100 out from a single doc. For every
`OUT_OF_SCOPE_MANIFEST` an author returns:

1. Send its items to `arc-100-librarian` for placement (Step 2 logic — same
   gates for `new_book` / intent splits).
2. For each newly-placed chapter, spawn another `arc-100-chapter-author`
   (Step 3) on that material.
3. Their manifests feed back into this step.

Loop until the manifests come back empty (`items: []`) — or a **depth cap of 3
manifest generations** is hit, at which point surface the remaining items to the
user rather than recursing further (a doc that fans out past depth 3 is usually
an intent question the human should resolve). Track what was placed vs deferred
in the ledger.

> Because subagents cannot call subagents, the author *cannot* reach the
> librarian directly — it hands you the manifest and you mediate. When that
> restriction lifts upstream, this step can collapse into the author; until
> then, the orchestrator is the courier.

### Step 5 — Diagrams (likec4-author)

For each `diagram_request` an author returned, dispatch `likec4-author` to add
the view to the `.c4` model. Once the view exists, the chapter's `likec4-view`
fence resolves on the next build. A **planned** diagram needs no dispatch — the
author already left a prose pointer; only request `likec4-author` when the view
should exist now.

### Step 6 — Activate (librarian)

The index row must always match the authored body. This is **two writes, and the
first is never skipped:**

1. **`placeholder → draft` — mechanical, ungated.** The instant an author returns
   a body written to `draft`, dispatch `arc-100-librarian` to set that chapter's
   `01-01` row to `draft`, in the **same turn** you accept the author's return —
   before you report back to the user. This is not gated on review: the body file
   now exists, so a `placeholder` row is simply false (§00-00.6). Skipping it
   leaves the index contradicting reality and is the most common activation bug.
2. **`draft → active` — the human gate.** The user reviews the drafted chapter;
   only on their acceptance do you have the librarian promote the row
   `draft → active`. For a high-confidence translation the user asked to land
   directly at `active`, the librarian sets `placeholder → active` in one step (no
   draft phase).

The librarian is the only actor that writes the index. The hook surfaces the
chapter on the next `mkdocs build`/`serve` — a `draft` is already a live link in
the index tree (carrying its status badge); no nav edit is ever needed.

### Step 7 — Source-doc fate (human gate)

A translated legacy doc is now duplicated by its <PROJECT>-100 chapter. Default:
**leave the legacy doc in place** and record the mapping in the ledger — the
<PROJECT>-100 chapter becomes the source of truth, the legacy doc a historical
artifact. Offer the user the alternatives (add a pointer/redirect line atop the
legacy doc; or remove it once the chapter is `active`). **Never delete a legacy
doc without explicit user confirmation.**

### Step 8 — Change manifest (chronological record, chapter-keyed)

Record every chapter creation and revision in a central change manifest — NOT as
an appendix inside each chapter, which would bloat the bodies. One entry per
`(chapter, change-event)`, in chronological append-only order, each strongly
keyed by the `BB-CC` book-chapter number so a build hook can parse the file and
surface "all changes for chapter X" without touching the chapter body:

```yaml
# <PROJECT>-100/.arc100/change-manifest.yml  (orchestrator-owned; NOT the index, NOT Book 00)
- chapter: "91-03"          # the join key — the BB-CC book-chapter number (matches arc_100_id)
  change: created            # created | revised | deprecated | superseded
  date: <YYYY-MM-DD>
  status: active             # the resulting index status (draft | active | …)
  summary: <one concise line — what changed and why>
  source: <path to the legacy doc this chapter was translated from>  # or "code: <where>"
  source_fate: kept          # kept | pointer | removed  (human-gated; see Absolute rule 1)
  spawned_from: null         # or the chapter id whose out-of-scope manifest spawned this one
```

- **One entry per chapter per change** — a multi-chapter translation appends
  several entries (one per chapter), so filtering by `chapter:` is exact.
- **Chronological + append-only** — never rewrite history; a later revision
  appends a new `change: revised` entry rather than editing the `created` one.
- **Chapter-bloat fix.** The per-chapter change history is meant to be RENDERED
  from this central file (a future build hook keyed on `arc_100_id`), not stored
  in each chapter `.md`. Chapters keep only a minimal `## Revisions` footer for
  in-chapter section renumbering.

The manifest is orchestrator state — distinct from the index (`01-01`,
librarian-owned) and Book 00. It is both the campaign's memory (what's done, what
fanned out, what's deferred — making a batch run resumable) AND the
system-of-record for chapter change history.

### Step 9 — Verify (optional)

For a high-stakes chapter or the end of a campaign, confirm the build is clean
and the chapter surfaces: `mkdocs build` against `<PROJECT>-100/mkdocs.yml` (or the
running `mkdocs serve` address) and check the chapter renders as a live link in
the generated index tree (it will once its **body file exists** — a `draft`
links too, carrying its status badge; only file-less `placeholder` rows are
inert). An `active` chapter additionally appears as a leaf in the mkdocs sidebar
nav (the sidebar is `active`-only; the index-tree link is file-exists-gated).

## Human gates (never auto-resolve)

1. **`new_book`** — the librarian halts; you ask the user.
2. **ONE-vs-MANY** chapter split for a doc — an intent call; ask.
3. **`draft→active`** promotion — the user reviews the drafted body.
4. **Legacy-doc fate** — keep / pointer / remove; never remove without consent.
5. **Manifest depth cap reached** — surface the remainder instead of recursing.

## The conventions this skill supplies to the author

Every `arc-100-chapter-author` dispatch carries (or relies on the agent already
knowing) the ARC-100 chapter contract — frontmatter schema, the
`## BB-CC` + "what this is / is not" frame, `### BB-CC.N —` sections, citation
format `[BB-CC §N]`, the **architecture-altitude** discipline (intent and shape —
load-bearing structure and governing intent; reference the code, never reproduce
it), the verify-and-reference burden for current state, the mark-as-planning
burden for intent, and the manifest format. The agent encodes
these; this skill's job is to make sure the author is pointed at the right
chapter id, the right source material, and the right mode/status — and that its
manifest, diagrams, and status flip are routed onward.

## Output (what to report back to the user)

```text
## Translated
<source doc(s)> → <PROJECT>-100 chapters: <ids> (status: draft|active)

## Fanned out (from manifests)
<overflow material> → <chapter ids> (or "deferred — needs your call: …")

## Diagrams
<view ids> authored via likec4-author (or "planned — prose pointers left")

## Gates awaiting you
<new_book ruling | split question | draft to review | legacy-doc fate>

## Change manifest
<n> entries appended to <PROJECT>-100/.arc100/change-manifest.yml
```
