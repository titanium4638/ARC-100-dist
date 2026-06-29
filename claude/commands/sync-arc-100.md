---
name: sync-arc-100
description: Clone the upstream ARC-100 distribution and run arc_sync.py against the <PROJECT>-100 instance to refresh inherited Book 00 index entries; judgment-bound decisions are escalated to <PROJECT>-100/.arc100/PENDING-INDEX-DECISIONS.yml for human review. Run from the project root.
---

# /sync-arc-100

> The ARC-100 docs instance lives in the `<PROJECT>-100/` subdirectory, while the
> arc-100 `.claude/` agents and commands live in your project's **main** `.claude/`
> (the project root). So the sync runs from the **project root**: `arc_sync.py`
> reconciles the docs into the instance, and `deploy_claude.py` deploys the
> agents/commands to the project-root `.claude/`.

Refresh the <PROJECT>-100 instance's inherited ARC-100 index entries by running the
upstream-delivered sync tool, and surface any index decisions that need human
review.

## Pre-check

Confirm that `<PROJECT>-100/ARC-100-SYNC.config.yml` exists. If it does not, tell the
user to copy the seeded example `<PROJECT>-100/ARC-100-SYNC.config.example.yml` to
`<PROJECT>-100/ARC-100-SYNC.config.yml` and set `project_name: <PROJECT>-100` before
re-running. (`project_name` is the only required key; `local_index_path` and
`local_chapter_root` are optional overrides that convention-derive to
`docs/01/01-01_<PROJECT>-100_Index.md` and `docs` respectively, **relative to the
instance root** `<PROJECT>-100/`.)

## Run the sync

The adopter runs **upstream-delivered code**: clone the public distribution
mirror at depth 1, then run its two tools from the **project root** — `arc_sync.py`
reconciles the docs into the `<PROJECT>-100/` instance, and `deploy_claude.py`
re-deploys the arc-100 agents/commands to your project's **main** `.claude/`.

```bash
CLONE="$(mktemp -d)"
git clone --depth 1 https://github.com/arc-100-standard/ARC-100-dist.git "$CLONE"
python3 "$CLONE/tools/arc_sync.py" --target <PROJECT>-100            # docs -> the instance
python3 "$CLONE/tools/deploy_claude.py" --src "$CLONE/claude" \
        --project-root . --name <PROJECT>-100                        # .claude/ -> the project root
rm -rf "$CLONE"
```

`arc_sync.py --target <PROJECT>-100` reconciles the docs into the instance
subdirectory (and is where index decisions can escalate — see the exit code
below). `deploy_claude.py` then copies the generic `.claude/` agents/commands/
skills to the project-root `.claude/`, substituting your project name — a fresh
overwrite each sync (no local-edit backup, so tailor an agent via its "Project-
specific extension" section, not the shipped body). The `<PROJECT>-100` is your
literal instance dir name — this command file is substituted at install. (A
project whose whole repo *is* the instance uses `--target .`.) Do **not** pass
`--source` to `arc_sync.py` — it defaults to the clone root. Add `--dry-run` to
`arc_sync.py` to preview the docs reconcile; capture its exit code.

## Read the exit code

- **0** — success: bootstrap completed, refresh applied, or clean no-op; no
  pending decision file on disk. Report "Sync complete; no human decisions
  needed" and show the stdout `summary:` line. If this run applied answered
  decisions (the re-run after a `/resolve-arc-100-issues` pass), ALSO surface
  the `decision: applied accepts=N rejects=M` line — the `summary:` line's
  `index entries applied=` counter reflects only the fresh refresh pass and
  reads `0` even when an accepted decision was just applied, so the summary
  line alone understates the run.
- **1** — human action required: this run escalated and wrote
  `<PROJECT>-100/.arc100/PENDING-INDEX-DECISIONS.yml` with **zero** index changes
  applied, OR a prior decision file still has unanswered blocks. Recommend
  `/resolve-arc-100-issues` to fill in each block's `decision:`, then re-run
  `/sync-arc-100` — the answered decisions apply on that next run.
- **2** — error: a bad or malformed config or payload, a path-containment
  violation, `--target` not a directory, or the config not found. Surface the
  stderr text verbatim, halt, and ask the user how to proceed. (The sync does no
  network work of its own, so exit 2 is never a network issue.)

## Wrap-up

Sync state lives under `<PROJECT>-100/.arc100/`: durable state at
`<PROJECT>-100/.arc100/state.yml`, the transient decision file at
`<PROJECT>-100/.arc100/PENDING-INDEX-DECISIONS.yml` (present only between an
escalating run and the run that applies it), and answered files archived under
`<PROJECT>-100/.arc100/decisions-archive/`.

Once the sync lands cleanly, suggest the user commit — as one coherent commit —
**everything the run touched, not just the index.** Run `git status <PROJECT>-100/
.claude/` to capture the actual set (the instance subtree **and** the project-root
`.claude/`, since `deploy_claude.py` re-deploys the agents/commands there);
depending on what the run did it can include:

- the working index `<PROJECT>-100/docs/01/01-01_<PROJECT>-100_Index.md` — only when this
  run applied index changes (a bootstrap, or the re-run that applies accepted
  decisions; a pure refresh or an all-rejected run leaves it untouched);
- the Book 00 mirrors `<PROJECT>-100/docs/00/00-01_ARC-100_Standard_Inventory.md`
  and `<PROJECT>-100/_hooks/arc100_master_index.py` — rewritten from upstream on
  every run, and shown as modified whenever upstream content differs from disk
  (e.g. a release bump). The stdout `mirror: ^ … (refreshed)` lines name them;
- durable state `<PROJECT>-100/.arc100/state.yml`;
- a new decision archive `<PROJECT>-100/.arc100/decisions-archive/<stamp>.yml` —
  whenever this run answered and applied a decision file.

Committing only the index strands the mirror refreshes and the archive, leaving
the working tree in a partial state.
