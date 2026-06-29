---
name: resolve-arc-100-issues
description: Walk the user through queued ARC-100 sync decisions in <PROJECT>-100/.arc100/PENDING-INDEX-DECISIONS.yml by dispatching arc-100-librarian with its Resolution skill to fill in each block's decision field (accept | reject). Run from the project root.
---

# /resolve-arc-100-issues

Dispatch the `arc-100-librarian` subagent to walk the user through each queued
<PROJECT>-100 sync decision and record an `accept` / `reject` choice on it.

## Pre-check

If `<PROJECT>-100/.arc100/PENDING-INDEX-DECISIONS.yml` does not exist, tell the user
"No pending decisions — the <PROJECT>-100 index is in sync with upstream." and exit.
Do NOT dispatch the librarian.

## Dispatch

Send the following directive to the `arc-100-librarian` subagent (use the Agent
tool with `subagent_type: arc-100-librarian`):

> Activate the **Resolution skill**. Walk the user through the pending <PROJECT>-100
> sync decisions at `<PROJECT>-100/.arc100/PENDING-INDEX-DECISIONS.yml`. For each
> block, present the proposal and, on confirmation, set that block's `decision:`
> field to `accept` or `reject` (a defer leaves it `null`). Edit only the
> `decision:` field — apply nothing, delete nothing, and do not archive the
> file; `arc_sync.py` applies and archives on its next run.

The Resolution skill is defined in `.claude/agents/arc-100-librarian.md` in your
project root's main `.claude/agents/` (the arc-100 assets install to the project's
main `.claude/`, not the `<PROJECT>-100/` instance), and walks the decision blocks
one at a time, proposing a resolution per block and filling in `decision:` only on
confirmation.

## After return

Re-read `<PROJECT>-100/.arc100/PENDING-INDEX-DECISIONS.yml` and report how many
blocks still carry `decision: null` (deferred). When every block is answered,
tell the user to re-run `/sync-arc-100` — the decisions apply on the next sync,
which also archives the answered file. The resolver's job ends at "all blocks
answered"; it never applies or deletes anything itself.
