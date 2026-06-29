#!/usr/bin/env python3
"""deploy_claude.py — deploy the generic ARC-100 .claude/ assets to a project's
main .claude/, substituting the <PROJECT> placeholder with the local project name.

The .claude/ agents/commands/skills are upstream-owned, project-AGNOSTIC templates.
Unlike the docs (which arc_sync.py reconciles statefully against a project's working
index), they are simply COPIED to the project root's .claude/ and re-deployed fresh
on every sync — an idempotent overwrite: no state, no drift-tracking, no backup.
Project-specific tailoring belongs in each asset's "Project-specific extension"
section, NOT in the shipped body (a re-deploy overwrites the body).

Self-contained: Python 3 stdlib only, no network. Used by RUN_FIRST.sh at bootstrap
and by the /sync-arc-100 command on every re-sync.

Usage (from a distribution payload/clone):
    python3 tools/deploy_claude.py --src <payload>/claude --project-root . --name FLOW-100
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def render(text: str, name: str) -> str:
    """Substitute the bounded, ordered (composite-first) <PROJECT> token set with
    the project name. Exact-string replace only — not eval/regex/format. Mirrors
    RUN_FIRST.sh's seed-token list; keep the two consistent."""
    for old, new in (
        ("<PROJECT> Project", name),
        ("<PROJECT_DESC>", f"{name} documentation"),
        ("<PROJECT_SLUG>", name),
        ("<PROJECT>-100", name),
        ("<PROJECT>", name),
    ):
        text = text.replace(old, new)
    return text


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--src", required=True, help="the payload's claude/ directory")
    ap.add_argument(
        "--project-root", default=".",
        help="project root whose .claude/ receives the assets (default: .)",
    )
    ap.add_argument("--name", required=True, help="project_name substituted for <PROJECT>")
    args = ap.parse_args(argv)

    src = Path(args.src)
    if not src.is_dir():
        print(f"ERROR: no .claude/ payload at {src}", file=sys.stderr)
        return 1
    dest_root = (Path(args.project_root) / ".claude").resolve()

    count = 0
    for f in sorted(src.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(src)
        out = (dest_root / rel).resolve()
        # Containment: the resolved target must stay under <project-root>/.claude/.
        if out != dest_root and dest_root not in out.parents:
            print(f"ERROR: refusing to write outside .claude/: {rel}", file=sys.stderr)
            return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(f.read_text(encoding="utf-8"), args.name), encoding="utf-8")
        count += 1
        print(f"claude: + .claude/{rel}")
    print(f"deployed {count} .claude/ file(s) to {dest_root} (substituted for {args.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
