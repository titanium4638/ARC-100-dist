#!/usr/bin/env bash
#
# RUN_FIRST.sh — name-first onboarding for an ARC-100 documentation system.
#
# Capture the system NAME before anything is built, so every name-dependent
# surface (working-index filename, <NAME>-INDEX-* markers, rendered home title,
# seed config) is correct from the first run — no placeholders to fix later.
#
#   prompt for a moniker (e.g. CS)  ->  normalize to <NAME>-100 (e.g. CS-100)
#   mkdir <NAME>-100/               ->  write its ARC-100-SYNC.config.yml + config.json
#   run arc_sync.py --target <NAME>-100  (bootstrap: Book 00 + working index + .claude + ulid)
#   substitute the residual <PROJECT>* seed tokens in the just-seeded files
#
# arc_sync.py is unchanged — it derives the index filename, the markers, and the
# home title from project_name. RUN_FIRST owns only the folder, the JSON asset,
# and the seed-token substitution.
#
# Robustness: the payload is validated (arc_sync.py present AND a real mirror/ tree
# under the effective --source) BEFORE any folder is created, so running this from
# a non-payload location (e.g. the bare repo scripts/ dir) fails fast with guidance
# instead of half-building. If a later step fails anyway, a <NAME>-100/ THIS run
# created is rolled back rather than left as wreckage.
#
# GATE: security-critical. The operator name is shape-validated here (the PRIMARY
# control) BEFORE any folder/file is created, and arc_sync.py re-gates the same
# value (re.fullmatch). Operator input reaches files via env -> python / printf
# of an already-charset-constrained value — never via sed/shell interpolation.
#
# Run from the distribution clone:  bash <clone>/RUN_FIRST.sh [NAME] [arc_sync flags…]
#   NAME              first positional, or one interactive read (default: PROJECT-100)
#   [arc_sync flags]  passed through to arc_sync.py (e.g. --source <staging>, --dry-run)

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

# Locate arc_sync.py in either layout: payload/clone (tools/ sibling) or the
# canonical source repo (scripts/ sibling, where RUN_FIRST.sh lives pre-release).
ARC_SYNC="${HERE}/tools/arc_sync.py"
[ -f "${ARC_SYNC}" ] || ARC_SYNC="${HERE}/arc_sync.py"

# The name is the first positional; remaining args pass through to arc_sync.py.
raw="${1:-}"
if [ "$#" -ge 1 ]; then shift; fi

# RUN_FIRST OWNS --target (the <NAME>-100/ folder it creates) and --config; a
# pass-through must not redirect them onto a tree whose config + config.json it
# never wrote. arc_sync re-gates both, but the named primary control should not
# hand a caller the steering wheel. --source / --dry-run pass through freely.
for arg in "$@"; do
  case "${arg}" in
    --target|--target=*|--config|--config=*)
      echo "ERROR: ${arg%%=*} is managed by RUN_FIRST and cannot be overridden." >&2
      exit 2 ;;
  esac
done

# Fail fast: this script bootstraps from a PAYLOAD — a tree with a mirror/ subdir
# (Book 00 + assets) and arc_sync.py. RUN_FIRST defaults --source to its own dir
# (HERE); a pass-through --source overrides it (argparse takes the last value).
# Resolve the EFFECTIVE source and verify the payload BEFORE creating anything, so
# running from a non-payload location (e.g. the bare repo scripts/ dir, which has
# no mirror/) errors cleanly instead of half-building a <NAME>-100/.
SOURCE="${HERE}"
prev=""
for arg in "$@"; do
  [ "${prev}" = "--source" ] && SOURCE="${arg}"
  case "${arg}" in --source=*) SOURCE="${arg#--source=}" ;; esac
  prev="${arg}"
done
if [ ! -f "${ARC_SYNC}" ] || [ ! -d "${SOURCE}/mirror" ]; then
  echo "ERROR: no ARC-100 payload here (need arc_sync.py and a '${SOURCE}/mirror' tree)." >&2
  echo "       Run RUN_FIRST.sh from a distribution clone or a staged payload — not the" >&2
  echo "       bare repo. From the ARC-100 repo, stage a payload first:" >&2
  echo "         out=\"\$(bash ARC-100-SYNC/scripts/release.sh --keep-staging)\"" >&2
  echo "         staging=\"\$(printf '%s\\n' \"\$out\" | sed -n 's/.*Staging kept: //p')/payload\"" >&2
  echo "         bash \"\$staging/RUN_FIRST.sh\" <NAME>" >&2
  exit 2
fi

[ -n "${raw}" ] || read -rp 'Name your documentation system (e.g. CS; "-100" is appended): ' raw || true
# Trim surrounding whitespace.
raw="$(printf '%s' "${raw}" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')"

if [ -z "${raw}" ]; then
  # Truly empty / declined input -> friendly default (re-runnable to rename).
  name="PROJECT-100"
  echo "No name given — defaulting to PROJECT-100 (re-run to rename)."
else
  # Strip a trailing band marker [sep]{0,3}100 (CS-100 / CS100 / CS 100 / CS_100
  # / CS - 100 / C100 all -> base), then re-append -100. A trailing 100 is ALWAYS
  # the band marker; a value that is ONLY the marker (e.g. "100") has no name.
  base="$(printf '%s' "${raw}" | sed -E 's/[[:space:]_-]{0,3}100[[:space:]]*$//; s/[[:space:]]+$//')"
  if [ -z "${base}" ]; then
    echo "ERROR: '${raw}' has no project name before the -100 band marker." >&2
    exit 2
  fi
  name="${base}-100"
fi

# Validate: single line AND charset — equivalent to arc_sync.py L147 re.fullmatch
# (which a multi-line value would fail; grep -qx alone would accept it line-wise).
# Reject BEFORE creating anything — never leave a folder for a bad name.
if [ "${name}" != "${name%%$'\n'*}" ] \
   || ! printf '%s' "${name}" | grep -qxE '[A-Za-z0-9][A-Za-z0-9._-]*'; then
  echo "ERROR: '${raw}' does not yield a valid system name (letters/digits/._- only, single segment)." >&2
  exit 2
fi

# Roll back a <NAME>-100/ THIS run creates if any later step fails (set -e or a
# signal). Only a folder we created is removed — never a pre-existing one. ${name}
# passed the strict shape gate above (single segment, [A-Za-z0-9._-]), so the rm
# target is a direct child of CWD with no traversal.
created=""
[ -e "${name}" ] || created="${name}"
roll_back() {
  status=$?
  if [ "${status}" -ne 0 ] && [ -n "${created}" ] && [ -d "${created}" ]; then
    rm -rf -- "${created}"
    echo "Rolled back partially-created ${created}/ after failure (exit ${status})." >&2
  fi
}
trap roll_back EXIT

mkdir -p "${name}"
# project_name is the only required key; the value passed the strict gate above
# (no YAML metacharacters possible), so a printf write is injection-safe.
printf 'project_name: %s\n' "${name}" > "${name}/ARC-100-SYNC.config.yml"
# config.json — the readable name asset for downstream scripts/agents. Built by
# json.dump from an env var (never string-built).
NAME="${name}" python3 - "${name}/config.json" <<'PY'
import json, os, sys
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    json.dump({"documentation_system_name": os.environ["NAME"]}, fh, indent=2)
    fh.write("\n")
PY

# Bootstrap the DOCS: Book 00 -> <NAME>-100/docs/00/, working index seeded +
# correctly named, ulid.py into the instance. "$@" passes through (e.g. --source).
python3 "${ARC_SYNC}" --source "${HERE}" --target "${name}" "$@"

# Deploy the .claude/ agents/commands/skills to the PROJECT ROOT (this CWD, the
# parent of <NAME>-100/), substituted for the system name — NOT the instance silo,
# so they work across the whole project. deploy_claude.py sits beside arc_sync.py
# in the payload (tools/) and reads the payload's claude/ dir (the effective SOURCE).
DEPLOY_CLAUDE="$(dirname "${ARC_SYNC}")/deploy_claude.py"
python3 "${DEPLOY_CLAUDE}" --src "${SOURCE}/claude" --project-root . --name "${name}"

# Substitute the residual <PROJECT>* seed tokens in the just-seeded files, and
# the <NAME> placeholder in the seeded working index, so the adopter never sees a
# placeholder. Ordered, bounded token list; one pass/file. (likec4 fence project=
# must equal likec4.config.json "name" -> both become the system name, which
# likec4 accepts as a project id.)
NAME="${name}" python3 - "${name}" <<'PY'
import os, sys
from pathlib import Path

name = os.environ["NAME"]
root = Path(sys.argv[1])
# Composites first so the bare <PROJECT> rule never double-appends -100.
subs = [
    ("<PROJECT> Project", name),          # mkdocs site_name -> bare system name
    ("<PROJECT_DESC>", f"{name} documentation"),
    ("<PROJECT_SLUG>", name),             # likec4 fence project= matches the config "name"
    ("<PROJECT>-100", name),              # -100 composites (template.c4, package.json, index.md, prose)
    ("<PROJECT>", name),                  # remaining standalone (site-<PROJECT>, likec4 "name", title, comment)
]
targets = [
    "mkdocs.yml",
    "docs/00/architectural-model.md",
    "docs/00/model/likec4.config.json",
    "docs/00/model/index.md",
    "architecture/LikeC4/package.json",
    "architecture/LikeC4/template.c4",
]
for rel in targets:
    p = root / rel
    if not p.is_file():
        continue          # a seed file may legitimately be absent for this target
    text = p.read_text(encoding="utf-8")
    for old, new in subs:
        text = text.replace(old, new)
    p.write_text(text, encoding="utf-8")

# Working index: fill ONLY the Book 01 placeholder title "<NAME> System".
# Do NOT run the <PROJECT> subs here — Book 00 entry descriptions carry generic
# "<PROJECT>-100" prose (the standard's own text, exempted by arc_sync's malformed
# gate) that must stay verbatim; rewriting it would both corrupt the content and
# make every such entry diverge from BASE (a mass refresh escalation). Filling
# <NAME> is refresh-safe: Book 01 syncs slot identity only (id/band/ulid), so
# arc_sync never compares — or reverts — the title on a later refresh.
wi = root / f"docs/01/01-01_{name}_Index.md"
if wi.is_file():
    wi.write_text(wi.read_text(encoding="utf-8").replace("<NAME>", name), encoding="utf-8")
PY

# Install succeeded. Disarm the rollback trap so the post-success helper below
# (port scan + recommendation) can never roll back a fully-built instance.
trap - EXIT

# Recommend a ready-to-run preview command: the instance config, livereload, the
# first free port at/above 8000, and -o (mkdocs opens the browser on serve).
port="$(python3 - <<'PY'
import socket
chosen = 8000
for p in range(8000, 9000):
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", p)); chosen = p; s.close(); break
    except OSError:
        s.close()
print(chosen)
PY
)" || port=8000
[ -n "${port}" ] || port=8000

echo ""
echo "Built ${name}/ — your ARC-100 documentation system."
echo ""

# The plain preview command — shown when the VS Code task offer is declined or
# there is no .vscode/ workspace.
recommend_cmd() {
  echo "Preview it (opens your browser):"
  echo "  mkdocs serve -f ${name}/mkdocs.yml --livereload --dev-addr localhost:${port} -o"
}

# Opt-in VS Code task wiring. A task is the easiest way to start the site, so
# offer it first — but ONLY in an interactive terminal with a .vscode/ workspace
# folder in the CWD (the VS Code workspace root, parent of the instance). The
# helper builds the task JSON from the gated name + scanned port via json.dump
# (no shell/JSON injection), backs up an existing tasks.json before editing, and
# falls back to printing a paste-ready snippet rather than risk corrupting it.
if [ -t 0 ] && [ -d ".vscode" ]; then
  ans=""
  read -rp "Would you like to create a task in Visual Studio Code's .vscode/tasks.json to start the mkdocs server hosting your ${name} site? [y/N] " ans || true
  case "${ans}" in
    [Yy] | [Yy][Ee][Ss])
      if NAME="${name}" PORT="${port}" python3 - <<'PY'
import json, os, re, shutil, sys

name = os.environ["NAME"]
port = os.environ["PORT"]
path = os.path.join(".vscode", "tasks.json")
label = f"Docs: MkDocs serve ({name} @ {port})"
task = {
    "label": label,
    "type": "shell",
    "command": "mkdocs",
    "args": ["serve", "-f", f"{name}/mkdocs.yml", "--livereload",
             "--dev-addr", f"localhost:{port}", "-o"],
    "options": {"cwd": "${workspaceFolder}"},
    "isBackground": True,
    "group": "build",
}
RUN_DEFAULT = ("Start it with Cmd-Shift-B (Run Build Task) — VS Code's built-in\n"
               "shortcut. (If Cmd-Shift-B is remapped: Cmd-Shift-P -> "
               "'Tasks: Run Task' -> the label.)")
RUN_PICK = ("Start it with Cmd-Shift-P -> 'Tasks: Run Task' -> the new label\n"
            "(Cmd-Shift-B runs your existing default build task).")

# No tasks.json yet -> create one. The new task is the only build task, so
# Cmd-Shift-B runs it directly.
if not os.path.exists(path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"version": "2.0.0", "tasks": [task]}, fh, indent=4)
        fh.write("\n")
    print(f'Created .vscode/tasks.json with task "{label}".')
    print(RUN_DEFAULT)
    sys.exit(0)

text = open(path, encoding="utf-8").read()
# Already wired for this instance? Cheap substring test, no JSON parse.
if f'"{name}/mkdocs.yml"' in text:
    print(f'A VS Code task for {name} already exists in .vscode/tasks.json — left as is.')
    print(RUN_PICK)
    sys.exit(0)

# Insert into the existing "tasks": [ ... ] array by text edit so JSONC comments
# and formatting survive. Back up first; if the array can't be found, print the
# snippet instead of risking a corrupt file.
m = re.search(r'"tasks"\s*:\s*\[', text)
if not m:
    print('Could not locate the "tasks" array — paste this into .vscode/tasks.json:')
    print(json.dumps(task, indent=2))
    print(RUN_PICK)
    sys.exit(0)
shutil.copy2(path, path + ".bak")
indented = "\n".join("        " + ln for ln in json.dumps(task, indent=4).splitlines())
empty = re.match(r"\s*\]", text[m.end():]) is not None
text = text[:m.end()] + "\n" + indented + ("" if empty else ",") + text[m.end():]
with open(path, "w", encoding="utf-8") as fh:
    fh.write(text)
print(f'Added a task to .vscode/tasks.json (original backed up to tasks.json.bak): "{label}".')
print(RUN_PICK)
PY
      then :
      else
        echo "(Could not write the VS Code task — use the command instead.)"
        recommend_cmd
      fi
      ;;
    *)
      recommend_cmd
      ;;
  esac
else
  recommend_cmd
fi

echo ""
echo "Open this project root as your editor workspace — the arc-100 agents and the"
echo "/sync-arc-100 command live in ./.claude/ (deployed there by RUN_FIRST)"
echo "and work across your whole project; your docs live in ${name}/."
echo ""
echo "Updates are on demand — nothing syncs in the background. Pull upstream"
echo "changes anytime by re-running the clone-and-run, or /sync-arc-100 in Claude Code."
