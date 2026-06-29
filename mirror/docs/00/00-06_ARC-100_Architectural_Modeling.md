---
title: 00-06 ARC-100 Architectural Modeling
arc_100_id: "00-06"
status: active
keywords: [architecture, modeling, c4, structurizr, diagrams, agent, sqlite, ulid]
agent_summary: |
  Standard chapter for ARC-100's architectural-modeling discipline.
  Adopts C4 (Simon Brown) as the framework; the production renderer
  is LikeC4 1.57.0 + the mkdocs-likec4 plugin (phase 3a/3b/3c —
  Revisions 7, 8, 9, 10). One agent (likec4-author) does the
  consequential model-authoring work; software (likec4 CLI + the
  mkdocs plugin) handles validation, rendering, and embedding —
  the post-POC "agents declare; software enforces and emits"
  pattern recorded in §00-06.9. The reader-facing surface (per-chapter
  embedded views + the Architectural Model page + the modal-gesture reference
  in §00-06.10.6) is operational; the author-facing toolchain
  distribution to downstream <PROJECT>-100 projects via ARC-100-SYNC
  is part of phase 4 of the v1 implementation. Specific deliberation
  questions remain open in §00-06.12 (storage model at scale,
  per-chapter sidecars, downstream inheritance, cross-system data
  exchange) but no longer characterise the chapter as a whole.
  Allocated in the 00-01 index under book 00.
prerequisites: ["00-00_ARC-100_General.md", "00-01_ARC-100_Standard_Inventory.md", "00-04_ARC-100_Standards_Comparisons.md"]
companions: ["00-04_ARC-100_Standards_Comparisons.md", "00-05_ARC-100_Synchronization.md"]
---

## 00-06 ARC-100 Architectural Modeling

> **What this chapter is.** An early-draft exploration of how
> architectural modeling — specifically the C4 model and a
> Structurizr-style data shape — could complement ARC-100. It maps
> the design space, surfaces tradeoffs (notably between text-file
> and embedded-SQL storage), and proposes candidate agent skills for
> building and maintaining the model. It is intentionally written
> as deliberation, not specification.
>
> **What this chapter is not.** A ratified standard. None of the
> decisions in here are final. Each section that resembles a ruling
> is hedged with "candidate" or "one option is". The hardening
> sweep — pruning options, naming chosen approaches, removing the
> "we could / one alternative is" language — happens in a later
> revision once the open questions in §00-06.12 have been worked
> through. Revision 2 has begun this hardening: §00-06.9 (the
> agent/software boundary) is now grounded in POC evidence rather
> than sketch, and Q11 is substantially resolved.
>
> **How to read it.** Skim for shape, then return to §00-06.12 and
> §00-06.6 with a deliberation lens. §00-06.10 (POC findings) is
> the empirical anchor — read it when the abstract framing of
> §00-06.4 (model schema) and §00-06.9 (agent/software boundary)
> feels too neat and you want to know what hurt during construction.
>
> **Status as of 2026-05-24 (Revision 10).** Architectural modeling
> with LikeC4 is integral to ARC-100. The reader-facing surface
> (LikeC4 model + per-chapter embedded views + the Architectural
> Model page + the modal gestures documented in §00-06.10.6) is
> operational. The author-facing surface (the `likec4-author`
> agent + the `likec4-introspection` skill + the
> `master-vault/likec4/` scoped install — per-tree split, phase 3.1d) is part of the planned
> ARC-100-SYNC distribution to downstream `<PROJECT>-100` projects,
> delivered in **phase 4** of the v1 implementation
> (`versions/v1/implementation/phase_4.md`, authored after this
> phase implements). This chapter therefore promotes from
> `status: draft` to `status: active`.

### 00-06.1 — Why a separate chapter

ARC-100 is a documentation-indexing standard. It tells you *where
chapters live and how they're numbered*. It is opinionated about
slot layout, lifecycle, and identity but is intentionally silent
about what a chapter must *say* — every chapter is free to describe
its subject in whatever shape best serves the reader.

Architectural modeling is a different discipline. It asks: *what is
the system shaped like? What are its parts? Who interacts with what?
What runs where? Where are the boundaries?* The answers don't fit
into the index — they fit into diagrams, element registries, and
views that exist alongside the prose chapters and reference them
without being controlled by them.

Two reasons this chapter is separate from `00-00 ARC-100 General`
rather than folded into it:

1. **Applicability.** Architectural modeling is useful for any
   system — even one that doesn't use ARC-100 for indexing. ARC-100
   shouldn't absorb adjacent disciplines; it should be a clean
   composable standard with documented integration points.
2. **Cadence.** The indexing standard changes slowly (numbers, slot
   conventions, lifecycle); the modeling discipline will evolve as
   tooling matures (diagram renderers improve, agents get more
   capable, data shapes are refined). Keeping them in separate
   chapters means revisions to one don't churn the other.

The chapter therefore explores the modeling discipline as a
*complement* to ARC-100: ARC-100 provides the substrate (chapters,
identity, governance); architectural modeling builds an additional
artifact (the model) that lives on top.

### 00-06.2 — How architectural modeling and ARC-100 relate

The two disciplines support each other in specific, identifiable ways.

**ARC-100 supports architectural modeling.** It provides:

- **Identity** — ULID generation that the model can reuse for
  architectural elements (the same `ARC-100-SYNC/scripts/ulid.py`
  that mints chapter ULIDs can mint element ULIDs, see §00-05.7).
- **Provenance** — every architectural element ultimately traces
  back to one or more chapters that describe it; ARC-100's slot
  numbering gives that link a stable target.
- **Lifecycle** — the `status: active | deprecated | superseded`
  vocabulary (§00-00.6) is directly applicable to architectural
  elements too. An element can be deprecated, just like a chapter.
- **Project portability** — the master-vs-version split (§00-00.8)
  gives a downstream `<PROJECT>-100` a place to extend or override
  the upstream model.

**Architectural modeling supports ARC-100.** It provides:

- **Visualizable summaries** — what a 280-line chapter says in prose
  is often more accessible as a 12-box diagram. Embedded diagrams
  let readers skim the architectural shape before committing to the
  prose.
- **Cross-chapter consistency** — when two chapters describe the
  same component (e.g., a sync engine referenced in both 00-05 and a
  hypothetical 12-XX decisions chapter), a shared registry catches
  drift between them.
- **Navigable structure** — interactive diagrams let a reader click
  a Container at C4-2 and zoom into its Components at C4-3, then
  follow a relationship back to a related chapter.

The integration is loose. ARC-100 doesn't *require* a model; the
model doesn't *replace* the prose. A project using ARC-100 can adopt
modeling fully, partially, or not at all. The two disciplines compose;
they don't entangle.

### 00-06.3 — The C4 model as a candidate framework

C4 (Simon Brown, originally 2006, current with the 2024 refresh) is
the strongest candidate for the modeling framework. Three reasons:

1. **Notation independence.** C4 is *about the data model*, not about
   any particular diagramming notation. The same C4 model can render
   as a Structurizr diagram, a PlantUML C4 diagram, a Mermaid C4
   diagram, or hand-drawn boxes. ARC-100 inherits the same independence.
2. **Hierarchical zoom.** Four levels (Context, Container, Component,
   Code), each a different audience. ARC-100 chapters already address
   different audiences (introductory chapters for everyone, deep
   chapters for implementers); C4's level discipline mirrors that.
3. **Supplementary diagrams.** C4 explicitly accommodates Deployment,
   Dynamic, and System Landscape diagrams as orthogonal views. Many
   ARC-100 concerns (versioning, scheduling, cross-project sync) are
   cross-cutting in exactly the way Supplementary diagrams handle.

Other frameworks worth considering — `arc42` (template-driven),
4+1 Views (Kruchten), ISO/IEC/IEEE 42010 (meta-standard for
architecture description) — are not ruled out. They could complement
C4 rather than replace it; chapter 00-04 already quantifies the overlap
across nine such standards.

For the rest of this chapter, "the model" means "a C4-style model"
unless otherwise noted. The choice is not final; a later revision may
revisit it if a different framework proves a better fit.

### 00-06.4 — Modeling the model: elements, relationships, views

The candidate data shape is Structurizr's. Three top-level concepts:

**Elements** are the boxes. Each carries:

- `ulid` — stable identity
- `name` — display label
- `type` — one of `Person`, `Software System`, `Container`,
  `Component`, `Code Element` (the 5 C4 types)
- `description` — one or two sentences, audience-appropriate
- `technology` — optional, where applicable (`Python 3.10+`,
  `mkdocs hook`, `bash 3.2+`)
- `tags` — free-form, used for diagram styling and filtering
- `properties` — open key-value bag for tool-specific metadata
- `provenance` — references back to chapter sections and/or plan
  documents that define this element

**Relationships** are the lines. Each carries:

- `ulid`
- `source_element_ulid` and `destination_element_ulid`
- `description` — the verb describing the interaction (`fetches`,
  `writes to`, `dispatches`, `renders`)
- `technology` — optional (`HTTPS GET`, `Python subprocess`,
  `subagent dispatch`)
- `tags` and `properties` — as for elements
- `provenance` — chapter or plan reference

**Views** are the diagrams. Each carries:

- `key` — display name (`SystemContext`, `ConformContainer`,
  `LibrarianComponent`)
- `type` — one of `SystemContext`, `Container`, `Component`,
  `Code`, `Dynamic`, `Deployment`, `SystemLandscape`
- `scope_element_ulid` — the element this view zooms into (e.g.,
  the Container view's scope is the system; the Component view's
  scope is one Container)
- `included_elements` — explicit list of element ULIDs in the view
- `included_relationships` — explicit list of relationship ULIDs in
  the view
- `layout` — optional, tool-specific positioning data

The three-table shape — elements, relationships, views — is the
minimum that lets diagrams be deterministically regenerated from the
model. Real Structurizr adds more (e.g., a `documentation` table, a
`decision_log` table); we can mirror those if they prove necessary.

### 00-06.5 — Identity: ULIDs for architectural elements

Reusing ARC-100's ULID conventions for architectural elements is the
obvious extension and gives us four properties for free:

- **Immutable** — renaming `install.sh` to `bootstrap.sh` doesn't
  invalidate every reference to its ULID.
- **Unique** — no collision between project-allocated elements and
  ARC-100-inherited elements (parallel to the `arc_100: true | false`
  ownership flag on chapters).
- **Time-sortable** — reading the registry chronologically reproduces
  the order in which the architecture grew. Useful for archaeology.
- **Project-portable** — a downstream `<PROJECT>-100` extending the
  upstream model never produces ULID conflicts.

A naming convention worth considering for *display* in tools that
benefit from human-readable identifiers: `ent.<slug>` for elements,
`rel.<slug>` for relationships, `view.<slug>` for views. The ULID is
the canonical key; the slug is a convenience alias maintained alongside
it. Two distinct elements may carry the same slug intentionally
(e.g., `ent.config` in two different scopes); the ULID disambiguates.

### 00-06.6 — Storage: tradeoffs between text, SQLite, and hybrid

This is one of the consequential decisions. The model has to live
somewhere; the storage choice shapes the tooling, the review
workflow, and the cross-project portability story. Three candidates.

#### 00-06.6.1 — Text files (YAML/JSON/Structurizr DSL)

Markdown-adjacent text files in git. Either one big project-wide
model file, or per-chapter sidecars (e.g.,
`docs/00/00-05_ARC-100_Synchronization.c4.yml`) merged at build time.

**Pros:**

- **Diff-friendly.** Every model change shows up in `git diff` as a
  line edit. Code review of model changes is trivially in PR.
- **Human-readable and -editable.** Any text editor works. No
  tooling-on-the-critical-path requirement.
- **Project-portable.** A downstream `<PROJECT>-100` can copy or
  symlink the upstream model files unchanged.
- **Cheap to lift between systems.** Structurizr DSL is exactly this
  shape and is read by every existing C4 tool.
- **Consistent with ARC-100's existing pattern.** The index lives in
  a markdown file with a YAML block; the model would live the same way.

**Cons:**

- **No indexing or query.** Finding "all Containers whose technology
  is Python" requires parsing every file. Manageable at 50 elements,
  painful at 500.
- **No referential-integrity enforcement.** A relationship pointing
  to a non-existent element passes silently until something tries to
  render the diagram.
- **Conflict resolution on concurrent edits is line-merge.** Usually
  fine; occasionally painful when two changes touch the same element.
- **Cross-project queries are awkward.** "Show me every element
  shared between FLOW-100 and CS-100" requires parsing multiple
  project repos.

#### 00-06.6.2 — Embedded SQL (Better SQLite, or plain SQLite)

The model lives in a single `.db` file, schema-versioned, with
foreign-key constraints and indexed queries.

**Pros:**

- **Native joins.** Element ↔ Relationship ↔ View queries are trivial
  SQL. "Show all relationships whose source is a Container and whose
  destination is an external Software System" is one statement.
- **Referential integrity at the schema level.** A FK on
  `source_element_ulid` makes orphaned relationships a write-time
  failure rather than a render-time mystery.
- **Constraint enforcement.** `CHECK (type IN ('Person', 'Software System', ...))`
  prevents typo-driven type drift.
- **Fast at scale.** Indexed queries stay fast as the model grows;
  text-file scan times grow with the model.
- **Single-file artifact.** Like the text option, a `.db` file lifts
  cleanly between projects.

**Cons:**

- **Binary diff in git.** No line-level code review of model changes.
  This is the dealbreaker for many teams; a "what changed?" question
  becomes "run a tool to diff two snapshots".
- **No hand-editing.** Authoring without a tool is impractical. Every
  change goes through `sqlite3` CLI, an ORM, or an agent that knows
  the schema.
- **Schema-migration discipline.** A schema change needs a migration
  step; downstream projects on an older schema break until they migrate.
  This is the same problem any database-backed system has, but it's
  new burden for projects that previously had only markdown.
- **One more tool in the install footprint.** SQLite is ubiquitous on
  Unix and macOS but not always present on Windows-without-WSL hosts;
  Python's `sqlite3` module makes it free for Python users, but
  introduces a runtime dep for tools written in other languages.

#### 00-06.6.3 — Hybrid: text as source, SQL as build-time index

The shape that earns its complexity. Text files are the authoritative
source (diff-friendly, editable, portable). At build time, a small
materialization step parses the text into a SQLite database, runs the
queries that views need, generates the diagrams, and discards or
caches the database. The reverse round-trip — export-from-SQLite to
edited-text — is supported but optional.

This pattern is *not* novel; it mirrors how ARC-100 itself works:

| Layer | ARC-100 today | Architecture modeling under hybrid |
|---|---|---|
| Source of truth | `00-01_ARC-100_Standard_Inventory.md` (YAML block) | `docs/architecture/model/*.yml` (or DSL) |
| Materialization step | mkdocs hook (Python) | A model-build script (Python) |
| Materialized artifact | `00/index.md` (generated, gitignored) | `model.db` (generated, gitignored) |
| Consumer | The mkdocs renderer | The diagram renderer |

The parallel is exact: ARC-100's index is text-authored and text-rendered,
with a generated artifact serving the rendering pipeline. Architecture
modeling under hybrid follows the same pattern with `model.db` taking
the role of the rendered tree.

**Pros (additive):** Diff-friendly authoring + queryable rendering;
referential integrity enforced at build time (the script can fail
the build on dangling refs); cross-project queries become possible
when the materialization step attaches multiple project databases.

**Cons (additive):** Two representations to keep in sync; small risk
of drift if someone edits the database directly and forgets to
round-trip back to text; one more step in the build pipeline.

#### 00-06.6.4 — Initial inclination, kept soft

The hybrid pattern is the natural fit for ARC-100's existing
text-source-and-generated-artifact rhythm, but the call shouldn't be
made until we have ~50 elements and have felt the text-only ergonomics
ourselves. A model of ARC-100-SYNC alone (chapter 00-05's worth of
material) probably runs to 10–20 elements and ~25 relationships;
text-only is unambiguously fine at that scale. The hybrid question
becomes load-bearing once the project has its own chapters in the
model (~10× the volume).

A reasonable progression:

1. Start text-only. One file per chapter, sidecar shape, easy to
   reason about.
2. Hit 50+ elements or run into "I need to query across files"
   ergonomics; introduce the build-time SQLite materialization.
3. Re-evaluate at 500+ elements; consider whether SQLite-as-source
   (with a text export workflow) becomes the better default.

Each transition is reversible; we are not locked in by starting
text-only.

### 00-06.7 — Markdown integration

The project's mkdocs configuration enables the `attr_list` extension,
which lets headings (and other elements) carry HTML-style attributes
directly in markdown:

```markdown
### 00-05.7 — Runtime composition { #c4-runtime-composition .c4-2 data-c4-level="container" data-entity-ulids="01KRYWZ...,01KRYX0..." }
```

This compiles to `<h3 id="..." class="c4-2" data-c4-level="container" data-entity-ulids="...">`
in the rendered HTML, but more importantly the attributes are *in
the markdown source* — the tooling can find them by grep without
ever rendering. The tags are nicknames for the ULID records that
live in the model: a chapter section names which elements it
describes, and the model registry name those elements canonically.

The integration is bidirectional:

- **From chapter to model.** Tooling reads a chapter, follows the
  `data-entity-ulids` attributes to pull the corresponding records
  out of the model, and (for example) renders an embedded
  Container diagram next to the section that defines those Containers.
- **From model to chapter.** Tooling reads the model, follows each
  element's `provenance` field back to chapter sections, and (for
  example) generates an index page that lists every Container with
  links to its defining chapter section.

Neither direction is yet built. The integration grammar matters
because it's a public contract between three independent actors:
the chapter author, the model registry, and the diagram-generation
pipeline. Pinning it down precisely — what attributes are mandatory,
what conventions govern multi-tag sections, what the fallback is when
an element is referenced but not yet in the model — is one of the
in-scope deliberations for a future revision.

### 00-06.8 — Diagram generation pipeline

Several candidates, each with a different sweet spot.

| Tool | Renders | Authoring shape | mkdocs-native? | Notes |
|---|---|---|---|---|
| **Structurizr Lite / Cloud** | C4 diagrams, supplementary diagrams, drill-down | Structurizr DSL or JSON | No (iframe or static export) | Most mature; click-to-zoom built-in; some hosted-vs-local tradeoffs |
| **C4-PlantUML** | C4 diagrams via PlantUML macros | `Container(id, "name", "tech", "desc")` syntax | Yes (mkdocs PlantUML plugins exist) | Free, self-hosted, less feature-rich than Structurizr |
| **Mermaid C4** (experimental) | C4 diagrams via Mermaid | Mermaid `C4Context` blocks | Yes (mkdocs-material renders Mermaid natively) | Newest, simplest to embed, layout control limited |
| **Likec4** | C4 diagrams from a DSL | Likec4 DSL | Static export | Newer entrant; more design-tool-like |
| **Custom (SVG)** | Anything | Whatever we want | Yes (just include SVG) | Most control, most cost |

Each is compatible with the same underlying model. The model layer
(elements, relationships, views) is renderer-independent; the choice
of renderer affects which views render most cleanly and what
interactivity is available, not what's modelable.

A reasonable initial choice for in-mkdocs embedding is Mermaid C4
(zero plugin cost, native to mkdocs-material), with the option of
emitting Structurizr DSL for the cases where Structurizr's
interactive drill-down is genuinely useful. We can defer this until
we have a model worth rendering.

### 00-06.9 — The agent/software boundary

Revision 1 of this chapter proposed **four agents** (`c4-modeler`,
`c4-validator`, `c4-diagram-author`, `c4-physical-mapper`) as the
toolchain for the modeling discipline. The proof-of-concept in
§00-06.10 hand-built a complete model of ARC-100-SYNC and tested
each proposed agent against the actual work involved. The result is
substantially different from revision 1: **only one of the four
proposed roles is genuinely agent territory; the other three are
software**.

The pattern that emerged from the POC:

> **Agents declare. Software enforces and emits.**
>
> The agent makes architectural decisions — which elements exist,
> what to call them, how they relate, what shape each view takes.
> Software encodes the rules that frame those decisions (the C4
> type vocabulary, the verb catalog, the integrity constraints) and
> executes the deterministic consequences (validation, rendering,
> embedding).

The four pieces, post-POC:

| Originally proposed | Post-POC classification |
|---|---|
| `c4-modeler` | **Agent.** Holistic decomposition is the consequential judgment work; no algorithmic answer. Opus-level reasoning. |
| `c4-validator` | **Software.** Deterministic integrity checks (FK, type vocabulary, parent chain). The `plan-reviewer` parallel that motivated the agent shape does not hold — plan review interprets intent; model validation enforces rules. |
| `c4-diagram-author` | **Software.** Reading `attr_list` tags from chapters + inserting Mermaid blocks at marked anchors is a deterministic transform. The judgment piece ("which view goes where?") is upstream in `c4-modeler`, not here. |
| `c4-physical-mapper` | **Software** for diff detection (set difference between the C4 model and CodeScan's physical perspective); **lightweight agent** for *interpreting* the diff. The interpretation is small enough to fold into `c4-modeler` rather than warrant its own agent. |

The sections below describe each piece in its post-POC shape. The
detailed revision-1 proposal — including its over-estimation of how
much of this work needs agent reasoning — is preserved in the
chapter's revision history as a recorded misstep, useful as a
cautionary worked example of the temptation to default-to-agent in
agent-rich projects.

#### 00-06.9.1 — `c4-modeler` (the one agent)

The agent that reads chapters and builds the model. Its skill set is
narrower than revision 1 proposed because the deterministic pieces
(validation, rendering, embedding) split off as software:

- **Holistic decomposition.** Read a chapter (or set of chapters) and
  identify the system's actors, neighbouring systems, deployable
  units, internal components, and code elements. Decide where the
  Container/Component boundary is — this is C4's hardest judgment
  call and has no algorithmic answer. Opus-level reasoning; no
  pattern-matching shortcut works.
- **C4-type classification.** Apply the closed 5-type vocabulary
  (`Person`, `SoftwareSystem`, `Container`, `Component`,
  `CodeElement`, plus `ContainerDb` for data-store containers).
  Reject "concept" classifications: the word "Identity" is not a
  Container.
- **Relationship identification.** Find inter-element relationships
  from prose; classify each verb against the controlled catalog
  (see §00-06.10.3 for the friction observation that motivated the
  catalog).
- **View scoping.** Decide which elements and relationships appear
  in each view. Not every Container-level relationship belongs in a
  Container diagram; the agent picks what serves the audience.
- **Description authoring.** Write the `name`, `description`, and
  `technology` fields for each element and relationship. Tone,
  length, and audience are taste decisions.
- **Provenance authoring with software assist.** Hand-authoring
  per-element provenance is tedious (POC finding §00-06.10.3.3).
  Software performs the text scan that maps element names to
  chapter sections; the agent handles ambiguous matches and
  approves the proposed provenance list.
- **Markdown tag application.** Once the model record is created,
  apply the `data-entity-ulids="..."` attribute to the chapter
  section that defines it.

ULID allocation is a single call to `ARC-100-SYNC/scripts/ulid.py`;
not a skill, just a tool the agent reaches for.

Hard prohibitions (mirroring the `arc-100-librarian` discipline):

- Never invent an element not named in source prose.
- Never collapse two distinct elements based on display-name similarity.
- Never modify an existing element's ULID (immutable, same as chapter
  ULIDs).
- Never emit a relationship with a placeholder verb; if the verb
  doesn't fit the controlled vocabulary, surface and ask the author
  to extend the catalog.

#### 00-06.9.2 — The validator (software)

Revision 1 proposed this as `c4-validator`, an agent parallel in
shape to `plan-reviewer`. The POC's `render.py` implements the
validator in ~50 lines of straight Python: foreign-key checks on
relationships and views, type-vocabulary enforcement, parent-chain
existence, included-element existence. Every rule is a deterministic
predicate; no judgment surface exists.

The validator runs as part of the build pipeline (or pre-commit
hook), refusing to render any output when validation fails. Output
is a list of error strings, machine-readable, no agent dispatch
required.

The `plan-reviewer` analogy that motivated the agent proposal turns
out not to fit: plan review must interpret author intent (was the
ambiguous step intentional or accidental?); model validation only
checks structure (does this slug exist in the registry?). The two
disciplines look similar at sketch level but split apart in practice.

#### 00-06.9.3 — The renderer (software)

The POC's `render.py` main flow. Reads YAML, walks each view, emits
one Mermaid C4 fenced block per view. Pure transform; no decisions.
The only knowledge encoded is the mapping from element type to
Mermaid primitive (`Container` → `Container(...)`,
`ContainerDb` → `ContainerDb(...)`, external suffix when the
element's parent chain doesn't include the view scope).

Easy to extend with additional output formats (Structurizr DSL,
C4-PlantUML, plain JSON) without touching the model or the agent.

#### 00-06.9.4 — The embedder (software)

Revision 1 proposed this as `c4-diagram-author`. The POC manual-
pastes Mermaid blocks from `output/*.mmd` into chapter sections; an
embedder script would do this deterministically by scanning chapters
for `data-c4-view="<view-key>"` attributes (or paired
`<!-- c4-diagram:<view-key> -->` anchor markers) and inserting the
matching rendered Mermaid block at each site.

No agent reasoning required. The judgment "which view goes where" is
already captured in the chapter author's choice of attribute tag;
the embedder mechanically executes that choice.

#### 00-06.9.5 — The drift detector and CodeScan bridge

Revision 1 proposed `c4-physical-mapper` as an agent. The POC didn't
build this piece (CodeScan integration is out of scope for the
ARC-100-SYNC POC), but the agent/software analysis applied to the
sketched workflow shows it splits the same way:

- **Diff detection: software.** Find elements in the C4 model that
  don't appear in CodeScan's physical-perspective data (and vice
  versa). A set difference over identifiers.
- **Interpretation: folded into `c4-modeler`.** What to do about
  each diff (record as a new element, flag as missing, ignore as
  out-of-scope) is the agent's domain — but it's small enough that
  a dedicated agent is overkill. The c4-modeler can take a diff
  report as input and propose resolutions in the same workflow it
  uses for chapter prose.

#### 00-06.9.6 — Granularity

Revision 1 left the agent-granularity question (§00-06.9.5 then)
open. The POC substantially answers it: **one agent doing the
consequential work, three pieces of software doing the rest.** The
shape mirrors how `arc-100-librarian` consolidates Slot-allocation,
Schema-sweep, and Resolution into one agent — keep judgment in one
place; don't multiply agents for each step.

Revision 7 (phase 3a) adds a second agent of the same shape:
`likec4-author`. It consolidates four LikeC4 skills (DSL model
authoring, view definition, theme/styling, mkdocs embedding
mechanics) into one agent rather than fanning them out into four —
parallel to the `c4-modeler` / `c4-validator` / `c4-diagram-author`
/ `c4-physical-mapper` collapse this section already records. The
canonical template lives at `ARC-100-SYNC/templates/agents/likec4-author.md`
(delivered mirror-class by `arc_sync.py` to a downstream project's **main**
`.claude/agents/` — the project root, not the `<PROJECT>-100/` instance — when it
opts into the modeling discipline).

### 00-06.10 — POC findings

This section records what was learned by hand-building a complete
C4 model of the ARC-100-SYNC system as a working proof-of-concept.
It exists because revision 1 of this chapter made several confident
proposals about agent shapes that the POC then disproved; capturing
the experience here gives later revisions a basis for staying
grounded in evidence rather than sketch.

#### 00-06.10.1 — What was built

A complete C4 model of the ARC-100-SYNC system at C4-1, C4-2, and
C4-3:

| Artifact | Path | Size |
|---|---|---|
| Model (YAML) | `architecture/c4/arc-100-sync.model.yml` | 23 elements, 29 relationships, 3 views (~610 lines) |
| Renderer | `architecture/c4/render.py` | ~270 lines, PyYAML stdlib only |
| Rendered output | `architecture/c4/output/*.mmd` | 3 Mermaid C4 fenced blocks |
| Chapter integration | `docs/00/00-05_ARC-100_Synchronization.md` | 6 headings tagged with `attr_list`; 2 diagrams embedded inline |
| mkdocs wiring | `mkdocs.yml` | `pymdownx.superfences` extended with Mermaid `custom_fence` |

Cost: one working session for the model + renderer + chapter
integration. mkdocs strict build passes. The chapter renders with
the two embedded diagrams visible inline after server restart.

> **2026-05-26 footnote.** Both `architecture/c4/` (POC) and
> `architecture/LikeC4/` (phase 3a–3c) were removed in phase 3.1d
> (2026-05-26) when the LikeC4 toolchain split per-tree into
> `master-vault/likec4/` (standard) and `docs/likec4/` (project). The
> YAML POC artifact is preserved in git history at commit `bc0dab6`.

#### 00-06.10.2 — The activity-by-activity boundary

Tracking what was done manually vs. mechanically while building the
POC produced the following map. This is the table that justifies
the §00-06.9 reclassification:

| Activity | Where it landed | Why |
|---|---|---|
| Decide which elements exist at each level | Manual / agent work | Judgment with no algorithmic answer. ARC-100-SYNC could plausibly have 6 Containers or 10; collapsing slash commands or splitting librarian skills are both defensible. |
| Classify each element's C4 type | Agent (proposes) + software (validates) | The 5-type vocabulary is a closed set — software enforces it; the classification itself is judgment |
| Write element descriptions | Manual / agent work | Tone, length, audience are taste decisions. Drafts from prose + human refinement work well |
| Identify and verb-name relationships | Manual / agent work | Repeatedly caught self agonising over "uses" vs "invokes" vs "dispatches" — these distinctions carry meaning. Needs a controlled-verb catalog so the agent doesn't drift |
| Decide which relationships appear in which view | Manual / agent work | View scoping is judgment — SystemContext shows 4 abstracted relationships; Container view shows 16 concrete ones from the same underlying model |
| Allocate ULIDs | Pure software (`ulid.py`) | Mechanical; same generator the librarian uses for chapters |
| Compute slugs from element names | Software (would be) | Deterministic kebab-case transform; authored by hand in POC, would be one function call |
| Compute provenance back to chapter sections | Software (would be) | Text scan finding where each element name appears in source chapters is deterministic; authored by hand in POC, was the most tedious step |
| Validate model integrity | Pure software (`render.py validate()`) | FK + type vocabulary + parent existence checks. Caught one unquoted-colon bug |
| Render YAML → Mermaid C4 | Pure software (`render.py`) | Deterministic transform once the per-type rules are encoded |
| Choose `Container_Ext` vs `Container` per view | Software | Given the view scope, the script computes externality from the parent chain |
| Decide which chapter sections to tag | Manual / agent work | Picked 6 of 14 headings — judgment about which sections describe diagrammable structure |
| Decide which view to embed where in the chapter | Manual / agent work | Judgment about reading flow — SystemContext after the system-framing section, ContainerView after the runtime-composition section |
| Embed diagrams at the tagged anchors | Software (would be) | Manual paste in POC; a small embedder script reading `data-c4-view` attrs and writing Mermaid blocks at marked locations is fully deterministic |

The agent/software split falls out of this table directly: nine
activities are software (or trivially become software); five are
genuinely judgment work.

#### 00-06.10.3 — Friction points observed during construction

Five things hurt enough during hand-construction that they should be
addressed before any agent or downstream tooling is built. These are
schema and pipeline issues, not agent-design issues:

##### 00-06.10.3.1 — View-include lists are repetitive

The POC's view definitions hand-list every element ULID and every
relationship ULID per view. For a 5-element SystemContext view this
is fine; for a 12-element Container view it is tedious; for a
50-element project-wide view it would be impractical. A higher-level
abstraction — something like `auto_include: { type: Container, scope: ent.arc-100-sync }`
that pulls every Container whose parent chain reaches the scope —
would cut view-definition volume by 5–10×. This is software work:
the render script synthesizes the implicit list from a small
declarative spec.

##### 00-06.10.3.2 — Description length blows out the rendered diagrams

The POC's elements carry full-sentence descriptions ("Bash bootstrap
installer with embedded FILES list. Fetches ARC-100-SYNC artifacts
from upstream via curl. Single use, per downstream project install.").
These are the right length for documentation but Mermaid C4
overflows the box they render into.

The fix is a separate `short_description` field (5–8 words, diagram-
sized) alongside the long `description`. The renderer uses
`short_description`; documentation and tooltips use `description`.
Schema change, ~one line per element to author.

##### 00-06.10.3.3 — Provenance is tedious to hand-author

Writing `provenance: [{chapter: "...", section: "00-05.N"}, ...]`
for 23 elements was the single longest part of the POC authoring
session. The information is mechanically discoverable: scan the
chapter for the element's `name` (and close variants), record every
section heading whose subtree contains a mention.

This should be software — a `provenance-scan` script that takes the
model + the chapter set and proposes provenance for every element.
The agent only adjudicates ambiguous matches. Defer until the
discovery rules are written down; the POC validated that hand-
authoring at scale is unsustainable.

##### 00-06.10.3.4 — Relationship verbs drift without a catalog

Caught self writing "writes to" / "writes" / "writes pending decisions to"
for the same conceptual relationship. Without a controlled catalog,
the same intent surfaces in three slightly different verbs and the
model loses comparability across relationships.

The fix is a small YAML catalog (would have lived at `architecture/c4/verb-catalog.yml` at POC time)
that lists allowed verbs with one-line definitions; the validator
refuses (or warns on) relationships whose `description` opens with
an off-catalog verb. Software work; small.

##### 00-06.10.3.5 — Tags field needs taxonomy discipline

The POC's `tags: [internal, datastore, c4-2, conform]` mixes three
different concerns: position-relative-to-scope (`internal` /
`external`), C4 level affinity (`c4-1`/`c4-2`/`c4-3`), and free-form
clustering (`conform` / `bootstrap` / `agent`). Mixing them led to
over-tagging and inconsistent application.

Split into three fields: `position`, `c4_levels` (multi-valued), and
`tags` (free-form clustering only). Schema change; mechanical to
adopt.

##### 00-06.10.3.6 — Pan/zoom on the embedded diagrams (resolved in revision 4)

Revision 3 vendored the third-party `svg-pan-zoom.min.js` library
(~30 KB minified) to give embedded diagrams a pan/zoom affordance.
Two ergonomic problems surfaced in use:

1. **Center-of-viewport zoom.** Wheel-zoom anchored on the SVG's
   center rather than the cursor. The reader had to alternate
   wheel-to-zoom + drag-to-pan to home in on a region of interest,
   instead of zooming directly on the spot under the mouse.
2. **Pan stops when the cursor leaves the SVG.** The library's pan
   listeners lived on the SVG element. Dragging the cursor off the
   diagram (which is easy to do given the 540px height) cancelled
   the pan mid-gesture.

Both behaviours have well-implemented alternatives in an adjacent
project (Flow's viewport module). Revision 4 retired the third-party
library and vendored Flow's `svgPanZoom` package at
`docs/assets/svgPanZoom/` — a position deliberately above the
book-00-specific `docs/00/assets/` tree so the library is available
to every book in the ARC-100 system, not just chapter 00-06's c4
diagrams. The Flow package ships as a zero-dependency ES module
(~5 KB unminified) with cursor-anchored zoom, document-level pan
listeners (panning continues when the cursor drifts off the SVG),
an auto-managed `%` zoom-level indicator, and an optional fade-in
on first render. Full API is documented at
`docs/assets/svgPanZoom/svgPanZoom.md`.

**Implementation details** for the C4 integration
(`docs/00/assets/c4-pan-zoom.js`):

- The file is now an ES module (`<script type="module">` in
  `mkdocs.yml`'s `extra_javascript`). The Flow package uses `export`
  rather than a UMD global, and modifying it would break the
  "transportable" property the package was extracted to provide.
- For each `<div class="c4-diagram" data-c4-view="…">` on the page,
  the script fetches the matching SVG from `assets/c4/<view>.svg`,
  inlines it, **wraps the SVG's existing children in a new
  `<g class="svgpz-viewport">`**, and calls
  `createSvgPanZoom({ svg, viewport, container, … })`. Mermaid's
  output doesn't reliably provide a single top-level group; wrapping
  programmatically is the robust path.
- **Wheel behaviour** (revision 5 — was: Ctrl/Cmd-gated): when the
  cursor is over the diagram, wheel and two-finger trackpad swipe
  drive Flow's cursor-anchored zoom (Flow's `onWheel` always calls
  `preventDefault()`, so the page does NOT scroll while the cursor
  is over the SVG). When the cursor is anywhere else on the page,
  wheel scrolls the page normally — no JS gate is needed because the
  c4-pan-zoom loader doesn't attach a wheel listener outside the
  SVG. This matches the Google-Maps / Figma / mkdocs-material-Mermaid
  pattern. The earlier revision-4 design gated zoom behind Ctrl/Cmd
  to avoid "accidental hover captures vertical page scroll" — that
  protection proved to be hidden ergonomics (readers who explored a
  diagram had to remember the modifier; readers who didn't never
  triggered zoom and assumed it was broken). The revision-5 trade-off
  is the inverse: a reader scrolling down a chapter whose cursor
  happens to cross the 540px-tall diagram will see the diagram zoom
  instead of the page scroll. This is the convention modern tools
  have settled on; readers learn to move the cursor off the diagram
  before scrolling, and the diagram itself is now correctly
  exploratory the moment the cursor lands on it.
- Per-container teardown: the script tracks the controller per
  `.c4-diagram` element in a `WeakMap`. On mkdocs-material's
  instant-navigation re-init, the prior controller is `destroy()`-ed
  before the next is created. This avoids leaking the document-level
  pan listeners the Flow library installs.
- `fitToContainer()` is deferred by one `requestAnimationFrame` after
  inline-mount so Mermaid's computed dimensions are available when
  `getBBox()` runs (the Flow `svgPanZoom.md` "Common gotchas" entry).

**CSS changes** in `docs/00/assets/arc100.css`: the previous
`.svg-pan-zoom-control` rules (from the retired library's controls
overlay) were replaced with `.svgpz-zoom-level` rules (Flow's
auto-managed `%` indicator) and `svg.panning` rules (Flow's cursor
feedback during drag-pan). The `.c4-diagram` container gained
`position: relative` so the `%` indicator's absolute positioning
resolves against the diagram box rather than the page.

**What this section is not:** a critique of `svg-pan-zoom.min.js` in
general. It's a robust library with broad use, good touch support,
and built-in controls UI. The match-up of needs for embedded-in-docs
C4 diagrams happens to favour the Flow package — cursor-anchored zoom
matters more than touch support; the smoother pan UX matters more than
having a controls overlay. Different surface, different tradeoffs.

##### 00-06.10.3.7 — Typography pass (Inter; resolved in revision 6)

Mermaid's default font stack for C4 diagrams is `"Open Sans",
sans-serif` at 12px (italic stereotype), 14px (description), and 16px
(bold title). On the rendered docs page — even after revision 3's
width tuning and the revision-4 pan/zoom upgrade — three problems
remained:

1. **12px italic was sub-legible at the column width**, even with
   pan/zoom available; readers shouldn't need to zoom to read the
   stereotype labels at default fit.
2. **Open Sans fell back to platform defaults on systems without it.**
   The dock-and-text mismatch produced inconsistent vertical metrics
   across diagrams on different browsers.
3. **Default weights produced a visually busy diagram.** Bold titles +
   normal descriptions + italic stereotypes at three nearby weights
   all in the same line-height pulled the eye in too many directions.

Revision 6 addresses all three by replacing Mermaid's default
typography on inlined C4 SVGs with **Inter** at three deliberately-
chosen weights, locally hosted at `docs/assets/fonts/`:

| Mermaid emits | Replaced with |
| --- | --- |
| 16px bold title | **18px Inter SemiBold 600** |
| 14px normal description | **14px Inter Light 300** |
| 12px italic stereotype | **14px Inter ExtraLight 200 Italic** |
| (any other text) | 14px Inter Light 300 (catch-all) |

The weight ladder (200 italic / 300 normal / 600 bold) is deliberately
wide. A narrower ladder (e.g. 300 / 400 / 500) would render at roughly
similar visual density — three weights blurring together. The wider
ladder lets a reader scan the diagram and immediately distinguish
"this is a title" from "this is a description" from "this is a type
annotation" by weight alone, before reading the text.

**Implementation:**

- **Font hosting**: `docs/assets/fonts/` (intentionally above the
  book-00-specific `docs/00/assets/` tree, mirroring the
  `docs/assets/svgPanZoom/` placement from revision 4 — the fonts are
  available to every book in the system). Three woff2 files sourced
  from `rsms/inter` (the canonical Inter project on GitHub), full
  Unicode set rather than Latin-subsetted (~340 KB total, cached after
  first load). Latin-only subsetting is a follow-up if payload size
  becomes a concern.
- **@font-face declarations**: `docs/assets/fonts/inter.css`, three
  rules with `font-display: swap` so a fallback renders immediately
  and Inter swaps in once loaded. Loaded first in
  `mkdocs.yml`'s `extra_css` list so the subsequent stylesheet can
  reference `"Inter"` by name.
- **SVG text selectors**: `docs/00/assets/c4-svg-typography.css`.
  Mermaid sets typography via inline `style="…"` attributes and SVG
  presentation attributes on text elements; CSS rules use `!important`
  paired with `.c4-diagram svg text[…]` substring selectors to win the
  cascade against Mermaid's inline `style="…font-weight: bold…"` form.
  Three selectors: `text[font-style="italic"]` (stereotype),
  `text[style*="font-weight: bold"]` (title),
  `text[style*="font-weight: normal"]` (description), plus a catch-all
  `text` rule for anything else (arrow labels, etc.). Loaded last in
  `extra_css` so it overrides anything earlier in the chain.
- **textLength stripping** in `c4-pan-zoom.js`: Mermaid sets
  `textLength` (a hard pixel target) + `lengthAdjust="spacing"` on
  italic stereotype text so it lays out at a Mermaid-computed width.
  Without intervention the raised 14px font would be compressed back
  to fit the original 12px-wide pixel target, producing visibly
  squished letter spacing. The loader strips both attributes during
  the inline step so the SVG re-lays-out the text naturally at the
  new font size.

**Improvisation note** — the user-facing direction set the font
schedule at the role level ("Light 300 for normal, ExtraLight 200
Italic for italic, SemiBold 600 for prominent text"), the 14px
minimum, and the 18px box-label target. Everything else is
improvised: the `font-feature-settings: "cv11", "ss03"` opt-in for
Inter's distinct "a" and "g" glyphs (quiet improvement; safe to
remove), the system-ui / sans-serif fallback chain (matches mkdocs-
material's existing fallback pattern), the catch-all rule at 14px
Light 300 for elements that don't match the three known patterns
(safer than letting Mermaid's font escape into a diagram via an
unrecognised text element). All of these are reversible.

**What this section is not:** a critique of Open Sans or of Mermaid's
default typography. Open Sans is a perfectly capable docs-grade
typeface; Mermaid's choices match what a generic-purpose diagram
renderer should default to. The replacement is project-specific:
ARC-100 is opinionated about the visual register of its docs, and a
consistent Inter family across both prose chapters (future work — the
chapters currently use the mkdocs-material default) and embedded
diagrams produces a calmer reading experience than a typeface mismatch
across the same page.

##### 00-06.10.3.8 — LikeC4 adoption (resolved in revision 7)

Revisions 3, 4, 5, and 6 each addressed a Mermaid-shaped friction
point (width tuning, pan/zoom retrofit, wheel UX iteration,
typography overlay). The cumulative pattern across those four
revisions is itself a finding: Mermaid C4 is a *general-purpose
diagram renderer with a C4 syntax skin*, and the friction-point
sequence was a project tuning a generic surface to behave like a
C4-purpose-built one. The decision in this revision substitutes the
renderer rather than continuing to layer overlays — **adopt LikeC4
(1.57.0) + the `mkdocs-likec4` plugin (1.1.1) as the C4 toolchain;
retire the Mermaid pipeline in revision 8 (phase 3b)**.

**Phase 3a (this revision)** is purely additive: it stands up the
LikeC4 infrastructure (scoped Node install — originally at `architecture/LikeC4/`; split per-tree in phase 3.1d to `master-vault/likec4/` + `docs/likec4/`,
plugin registered in `mkdocs.yml`, project config at
`docs/architecture/likec4.config.json`, hash-pinned `requirements.txt`
for the Python deps, `likec4-author` agent at `.claude/agents/` +
canonical template at `ARC-100-SYNC/templates/agents/`) and proves
the pipeline renders a trivial hello-world view. The Mermaid pipeline
continues to function alongside — `architecture/c4/render.py`,
`output/*.mmd`, `docs/00/assets/c4/*.svg`, `c4-pan-zoom.js`, and
`c4-svg-typography.css` are all unchanged. Chapter 00-05's
`<div class="c4-diagram">` blocks still render via Mermaid. The
deferral is deliberate: phase 3b will retire the Mermaid pipeline
atomically with the chapter-00-05 substitution (`<div class="c4-diagram">`
→ `<likec4-view>`) so the chapter never has a visibly-broken
intermediate state.

**Phase 3b will then supersede four prior friction-point entries**
via revision 8 of this chapter:

- **§00-06.10.3.2** — the `short_description` YAML field becomes
  moot once the YAML schema is gone; LikeC4's DSL is the new
  schema and exposes its own description handling.
- **§00-06.10.3.4** — LikeC4 ships its own implicit verb catalog
  rather than requiring a project-local YAML; the verb-catalog
  finding is superseded.
- **§00-06.10.3.6** — pan/zoom is built into LikeC4's web component;
  the Flow `svgPanZoom` package is retained at
  `docs/assets/svgPanZoom/` per user direction but becomes
  vestigial.
- **§00-06.10.3.7** — Inter typography is re-expressed via a small
  CSS file at `docs/00/assets/likec4-typography.css` (LikeC4 1.57.0's
  theme schema has `colors` and `sizes` only; no `fontFamily`
  primitive — a phase 3a Implementation Finding recorded in the
  phase plan §13.3); the Mermaid-specific `c4-svg-typography.css`
  retires.

**What didn't transfer** (recorded for future readers):

- The YAML schema (`short_description`, `position`,
  `c4_levels` taxonomy splits from §00-06.10.3.5). LikeC4's DSL is
  the new schema; the YAML structure has no analogue.
- The Mermaid-specific CSS-cascade tactics (`!important` paired with
  attribute-substring selectors targeting Mermaid's inline `style`).
  LikeC4's renderer marks up its SVG/HTML differently; the
  `likec4-typography.css` file phase 3b creates uses different
  selectors against the LikeC4 web-component shadow DOM (the exact
  selectors are a phase 3b discovery item).

**What improved:**

- Layout via ELK/dagre (LikeC4's bundled layouter) rather than
  Mermaid's renderer — fewer label collisions, more deliberate
  edge routing.
- C4-purpose-built vocabulary (SoftwareSystem, Container, Component,
  Person, plus a `dynamic` view kind for sequence-style flows) rather
  than Mermaid's general diagram primitives mapped to C4 by
  convention.
- Built-in pan/zoom + browser chrome via the web component — the
  custom `c4-pan-zoom.js` (revision 4's work) becomes unnecessary.
- The `mkdocs-likec4` plugin (Python; runs inside `mkdocs build` via
  the plugin API) rewrites `likec4-view` fenced blocks into
  `<likec4-view>` web components and generates the project-specific
  JS bundle at `site/assets/mkdocs_likec4/likec4_views_<project>.js`.
  No custom asset-wrangling needed in `mkdocs.yml` beyond plugin
  registration.

**What is unresolved at the new layer** (phase 3b discovery items):

- LikeC4 1.57.0's theme schema's per-role expressiveness — phase 3b
  authors the real ARC-100-SYNC model where all three roles (title,
  description, stereotype) surface naturally and the weight mapping
  becomes observable; the CSS-fallback path is already scoped.
- Cross-file model semantics for phase 3b (two disjoint systems —
  ARC-100-SYNC and the LikeC4 tooling itself — in one workspace).
- The runtime-composition consequence: this is ARC-100's first Node
  footprint (LikeC4 is Node-toolchain). Phase 3a §7 records the
  integrity-test answer; phase 3a §13.3 will record whether the
  install was friction-free in practice.

#### 00-06.10.4 — Implications for the next iteration

The POC validates the overall shape (YAML source → render script →
Mermaid in chapters works end-to-end) and surfaces a specific list
of refinements (§00-06.10.3) to address before any active software
(embedder, drift detector) is built. The natural ordering:

1. Refine the schema — fold in `auto_include`, `short_description`,
   split tags by concern, codify the verb catalog. Document the
   schema as the authoritative spec; lock the format before
   building tools that consume it.
2. Re-author the ARC-100-SYNC model against the refined schema as a
   second-pass POC. Confirm authoring cost drops and the rendered
   diagrams improve.
3. Build the provenance-scan tool. This removes the most-tedious
   manual step.
4. Build the embedder. This eliminates the manual-paste step and
   proves the full software pipeline is automatable.
5. Only after steps 1–4 settle: design the `c4-modeler` agent
   against the now-stable schema and toolchain. The agent's
   prompt becomes much shorter when it doesn't have to also
   describe the friction points.

This sequencing — schema, scripts, agent in that order — is the
opposite of how revision 1 framed the work (agent first, with
software as scaffolding). The POC inverted the priority because the
schema and tooling carry most of the load; the agent is a thin layer
on top once the substrate is stable.

#### 00-06.10.5 — LikeC4 in production: what works (added in revision 9)

§00-06.10.4 above is the *planning* surface as it stood before
phase 3a/3b implemented. This section is the *retrospective + operational*
surface: what the Mermaid → LikeC4 substitution actually delivered, and
the per-view settings the project has converged on. The historical
record of the Mermaid POC stays where it is (§00-06.10.3.1–.3.7 friction
points; §00-06.10.3.8 LikeC4-adoption decision; Revision 8 atomic-retirement
table row) — this section adds the empirical layer that surfaced once the
chapter-00-05 diagrams were actually rendered through LikeC4 against
the real ARC-100-SYNC model.

##### 00-06.10.5.1 — Why we left Mermaid

The Mermaid C4 POC ran end-to-end (YAML model → `render.py` → inlined
SVG → custom pan/zoom JS → CSS typography overlay) and validated the
overall *shape* of the modeling discipline. It did not validate
Mermaid as the long-term renderer. Two root causes accumulated across
revisions 3–6:

1. **Visualization quality was poor at default settings.** Mermaid C4
   targets the generalist-diagram use case: its layout engine packs
   long descriptions into narrow boxes, then scales the entire SVG
   down to fit the rendered column width, producing 8–12px text that
   readers needed to zoom to read. Revisions 3, 4, 5, 6 each layered
   a custom workaround on top (`short_description` YAML field to
   shorten labels; vendored `svg-pan-zoom.min.js` then Flow `svgPanZoom`
   for pan/zoom; Ctrl/Cmd wheel gating then cursor-anchored zoom;
   Inter typography via `!important`-laden CSS overrides on inline
   SVG `style="…"` attributes). Each fix succeeded individually; the
   cumulative pattern was a project re-implementing a C4-purpose-built
   renderer on top of a generalist one. §00-06.10.3.8 captured this
   verdict — *"Mermaid C4 is a general-purpose diagram renderer with
   a C4 syntax skin, and the friction-point sequence was a project
   tuning a generic surface to behave like a C4-purpose-built one"* —
   and committed to the renderer substitution rather than another
   overlay.
2. **Lack of a unified DSL forced parallel project-local infrastructure.**
   Mermaid C4 is a rendering syntax, not a model. The project had to
   maintain its own YAML schema (`architecture/c4/arc-100-sync.model.yml`)
   to hold what Mermaid's syntax could not express: ULID provenance
   (§00-06.10.3.3), the relationship verb catalog (§00-06.10.3.4), the
   tag taxonomy (§00-06.10.3.5), the per-element `short_description`
   field (§00-06.10.3.2), and the view-includes lists (§00-06.10.3.1).
   Every one of those was a fragment the project owned because Mermaid
   didn't. A custom `render.py` (352 lines) translated YAML → Mermaid,
   another script handled validation, another would have handled
   chapter embedding. The cost of "Mermaid as the renderer" was *not*
   Mermaid itself — it was the bespoke YAML + script substrate that
   Mermaid forced the project to grow around it.

LikeC4 inherits both pieces natively: a purpose-built C4 renderer
(layout, pan/zoom, typography, web-component embedding all first-class)
*and* a unified DSL where model + views + theme + element kinds + view
scoping are one source-of-truth language. The retirement (phase 3b /
Revision 8) deleted nine project-owned files (`render.py`, three
`*.mmd`, three `*.svg`, `c4-pan-zoom.js`, `c4-svg-typography.css`) and
the `mkdocs.yml` plumbing that wired them in. The YAML model at
`architecture/c4/arc-100-sync.model.yml` was retained as a POC museum piece through phase 3c; phase 3.1d dropped it. Git history at commit `bc0dab6` preserves the file as the POC artifact. The renderer + glue substrate is
gone for good.

##### 00-06.10.5.2 — What survived from the Mermaid era

Not all of the Mermaid-era investment retired with the renderer. Two
pieces carried forward:

- **The Inter weight schedule** (§00-06.10.3.7) — 18px SemiBold 600
  titles, 14px Light 300 descriptions, 14px ExtraLight 200 Italic
  stereotypes. Re-expressed against LikeC4's discovered per-role
  HTML data-attributes (`[data-likec4-node-title]`,
  `[data-likec4-node-description]`, `[data-likec4-node-technology]`)
  plus the LikeC4-exposed CSS variables `--fonts-likec4-element` and
  `--fonts-likec4-compound`. The `docs/00/assets/likec4-typography.css`
  file is the LikeC4-era replacement for the retired
  `c4-svg-typography.css`. The same `docs/assets/fonts/inter.css`
  @font-face declarations carry over unchanged.
- **The Flow `svgPanZoom` library** at `docs/assets/svgPanZoom/` —
  retained per user direction even though LikeC4's web component has
  built-in pan/zoom. Vestigial today; available if a future
  integration wants it. Phase 3b §13.2 confirms zero-change.

The two `.c4-1` / `.c4-2` / `.c4-3` CSS classes on chapter 00-05's H3
headings were stripped during phase 3b (simplifier-driven; verified
zero CSS rules reference them). The `data-c4-*` attribute decorations
and `data-entity-ulids` lists were stripped at the same time — they
were Mermaid-pipeline metadata for `c4-pan-zoom.js` and have no LikeC4
analogue. Chapter 00-05's H3s now carry only their `{ #anchor-id }`.

##### 00-06.10.5.3 — Operational settings (post-implementation eyeball pass)

The chapter-00-05 substitution surfaced one significant empirical
finding that the phase 3b plan had not anticipated, and that drives
the project's per-view embedding standard going forward.

**The finding**: the inline `LikeC4View` (the React Flow surface
mounted inside each `<likec4-view>` web component) is rendered as
an auto-fit *static* thumbnail by default. Its `pannable`, `zoomable`,
and `controls` props from LikeC4's React API exist — but the
`mkdocs-likec4` 1.1.1 fence syntax does not parse them, and the
underlying `<likec4-view>` web component's `observedAttributes` is
similarly minimal (`view-id`, `browser`, `dynamic-variant`,
`color-scheme` only). Setting `pannable=…` in the fence is silently
ignored; setting it via raw HTML on the web component is also inert.
The only readability escape hatch the plugin currently exposes is
`browser=true`, which enables a click handler that opens the
`LikeC4Browser` modal (a full interactive popup with pan / zoom /
focus mode / element details / navigation between views).
`browser=false` disables this click handler — making any view with
more than ~5 elements visually unreadable on the page with no
recovery path. Phase 3a's author decision #2 (`browser=false` default
for chapter-embedded views) was based on a mis-assumption that
`browser=false` would still produce an interactive inline surface;
in practice it strips the only path to readability.

**The standard adopted in revision 9 (Plan A)**: `browser=true`
for every embedded view. Performance-neutral vs `browser=false`
(the `LikeC4Browser` modal code is in the bundle either way; only a
click handler differs). The standard is encoded in the `likec4-author`
agent body (Skill 4 — mkdocs embedding mechanics) and the
`likec4-introspection` skill cross-references it.

**Provisional refinement**: if and when the mkdocs-likec4 plugin
(or LikeC4's `__app__/codegen/webcomponent.mjs` template) gains
`pannable` / `zoomable` / `controls` support, the convention becomes:
prefer in-place interactivity (`pannable=true zoomable=true controls=true`)
for views with ≤ 5 elements; reserve `browser=true` for views with
> 5 elements where the modal's expanded canvas pays for itself.
Until that lands, `browser=true` universally is the operational rule.

##### 00-06.10.5.4 — Hosting-cost disciplines

The chapter-00-05 build measured the actual cost model for the first
time. Three independent cost axes:

| Axis | What scales it | Discipline |
| --- | --- | --- |
| Per-project JS bundle (~2.3 MB for ARC-100) | Number of distinct LikeC4 projects (separate `likec4.config.json` files with different `name:` values) | **One LikeC4 project per documentation site, by default.** Disjoint systems live as separate `.c4` files in the SAME project, sharing one workspace. The bundle's React + Mantine UI + ELK + graphviz-WASM runtime is duplicated per project — splitting one project into two ships ~2.3 MB twice. Within one project, adding `.c4` files / elements is ~free (variable model-data portion is < 1 % of the bundle; the runtime is fixed). |
| Per-page `<script>` tag | One per project referenced on the page | A page that embeds views from N distinct projects loads N bundles. The "one project default" rule above keeps this at one tag per page. |
| Per-view React mount | Number of `<likec4-view>` blocks on a single page | Each block mounts its own Shadow DOM + React reconciler. ~10–20 mounts per page is comfortable; > 30 starts to feel sluggish at page load. **Per-page budget: warn at > 10 blocks on one page.** If a chapter needs to embed many views, split across sub-sections, or use one higher-level (Container / Component) view rather than N sibling free-standing views, or use `view of <element>` scoping to consolidate. |

These are advisory budgets, not hard limits — measure if the boundary
matters for a specific chapter. The `browser=true` standard does not
add to any of these axes (the modal code is in the bundle either way).

##### 00-06.10.5.5 — Where the operational specifics live

| Concern | Source of truth |
| --- | --- |
| Per-view embedding standard (`browser=true`, hosting-cost disciplines) | `.claude/agents/likec4-author.md` Skill 4 + the new "Hosting-cost considerations" sub-section (canonical template at `ARC-100-SYNC/templates/agents/likec4-author.md`, delivered mirror-class to a downstream project's main `.claude/agents/` — project root, not the `<PROJECT>-100/` instance) |
| Read-only model introspection patterns (MCP tool selection by question) | `.claude/skills/likec4-introspection/SKILL.md` |
| Inter weight schedule (CSS-fallback selectors against LikeC4's per-role data-attributes) | `docs/00/assets/likec4-typography.css` |
| LikeC4 model source (ARC-100 Standard) | `master-vault/likec4/arc100-sync.c4` (23 elements / 29 relationships / 3 views) |
| LikeC4 model source (ARC-100 Project) | `docs/likec4/placeholder.c4` (seed; real software model authored in a follow-up phase per V1_STRATEGY §6.8.2) |
| LikeC4 project discovery + config | `master-vault/docs/00/model/likec4.config.json` (project `name: arc-100`; `include.paths: ["../../../likec4/"]`) + `docs/01/model/likec4.config.json` (project `name: arc-100-project`; `include.paths: ["../../likec4/"]`) |
| mkdocs plugin registration | Both `mkdocs.arc100.yml` and `mkdocs.arc100project.yml` `plugins:` blocks (`likec4: { use_dot: false }`); red site's `extra_css:` entry for `likec4-typography.css` |
| Wrapper scripts | `master-vault/likec4/bin/likec4` (cwd-disciplined to `master-vault/docs/00/model/`) + `docs/likec4/bin/likec4` (cwd-disciplined to `docs/01/model/`) — per-tree cd discipline keeps each workspace scan inside its own tree |
| LikeC4 toolchain pin | `master-vault/likec4/package.json` + `docs/likec4/package.json` (both pin `likec4@~1.57.0`, byte-identical except for `name`/`description`); lockfiles tracked alongside |

##### 00-06.10.6 — Operating an embedded view

Every embedded `<arc-100-view browser=true>` on this site is two surfaces
in one: the static auto-fit *thumbnail* you see in-page, and the interactive
*modal* that opens when you click the thumbnail. The modal is the productive
surface — these are the gestures it supports (every one defaults on; the UI
just doesn't advertise them):

| Gesture | Effect |
| --- | --- |
| Click the inline thumbnail | Opens the LikeC4Browser modal (full canvas) |
| `Ctrl-K` / `Cmd-K` inside the modal | Element search (by name, kind, tag) |
| Double-click an element | Focus mode — re-centres the canvas on that element with its 1-hop neighbours |
| Single-click an element | Element details panel — description, technology, tags, incoming/outgoing relationships |
| Click an edge label (the verb on a relationship line) | Relationship browser — the verb's source, destination, and any documented details |
| Top-left chevrons (back / forward) | Navigate the view-history stack inside the modal (appear once you've navigated at least once) |
| `Esc` or click outside the canvas | Close the modal — return to the inline thumbnail |

These are inherited from LikeC4's React component defaults (`enableSearch`,
`enableFocusMode`, `enableElementDetails`, `enableRelationshipBrowser`,
`showNavigationButtons`, `enableNotations` — all default `true`); the
`mkdocs-likec4` 1.1.1 fence syntax does not expose them as per-block knobs.
The gap this sub-section closes is *discoverability*, not *capability* —
every feature was already there in phase 3b; the modal just doesn't
advertise them. Cross-reference §00-06.10.5.3 for the *why* of the
`browser=true` standard; this sub-section is the *how*.

> **Caveat — `Ctrl-K` / `Cmd-K` may be shadowed.** mkdocs-material's
> instant-search overlay binds globally to `Cmd-K` / `Ctrl-K` (and `S`
> and `/`) at the document level and may intercept the keystroke before
> the open modal receives it. If the shortcut pops the site search
> overlay instead of the modal's element search at your install, use
> the magnifying-glass icon in the modal toolbar to invoke search.

### 00-06.11 — Use cases for the generated artifacts

Three deployment surfaces for the diagrams the model produces. None
are mutually exclusive; a mature project may use all three.

**Surface 1 — Embedded in the project's `-100` mkdocs site.** The
most obvious use: a chapter section tagged `c4-2` carries an embedded
Container diagram immediately below its heading; a chapter section
tagged `c4-3` carries an embedded Component diagram of one specific
Container. The reader gets a visual summary alongside the prose
without leaving the site. Drill-down navigation (click a Container,
see its Components) is supported by Structurizr natively and by
Mermaid C4 with custom click handlers.

**Surface 2 — In CodeScan, complementary to the existing physical
perspective.** CodeScan already maintains a physical-perspective view
of a system. The C4 model adds a *logical* perspective alongside it.
A unified UI could show both side-by-side: the logical intent (what
the architecture *should* be) and the physical reality (what the
code *actually is*), with drift between them as a navigable concern.
This is the surface most likely to drive cross-system data-sharing
questions — what wire format does ARC-100 publish so CodeScan can
consume?

**Surface 3 — A standalone modeling application.** A focused tool
that does nothing but author and explore the C4 model, with no
prose dependency. This is what Structurizr Cloud is. Building a
custom one for ARC-100 only makes sense if Structurizr's specific
ergonomics don't fit; the cheaper path is to emit Structurizr DSL
and let the existing tool render. The "standalone application"
surface is the least committed-to of the three; mostly worth
mentioning as a fallback if surface 1 and surface 2 hit limits.

### 00-06.12 — Open architectural questions

These are the deliberation surfaces. The decisions are not yet made;
their resolution is what would let a later revision of this chapter
present as a hardened specification rather than an exploration.

**Q1 — Storage model: text-only, SQLite-only, or hybrid?** §00-06.6
laid out the tradeoffs. A reasonable progression starts text-only
and migrates to hybrid at scale; the question is whether to commit
to the hybrid endpoint now (and design the materialization step into
the v1 tooling) or defer until ergonomics demand it. *POC-informed
(§00-06.10): the 23-element model was authored as a single YAML file
under `architecture/c4/` at POC time (removed in phase 3.1d). Text-only is unambiguously fine at this
scale. Hybrid still appears to be the right destination once the
project's own architecture is modeled (estimated ~150–250 elements),
but the case for the build-time SQLite materialization is not yet
operationally felt.*

**Q2 — Per-chapter sidecars vs. project-wide model file?** The
sidecar shape matches ARC-100's per-chapter ownership; the project-
wide shape matches Structurizr's expectations and makes cross-cutting
queries cheaper. Hybrid storage could split the difference (sidecars
as source; project-wide DB as build-time materialization), but
that's another layer. *POC-informed: the model lived at
`architecture/c4/arc-100-sync.model.yml` (POC era; superseded by per-tree DSL in phase 3.1d) — one project-wide file per
system being modeled, outside the `docs/` tree. That layout worked
cleanly. Per-chapter sidecars would have meant fragmenting cross-
chapter relationships into multiple files; the project-wide-per-
system shape avoids that.*

**Q3 — Inheritance semantics for downstream `<PROJECT>-100` projects.**
ARC-100 itself has a model (modest — sync engine, librarian, hook).
A downstream FLOW-100 inherits the ARC-100 entries via ARC-100-SYNC.
Does FLOW-100 also inherit the architecture-model entries? If so, by
what mechanism? The model registry would need a `arc_100: true` flag
parallel to the index's, and a sync engine for the model parallel to
the index's conform engine. Whether to build that — or to keep the
model fully project-local — is open.

**Q4 — Diagram renderer choice.** §00-06.8 listed five candidates.
Each has a different cost-benefit. Choosing Mermaid C4 for v1 (cheapest)
is reasonable; the model layer is renderer-independent so the choice
is reversible. *POC-informed: Mermaid C4 was used in the POC. Two
limitations surfaced — (a) limited layout control compared to
Structurizr, (b) Mermaid C4 is still labelled experimental and
syntax is subject to change. Both are tolerable for a working draft;
neither is a blocker. The model-layer renderer-independence held —
emitting Structurizr DSL as an alternative output would be a small
extension to `render.py`.*

**Q5 — Where do views live in the markdown tree?** Three candidates:
(a) embedded in chapter prose at the section the view describes;
(b) collected on a dedicated `docs/architecture/` page; (c) a
separate top-level book in ARC-100's banded index (e.g., a new band
or a dedicated chapter under existing bands). Option (a) is
proximity; option (b) is single-page discoverability; option (c) is
governance-via-ARC-100. Probably not mutually exclusive. *POC-
informed: the POC used option (a) — diagrams embedded inline in
chapter 00-05 at relevant section breaks (SystemContext after the
system-framing section §00-05.1; ContainerView after the runtime-
composition section §00-05.7). Proximity proved valuable. Options
(b) and (c) remain open for project-wide indexes once multiple
systems are modeled.*

**Q6 — How is the `c4-modeler`'s holistic-decomposition output
validated?** Holistic decomposition is judgment work with no
algorithmic ground truth. A first cut by the agent is rarely the
final answer. What's the review workflow? Author-reviews-agent (the
agent proposes, the human approves)? Agent-reviews-agent (a separate
validator pass)? Both? *POC-informed: the POC was the inverse —
human-authored decomposition, then software-validated. The validator
(now scoped as software per §00-06.9.2) cannot validate the
decomposition itself; only the structure that results from it.
Validation of decomposition quality remains a human-review concern.
Question still genuinely open; the POC narrowed it from "what's the
workflow?" to "what helps a human review an agent's decomposition
proposal?"*

**Q7 — Cross-system data exchange with CodeScan.** If the C4 model is
to be a complement to CodeScan's physical perspective (use case 2,
§00-06.10), the two systems need a wire format. JSON? Structurizr's
JSON workspaces? A purpose-built ARC-100 / CodeScan exchange schema?
The answer affects how Q3 (downstream inheritance) plays out, since
cross-project sync and cross-system sync are structurally similar.

**Q8 — Element lifecycle and deprecation.** ARC-100 chapters have a
status lifecycle. Architectural elements probably should too — a
Container can be retired, a Component can be superseded. Should the
model adopt the same `active | deprecated | superseded` vocabulary,
or does architecture deprecation require richer states (e.g.,
`planned`, `prototyped`, `in_production`, `sunsetting`)?

**Q9 — Cross-project element references.** Can FLOW-100's
"auth service" element ULID-link to CS-100's "auth service" element
if they refer to the same deployed thing? If yes, that's a form of
horizontal coupling between project models; if no, every project has
its own siloed view of shared infrastructure. The right answer
probably depends on Q7's wire-format decision.

**Q10 — Model versioning.** Is the model pinned to an ARC-100 version,
or does it have its own version cadence? ARC-100's master/version
split (§00-00.8) gives a precedent: the master spec carries one
version; each downstream project's version is independent. The model
could mirror this — a master architecture model that downstream
projects fork, with explicit sync semantics — but adopting this adds
the same complexity that ARC-100-SYNC handles for the index.

**Q11 — Agent granularity.** *Substantially resolved by the POC.*
The revision-1 proposal of four agents (`c4-modeler`,
`c4-validator`, `c4-diagram-author`, `c4-physical-mapper`) was
tested against actual hand-construction work in §00-06.10; three of
the four turned out to be software. The post-POC shape is one agent
(`c4-modeler`) doing the consequential work + three software pieces
(validator, renderer, embedder). Q6 (validation workflow for
holistic decomposition) and Q7 (cross-system bridge) remain open but
are no longer entangled with the granularity question.

### 00-06.13 — Out-of-scope topics

The following are explicitly *not* part of this chapter or the
discipline it sketches:

- **Code-level documentation (UML class diagrams, method-level
  contracts).** C4-4 is optional in C4 itself, and explicitly so
  in this chapter. The plans (`versions/v1/implementation/...`)
  already carry function-level specifications; a UML-style C4-4
  layer would duplicate them.
- **Runtime tracing or observability.** Architecture modeling
  describes the *intent*; tracing tools describe *behaviour*. The
  two are complementary but distinct disciplines.
- **Threat modeling.** §00-04 already names threat modeling as
  adjacent; chapter 00-05 §00-05.11 carries phase_2a/2b's threat-
  modeler output. A dedicated threat-modeling chapter is a separate
  potential allocation (cf. the proposed `93-01 Supply Chain Trust`
  chapter from phase_2b's revision-4 history).
- **Cost modeling / capacity planning.** Architecture's
  Deployment view names *what runs where*; capacity modeling names
  *how much it costs*. Out of scope.
- **Code generation.** The C4 model describes the architecture, not
  the implementation. Tooling that scaffolds code from the model is
  conceivable but not part of this chapter's scope.

### 00-06.14 — Pointers

- Chapter 00-04 (`docs/00/00-04_ARC-100_Standards_Comparisons.md`) —
  the quantified comparison of ARC-100 against C4 and eight other
  standards. The starting point for any deliberation about which
  framework fits.
- Chapter 00-05 (`docs/00/00-05_ARC-100_Synchronization.md`) — the
  sync system's intent capture; a natural first target for a
  hand-authored architecture model as a proof-of-concept.
- `c4model.com` — the canonical reference for C4 (Simon Brown).
- Structurizr — `structurizr.com` — the reference tooling stack
  whose data model this chapter draws from.
- `ARC-100-SYNC/scripts/ulid.py` — the ULID generator the model
  reuses for element identity.
- `architecture/c4/arc-100-sync.model.yml` — the POC model
  documented in §00-06.10. Source of truth for the rendered
  diagrams in chapter 00-05.
- `architecture/c4/render.py` — the POC renderer (validator +
  YAML→Mermaid C4 emitter).
- `architecture/c4/output/` — generated Mermaid C4 blocks per view.

> These three POC artifacts were dropped from the working tree in
> phase 3.1d (2026-05-26); git history at commit `bc0dab6` preserves
> them.

## Revisions

| Date | Change |
| --- | --- |
| 2026-05-18 | Initial early-draft authoring as an exploration of how C4 / Structurizr can complement ARC-100 (option α from chat-time deliberation). Intentionally exploratory tone; most decisions framed as open questions in §00-06.11. Status set to `draft` rather than `active` — the chapter is a deliberation surface, not a ratified specification. Not yet allocated in the `00-01` index; allocation is a separate decision pending working through the open questions. Companions cite §00-04 (standards landscape) and §00-05 (synchronization, where the modeling discussion was first raised). |
| 2026-05-19 | Revision 2: POC-driven reclassification of the agent/software boundary. Built a complete C4 model of the ARC-100-SYNC system end-to-end (model YAML + renderer + chapter-embedded diagrams) and tracked every authoring activity against an agent-vs-software lens. The revision-1 proposal of four agents (`c4-modeler`, `c4-validator`, `c4-diagram-author`, `c4-physical-mapper`) was wrong on three of four: validator, renderer-orchestrator, and physical-mapper turned out to be deterministic software, not agent territory. Only `c4-modeler` (holistic decomposition + description authoring + view scoping) genuinely needs agent reasoning. Pattern recorded as the headline takeaway: **"Agents declare; software enforces and emits."** §00-06.9 rewritten in place; new §00-06.10 captures the POC findings (what was built, the activity-by-activity boundary, five friction points worth addressing before more tooling is built). Open Questions Q1, Q2, Q4, Q5, Q6, Q11 annotated with POC-informed notes; Q11 substantially resolved. Section numbering ripple: previous §00-06.10–.13 renumbered to §00-06.11–.14 to make room for the new POC-findings section. Chapter remains `status: draft`. |
| 2026-05-19 | Revision 3: readability sweep on the POC rendering pipeline — implemented the three-step plan from a chat-time deliberation about diagram unreadability (text size 8px–12px target at the 1342px full-page width; readable when CSS-shrunk to the 809px content column). **Step 1 — short_description schema field**: added to all 23 elements + all 29 relationships in `architecture/c4/arc-100-sync.model.yml`. The renderer reads `short_description` first; falls back to `description` when absent. Box and arrow labels are now 5–8 words instead of full sentences, which is the root cause of the prior unreadable text (Mermaid scales the whole SVG down to fit the column; long labels force tiny text). **Step 2 — standalone SVG via `npx mmdc`**: extended `render.py` with `--svg` and `--width` flags that shell out to `npx --yes -p @mermaid-js/mermaid-cli mmdc -w 2000 -b transparent`. SVGs land at `docs/00/assets/c4/<view>.svg` (committed; parallel to the existing `docs/00/assets/comparisons/` pattern). Mermaid's natural layout produced 865–954px widths with uniform 12px text — readable at the column width without further scaling. **Step 3 — `svg-pan-zoom`**: vendored 3.6.1 locally at `docs/00/assets/svg-pan-zoom.min.js` (~30 KB); wrote `docs/00/assets/c4-pan-zoom.js` that scans for `<div class="c4-diagram" data-c4-view="…">` containers, fetches the matching SVG, inlines it, and initialises pan-zoom (Ctrl/Cmd+wheel zoom + drag pan + in-diagram controls). Mouse-wheel hijacking deliberately gated behind the modifier key so the diagram doesn't capture page scroll on accidental hover. Both new JS files wired in via `extra_javascript:` in `mkdocs.yml`. **CSS**: added `.c4-diagram` container styling to `docs/00/assets/arc100.css` (540px initial viewport height, light border, grab cursor, opacity-on-hover controls). **Chapter 00-05 embedding**: replaced the two inline-Mermaid blocks with `<div class="c4-diagram" data-c4-view="…"></div>` placeholders. **Markdownlint policy**: added `MD033: false` to `.markdownlint.json` — the project's mkdocs config explicitly opts into `md_in_html`, and the C4 diagram placeholders use the same inline-HTML capability as the existing critical-banner pattern from phase_2a. Chapter remains `status: draft`. No POC findings (§00-06.10) changed; the friction points 1, 3, 4, 5 (auto_include, provenance auto-discovery, verb catalog, taxonomy split) are still pending. Friction point 2 (`short_description`) is now addressed in `arc-100-sync.model.yml`. |
| 2026-05-21 | Revision 4: pan/zoom library substitution — retired the third-party `svg-pan-zoom.min.js` (~30 KB, vendored in revision 3) in favour of the Flow-project `svgPanZoom` package (~5 KB unminified, zero dependencies). Motivation: Flow's library anchors wheel-zoom on the cursor (Google Maps-style) rather than the SVG center, and its pan listeners live on `document` so panning continues smoothly when the cursor drifts off the diagram bounds — both noticeably better UX for embedded-in-docs reading than the third-party library provided. **Package placement**: vendored at `docs/assets/svgPanZoom/` (a position deliberately above the book-00-specific `docs/00/assets/` tree, so the library is available to every book in the ARC-100 system rather than scoped to chapter 00-06's c4 diagrams). The package ships as two files: `svgPanZoom.js` (the ES-module library) and `svgPanZoom.md` (the API + migration documentation). **c4-pan-zoom.js rewrite**: now an ES module (`<script type="module">` in `mkdocs.yml`'s `extra_javascript`); imports `createSvgPanZoom` from `../../assets/svgPanZoom/svgPanZoom.js`; programmatically wraps the inlined SVG's children in a `<g class="svgpz-viewport">` (Mermaid's output doesn't reliably provide one top-level group); registers a wheel listener BEFORE creating the controller that calls `stopImmediatePropagation()` when no modifier key is pressed, preserving the revision-3 Ctrl/Cmd-gated zoom UX while letting Flow's cursor-anchored zoom run when the modifier is held; per-container controller tracking via `WeakMap` so mkdocs-material instant-navigation re-init can `destroy()` the prior controller and prevent document-level listener leaks; `fitToContainer()` deferred via `requestAnimationFrame` so `getBBox()` runs after Mermaid's computed dimensions are in. **CSS replacement** in `docs/00/assets/arc100.css`: the previous `.svg-pan-zoom-control` rules (overlay buttons from the retired library) replaced with `.svgpz-zoom-level` rules (Flow's auto-managed `%` indicator that briefly surfaces during wheel events) and `svg.panning` rules (Flow's cursor feedback during drag-pan); the `.c4-diagram` container gained `position: relative` so the indicator's absolute positioning resolves against the diagram box. **mkdocs.yml**: the `extra_javascript` entry for the retired `svg-pan-zoom.min.js` was removed; the entry for `c4-pan-zoom.js` was rewritten using the dict form with `type: module` so mkdocs renders the `<script>` tag with the ES-module attribute. **Files removed**: `docs/00/assets/svg-pan-zoom.min.js`. **Files added**: `docs/assets/svgPanZoom/svgPanZoom.js`, `docs/assets/svgPanZoom/svgPanZoom.md`. **POC findings**: §00-06.10.3.6 added as a new friction-point entry recording the migration with full implementation detail; friction points 1, 3, 4, 5 from revision 3 are still pending. Chapter remains `status: draft`. |
| 2026-05-21 | Revision 5: wheel-behaviour UX change — removed the Ctrl/Cmd-gated wheel handler that revision 4 had registered before Flow's `createSvgPanZoom()`. Wheel and two-finger trackpad swipe now drive cursor-anchored zoom whenever the cursor is over the diagram, with no modifier required; outside the diagram, wheel scrolls the page normally (no JS gate is involved — c4-pan-zoom simply doesn't attach a wheel listener outside the SVG). Motivation: the revision-4 Ctrl/Cmd gate was a deliberate protection against "accidental hover captures vertical page scroll", but in practice it was hidden ergonomics — readers exploring a diagram had to remember the modifier (often didn't), and readers who never explored never learned the zoom existed. Modern tools (Google Maps, Figma, mkdocs-material's own Mermaid integration when not embedded) have settled on the "cursor-over-canvas zooms" convention; this revision adopts it. The trade-off is real and recorded in §00-06.10.3.6: a reader scrolling down a chapter whose cursor crosses the 540px-tall diagram will see the diagram zoom instead of the page scroll. Documented as a known interaction; readers learn to move the cursor off the diagram before scrolling. **Code change**: one block removed in `docs/00/assets/c4-pan-zoom.js` (the `svg.addEventListener("wheel", …, { passive: true, capture: false })` that called `stopImmediatePropagation()` when no modifier was pressed). **Doc change**: §00-06.10.3.6's "wheel gating" bullet was rewritten in place to describe the revision-5 behaviour and the trade-off; the revision-4 history row above is unchanged (historical record of the prior design). No other code or asset changed. Chapter remains `status: draft`. |
| 2026-05-21 | Revision 6: typography pass — replaced Mermaid's default `"Open Sans", sans-serif` stack on inlined C4 SVGs with **Inter** at three locally-hosted weights. **Font hosting**: three woff2 files at `docs/assets/fonts/` (universal location above the book-00-specific tree, mirroring the revision-4 svgPanZoom placement) sourced from the canonical `rsms/inter` GitHub project — `Inter-Light.woff2` (300), `Inter-SemiBold.woff2` (600), `Inter-ExtraLightItalic.woff2` (200 italic), ~340 KB total full-Unicode (Latin subsetting is a follow-up if payload becomes a concern). **@font-face declarations**: `docs/assets/fonts/inter.css` with `font-display: swap`. **Role-to-weight schedule** (user-directed): bold box title → 18px Inter SemiBold 600 (was 16px bold); normal description → 14px Inter Light 300 (was 14px normal); italic stereotype → 14px Inter ExtraLight 200 Italic (was 12px italic). **SVG selectors**: `docs/00/assets/c4-svg-typography.css` targets `.c4-diagram svg text[font-style="italic"]`, `.c4-diagram svg text[style*="font-weight: bold"]`, `.c4-diagram svg text[style*="font-weight: normal"]`, plus a catch-all rule for any other text. Each rule uses `!important` to win the cascade against Mermaid's inline `style="…"` and presentation-attribute typography. **c4-pan-zoom.js**: stripped `textLength`/`lengthAdjust` attributes from inlined SVG text elements — Mermaid pins italic stereotype text to a 12px-wide pixel target via `textLength`, which would compress the new 14px glyphs back to fit the old width (visibly squished letter spacing). Strip is a 3-line `querySelectorAll("text[textLength]")` loop in the inline-mount step. **mkdocs.yml**: `extra_css` list grew by two entries — `assets/fonts/inter.css` first (so `"Inter"` is available by name to later sheets) and `00/assets/c4-svg-typography.css` last (so it overrides Material's stylesheet chain). **POC findings**: §00-06.10.3.7 added as a new friction-point entry recording the typography pass with full role-to-weight rationale + improvisation note covering the choices the user-direction didn't pin (font-feature-settings opt-in for cv11/ss03 stylistic sets, fallback chain, catch-all rule). Chapter remains `status: draft`. |
| 2026-05-23 | Revision 7: phase 3a LikeC4 adoption (infrastructure-only). Installed **LikeC4 1.57.0** as a scoped Node-toolchain at `architecture/LikeC4/` (devDependency-only, gitignored `node_modules/`, wrapper script at `architecture/LikeC4/bin/likec4` invoked via `npm exec --prefix`) and registered the `mkdocs-likec4==1.1.1` plugin in `mkdocs.yml`'s `plugins:` block with `use_dot: false` (bundled WASM graphviz; no system `dot` binary required). **Project config**: `docs/architecture/likec4.config.json` declares `name: "arc-100"` and `include.paths: ["../../architecture/LikeC4/"]` — phase 3a finding (Q1): LikeC4 1.57.0's config schema uses `include.paths`, not the build-plan-assumed `sources` field. **Validation harness**: `architecture/LikeC4/hello-world.c4` (trivial 2-element / 1-view model; deleted in phase 3b when the real ARC-100-SYNC model lands). **First Python dep manifest**: hash-pinned `requirements.txt` at the repo root per TM-3a-2 (six packages: mkdocs, mkdocs-material, pymdown-extensions, pyyaml, mkdocs-likec4, pyjson5 — the last is mkdocs-likec4's dep, picked up during the install). Installs via `python3 -m pip install --user --require-hashes -r requirements.txt`; CLAUDE.md gained a `## Verification` pointer. **`likec4-author` agent**: 350-line agent at `.claude/agents/likec4-author.md` covering four skills (DSL model authoring, view definition, theme/styling, mkdocs embedding mechanics); canonical template mirrored to `ARC-100-SYNC/templates/agents/likec4-author.md` for downstream distribution via `install.sh`. The agent body inlines the Inter weight schedule from §00-06.10.3.7 (preserving the spec ahead of phase 3b's deletion of the Mermaid-specific `c4-svg-typography.css`). **Per-role theme deferred to phase 3b**: phase 3a finding (Q3): LikeC4 1.57.0's `styles.theme` schema exposes `colors` and `sizes` only — no `fontFamily` primitive — so the Inter declaration moves to a CSS fallback at `docs/00/assets/likec4-typography.css` in phase 3b. **Mermaid pipeline retained**: per simplifier-driven retirement deferral, all Mermaid pipeline files (`architecture/c4/render.py`, `output/*.mmd`, `docs/00/assets/c4/*.svg`, `c4-pan-zoom.js`, `c4-svg-typography.css`, and the `mkdocs.yml` `extra_javascript`/`extra_css` entries) remain unchanged in phase 3a and continue to power chapter 00-05's `<div class="c4-diagram">` blocks. **Phase 3b's revision 8 will supersede four prior friction-point entries**: §00-06.10.3.2 (LikeC4's DSL replaces the YAML schema's `short_description`), §00-06.10.3.4 (LikeC4 ships its own verb catalog), §00-06.10.3.6 (LikeC4's web component has built-in pan/zoom; Flow's `svgPanZoom` retained but vestigial), §00-06.10.3.7 (Inter typography re-expressed via the new CSS fallback). **Runtime composition consequence**: this is ARC-100's first Node footprint. Phase 3a §7 records the integrity-test answer (LikeC4 is the C4-purpose-built renderer Python lacks; cost contained via the scoped install pattern). **POC findings**: §00-06.10.3.8 added as the LikeC4-adoption friction-point entry; §00-06.9.6 gained a paragraph noting `likec4-author` as a second instance of the post-POC "one agent, multiple skills" pattern. Chapter remains `status: draft`. |
| 2026-05-23 | Revision 8: phase 3b LikeC4 model translation + atomic Mermaid retirement. Translated `architecture/c4/arc-100-sync.model.yml` (23 elements / 29 relationships / 3 views: SystemContext / ContainerView / ConformComponent) into LikeC4 DSL at `architecture/LikeC4/arc100-sync.c4`. Each YAML element became a DSL declaration with the closed C4 vocabulary (Person→actor, SoftwareSystem→softwareSystem, Container→container, ContainerDb→containerDb [custom kind — no built-in DB-flavoured shape in LikeC4 1.57.0; default rectangular shape accepted per phase 3b Q2 simplifier adoption], Component→component); nesting respected the YAML's `parent` field (containers under `arc_100_sync`; components under `arc_100_sync.conform_py`); relationships translated to `source -> target 'verb' { description '…' technology '…' }` form. `view ConformComponent of arc_100_sync.conform_py` exercised the LikeC4 "view of element" scoping syntax that phase 3a's hello-world had not yet validated. The `architecture/LikeC4/hello-world.c4` smoke-test harness was deleted in the same step (its `actor` kind declaration would have collided with arc100-sync.c4's). **CSS fallback authored**: `docs/00/assets/likec4-typography.css` encodes the project's Inter weight schedule via LikeC4's discovered per-role data-attributes (`[data-likec4-node-title]` → 18px SemiBold 600; `[data-likec4-node-description]` → 14px Light 300; `[data-likec4-node-technology]` → 14px ExtraLight 200 Italic; `.likec4-compound-title` → Inter SemiBold; plus a `--fonts-likec4-element`/`--fonts-likec4-compound` CSS-variable override on the `<likec4-view>` host for the global font-family). Phase 3b finding: LikeC4 1.57.0 renders via React+CSS (HTML node containers via `@xyflow/react`), NOT SVG `<text>` elements as both Mermaid and the phase 3b plan template anticipated — the selector strategy resolved cleanly via the per-role `data-likec4-*` attributes once the LikeC4 bundled stylesheet was inspected. No `!important` was needed (LikeC4's cascade is well-behaved). **Atomically retired the Mermaid pipeline in the same commit**: deleted `architecture/c4/render.py`, `output/{SystemContext,ContainerView,ConformComponent}.mmd`, `docs/00/assets/c4/{SystemContext,ContainerView,ConformComponent}.svg`, `c4-pan-zoom.js`, `c4-svg-typography.css`. Removed the `extra_javascript` block (the `c4-pan-zoom.js` entry) AND the `c4-svg-typography.css` entry from `mkdocs.yml`'s `extra_css`. Also retired the dead `pymdownx.superfences custom_fences:mermaid` registration (mkdocs.yml L63-L70 reduced to bare `- pymdownx.superfences`) — phase 3b simplifier adoption, no `` ```mermaid `` fences remain anywhere under `docs/`. **Chapter 00-05 substituted**: replaced the two `<div class="c4-diagram">` blocks with `<likec4-view>` fenced code blocks (SystemContext with `browser=true` per author decision #2 for entry-point views; ContainerView with `browser=false` for inline second-tier diagrams); deleted the two `<p class="c4-diagram-hint">` paragraphs (they referenced files this revision deleted); stripped all six chapter-00-05 H3 attr-lists of `.c4-1` / `.c4-2` / `.c4-3` CSS classes, `data-c4-*` attributes, and `data-entity-ulids` lists (phase 3b simplifier adoption — grep confirmed zero CSS rules reference the `.c4-N` classes; H3s reduced to bare `{ #anchor-id }`). **Supersedes four prior friction-point entries** as Revision 7 anticipated: §00-06.10.3.2 (LikeC4's DSL replaces the YAML schema's `short_description`), §00-06.10.3.4 (LikeC4 ships its own implicit verb catalog), §00-06.10.3.6 (LikeC4's web component has built-in pan/zoom; the Flow `svgPanZoom` library is retained per user direction but now vestigial), §00-06.10.3.7 (Inter typography re-expressed via `docs/00/assets/likec4-typography.css`). **YAML retention**: `architecture/c4/arc-100-sync.model.yml` retained as the historical POC artifact this chapter §00-06.10 references (phase 3b Q3 author decision: Retain). The `render.py` + `output/*.mmd` were deleted alongside the rendered SVGs — the YAML alone is the museum piece, with the historical render path no longer reproducible from source. **install.sh FILES array bumped 10 → 11** to include `templates/agents/likec4-author.md`; phase 2b's smoke-test count assertion updated to match (3 literal-number edits in the test block + 1 in the expected-files comment). **Phase 3a deliverable retention**: the LikeC4 install (`architecture/LikeC4/`), the wrapper, `requirements.txt`, the `likec4-author` agent (both copies), the `likec4.config.json`, and the chapter-00-06 Revision 7 row are all unchanged. Chapter remains `status: draft`. |
| 2026-05-24 | Revision 9: post-phase-3b operational settings (Plan A). Eyeball pass on the chapter-00-05 LikeC4 diagrams surfaced an empirical finding the phase 3b plan had not anticipated: the inline `LikeC4View` is a static auto-fit thumbnail by default, and the React props that would enable in-place interactivity (`pannable`, `zoomable`, `controls`) are NOT reachable through the mkdocs-likec4 1.1.1 fence syntax (only `browser` / `dynamic-variant` / `project` are parsed) NOR through a raw HTML escape hatch on the `<likec4-view>` web component (its `observedAttributes` is limited to `view-id` / `browser` / `dynamic-variant` / `color-scheme`). Setting `browser=false` therefore disables the only readability escape hatch the plugin currently exposes — clicking the inline thumbnail does nothing, and any view with more than ~5 elements becomes visually unreadable. Phase 3a author decision #2 (`browser=false` default for chapter-embedded diagrams) was based on a mis-assumption about what `browser=false` did; in practice it strips the path to readability. **Standard adopted (Plan A)**: `browser=true` for every embedded view; performance-neutral vs `browser=false` (the `LikeC4Browser` modal code is in the bundle either way; only a click handler differs). Chapter 00-05's ContainerView fence flipped from `browser=false` to `browser=true` to align with SystemContext (which already had it). **Provisional refinement**: once the plugin (or LikeC4's `__app__/codegen/webcomponent.mjs` template) gains `pannable` / `zoomable` / `controls` support, prefer in-place interactivity for views with ≤5 elements and `browser=true` only for views with >5 elements. **Hosting-cost disciplines surfaced from empirical bundle measurement**: the arc-100 webcomponent bundle at `site/assets/mkdocs_likec4/likec4_views_arc-100.js` is 2.3 MB (3 views currently); the DSL source (`arc100-sync.c4`, 11 KB) is 0.46 % of the bundle — the remaining 99.5 % is the React + Mantine UI + ELK + graphviz-WASM runtime that is fixed-cost per LikeC4 project. Two advisory disciplines encoded: (i) **one LikeC4 project per documentation site, by default** — disjoint systems live as separate `.c4` files in the SAME project, sharing one workspace (splitting into multiple projects duplicates the 2.3 MB runtime per project); (ii) **per-page block budget warns at >10 `<likec4-view>` blocks on one page** — each block mounts its own Shadow DOM + React reconciler. Settings + disciplines encoded in the `likec4-author` agent body (Skill 4 — mkdocs embedding mechanics + new "Hosting-cost considerations" sub-section); the `likec4-introspection` skill gained a cross-reference paragraph pointing at the write-side standard. **POC findings**: §00-06.10.5 added as the post-phase-3b retrospective + operational-settings sub-section, covering five sub-sub-sections — why we left Mermaid (visualization quality + DSL fragmentation as root causes; §00-06.10.3.1–.3.7 cited as evidence), what survived (Inter weight schedule re-expressed; Flow `svgPanZoom` retained vestigial), the operational `browser=true` standard, the hosting-cost disciplines, and a source-of-truth table for where each operational specific lives. Chapter remains `status: draft`. |
| 2026-05-24 | Revision 10: phase 3c LikeC4 completion. Promoted chapter from `status: draft` to `status: active` — the chapter has stabilised, the friction-point catalogue (§00-06.10.3) is essentially closed, the operational settings (§00-06.10.5 from phase 3b's Revision 9) capture the production state, and the wayfinding gestures the modal supports are now documented in the new §00-06.10.6. Rewrote the front-matter `agent_summary:` scalar to reflect the active/stabilised state (dropped the prior "Intentionally exploratory" + "Not yet allocated in 00-01" phrases; preserved the agents-declare-software-emits POC callback; cross-references §00-06.10.6 and §00-06.12). Added the brief integration note above §00-06.1 recording that architectural modeling with LikeC4 is integral to ARC-100 and that the author-facing toolchain distribution is part of the planned ARC-100-SYNC distribution in phase 4 (`versions/v1/implementation/phase_4.md`, authored after this phase implements). Added §00-06.10.6 — Operating an embedded view (gesture reference: click thumbnail → modal, Ctrl-K/Cmd-K search, double-click focus mode, single-click element details, edge-label click for relationship browser, top-left chevrons for view-history navigation, Esc to close); the gestures are inherited from LikeC4's React component defaults — the discoverability gap §00-06.10.5.3 identified is now closed by canonical-reference prose. Chapter 00-06 also allocated in `docs/00/00-01_ARC-100_Standard_Inventory.md` via `arc-100-librarian` Slot-allocation dispatch (D5 of phase 3c; the chapter is now a registered ARC-100 standard chapter under book 00). No edits to any other docs/00 chapter; no DSL changes; no asset additions. A new top-level **Architectural Model** page (`docs/architectural-model.md`) was authored in this phase as the entry-point view surface (D1; redesigned mid-implementation from the initial hook-extension approach per user direction — the master-index and the architectural-model surfaces are conceptually distinct and should not share a page); `mkdocs.yml` gained an explicit `nav:` block (constructed by `_hooks/arc100_master_index.py:_build_nav`) with two top-level entries (Master Index + Architectural Model) plus a `not_in_nav` glob silencing the chapter-file orphan-warnings the explicit-nav omission would otherwise surface. Chapter pages remain built and link-reachable; readers reach them via the Master Index tree. |
| 2026-05-26 | Revision 11: phase 3.1d per-tree LikeC4 toolchain split. The repo-root singleton `architecture/LikeC4/` is removed; the ARC-100 Standard's install now lives at `master-vault/likec4/` and the ARC-100 Project's install at `docs/likec4/`. Each tree carries its own `package.json` + `package-lock.json` + `bin/likec4` wrapper. Per-tree discovery configs (`master-vault/docs/00/model/likec4.config.json` with `name: arc-100` and `docs/01/model/likec4.config.json` with `name: arc-100-project`) keep the workspace scans isolated. The repo-root `architecture/c4/` POC folder (including `arc-100-sync.model.yml`) is dropped wholesale; git history at commit `bc0dab6` preserves the YAML. Source-of-truth table at §00-06.10.5.5 rewritten; chapter prose citations swept per phase_3.1d.md §6.6. The green-site `mkdocs.arc100project.yml` gained an `exclude_docs: likec4/` directive (the project-tree install sits inside `docs_dir` because the green site's tree root IS `docs/`; without the exclusion, mkdocs would scan `docs/likec4/node_modules/**/README.md` and surface strict-mode anchor warnings). Both `mkdocs build --strict` runs pass. Chapter remains `status: active`. |
| 2026-06-28 | Revision 12: phase 5 — likec4-author delivery-base wording de-siloed + corrected. §00-06.9.6 prose and the §00-06.10.5.5 source-of-truth table row both stated the canonical template was "distributed to downstream `<PROJECT>-100` projects via `install.sh`" — but `install.sh` is retired (the live tool is `arc_sync.py`) and the delivery base is now the project's **main** `.claude/agents/` (the project root via `arc_sync.py --claude-target`), not the `<PROJECT>-100/` instance silo. Both repointed to "delivered mirror-class by `arc_sync.py` to a downstream project's main `.claude/agents/` (project root, not the instance)". Prose-only; no section renumbered, no anchor/citation moved, no `00-01` change. See `versions/v2/implementation/phase_5.md` (D6). Chapter remains `status: active`. |
