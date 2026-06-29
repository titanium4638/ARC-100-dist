---
title: 00-07 ARC-100 Getting Started
arc_100_id: "00-07"
status: active
keywords: [getting-started, clone, onboarding, adopt, downstream, sync, likec4, agents]
agent_summary: |
  The concise getting-started chapter for adopting ARC-100: clone the public
  mirror, run RUN_FIRST.sh to stand up a named <NAME>-100/ instance, install
  deps, preview the site, and keep it current with the on-demand /sync-arc-100.
  Also covers where your own books/chapters go, the two Claude Code agents,
  removal, troubleshooting, and current limitations. Deliberately thin — it
  links the depth to 00-00 (numbering, bands, lifecycle, hard rules), 00-05 (the
  sync model), and 00-06 (LikeC4) rather than restating them. Open your project
  root as your editor/Claude Code workspace; the arc-100 agents and /sync-arc-100
  install to the project's main .claude/ and work across the whole project.
prerequisites: ["00-00_ARC-100_General.md"]
companions: ["00-05_ARC-100_Synchronization.md", "00-06_ARC-100_Architectural_Modeling.md"]
---

## 00-07 ARC-100 Getting Started

> **Start here to put ARC-100 on a project.** By the end you will have a
> running `<NAME>-100/` documentation instance — cloned, synced, previewing in
> your browser, with your own books ready to fill. This chapter is deliberately
> thin: it gives the steps and the few things you must decide, and links the
> depth to [00-00 General](00-00_ARC-100_General.md) (numbering, bands,
> lifecycle, hard rules), [00-05 Synchronization](00-05_ARC-100_Synchronization.md)
> (how the sync works), and
> [00-06 Architectural Modeling](00-06_ARC-100_Architectural_Modeling.md)
> (LikeC4). New to ARC-100? Read [00-00](00-00_ARC-100_General.md) first.

### 00-07.1 — Your `<NAME>-100` instance

Adopting ARC-100 means creating **your own named instance** — `CS-100`,
`ACME-100`, `FLOW-100`. It *inherits* the Book 00 standard chapters (kept fresh
by the sync) and *adds* your own books in the slots the standard reserves for
you (§00-07.5). The onboarding script (§00-07.2) builds the `<NAME>-100/` docs
instance under your project root, and installs the arc-100 agents/commands into
your project's **main** `.claude/`:

| Inside `<NAME>-100/` | What it is | Who maintains it |
| --- | --- | --- |
| `docs/00/` | Book 00 standard chapters + the mirrored ARC-100 index | Upstream — synced, read-only ([00-00 §00-00.11](00-00_ARC-100_General.md)) |
| `docs/01/01-01_<NAME>-100_Index.md` | **Your working index** — the one your site renders from | The `arc-100-librarian` agent |
| `docs/01/`, `docs/02/`, … | Your own books and chapters | You |
| `assets/`, `_hooks/`, `mkdocs.yml` | Theme assets, the build hook, site config | Synced (some seed-class — §00-07.3) |

The arc-100 Claude Code agents/commands/skill do **not** live inside
`<NAME>-100/` — they are copy-deployed (by `deploy_claude.py`, run by the
onboarding script and `/sync-arc-100`) to your project's main `.claude/` at the
project root, substituted for your project name.

> **Open your project root as your editor / Claude Code workspace.** The arc-100
> agents and commands live in your project's **main** `.claude/` (the project
> root), so `/sync-arc-100` and the `arc-100-librarian` / `arc-100-chapter-author`
> / `likec4-author` agents work across your whole project — not only when the
> `<NAME>-100/` docs subfolder is the open workspace. The `<NAME>-100/` instance
> holds your docs, index, and site config.

ARC-100 keeps two indexes: the upstream inventory at `docs/00/00-01_…`
(read-only) and *your* working index at `docs/01/01-01_…` — only the latter
renders your site. The full two-index model is
[00-00 §00-00.10.1](00-00_ARC-100_General.md).

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
bash "$CLONE/RUN_FIRST.sh"          # prompts for your system's name
rm -rf "$CLONE"
```

`mktemp -d` makes a fresh throwaway directory and the trailing `rm -rf`
discards the clone once it has run — so the block is safe to re-run (it never
trips over a leftover) and leaves nothing behind. The clone is only a
delivery vehicle; nothing of yours lives in it.

Give `RUN_FIRST.sh` your system's name — at the prompt, or as one argument
(`ACME` → `ACME-100`). From that one input it does everything in a single pass:
creates the `<NAME>-100/` folder, writes its config (`project_name` is the only
key) and a `config.json` name asset, runs the bootstrap (`arc_sync.py` — Book 00,
your working index, the agents, the ULID minter), and fills in every
name-dependent placeholder, **so nothing is left to hand-fix.** It manages
`--target`/`--config` itself (passing either is refused); only `--source` and
`--dry-run` reach `arc_sync.py`. The name must be a single path segment
(letters/digits/`._-`); a bad one is rejected before anything is created
(§00-07.8).

**Exit codes.** The first run bootstraps, so it exits `0` (done) or `2`
(error — bad name, bad config or payload, or a path-containment violation;
stderr says which). The `1` (index decisions pending — it wrote
`.arc100/PENDING-INDEX-DECISIONS.yml`) only arises on a later re-sync
(§00-07.4). No network runs after the clone, so exit `2` is never a network
failure.

> **You are running upstream code.** Cloning and running `RUN_FIRST.sh` (and
> the `arc_sync.py` it calls) means executing upstream-delivered code on
> your machine — a sync tool that writes your files has to run somewhere.
> Both are auditable scripts (the sync tool is a single Python file —
> standard library + PyYAML, no network); read them in the clone before you
> run them if you want to. Integrity rests on the public mirror, the
> immutable `vN` index tags, and an out-of-band digest in each release's
> notes. See [00-05 §00-05.11](00-05_ARC-100_Synchronization.md) for the
> full posture.

### 00-07.3 — After the bootstrap: deps and a first preview

Almost everything is delivered and kept fresh by re-sync (**mirror-class** —
Book 00, the hook, assets, the agents; don't hand-edit, a local edit is backed
up before overwrite). A few files are yours (**seed-class** — written only if
absent, so your edits survive a re-sync), and `RUN_FIRST.sh` has already filled
their name placeholders. The file-class model is
[00-05 §00-05.5](00-05_ARC-100_Synchronization.md); in practice the only
seed-class edit you may want is tuning `mkdocs.yml`'s `not_in_nav` globs to your
book numbers.

**Install build deps.** `requirements.txt` is seeded; run the exact command the
**doctor** printed after the sync —
`python3 -m pip install --user --require-hashes -r requirements.txt` (the
`--require-hashes` flag is non-negotiable). The doctor only prints; it never
installs anything itself ([00-05 §00-05.8.1](00-05_ARC-100_Synchronization.md)).

**Preview.** `RUN_FIRST.sh` prints this command with your name and a free port
already filled in:

```bash
mkdocs serve -f <NAME>-100/mkdocs.yml --livereload --dev-addr localhost:<PORT> -o
mkdocs build -f <NAME>-100/mkdocs.yml      # static site -> <NAME>-100/site-<NAME>-100/
```

`-o` opens the browser. The home page is the generated index, which links every
chapter — there is no hand-maintained sidebar, so mkdocs's "not included in the
nav" notes are **expected, not errors.** A fresh instance is `--strict`-clean
except the inherited Book 00 architecture views (their `project=arc-100` LikeC4
diagrams resolve only on the standard's own site —
[00-06](00-06_ARC-100_Architectural_Modeling.md)).

### 00-07.4 — Keeping current

Your first run is `RUN_FIRST.sh`. After that, **updating is on-demand —
nothing syncs in the background** (a sync can raise index decisions that need
you, so it stays human-in-the-loop, not a daemon). Pull updates whenever you
choose, two equivalent ways:

- **`/sync-arc-100`** — the Claude Code slash command installed in your project's
  main `.claude/commands/`, available whenever your project root is the open
  workspace (§00-07.1).
- **The clone-and-run block** from §00-07.2, run again.

Either re-clones the mirror and runs `arc_sync.py` against your instance; it
re-syncs (you do not re-run `RUN_FIRST.sh`, which is first-run only).

**When a sync needs you (exit `1`).** The reconcile folds upstream index
changes into your working index (a renumber reads as a move, not
delete-plus-add), auto-applies the safe ones, and **escalates the
judgment-bound ones** to `.arc100/PENDING-INDEX-DECISIONS.yml` — applying
*nothing* until you answer. Fill each block's `decision:` (`accept`/`reject`)
— the `arc-100-librarian` can do this via `/resolve-arc-100-issues` (§00-07.6)
— then **re-run the sync** to apply them. Re-running *is* the applier; there is
no separate apply command. The classification rules, the two-axis (`vN`)
version model, and the banner flow are in
[00-05 §00-05.4–§00-05.9](00-05_ARC-100_Synchronization.md). Your own entries
(`arc_100: false`) are never touched; a hand-edited mirror file is backed up
to `.arc100/backups/` before any overwrite.

### 00-07.5 — Where your own documentation goes

Your books and chapters follow the standard's numbering
(`<book>-<chapter>_<title>.md`, seven bands) — the full format and band table
are [00-00 §00-00.7](00-00_ARC-100_General.md). Two rules you use constantly:

- **Chapters in an inherited book:** the standard uses slots 01–49; **you take
  50 upward.**
- **New books in a band:** the standard allocates low; **you allocate high and
  work down** (99, 98, …) — this minimises collisions when the standard adds a
  book.

You never invent chapter numbers or ULIDs by hand: the `arc-100-librarian`
(§00-07.6) allocates them and is the only writer of your working index. Your own
book is Book 01; the librarian titles it **"`<NAME>-100 System`"** when it
allocates it (mirroring the standard's Book 00 = "ARC-100 System").

You don't convert everything on day one: bootstrap ARC-100 alongside your
existing tree, and do the **bulk migration of legacy docs as a single planned
operation at version closeout** — not piecemeal during development
([00-00 §00-00.10](00-00_ARC-100_General.md)). The per-doc mechanic is the
librarian loop (§00-07.6): place a doc as a chapter, author its body, re-sync.
If a bootstrap lands a mirror-class file over a pre-existing one, the colliding
copy is moved to `.arc100/backups/<stamp>/` first.

### 00-07.6 — The agents

ARC-100 installs its Claude Code agents in your project's **main** `.claude/agents/`
(§00-07.1), so they work across your whole project. You drive them by asking; they
keep the disciplined rules so you don't have to.

- **`arc-100-librarian`** — the only writer of your working index. Ask "where
  does X belong?" or "allocate the next chapter in band 40"; it does
  chapter-identity rulings, slot allocation, ULID minting, schema sweeps, and
  fills queued sync decisions (`/resolve-arc-100-issues`). It never allocates a
  new book autonomously (that halts for your review), edits chapter bodies, or
  mutates a ULID.
- **`likec4-author`** — authors the LikeC4 model, views, and the `likec4-view`
  fences you embed; full guide in
  [00-06](00-06_ARC-100_Architectural_Modeling.md).

**The working loop:** librarian places a doc as a chapter → you (or
`likec4-author`) write the body/diagrams → `mkdocs build` → `/sync-arc-100`
keeps the inherited standard fresh.

A **migration toolkit** also ships in your project's `.claude/` for translating
existing project documentation into ARC-100 chapters: the
`arc-100-documentation-skill` orchestrator routes the `arc-100-chapter-author`
agent (writes chapter bodies, verified against code) and the librarian (placement
and index) with human gates. Engage it when bringing legacy docs into your instance.

### 00-07.7 — Removing the synced ARC-100 footprint

There is no `ARC-100-SYNC/` tree to delete — the onboarding script ran from
a throwaway clone. To peel the synced ARC-100 footprint out while keeping your
own books and chapters, run the instance-relative removals **from inside your
`<NAME>-100/` folder**, and the `.claude/` removal **from your project root**
(that is where the arc-100 agents/commands install):

```bash
# from inside <NAME>-100/ — the docs-instance footprint:
rm -rf .arc100/                              # per-project sync state + backups
rm ARC-100-SYNC.config.yml config.json       # the generated config + name asset
rm docs/00/00-*.md                           # the synced Book 00 chapters + mirrored index
rm _hooks/arc100_master_index.py             # the master-index hook
rm -rf assets/arc100/                        # home-page assets + fonts + the ULID minter

# from your project root — the arc-100 .claude/ assets:
rm .claude/agents/arc-100-librarian.md .claude/agents/arc-100-chapter-author.md \
   .claude/agents/likec4-author.md \
   .claude/commands/sync-arc-100.md .claude/commands/resolve-arc-100-issues.md \
   .claude/skills/arc-100-documentation-skill/SKILL.md   # if present
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

ARC-100 dogfoods its own install with the same flow as §00-07.2, but against a
**locally-assembled payload** (so a standup is verifiable independent of any
publish). From the ARC-100 repo root:

```bash
out="$(bash ARC-100-SYNC/scripts/release.sh --keep-staging)"          # assemble a local payload
staging="$(printf '%s\n' "$out" | sed -n 's/.*Staging kept: //p')/payload"
bash "$staging/RUN_FIRST.sh" INTARC                                   # creates ./INTARC-100/
```

This stands up a complete, *separate* `INTARC-100/` instance (Book 00, working
index, `.arc100/`, `.claude/`, assets, `config.json`, `mkdocs.yml`). Migrating
the existing green `docs/` content into it is the dogfood activity that follows
(§00-07.6), not part of standing it up.

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
| 2026-06-16 | Revision 11: dropped the literal name from the §00-07.2 clone command (`bash "$CLONE/RUN_FIRST.sh"`, no argument — it prompts when none is given), so it can't be copy-pasted into a documentation system literally named "ACME"; the placeholder wasn't obviously a placeholder. (`RUN_FIRST.sh` still *accepts* an optional positional name for automation/tests/the dogfood runbook — the docs just never show it.) Also clarified §00-07.4 "Keeping current": `/sync-arc-100` is a Claude Code slash command (not a filesystem path; at `.claude/commands/sync-arc-100.md`), and updating is **on-demand** — there is no background/daemon sync (human-in-the-loop by design, since a sync can raise index decisions). Command + prose only; no section renumbered. |
| 2026-06-16 | Revision 12: major simplification (author direction) + the workspace fix. Cut §00-07.1's rehash of *what ARC-100 is* (→ a tight instance-orientation table + a link to 00-00) and the §00-07.2–.6 restatements of the 00-05 sync model and 00-00 numbering (→ links), while keeping every action and genuine complexity (clone, exit codes, the index-decision escalation flow, the slot/book allocation rules, current limitations). **Fixed the `/sync-arc-100` doc gap:** §00-07.1 (new note), §00-07.4, and §00-07.6 now state that the `<NAME>-100/` instance *is* your editor/Claude Code workspace — Claude Code discovers `.claude/` commands and agents from the workspace root, so `/sync-arc-100` and the agents resolve only when the instance (not its parent) is the open workspace; `RUN_FIRST.sh`'s closing message says the same. Retitled §00-07.1 → "Your `<NAME>-100` instance", §00-07.3 → "After the bootstrap: deps and a first preview", §00-07.4 → "Keeping current"; trimmed §00-07.11's verbose file-tree. Title-only changes; no section number moved, all `[BB-CC §N]` citations intact. A 3-lens adversarial pass (complexity-preservation / rehash / links) confirmed no real action or complexity was lost; its fixes are folded in — restored the version-closeout bulk-migration constraint (§00-07.5, [00-00 §00-00.10](00-00_ARC-100_General.md)), scoped the `1` exit code to the re-sync path (the first run only bootstraps → `0`/`2`), and dropped the non-actionable banner-rendering troubleshooting bullet (the hook is mirror-class; that note belongs to 00-05.6). |
| 2026-06-28 | Revision 13: phase 5 — **de-silo correction** (reverses Revision 12's workspace claim). The arc-100 Claude Code agents/commands/skill are now copy-deployed to the project's **main** `.claude/` (the project root, by `deploy_claude.py` run from the onboarding script and `/sync-arc-100`), NOT the `<NAME>-100/` instance silo — so they resolve when your **project root** is the open workspace and work across the whole project (the prior "open `<NAME>-100/` as your workspace" guidance made them useless while coding elsewhere in the project). Edits: the frontmatter `agent_summary`; §00-07.1 NOTE + the "Inside `<NAME>-100/`" table (dropped the `.claude/` row, added a project-root note); §00-07.4 `/sync-arc-100` location; §00-07.6 retitled "The two agents" → "The agents", de-siloed, + a migration-toolkit note (the new `arc-100-chapter-author` + `arc-100-documentation-skill`); §00-07.7 removal split into instance-relative (from `<NAME>-100/`) vs project-root `.claude/` removals, with the two new assets added. Prose-only; only the §00-07.6 title text changed (no section number moved, no `[BB-CC §N]` citation moved), no `00-01` change. See `versions/v2/implementation/phase_5.md` (D6). |
