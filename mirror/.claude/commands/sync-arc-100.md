---
name: sync-arc-100
description: Clone the upstream ARC-100 distribution and run arc_sync.py against this project to refresh inherited Book 00 index entries; judgment-bound index decisions are escalated to .arc100/PENDING-INDEX-DECISIONS.yml for human review.
---

# /sync-arc-100

Refresh this project's inherited ARC-100 index entries by running the
upstream-delivered sync tool, and surface any index decisions that need human
review.

## Pre-check

Confirm that `ARC-100-SYNC.config.yml` exists at the project root. If it does
not, tell the user to copy the seeded example
`ARC-100-SYNC.config.example.yml` (it lands at the project root on the first
sync, copy-if-absent) to `ARC-100-SYNC.config.yml` and set `project_name`
before re-running.

`project_name` is the **only** required key. It must be a single path segment —
letters, digits, and `._-`; no `/`, no whitespace, no leading dot — because it
fuses into the derived index filename. `local_index_path` and
`local_chapter_root` are optional overrides; when omitted they convention-derive
to `docs/01/01-01_<project_name>_Index.md` and `docs` respectively.

## Run the sync

The adopter runs **upstream-delivered code**: clone the public distribution
mirror at depth 1, then run its `arc_sync.py` against the project root.

```bash
CLONE="$(mktemp -d)"
git clone --depth 1 https://github.com/arc-100-standard/ARC-100-dist.git "$CLONE"
python3 "$CLONE/tools/arc_sync.py" --target .
rm -rf "$CLONE"
```

Do **not** pass `--source` — it defaults to the clone root, which is what an
adopter wants. Add `--dry-run` to preview without writing anything; the dry run
mirrors the exit code its real run would produce. Capture the exit code.

## Read the exit code

- **0** — success: bootstrap completed, refresh applied, or clean no-op; no
  pending decision file on disk. Report "Sync complete; no human decisions
  needed" and show the stdout summary line.
- **1** — human action required: this run escalated and wrote
  `.arc100/PENDING-INDEX-DECISIONS.yml` with **zero** index changes applied, OR
  a prior decision file still has unanswered blocks. Recommend
  `/resolve-arc-100-issues` to fill in each block's `decision:`, then re-run
  `/sync-arc-100` — the answered decisions apply on that next run.
- **2** — error: a bad or malformed config or payload, a path-containment
  violation, `--target` not a directory, or the config not found. Surface the
  stderr text verbatim, halt, and ask the user how to proceed. (The sync does
  no network work of its own, so exit 2 is never a network issue.)

## Wrap-up

Sync state lives under `.arc100/` at the project root: durable state at
`.arc100/state.yml`, the transient decision file at
`.arc100/PENDING-INDEX-DECISIONS.yml` (present only between an escalating run
and the run that applies it), and answered files archived under
`.arc100/decisions-archive/`. Once the sync lands cleanly, suggest the user
commit the modified working index — `docs/01/01-01_<project_name>_Index.md`
(e.g. `docs/01/01-01_FLOW-100_Index.md`) — together with `.arc100/state.yml`.
