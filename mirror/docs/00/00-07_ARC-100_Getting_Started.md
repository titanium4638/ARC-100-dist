---
title: 00-07 ARC-100 Getting Started
arc_100_id: "00-07"
status: active
keywords: [getting-started, clone, onboarding, adopt, downstream, sync, likec4, agents]
agent_summary: |
  The single a-priori onboarding chapter for adopting ARC-100 in a
  project. Covers what ARC-100 and a `<PROJECT>-100` instance are, how to
  clone the public ARC-100 mirror and run the name-first onboarding script
  (prerequisites, the depth-1 clone, `RUN_FIRST.sh <NAME>` — which creates
  the named `<NAME>-100/` instance folder and runs
  `arc_sync.py --target <NAME>-100`), the first sync and keeping
  the standard current, where a project's own books and chapters go, the
  two Claude Code agents (arc-100-librarian, likec4-author), removal, and
  troubleshooting. It is deliberately concise: the depth lives in the
  chapters it links to (00-00 numbering/lifecycle, 00-05 synchronization,
  00-06 architectural modeling), which a reader of the rendered site can
  open directly.
prerequisites: ["00-00_ARC-100_General.md"]
companions: ["00-05_ARC-100_Synchronization.md", "00-06_ARC-100_Architectural_Modeling.md"]
---

## 00-07 ARC-100 Getting Started

> **What this chapter is.** The one place to start when you want to give
> some *other* software project a well-organized, machine-indexable
> documentation tree using ARC-100. No prior ARC-100 experience is
> assumed. By the end you will have cloned the public ARC-100 mirror, run
> your first sync, resolved any index decisions it raised, and learned
> where your own docs go and which agents write them.
>
> **What this chapter is not.** A deep reference. It states the essentials
> and links to the chapters that own the detail —
> [00-00 General](00-00_ARC-100_General.md) (numbering, bands, lifecycle,
> hard rules), [00-05 Synchronization](00-05_ARC-100_Synchronization.md)
> (the sync-and-rectify model), and
> [00-06 Architectural Modeling](00-06_ARC-100_Architectural_Modeling.md)
> (LikeC4). Open those for anything this chapter summarises.

### 00-07.1 — What ARC-100 is, and what a `<PROJECT>-100` is

**ARC-100** is two things working together:

1. **A documentation-indexing standard** — a fixed, numbered chapter
   scheme (books and chapters grouped into seven topic *bands*), a
   machine-parseable master index, an immutable-ULID identity model, and
   conventions for embedding C4 architecture diagrams. The standard ships
   as the "Book 00" chapters (`00-00`…`00-07`). See
   [00-00 General](00-00_ARC-100_General.md) for the full specification
   and [00-02 Glossary](00-02_ARC-100_Glossary.md) for vocabulary.
2. **A sync toolkit (ARC-100-SYNC)** — published as a **public git mirror**
   you clone, carrying the sync tool (`tools/arc_sync.py`), the Book 00
   content, the Claude Code agent and slash-command templates, and a
   LikeC4 modeling toolchain. Running it lands the standard in your repo
   and keeps it in step with upstream as the standard evolves
   ([00-05 Synchronization](00-05_ARC-100_Synchronization.md)).

When you adopt ARC-100 you create **your project's own instance**, named
`<PROJECT>-100` — e.g. `FLOW-100`, `CS-100`, `ACME-100`. Your instance
*inherits* the Book 00 chapters verbatim (kept fresh by the sync tool) and
*adds* your own books and chapters in the slots the standard reserves for
you (§00-07.5). The onboarding script (§00-07.2) builds that instance in a
folder **named for it** — `<PROJECT>-100/` — so the `docs/00/`, `docs/01/`,
`.arc100/`, and `.claude/` paths in the table below are all rooted at that
folder, not at a bare repo root.

ARC-100 keeps **two indexes**, and the distinction matters from day one
(00-00 §00-00.10.1):

| Thing | Where it lands | Who owns it |
| --- | --- | --- |
| The Book 00 standard chapters | `docs/00/00-00…00-07_*.md` | Upstream (synced; do not hand-edit) |
| The mirrored ARC-100 index | `docs/00/00-01_ARC-100_Standard_Inventory.md` | Upstream (synced read-only reference, like every Book 00 chapter) |
| Your **working index** (chapter 01-01) | `docs/01/01-01_<PROJECT>-100_Index.md` | The librarian agent only — your single mkdocs site renders from this |
| Your project chapters | `docs/01/`, `docs/02/`, `docs/10/`, … | You |
| LikeC4 architecture model | `architecture/LikeC4/<project>.c4` | You (via `likec4-author`) |
| The two agents + two slash commands | `.claude/agents/`, `.claude/commands/` | Delivered by the sync |

> **Whose rule is "do not hand-edit"?** This table describes *your*
> downstream `<PROJECT>-100`: there, Book 00 — including the mirrored
> ARC-100 index at `docs/00/00-01_…` — is a synced, **read-only mirror**,
> so the sync tool, not you, maintains it. Your own **working index** at
> `docs/01/01-01_…` is the one the librarian curates. Inside the ARC-100
> standard's *own* repository, Book 00 is the source of record and is
> authored directly. See the hard rule in 00-00 §00-00.11.

### 00-07.2 — Clone the mirror and run the onboarding script

**Prerequisites.**

- **`git`** and **Python 3.10+** (the sync tool, the ULID generator, and
  mkdocs all run on Python). The tool itself needs only the Python
  standard library plus PyYAML.
- **Node** and the **LikeC4 toolchain** are *not* bootstrap prerequisites
  — they are needed only if you author an architecture model, and the
  doctor (below) checks for them and prints the command to install them.

**Clone and run** (from the directory that should *hold* your instance — a
parent folder; the script creates the named instance folder under it):

```bash
CLONE="$(mktemp -d)"
git clone --depth 1 https://github.com/arc-100-standard/ARC-100-dist.git "$CLONE"
bash "$CLONE/RUN_FIRST.sh" ACME
rm -rf "$CLONE"
```

`mktemp -d` makes a fresh throwaway directory and the trailing `rm -rf`
discards the clone once it has run — so the block is safe to re-run (it never
trips over a leftover) and leaves nothing behind. The clone is only a
delivery vehicle; nothing of yours lives in it.

`RUN_FIRST.sh` is **name-first onboarding**: the one input it needs is your
system's name — passed as the single argument, or prompted for
interactively if you omit it. From that one input it does everything else
in a single pass:

1. **Normalises the name to `<NAME>-100`** (`ACME` → `ACME-100`; a trailing
   `-100`, `100`, or `_100` you type is folded, never doubled).
2. **Creates the `<NAME>-100/` folder** in the current directory. Your
   instance is *proudly called what it is* — `ACME-100/` — not an anonymous
   `docs/` tree at a repo root.
3. **Writes the config for you** — `<NAME>-100/ARC-100-SYNC.config.yml`
   with `project_name` already set, plus `<NAME>-100/config.json`, a
   readable name asset (`{"documentation_system_name": "<NAME>-100"}`) your
   own scripts and agents can read.
4. **Runs `arc_sync.py --target <NAME>-100`** — the bootstrap that delivers
   Book 00, seeds your chapter 01-01 working index, and lands the agents
   and the ULID minter (§00-07.3).
5. **Substitutes the residual `<PROJECT>` seed tokens** in the just-seeded
   files, so **no placeholder is left to hand-fix**: the rendered home
   title, the working-index filename, the on-disk `<NAME>-100-INDEX-*`
   markers, and the LikeC4 project id are all correct from the first build.

The clone is a throwaway delivery vehicle, not part of your instance.
`RUN_FIRST.sh` **owns** `--target` and `--config` — it manages the
`<NAME>-100/` folder and the config inside it, so passing either is refused
(exit `2`); only `--source` (defaulted to the clone root) and `--dry-run`
pass through to `arc_sync.py`.

> **You no longer hand-author the config.** `RUN_FIRST.sh` writes
> `ARC-100-SYNC.config.yml` with `project_name` set. `project_name` is the
> only required key — a single path segment (letters, digits, `._-`; no
> `/`, no whitespace, no leading dot), because it fuses into your derived
> index filename; `RUN_FIRST.sh` validates the name to exactly that shape
> before creating anything. `local_index_path` is **optional** and
> convention-derives to `docs/01/01-01_<project_name>_Index.md`; edit the
> generated config to override it only if you must.

**The exit-code contract.** `RUN_FIRST.sh` surfaces `arc_sync.py`'s exit
code: `0` (success — bootstrap done), `1` (human action required — it wrote
`.arc100/PENDING-INDEX-DECISIONS.yml`; see §00-07.4), or `2` (error — a
bad name, bad config or payload, or a path-containment violation; the
stderr text says which). The tool does no network work of its own, so exit
`2` is never a network failure.

> **You are running upstream code.** Cloning and running `RUN_FIRST.sh` (and
> the `arc_sync.py` it calls) means executing upstream-delivered code on
> your machine — a sync tool that writes your files has to run somewhere.
> Both are auditable scripts (the sync tool is a single Python file —
> standard library + PyYAML, no network); read them in the clone before you
> run them if you want to. Integrity rests on the public mirror, the
> immutable `vN` index tags, and an out-of-band digest in each release's
> notes. See [00-05 §00-05.11](00-05_ARC-100_Synchronization.md) for the
> full posture.

### 00-07.3 — After the sync: what landed, and what you finish

The onboarding script delivers most of the setup for you, all inside your
`<NAME>-100/` instance folder. Files split into two classes
([00-05 §00-05.5](00-05_ARC-100_Synchronization.md)):

- **Mirror-class — delivered automatically, do not hand-edit.** The Book
  00 chapters and the mirrored ARC-100 index land under
  `<NAME>-100/docs/00/`; the master-index hook at
  `<NAME>-100/_hooks/arc100_master_index.py`; the home-page assets, Inter
  fonts, and the ULID minter (`assets/arc100/tools/ulid.py`) under
  `<NAME>-100/assets/arc100/`; the two agents and two slash commands under
  `<NAME>-100/.claude/`. A re-sync refreshes these; a local edit is backed
  up to `.arc100/backups/` before being overwritten.
- **Seed-class — delivered copy-if-absent, then yours to edit.** These are
  written only if not already present, so your edits survive a re-sync —
  and `RUN_FIRST.sh` has already substituted the name-dependent `<PROJECT>`
  tokens in them, so **no placeholder is left to fix**:
  1. **Sync config** — `ARC-100-SYNC.config.yml`, written for you with
     `project_name` set (§00-07.2).
  2. **Site config** — `mkdocs.yml`, already carrying your name
     (`site_name: <NAME>-100`; the home renders as `"<NAME>-100 Index"`);
     the only edit left is tuning the `not_in_nav` globs to your book
     numbers.
  3. **Standalone Architectural-Model page** — its `<NAME>-100` title and
     `project=<slug>` fence argument are filled in already (relevant only
     if you author a model).
  4. **LikeC4 placeholders** — the `name` field in
     `architecture/LikeC4/package.json` and
     `docs/00/model/likec4.config.json` is already your project slug; if
     you author a model, just verify with
     `architecture/LikeC4/bin/likec4 --version` and `… validate`
     (§00-07.6).

**Python deps.** `requirements.txt` is seeded; the **doctor** prints the
exact command after each sync — run what it printed:
`python3 -m pip install --user --require-hashes -r requirements.txt` (the
`--require-hashes` flag is non-negotiable). The doctor never runs pip for
you; a missing Node or LikeC4 toolchain is likewise a printed suggestion,
never a gate ([00-05 §00-05.8.1](00-05_ARC-100_Synchronization.md)).

**Preview your site.** Once the build deps are installed, serve or build the
site with `-f` pointed at the instance config (run from the folder's
parent). `RUN_FIRST.sh` prints this exact command on completion with your
name and a free port already filled in:

```bash
mkdocs serve -f <NAME>-100/mkdocs.yml --livereload --dev-addr localhost:<PORT> -o
mkdocs build -f <NAME>-100/mkdocs.yml      # static site -> <NAME>-100/site-<NAME>-100/
```

The **`-o`** opens the rendered site in your default browser once the build
finishes (drop it to skip). `--livereload` rebuilds on every save. Your home
page is the **generated index** (titled `<NAME>-100 Index`), which links to
every chapter — the site has no hand-maintained sidebar, so the `mkdocs`
"pages … not included in the nav configuration" notes are **expected, not
errors**. (For a CI gate use `mkdocs build --strict`, which turns warnings
into failures; a fresh instance is strict-clean apart from the inherited
Book 00 architecture views, whose `project=arc-100` LikeC4 diagrams resolve
only on the standard's own site — see
[00-06](00-06_ARC-100_Architectural_Modeling.md).)

### 00-07.4 — First sync, and keeping ARC-100 updated

Your **first** run is `RUN_FIRST.sh` (§00-07.2) — it builds and bootstraps
the `<NAME>-100/` instance. After that, keep current with `/sync-arc-100`
**run from inside your `<NAME>-100/` folder** (it wraps the clone + the
`arc_sync.py --target .` call, where `--target .` is the instance root);
re-syncs do not go back through `RUN_FIRST.sh`, which is first-run only. The
tool auto-detects its mode:

- **Bootstrap** (no `.arc100/state.yml` yet, index unseeded): seeds your
  working index from the upstream entries, records the `BASE` snapshot,
  and exits `0` — no decisions.
- **Refresh** (`.arc100/state.yml` present): syncs the payload and folds
  the upstream index into your working index by a 3-way ULID reconcile
  (so a renumber reads as a move, not a delete-plus-add), auto-applying
  the safe changes and escalating the judgment-bound ones.

**Exit codes:** `0` clean · `1` index decisions pending · `2` hard error.
On **`1`**, the tool wrote `.arc100/PENDING-INDEX-DECISIONS.yml` and
applied **nothing**. Fill in each block's `decision:` (`accept` or
`reject`) — the **arc-100-librarian** can do this for you via
`/resolve-arc-100-issues` (§00-07.6) — then **re-run the sync**: the
answered decisions apply on that next run, which also archives the
decision file. There is no separate command that "applies" the decisions;
re-running the sync is the applier. The classification tables and the
reconcile contract live in
[00-05 §00-05.4](00-05_ARC-100_Synchronization.md)–[§00-05.5](00-05_ARC-100_Synchronization.md);
the banner and resolution flow are in
[§00-05.6](00-05_ARC-100_Synchronization.md).

**Keeping current.** There is no installer to re-run — re-clone the mirror
and run the sync again (or just `/sync-arc-100`). Content updates arrive
continuously: every upstream `main` commit republishes chapter bodies,
tooling, and descriptions, while the ARC-100 **index version** (`vN`)
changes only when chapters are added or removed upstream — the two-axis
model in [00-05 §00-05.9](00-05_ARC-100_Synchronization.md). Discipline:

- Mirror-class files (`docs/00/`, `_hooks/`, `assets/arc100/`) are
  upstream-owned; a re-sync refreshes them. If you hand-edited one, the
  tool backs your copy up to `.arc100/backups/<stamp>/` before
  overwriting, and reports it — it never clobbers silently.
- Seed-class files you own (`ARC-100-SYNC.config.yml`, `mkdocs.yml`, the
  Architectural-Model page, the LikeC4 placeholders) are written only if
  absent, so a re-sync leaves your edits intact.
- Your working index at `docs/01/01-01_<PROJECT>-100_Index.md` is
  reconciled, never blindly overwritten; project-authored entries
  (`arc_100: false`) are off-limits to the sync entirely.

### 00-07.5 — Where your `<PROJECT>-100` documentation goes

Files follow `<book>-<chapter>_<title>.md` with two-digit zero-padded
numbers (e.g. `40-50_Architecture_Reference.md`); section headings inside
a chapter follow `### BB-CC.N — Title`; cite other chapters as
`[BB-CC §N]`. Every book number falls into one of seven bands
(Application, Governance, Client, Server, Data, Tooling, Operations) —
the band table and the four structural rules are in
[00-00 §00-00.7](00-00_ARC-100_General.md).

The two rules you will use constantly:

- **Chapters in an inherited (`arc_100: true`) book:** ARC-100 uses slots
  01–49; **you allocate from 50 upward.**
- **New project books in a band:** ARC-100 allocates from the low end;
  **you allocate from the high end and work downward** (99, 98, …). This
  minimises rebase collisions when the standard adds a book.

Each index entry carries an immutable `arc_100_ulid` (the join key the
sync tool matches on — never invent or edit one by hand) and a
`status` (`placeholder` → `draft` → `active` → `superseded`/`deprecated`).
Only the librarian (§00-07.6) writes the index or changes status. Your
**working index** is chapter **01-01** at
`docs/01/01-01_<PROJECT>-100_Index.md` — Book 01 is your project's own
book, and your single site renders from this index, never from the
mirrored ARC-100 inventory at `docs/00/00-01_…`. By convention the
librarian titles that first own book **"`<NAME>-100 System`"** (e.g.
"`CS-100 System`") when it allocates it — mirroring the standard's own
Book 00 = "ARC-100 System".

You do not migrate everything at once: bootstrap ARC-100 alongside your
existing tree and bulk-migrate legacy docs as a single planned operation at
version closeout ([00-00 §00-00.10](00-00_ARC-100_General.md)). When the
bootstrap lands a mirror-class file on top of a pre-existing one, the tool
moves the colliding copy aside to `.arc100/backups/<stamp>/` before
writing — it never clobbers silently. Migration itself is the manual
librarian loop in §00-07.6 — place each existing doc as a chapter, author
its body, re-sync — done incrementally, at your own pace.

### 00-07.6 — The two agents

ARC-100 ships two Claude Code agents you drive by asking questions; they
do the disciplined parts so you do not memorise the rules.

- **`arc-100-librarian` — the only writer of the index.** It does
  chapter-identity rulings, slot allocation, ULID minting, schema sweeps,
  and filling in queued sync decisions — it sets each block's `decision:`
  (`accept`/`reject`) in `.arc100/PENDING-INDEX-DECISIONS.yml`; the next
  `arc_sync.py` run applies them. You never invent a chapter
  number; you ask the librarian ("Where does concept X belong?" /
  "Allocate the next chapter in band 40") and it commits the entry. It
  emits one of three ruling shapes (`existing_chapter`, `new_chapter`,
  `new_book` — the last is a halt for human review) and never allocates a
  new book autonomously, edits chapter content, renames an `arc_100: true`
  chapter, or mutates a ULID by hand.
- **`likec4-author` — the architecture model.** It authors the LikeC4 DSL
  model, defines views, applies theme/styling, and produces the
  `likec4-view` fences you embed in chapters. The element vocabulary, view
  taxonomy, theming, embedding mechanics, hosting-cost disciplines, and a
  full worked example are in
  [00-06 Architectural Modeling](00-06_ARC-100_Architectural_Modeling.md).

The migration loop ties them together: ask the librarian to place an
existing doc as a chapter → author the chapter body → ask `likec4-author`
to model the system and embed per-chapter views → `mkdocs build --strict`
→ `/sync-arc-100` (`tools/arc_sync.py --target .`) keeps the inherited
standard fresh over time.

### 00-07.7 — Removing the synced ARC-100 footprint

There is no `ARC-100-SYNC/` tree to delete — the onboarding script ran from
a throwaway clone. To peel the synced ARC-100 footprint out of your instance
while keeping your own books and chapters, run these **from inside your
`<NAME>-100/` folder** (the paths are instance-relative):

```bash
rm -rf .arc100/                              # per-project sync state + backups
rm ARC-100-SYNC.config.yml config.json       # the generated config + name asset
rm docs/00/00-*.md                           # the synced Book 00 chapters + mirrored index
rm _hooks/arc100_master_index.py             # the master-index hook
rm -rf assets/arc100/                        # home-page assets + fonts + the ULID minter
rm .claude/agents/arc-100-librarian.md .claude/agents/likec4-author.md \
   .claude/commands/sync-arc-100.md .claude/commands/resolve-arc-100-issues.md   # if present
```

Then drop the hook line and the `arc100`/font references from `mkdocs.yml`.
Your own books and chapters (Book 01 and up), your working index, and your
project files are untouched. (To discard the instance entirely, just
`rm -rf <NAME>-100/`.)

### 00-07.8 — Troubleshooting

- **The clone failed.** The only network step is the `git clone` of the
  mirror; re-run it. The sync tool itself does no network work, so a tool
  error (exit `2`) is never a network failure — read its stderr for the
  real cause (bad config, malformed payload, a path-containment violation).
- **Name shape error** — your system name must be a single path segment
  (letters, digits, `._-`; no `/`, whitespace, or leading dot) because it
  fuses into the derived index filename and the on-disk `<NAME>-100-INDEX`
  markers. `RUN_FIRST.sh` validates the name to exactly that shape **before
  creating anything** (a bad name exits `2` and leaves no folder behind),
  and `arc_sync.py` re-gates the same value. `RUN_FIRST.sh` also sets
  `mkdocs.yml`'s `site_name` to match, so the rendered home is labelled
  consistently (the master-index hook titles the home from `project_name`).
- **Malformed upstream rows** (HTML, control bytes, fields over
  `FIELD_MAX_CHARS`) are refused at the boundary and escalated under
  `malformed_upstream` — they never auto-apply
  ([§00-05.5](00-05_ARC-100_Synchronization.md)).
- **Banner renders as raw `##` text** — the banner `<div>` needs
  `markdown="1"` for Python-Markdown's `md_in_html`
  ([§00-05.6](00-05_ARC-100_Synchronization.md)).

### 00-07.9 — Pointers

- [00-00 General](00-00_ARC-100_General.md) — numbering, the band table,
  status lifecycle, ULID/lineage rules, and the §00-00.11 hard rules.
- [00-03 Documentation Site](00-03_ARC-100_Documentation_Site.md) — the
  mkdocs rendering layer and theme conventions.
- [00-05 Synchronization](00-05_ARC-100_Synchronization.md) — the
  sync-and-rectify model, the three modes, classifications, and the
  mirror-clone security posture.
- [00-06 Architectural Modeling](00-06_ARC-100_Architectural_Modeling.md)
  — LikeC4 conventions, the view taxonomy, embedding, and the Inter
  typography schedule.
- [Architectural Model](architectural-model.md) — the interactive C4
  SystemContext view of ARC-100-SYNC.

### 00-07.10 — Current limitations

- **Cross-platform by construction.** There is no installer and no
  platform gate: the tool is plain Python 3.10+ and runs anywhere Python
  and git do. (Node, needed only for LikeC4 authoring, is the doctor's
  concern, not a bootstrap blocker.)
- **Diagram fonts fall back outside the standard's CSS.** LikeC4 1.57.0
  has no font-family theme primitive, so the Inter weight schedule is a
  CSS override; environments that do not load
  `docs/00/assets/likec4-typography.css` see the default font.
- **A couple of setup steps stay manual** — `RUN_FIRST.sh` now writes the
  config and substitutes every seeded `<PROJECT>` placeholder, so what
  remains is tuning `mkdocs.yml`'s `not_in_nav` globs to your book numbers
  and running the exact commands the doctor printed (`pip`, optionally
  `npm ci`). These are one-time human decisions, not automation.

### 00-07.11 — Dogfooding ARC-100 itself (INTARC-100)

> **For maintainers of the ARC-100 standard, not adopters.** This section
> exercises the onboarding flow above against ARC-100's own tree, standing
> up an instance named **INTARC-100**. A downstream adopter never runs
> `release.sh` — it is ARC-100-internal tooling, not shipped in the payload
> — and follows §00-07.2 against the public mirror instead.

ARC-100 dogfoods its own install by running `RUN_FIRST.sh` exactly as an
adopter would, but against a **locally-assembled payload** rather than the
public mirror, so the standup is verifiable before — or independent of —
any publish. From the ARC-100 repo root:

```bash
out="$(bash ARC-100-SYNC/scripts/release.sh --keep-staging)"          # assemble a local payload
staging="$(printf '%s\n' "$out" | sed -n 's/.*Staging kept: //p')/payload"
bash "$staging/RUN_FIRST.sh" INTARC                                   # creates ./INTARC-100/
```

`RUN_FIRST.sh` creates `INTARC-100/` in the current directory (so run it
from wherever the instance should land — the repo root puts it parallel to
the green `docs/` tree). In one pass it writes
`INTARC-100/{ARC-100-SYNC.config.yml, config.json}`, runs
`arc_sync.py --source "$staging" --target INTARC-100` (`RUN_FIRST.sh`
defaults `--source` to its own directory, so passing it is optional), and
substitutes the seed `<PROJECT>` tokens. The result is a fully-named,
empty instance:

```text
INTARC-100/
├── docs/00/                              # Book 00 (8 chapters) + mirrored index
├── docs/01/01-01_INTARC-100_Index.md     # working index, INTARC-100-INDEX-* markers
├── .arc100/state.yml                     # sync state
├── .claude/{agents,commands}/            # the two agents + two slash commands
├── assets/arc100/…                       # home-page assets, fonts, tools/ulid.py
├── config.json                           # {"documentation_system_name": "INTARC-100"}
└── mkdocs.yml                            # site_name: INTARC-100, no residual <PROJECT>
```

Pass **only the name** — `RUN_FIRST.sh` manages `--target` and `--config`
(passing either exits `2`). INTARC-100 is a *separate, parallel* instance;
migrating the existing green `docs/` content into it is the dogfood
activity that follows — the manual librarian loop (§00-07.6), done by hand
at your own pace — not part of standing the instance up.

## Revisions

| Date | Change |
| --- | --- |
| 2026-05-30 | Initial creation. Consolidates the two previously-fragmented a-priori onboarding documents — the standalone `website/GETTING_STARTED.md` and the offline `ARC-100-SYNC/docs/README.md` — into a single Book 00 chapter that renders on the ARC-100 site and links to 00-00 / 00-05 / 00-06 for depth rather than duplicating them. Folds in the Removal and Troubleshooting material that previously lived only in `ARC-100-SYNC/docs/README.md`. Allocated at 00-07 via the `arc-100-librarian`; distributed to downstreams as part of Book 00. |
| 2026-06-01 | Revision 2: phase 6b threat-modeler hardening. Hardened both documented bootstrap one-liners in §00-07.2 (Option A pinned-version + Option B latest) from a bare `curl -sSL` to `curl -sSL --fail --proto '=https' --tlsv1.2 --max-redirs 2` — matching `install.sh`'s already-pinned internal per-file fetches (TM-2b-2) and its L5 usage comment. Closes a protocol-downgrade / off-host-redirect gap on the *outer* bootstrap fetch, and lets the phase-6b published-install gate (`test_publish.sh`) exercise the EXACT flag string real adopters run (the "gate tests the real path" requirement). Distributed `templates/book-00/00-07` twin updated byte-identically. No change to install behaviour or chapter content. See `versions/v1/implementation/phase_6b.md`. |
| 2026-06-01 | Revision 3: clarified the context-based switch on the "do not hand-edit Book 00" directive (user direction). Added a note after the §00-07 ownership table making explicit that the table — and its "do not hand-edit" guidance — describes a *downstream* `<PROJECT>-100`, where Book 00 is a synced read-only mirror the conform engine maintains; inside the ARC-100 standard's *own* repository Book 00 is the source of record and is authored directly. Cross-references the canonical hard rule newly added to 00-00 §00-00.11. No install-behaviour or numbering change. Distributed twin updated byte-identically. |
| 2026-06-01 | Revision 4: phase 7 authenticated private-repo install. Split §00-07.2 into §00-07.2.1 — Install from a public repository (the existing Option A/B `raw.githubusercontent.com` commands, with a prominent note that `titanium4638/ARC-100` is NOT yet public, so those 404 against the canonical upstream) and §00-07.2.2 — Install from a private repository (the authenticated path that resolves today: `GH_TOKEN=$(gh auth token)`, `api.github.com` Contents API, Bearer token via a `curl -K` stdin config so the token never touches argv/disk, `--max-redirs 0` so a redirect cannot carry the auth header off-host, the collaborator/Team/fine-grained-PAT/deploy-key access-grant model, and a `gh api` convenience). The *same* `install.sh` auto-selects authenticated vs public by token presence — no second installer. No numbering change to existing sections (anchors preserved); two new `BB-CC.N.M` subsections added. Distributed `templates/book-00/00-07` twin updated byte-identically. See `versions/v1/implementation/phase_7.md`. |
| 2026-06-14 | Revision 5: phase 3d — clone-and-run onboarding rewrite. Replaced the curl-installer onboarding with the clone-and-run model: §00-07.2 is now "clone the public mirror `titanium4638/ARC-100-dist` at depth 1 and run `python3 <clone>/tools/arc_sync.py --target .`" — the public/private curl one-liners, the entire token-auth block (former §00-07.2.1 / .2.2), the "what a version pins" prose, and the installer's-role table are deleted; the "you are running upstream code" expectation is stated (P1 §9). §00-07.3 collapses the nine manual `cp` steps into the mirror-class (auto-delivered) vs seed-class (copy-if-absent, then yours) file-class split, with the doctor printing the exact `pip --require-hashes` command; the sync-check-hook step is deleted (hook retired in 3a). §00-07.1 teaches the two-index model (mirrored ARC-100 index read-only at `docs/00/00-01_…`; the project's working index is chapter 01-01 at `docs/01/01-01_<P>_Index.md`, librarian-curated, the single site's render source) and drops the `ARC-100-SYNC/`-tree row. §00-07.4 rewrites first-sync / keeping-current to the 0/1/2 exit contract with apply-on-next-run (fill `.arc100/PENDING-INDEX-DECISIONS.yml` `decision:`, re-run to apply — no separate resolve command applies) and the two-axis update story; §00-07.7 retitled "Removing the synced ARC-100 footprint" (delete `.arc100/` + seeded config + synced Book 00 + hook + assets + `.claude/` if present; no `ARC-100-SYNC/` tree); §00-07.8 drops the sync-check-log bullet and pins the `project_name` shape gate to `arc_sync.py` (the tool no longer validates `site_name`); §00-07.10 drops the macOS-only / installer-exit-2 limitation. `/conform-to-arc-100` → `/sync-arc-100` throughout; the `FIELD_MAX_CHARS` correction; convention-derived index path. No section renumbered (the two `####` token-mode leaves removed shift no top-level number). See `versions/v2/implementation/phase_3d.md`. |
| 2026-06-14 | Revision 6: phase 4b — name-first onboarding via `RUN_FIRST.sh` + the `<NAME>-100/` container. §00-07.2 is now "clone the public mirror, then `bash <clone>/RUN_FIRST.sh <NAME>`": the script captures the system name, normalises it to `<NAME>-100`, creates the **`<NAME>-100/` instance folder**, writes its `ARC-100-SYNC.config.yml` (`project_name` set) + `config.json` name asset, runs `arc_sync.py --target <NAME>-100`, and substitutes the seed `<PROJECT>` tokens — so no placeholder is left to hand-fix (the former manual "Configure once" config-authoring and `<PROJECT>`-placeholder edits are gone). This amends the 2026-06-11 adopter convention: the general install `--target` moves from `.` (repo-root `docs/`) to a named `<NAME>-100/` container (author directive 2026-06-14, "proudly called what it is"); the charter-frozen *internal* layout is preserved (`docs/01/01-01_<P>_Index.md`, `local_chapter_root: docs`) — only the container moves. §00-07.1 notes the instance paths are rooted at `<NAME>-100/`; §00-07.3 file classes shift under `<NAME>-100/`, fold in the now-mirror-class `.claude/` agents+commands and `assets/arc100/tools/ulid.py`, and state the seed files arrive token-substituted; §00-07.4 makes `RUN_FIRST.sh` the first run and `/sync-arc-100`-from-inside-`<NAME>-100/` the re-sync; §00-07.5 adds the book-01 = "`<NAME>-100 System`" naming convention (mirroring Book 00 = "ARC-100 System") + the `.arc100/backups/` collision behavior + the P5 migration-toolkit pointer; §00-07.7 removal runs from inside `<NAME>-100/` and adds `config.json`; §00-07.8 repoints the name-shape gate to `RUN_FIRST.sh`; §00-07.10 trims the "manual setup" limitation. New trailing §00-07.11 — "Dogfooding ARC-100 itself (INTARC-100)" — the maintainer runbook (`release.sh --keep-staging` → `RUN_FIRST.sh INTARC` against the local staging payload). No existing section renumbered (00-07.11 is a purely additive trailing section). See `versions/v2/implementation/phase_4b.md`. |
| 2026-06-15 | Revision 7: removed the "forthcoming P5" framing (author direction — the v2 campaign closes at four phases; there is no P5). §00-07.5 no longer promises a discovery-and-migration toolkit as future-phase work — migration is simply the manual librarian loop (§00-07.6), done incrementally; §00-07.11 reframes green-content migration as the dogfood *activity* performed by hand with the working installer, not a future phase. Prose-only; no section renumbered. Pairs with the `RUN_FIRST.sh` fail-fast + rollback hardening (so running it outside a payload errors cleanly instead of half-building) and the mirror republish that makes §00-07.2's clone-and-run flow live. |
| 2026-06-15 | Revision 8: added a "Preview your site" block to §00-07.3 (dogfood finding — the chapter described install + sync but never said how to actually *run* the site). Documents `mkdocs serve -f <NAME>-100/mkdocs.yml --livereload --dev-addr localhost:<PORT> -o` (and `mkdocs build -f …`), run from the folder's parent — `-o` opens the browser on serve, and `RUN_FIRST.sh` now prints this exact command on completion with the name and a scanned free port pre-filled. Explains the home is the generated index (no hand-maintained sidebar, so the "not included in nav" notes are expected) and that `--strict` is a CI gate (a fresh instance is strict-clean apart from the inherited Book 00 `project=arc-100` LikeC4 views). Prose-only; no section renumbered. (Pairs with `RUN_FIRST.sh` now filling the Book 01 placeholder title "`<NAME> System`" → "`<NAME>-100 System`", refresh-safe since Book 01 syncs slot identity only.) |
| 2026-06-15 | Revision 9: repointed the §00-07.2 clone command to the **`arc-100-standard/ARC-100-dist`** mirror (the dist repo was transferred into a new GitHub org for a project-neutral owner; the old URL redirects, but the canonical command should name the new owner). URL only; no section renumbered. |
| 2026-06-16 | Revision 10: made the §00-07.2 clone idempotent + self-cleaning. The throwaway clone now goes into a fresh `mktemp -d` directory and is `rm -rf`'d after, instead of the fixed `${TMPDIR:-/tmp}/ARC-100-dist` path. The fixed path collided on re-run (`destination path … already exists and is not an empty directory`), which silently broke the re-clone-to-re-sync flow; the ephemeral dir is unique per run, auto-discarded, and never clutters the adopter's tree. Added a one-line note explaining the `mktemp`/`rm -rf` pattern. Command + note only; no section renumbered. |
