#!/usr/bin/env python3
"""arc_sync.py — ARC-100 install + refresh tool core (phase 2a + 2b).

Self-contained (stdlib + PyYAML). Runs from a local payload tree — in
production a throwaway depth-1 clone of the public mirror repo, in
dogfood/testing any directory passed via ``--source``. There is no
network code in this tool; obtaining the payload is the caller's job.

Modes (implicit, no flag):
  * ``<target>/.arc100/state.yml`` present  -> REFRESH.
  * state absent, local index already seeded with inherited entries
    -> REFRESH in lost-state degradation (no BASE: every inherited
    NEW-vs-LOCAL difference escalates; mirror files all read as
    locally edited and are backed up before overwrite).
  * state absent, repo unseeded -> BOOTSTRAP (defensive: any
    pre-existing payload-target file is backed up to
    ``.arc100/backups/<stamp>/`` before being written).

Release metadata convention (plan leaves this open; fixed here): if
``<source>/payload.yml`` exists and is a YAML mapping with keys
``release_tag`` / ``source_sha``, those values are used; otherwise
``release_tag`` is ``"local"`` and ``source_sha`` is ``""``. P1's
publish step supplies ``payload.yml`` in real payloads.

Exit codes:
  0 — success (bootstrap completed; refresh fully applied or clean no-op).
  1 — human action required (index batch escalated and
      ``.arc100/PENDING-INDEX-DECISIONS.yml`` was written, or a prior
      decision file still has unanswered items). ``--dry-run`` mirrors
      the exit code its real run would produce.
  2 — error (bad config, malformed payload/state, path-containment
      violation, malformed upstream field during bootstrap, …).

Phase 2b additions: the seed file class (copy-if-absent in BOTH
modes; an existing target is never overwritten, never backed up, and
never recorded in state.yml.files) and the doctor summary
(presence-only toolchain checks printing prepared commands — the safe
residue of the cut guided installer; it never installs, never gates
the sync, and never alters the exit code).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import posixpath
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Garbage bound, not a style limit: production 00-01 descriptions are
# paragraph-length by design (42/179 entries exceeded the original 200;
# longest today is 645 chars — recalibrated 2026-06-10, P1 G6). Display
# rendering truncates at FIELD_ELLIPSIS_THRESHOLD regardless.
FIELD_MAX_CHARS = 2000
FIELD_ELLIPSIS_THRESHOLD = 150

UPSTREAM_START = "<!-- ARC-100-INDEX-START -->"
UPSTREAM_END = "<!-- ARC-100-INDEX-END -->"

STATE_REL = ".arc100/state.yml"
PENDING_REL = ".arc100/PENDING-INDEX-DECISIONS.yml"
BACKUPS_REL = ".arc100/backups"
ARCHIVE_REL = ".arc100/decisions-archive"

# Synced-field classes (§6.2): Book 00 entries mirror fully; all other
# books sync slot identity only (00-00 §00-00.7.1).
SYNCED_FIELDS_FULL: tuple[str, ...] = (
    "title", "description", "keywords", "status", "id", "band",
)
SYNCED_FIELDS_SLOT: tuple[str, ...] = ("arc_100_ulid", "id", "band")

_CONTROL_BYTES_RE = re.compile(r"[\x00-\x08\x0b-\x1f]")
# The standard's own placeholder vocabulary ("<PROJECT>-100", a "<NAME>
# System" placeholder title — both live in the production 00-01 index) is
# legitimate index text, not HTML. The negative lookahead exempts EXACTLY
# those two tokens; anything else — including uppercase HTML such as
# <SCRIPT>, and unknown placeholders like <BOOK> — is still rejected.
# Extending the vocabulary is a deliberate edit here, never a loosening.
_HTML_TAG_RE = re.compile(r"<(?!(?:PROJECT|NAME)>)[a-zA-Z][^>]*>")
_PATH_WHITELIST_RE = re.compile(r"^[A-Za-z0-9._/-]+$")

_VALID_DECISIONS = ("accept", "reject")


# ---------------------------------------------------------------------------
# Errors and sentinels
# ---------------------------------------------------------------------------


class SyncParseError(Exception):
    """Raised when payload, local index, config, or decision YAML is
    malformed or violates the ULID coverage pre-flight."""


class PathEscapeError(Exception):
    """Raised when a write/remove/backup target fails path containment."""


class MalformedUpstream:
    """Sentinel returned by md_cell_escape for rejected upstream text."""

    __slots__ = ("reason",)

    def __init__(self, reason: str) -> None:
        self.reason = reason


# ---------------------------------------------------------------------------
# Config (lifted from conform.py load_config; distribution fields dropped)
# ---------------------------------------------------------------------------


@dataclass
class Config:
    project_name: str
    local_index_path: Path
    local_chapter_root: Path


def load_config(path: Path) -> Config:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise SyncParseError("config root is not a mapping")
    # project_name is the ONLY required key; local_index_path / local_chapter_root
    # convention-derive from it when absent (see below).
    for required in ("project_name",):
        if not raw.get(required):
            raise SyncParseError(f"config missing required field: {required}")
    name = str(raw["project_name"])
    # Shape gate (security-critical): project_name fuses into the derived index
    # filename segment (docs/01/01-01_<name>_Index.md), so post-interpolation
    # contained_path can no longer reject a hostile name ('01-01_..' is a literal
    # dir name, not a '..' traversal segment). Constrain to a single path segment
    # here — this is the PRIMARY control for the derived path. It also keeps the
    # marker pair (<!-- <name>-INDEX-START -->) sane.
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
        raise SyncParseError(
            "project_name must be a single path segment: letters, digits, `._-`, "
            f"no leading dot, no `/` or whitespace (got {name!r})"
        )
    # Convention-derivation (author-clarified): the working index is chapter 01-01
    # INSIDE docs_dir, and the chapter root is `docs` — matches the dogfood, the
    # model layout. Explicit keys override by truthiness; an absent key falls to
    # the convention (NOT local_index.parent, NOT project_name — the retired
    # namespace shape; see phase 3a §3.1).
    local_index = (Path(str(raw["local_index_path"])) if raw.get("local_index_path")
                   else Path(f"docs/01/01-01_{name}_Index.md"))
    chapter_root = (Path(str(raw["local_chapter_root"])) if raw.get("local_chapter_root")
                    else Path("docs"))
    return Config(
        project_name=name,
        local_index_path=local_index,
        local_chapter_root=chapter_root,
    )


# ---------------------------------------------------------------------------
# Path containment (security-critical write gate; pure — §6.5)
# ---------------------------------------------------------------------------


def contained_path(target: Path, rel: str) -> Path:
    """Validate ``rel`` and return the joined path under ``target``.

    Pure: reads the filesystem only via ``Path.resolve`` (no writes).
    Two layers, both required:
      1. Lexical whitelist ``^[A-Za-z0-9._/-]+$`` plus rejection of
         absolute paths and any ``..`` segment.
      2. Load-bearing resolved check: ``Path(target, rel).resolve()``
         must be relative to ``target.resolve()`` — catches symlinked
         intermediate directories that the lexical check cannot.

    Raises PathEscapeError on any violation.
    """
    if not rel or not _PATH_WHITELIST_RE.match(rel):
        raise PathEscapeError(f"refusing path (failed whitelist [A-Za-z0-9._/-]+): {rel!r}")
    if rel.startswith("/"):
        raise PathEscapeError(f"refusing absolute path: {rel!r}")
    segments = rel.split("/")
    if rel in (".", "..") or ".." in segments:
        raise PathEscapeError(f"refusing path-traversal segment: {rel!r}")
    joined = Path(target, rel)
    if not joined.resolve().is_relative_to(target.resolve()):
        raise PathEscapeError(f"refusing path resolving outside target: {rel!r}")
    return joined


# ---------------------------------------------------------------------------
# Index model (lifted from conform.py: extract_yaml, Entry,
# index_entries_by_ulid, verify_ulid_coverage)
# ---------------------------------------------------------------------------


def extract_yaml(markdown: str, start_marker: str, end_marker: str) -> dict:
    pattern = re.compile(
        rf"{re.escape(start_marker)}\s*\n```yaml\n(.*?)\n```\s*\n{re.escape(end_marker)}",
        re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        raise SyncParseError(f"index markers not found ({start_marker} / {end_marker})")
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise SyncParseError(f"YAML parse failed: {exc}") from exc
    if not isinstance(data, dict):
        raise SyncParseError("index YAML root is not a mapping")
    return data


@dataclass
class Entry:
    ulid: str
    kind: str  # "book" | "chapter"
    id: str
    data: dict


def _index_books(index_dict: dict) -> list:
    return index_dict.get("books") or index_dict.get("chapters") or []


def flatten_entries(index_dict: dict) -> list[Entry]:
    """Flatten books + chapters to Entry records, INCLUDING entries
    without a ULID (ulid='') — project-owned entries may lack one but
    still occupy slots (trigger b) and parent-book positions (g)."""
    flat: list[Entry] = []
    for book in _index_books(index_dict):
        if not isinstance(book, dict):
            continue
        flat.append(
            Entry(
                ulid=str(book.get("arc_100_ulid") or ""),
                kind="book",
                id=str(book.get("id", "")),
                data=book,
            )
        )
        for chapter in book.get("chapters") or book.get("sub_chapters") or []:
            if not isinstance(chapter, dict):
                continue
            flat.append(
                Entry(
                    ulid=str(chapter.get("arc_100_ulid") or ""),
                    kind="chapter",
                    id=str(chapter.get("id", "")),
                    data=chapter,
                )
            )
    return flat


def index_entries_by_ulid(index_dict: dict) -> dict[str, Entry]:
    return {e.ulid: e for e in flatten_entries(index_dict) if e.ulid}


def verify_ulid_coverage(index_dict: dict, side: str, require_arc_100: bool) -> None:
    """Pre-flight: every (inherited, when require_arc_100) entry must
    carry arc_100_ulid. Raises SyncParseError listing offenders."""
    offenders: list[str] = []
    for entry in flatten_entries(index_dict):
        if require_arc_100 and not entry.data.get("arc_100"):
            continue
        if not entry.ulid:
            offenders.append(f"{entry.kind} {entry.id or '?'}")
    if offenders:
        raise SyncParseError(
            f"{side} entries missing arc_100_ulid: " + ", ".join(offenders)
        )


# ---------------------------------------------------------------------------
# Untrusted-content escape (lifted from conform.py)
# ---------------------------------------------------------------------------


def md_cell_escape(s: Any) -> str | MalformedUpstream:
    """Untrusted-content gate: control bytes / HTML tag /
    >FIELD_MAX_CHARS return the MalformedUpstream sentinel;
    long-but-legal strings are truncated for display (a UX nicety,
    never a security control)."""
    if s is None:
        return ""
    text = str(s)
    if _CONTROL_BYTES_RE.search(text):
        return MalformedUpstream("control bytes")
    if _HTML_TAG_RE.search(text):
        return MalformedUpstream("html tag")
    if len(text) > FIELD_MAX_CHARS:
        return MalformedUpstream(f"length {len(text)} > {FIELD_MAX_CHARS}")
    if len(text) > FIELD_ELLIPSIS_THRESHOLD:
        text = text[: FIELD_ELLIPSIS_THRESHOLD - 1].rstrip() + "…"
    return text.replace("|", r"\|")


def _escape_or_malformed(*fields: Any) -> str | MalformedUpstream:
    parts: list[str] = []
    for value in fields:
        escaped = md_cell_escape(value)
        if isinstance(escaped, MalformedUpstream):
            return escaped
        parts.append(escaped)
    return " · ".join(p for p in parts if p)


def _safe_cell(value: Any) -> str:
    escaped = md_cell_escape(value)
    if isinstance(escaped, MalformedUpstream):
        return f"<malformed:{escaped.reason}>"
    return escaped


def compute_decision_id(kind: str, upstream_ulid: str, local_ulid: str) -> str:
    payload = f"{upstream_ulid or ''}|{local_ulid or ''}".encode("utf-8")
    return f"{kind}-{hashlib.sha256(payload).hexdigest()[:8]}"


def entry_field_violation(data: dict, include_chapters: bool = False) -> str | None:
    """§6.2 malformed-upstream gate over title/description/keywords/
    status. Returns the first violation reason, or None. Pure."""
    for field_name in ("title", "description", "status"):
        escaped = md_cell_escape(data.get(field_name))
        if isinstance(escaped, MalformedUpstream):
            return f"{field_name}: {escaped.reason}"
    keywords = data.get("keywords")
    items = keywords if isinstance(keywords, list) else ([keywords] if keywords is not None else [])
    for item in items:
        escaped = md_cell_escape(item)
        if isinstance(escaped, MalformedUpstream):
            return f"keywords: {escaped.reason}"
    if include_chapters:
        for chapter in data.get("chapters") or []:
            if isinstance(chapter, dict):
                nested = entry_field_violation(chapter)
                if nested:
                    return f"chapter {chapter.get('id', '?')}: {nested}"
    return None


# ---------------------------------------------------------------------------
# Slot-identity helpers (lifted from conform.py L702–729)
# ---------------------------------------------------------------------------


def _book_id_from_local_entry(local_target: dict) -> str:
    eid = str(local_target.get("id", ""))
    if "-" in eid:
        return eid.split("-", 1)[0]
    return eid


def _is_slot_identity_only_book(book_id: str) -> bool:
    """Per 00-00 §00-00.7.1: only Book 00 follows the full-mirror
    semantic; every other book syncs slot identity only."""
    return book_id != "00"


def _find_target_book(local_index: dict, chapter_id: str) -> dict | None:
    book_prefix = chapter_id.split("-", 1)[0] if "-" in chapter_id else None
    if book_prefix:
        for book in _index_books(local_index):
            if str(book.get("id", "")) == book_prefix:
                return book
    return None


def synced_fields_for(entry_id: str) -> tuple[str, ...]:
    """Field-equality class for an entry, derived from its book id."""
    book_id = entry_id.split("-", 1)[0] if "-" in entry_id else entry_id
    return SYNCED_FIELDS_SLOT if _is_slot_identity_only_book(book_id) else SYNCED_FIELDS_FULL


def project_fields(data: dict, fields: tuple[str, ...]) -> dict:
    """Projection of an entry onto its synced fields (missing -> None)."""
    return {f: data.get(f) for f in fields}


def _parent_book_id(chapter_id: str) -> str:
    return chapter_id.split("-", 1)[0] if "-" in chapter_id else ""


def _deep_copy(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _deep_copy(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_deep_copy(v) for v in value]
    return value


# ---------------------------------------------------------------------------
# The 3-way reconcile core (written fresh from plan §6.2 — PURE, no I/O)
# ---------------------------------------------------------------------------


@dataclass
class Action:
    """One auto-apply candidate. kind: update | insert_chapter |
    insert_book | delete | noop (noop = LOCAL==NEW, refresh BASE only;
    never counted toward the bulk guard)."""

    kind: str
    ulid: str
    entry_id: str
    data: dict | None = None
    fields: tuple[str, ...] = ()
    entry_count: int = 1
    note: str = ""


@dataclass
class Escalation:
    """One deferred item. action records what an 'accept' will do on
    the next run (update | insert_chapter | insert_book | delete | none)."""

    kind: str
    ulid: str
    reason: str
    action: str = "none"
    current: dict | None = None
    proposed: dict | None = None
    local_ulid: str = ""


@dataclass
class ReconcileResult:
    actions: list[Action] = field(default_factory=list)
    escalations: list[Escalation] = field(default_factory=list)
    diverged_drop: list[str] = field(default_factory=list)
    changed: int = 0
    inherited: int = 0


def _sanitized_insert(data: dict, kind: str) -> dict:
    """Deep-copy a NEW entry for insertion: arc_100 true; chapters
    (and chapters of a new book) carry status: placeholder (§6.2)."""
    entry = _deep_copy(data)
    entry["arc_100"] = True
    if kind == "chapter":
        entry["status"] = "placeholder"
    else:
        for chapter in entry.get("chapters") or []:
            if isinstance(chapter, dict):
                chapter["arc_100"] = True
                chapter["status"] = "placeholder"
    return entry


def reconcile_index(
    base_snapshot: list[dict],
    new_index: dict,
    local_index: dict,
    diverged: dict[str, dict],
) -> ReconcileResult:
    """The load-bearing 3-way reconcile (§6.2). Pure: dicts in,
    actions/escalations out; mutates nothing it is given.

    BASE = state.yml index_snapshot; NEW = payload index entries
    (upstream-owned by construction); LOCAL = the project index.
    Keyed by arc_100_ulid. The caller enforces atomicity: if
    result.escalations is non-empty, NO action may be applied.
    """
    result = ReconcileResult()

    base_by_ulid: dict[str, dict] = {}
    for item in base_snapshot:
        if isinstance(item, dict):
            ulid = str(item.get("arc_100_ulid") or "")
            if ulid:
                base_by_ulid[ulid] = item

    new_flat = flatten_entries(new_index)
    new_by_ulid = {e.ulid: e for e in new_flat if e.ulid}

    local_flat = flatten_entries(local_index)
    local_by_ulid = {e.ulid: e for e in local_flat if e.ulid}
    project_owned_slots = {
        e.id: e for e in local_flat if not e.data.get("arc_100") and e.id
    }
    local_book_ids = {e.id for e in local_flat if e.kind == "book"}
    result.inherited = sum(1 for e in local_flat if e.data.get("arc_100"))

    # --- Diverged short-circuit (checked BEFORE classification, §6.2) ---
    # A dropped (re-opened) ULID must RE-ESCALATE under trigger c/d, never
    # silently auto-apply: index_snapshot keeps it at the LOCAL value, so
    # LOCAL==BASE would otherwise read true and rule 1/4 would write past
    # the human's recorded rejection (§6.2 "Rejected decisions").
    suppressed: set[str] = set()
    reopened: set[str] = set()
    for ulid, recorded in diverged.items():
        if not isinstance(recorded, dict):
            result.diverged_drop.append(ulid)
            reopened.add(ulid)
            continue
        new_entry = new_by_ulid.get(ulid)
        if new_entry is None:
            if recorded.get("deleted") is True:
                suppressed.add(ulid)  # rejected deletion, still deleted upstream
            else:
                result.diverged_drop.append(ulid)
                reopened.add(ulid)
        else:
            fields = synced_fields_for(new_entry.id)
            if not recorded.get("deleted") and project_fields(
                new_entry.data, fields
            ) == project_fields(recorded, fields):
                suppressed.add(ulid)  # human already said no to exactly this
            else:
                result.diverged_drop.append(ulid)
                reopened.add(ulid)

    # --- NEW-only books: their chapters ride along inside the book insert ---
    pending_book_ids: set[str] = set()
    for e in new_flat:
        if (
            e.kind == "book"
            and e.ulid
            and e.ulid not in suppressed
            and e.ulid not in local_by_ulid
            and e.ulid not in base_by_ulid
        ):
            pending_book_ids.add(e.id)
    covered_chapters: set[str] = set()
    for e in new_flat:
        if (
            e.kind == "chapter"
            and e.ulid
            and e.ulid not in suppressed
            and e.ulid not in local_by_ulid
            and e.ulid not in base_by_ulid
            and _parent_book_id(e.id) in pending_book_ids
        ):
            covered_chapters.add(e.ulid)

    # --- Pass 1: every NEW entry ---
    for e in new_flat:
        if not e.ulid or e.ulid in suppressed or e.ulid in covered_chapters:
            continue
        local_e = local_by_ulid.get(e.ulid)
        base_d = base_by_ulid.get(e.ulid)
        fields = synced_fields_for(e.id)

        if local_e is not None:
            if not local_e.data.get("arc_100"):
                # Trigger e — lineage anomaly.
                result.escalations.append(
                    Escalation(
                        kind="lineage_anomaly",
                        ulid=e.ulid,
                        reason=(
                            f"payload ULID matches local entry {local_e.id} "
                            "which lacks arc_100: true"
                        ),
                        action="update",
                        current=local_e.data,
                        proposed=e.data,
                        local_ulid=local_e.ulid,
                    )
                )
                continue
            local_proj = project_fields(local_e.data, fields)
            new_proj = project_fields(e.data, fields)
            if local_proj == new_proj:
                # Rule 3 — already matches incoming: no-op, refresh BASE only.
                result.actions.append(Action(kind="noop", ulid=e.ulid, entry_id=e.id))
                continue
            if e.id != local_e.id and e.id in project_owned_slots:
                # Trigger b — renumber into a project-owned slot.
                collision = project_owned_slots[e.id]
                result.escalations.append(
                    Escalation(
                        kind="slot_collision",
                        ulid=e.ulid,
                        reason=(
                            f"payload renumber {local_e.id} -> {e.id} collides "
                            f"with project-owned slot {collision.id}"
                        ),
                        action="update",
                        current=collision.data,
                        proposed=e.data,
                        local_ulid=collision.ulid,
                    )
                )
                continue
            base_proj = project_fields(base_d, fields) if base_d is not None else None
            if base_proj is not None and local_proj == base_proj:
                # Rule 1 — update in place; malformed gate first (§6.2).
                violation = entry_field_violation(e.data)
                if violation:
                    result.escalations.append(
                        Escalation(
                            kind="malformed_upstream",
                            ulid=e.ulid,
                            reason=f"upstream field rejected: {violation}",
                            action="none",
                            current=local_e.data,
                            proposed=e.data,
                            local_ulid=local_e.ulid,
                        )
                    )
                elif e.ulid in reopened:
                    # §6.2 "Rejected decisions": the payload now proposes
                    # a value DIFFERENT from the recorded rejection —
                    # re-escalate (trigger c), never auto-apply past it.
                    result.escalations.append(
                        Escalation(
                            kind="local_edit_conflict",
                            ulid=e.ulid,
                            reason=(
                                "a prior upstream change for this entry was "
                                "rejected; the payload now proposes a "
                                "different value"
                            ),
                            action="update",
                            current=local_e.data,
                            proposed=e.data,
                            local_ulid=local_e.ulid,
                        )
                    )
                else:
                    result.actions.append(
                        Action(
                            kind="update",
                            ulid=e.ulid,
                            entry_id=e.id,
                            data=_deep_copy({k: v for k, v in e.data.items() if k != "chapters"}),
                            fields=fields,
                        )
                    )
            else:
                base_id = str(base_d.get("id") or "") if base_d is not None else ""
                if base_proj is not None and base_id and base_id != e.id:
                    # Trigger d (renumber variant) — NEW renumbers an entry
                    # whose LOCAL differs from BASE (§6.2; the delete
                    # variant of trigger d is pass 2).
                    result.escalations.append(
                        Escalation(
                            kind="modified_then_upstream_changed",
                            ulid=e.ulid,
                            reason=(
                                f"payload renumbers {base_id} -> {e.id}, but "
                                "the local entry differs from BASE"
                            ),
                            action="update",
                            current=local_e.data,
                            proposed=e.data,
                            local_ulid=local_e.ulid,
                        )
                    )
                    continue
                # Trigger c — LOCAL differs from BASE (or BASE absent: lost state).
                why = (
                    "local entry differs from BASE (hand-edited outside the agent path)"
                    if base_proj is not None
                    else "no BASE record for entry (lost or incomplete state)"
                )
                result.escalations.append(
                    Escalation(
                        kind="local_edit_conflict",
                        ulid=e.ulid,
                        reason=f"{why}; payload also differs",
                        action="update",
                        current=local_e.data,
                        proposed=e.data,
                        local_ulid=local_e.ulid,
                    )
                )
            continue

        # ULID absent from LOCAL.
        if base_d is not None:
            # Trigger f — project deleted an inherited entry still shipped.
            result.escalations.append(
                Escalation(
                    kind="local_deletion_conflict",
                    ulid=e.ulid,
                    reason=(
                        f"entry {e.id} is in BASE and still shipped, but absent "
                        "from the local index (deleted locally)"
                    ),
                    action="insert_chapter" if e.kind == "chapter" else "insert_book",
                    current=None,
                    proposed=e.data,
                )
            )
            continue

        # Rule 2 — insertion (ULID in NEW only).
        if e.id in project_owned_slots:
            collision = project_owned_slots[e.id]
            result.escalations.append(
                Escalation(
                    kind="slot_collision",
                    ulid=e.ulid,
                    reason=(
                        f"incoming {e.id} collides with project-owned slot "
                        f"{collision.id}"
                    ),
                    action="insert_chapter" if e.kind == "chapter" else "insert_book",
                    current=collision.data,
                    proposed=e.data,
                    local_ulid=collision.ulid,
                )
            )
            continue
        violation = entry_field_violation(e.data, include_chapters=(e.kind == "book"))
        if violation:
            result.escalations.append(
                Escalation(
                    kind="malformed_upstream",
                    ulid=e.ulid,
                    reason=f"upstream field rejected on insertion: {violation}",
                    action="none",
                    proposed=e.data,
                )
            )
            continue
        if e.kind == "chapter":
            if _parent_book_id(e.id) in local_book_ids:
                result.actions.append(
                    Action(
                        kind="insert_chapter",
                        ulid=e.ulid,
                        entry_id=e.id,
                        data=_sanitized_insert(e.data, "chapter"),
                    )
                )
            else:
                # Trigger g — parent book absent; never silently drop.
                result.escalations.append(
                    Escalation(
                        kind="new_no_parent",
                        ulid=e.ulid,
                        reason=(
                            f"new chapter {e.id} has no parent book "
                            f"{_parent_book_id(e.id)} in the local index"
                        ),
                        action="insert_chapter",
                        proposed=e.data,
                    )
                )
        else:
            chapter_count = sum(
                1
                for ch in e.data.get("chapters") or []
                if isinstance(ch, dict) and ch.get("arc_100_ulid")
            )
            result.actions.append(
                Action(
                    kind="insert_book",
                    ulid=e.ulid,
                    entry_id=e.id,
                    data=_sanitized_insert(e.data, "book"),
                    entry_count=1 + chapter_count,
                )
            )

    # --- Pass 2: BASE entries removed in NEW ---
    for ulid, base_d in base_by_ulid.items():
        if ulid in suppressed or ulid in new_by_ulid:
            continue
        local_e = local_by_ulid.get(ulid)
        if local_e is None:
            continue  # NEW also dropped it -> clean no-op (trigger f exception)
        if not local_e.data.get("arc_100"):
            # Fail closed: BASE should hold only inherited entries; a BASE
            # ULID landing on a project-owned entry is a lineage anomaly,
            # never an auto-delete of project-owned content.
            result.escalations.append(
                Escalation(
                    kind="lineage_anomaly",
                    ulid=ulid,
                    reason=(
                        f"BASE ULID matches local entry {local_e.id} which "
                        "lacks arc_100: true; payload no longer ships it"
                    ),
                    action="none",
                    current=local_e.data,
                    local_ulid=local_e.ulid,
                )
            )
            continue
        fields = synced_fields_for(local_e.id)
        if project_fields(local_e.data, fields) == project_fields(base_d, fields):
            if ulid in reopened:
                # §6.2 "Rejected decisions": a rejected update is on
                # record and the payload now DELETES the entry — a
                # different proposal: re-escalate (trigger d), never
                # auto-delete past the rejection.
                result.escalations.append(
                    Escalation(
                        kind="modified_then_upstream_changed",
                        ulid=ulid,
                        reason=(
                            f"payload removed {local_e.id} after a prior "
                            "upstream change for it was rejected"
                        ),
                        action="delete",
                        current=local_e.data,
                        local_ulid=ulid,
                    )
                )
            else:
                result.actions.append(
                    Action(kind="delete", ulid=ulid, entry_id=local_e.id)
                )
        else:
            # Trigger d — deleted upstream but modified locally.
            result.escalations.append(
                Escalation(
                    kind="modified_then_upstream_changed",
                    ulid=ulid,
                    reason=(
                        f"payload removed {local_e.id}, but the local entry "
                        "differs from BASE"
                    ),
                    action="delete",
                    current=local_e.data,
                    local_ulid=ulid,
                )
            )

    # --- Pass 3: LOCAL inherited entries unknown to BASE and NEW ---
    for ulid, local_e in local_by_ulid.items():
        if (
            ulid in suppressed
            or ulid in new_by_ulid
            or ulid in base_by_ulid
            or not local_e.data.get("arc_100")
        ):
            continue
        result.escalations.append(
            Escalation(
                kind="modified_then_upstream_changed",
                ulid=ulid,
                reason=(
                    f"inherited local entry {local_e.id} is absent from the "
                    "payload and has no BASE record"
                ),
                action="delete",
                current=local_e.data,
                local_ulid=ulid,
            )
        )

    # --- Book-deletion guard: never auto-delete a book whose chapters
    #     are not all deleted in the same batch (fail closed). ---
    delete_ulids = {a.ulid for a in result.actions if a.kind == "delete"}
    guarded: list[Action] = []
    for action in result.actions:
        if action.kind == "delete":
            local_e = local_by_ulid.get(action.ulid)
            if local_e is not None and local_e.kind == "book":
                leftover = [
                    ch
                    for ch in local_e.data.get("chapters") or []
                    if isinstance(ch, dict)
                    and str(ch.get("arc_100_ulid") or "") not in delete_ulids
                ]
                if leftover:
                    result.escalations.append(
                        Escalation(
                            kind="modified_then_upstream_changed",
                            ulid=action.ulid,
                            reason=(
                                f"payload removed book {action.entry_id}, but "
                                f"{len(leftover)} of its local chapters are not "
                                "removed in this batch"
                            ),
                            action="delete",
                            current=local_e.data,
                            local_ulid=action.ulid,
                        )
                    )
                    continue
        guarded.append(action)
    result.actions = guarded

    # --- Trigger a: bulk guard (formula from §6.2) ---
    result.changed = sum(
        a.entry_count for a in result.actions if a.kind != "noop"
    )
    changed, inherited = result.changed, result.inherited
    if changed > 10 or (changed >= 3 and inherited > 0 and changed > 0.20 * inherited):
        bulk_reason = (
            f"bulk guard: {changed} changed entries vs {inherited} inherited "
            "(threshold: >10, or >=3 and >20%)"
        )
        for action in result.actions:
            if action.kind == "noop":
                continue
            local_e = local_by_ulid.get(action.ulid)
            new_e = new_by_ulid.get(action.ulid)
            result.escalations.append(
                Escalation(
                    kind="bulk_change",
                    ulid=action.ulid,
                    reason=f"{bulk_reason}; this item: {action.kind} {action.entry_id}",
                    action=action.kind,
                    current=local_e.data if local_e else None,
                    proposed=new_e.data if new_e else None,
                    local_ulid=local_e.ulid if local_e else "",
                )
            )

    return result


# ---------------------------------------------------------------------------
# Applying actions to the LOCAL index dict
# ---------------------------------------------------------------------------


def _locate_entry(local_index: dict, ulid: str) -> tuple[list, int, dict] | None:
    books = _index_books(local_index)
    for i, book in enumerate(books):
        if not isinstance(book, dict):
            continue
        if str(book.get("arc_100_ulid") or "") == ulid:
            return books, i, book
        chapters = book.get("chapters") or book.get("sub_chapters") or []
        for j, chapter in enumerate(chapters):
            if isinstance(chapter, dict) and str(chapter.get("arc_100_ulid") or "") == ulid:
                return chapters, j, chapter
    return None


def _insert_chapter_sorted(chapters: list, new_entry: dict) -> None:
    nid = str(new_entry.get("id", ""))
    for i, chapter in enumerate(chapters):
        if isinstance(chapter, dict) and str(chapter.get("id", "")) > nid:
            chapters.insert(i, new_entry)
            return
    chapters.append(new_entry)


def _band_start(book: dict) -> int:
    match = re.match(r"(\d+)", str(book.get("band") or ""))
    if match:
        return int(match.group(1))
    match = re.match(r"(\d+)", str(book.get("id") or ""))
    return int(match.group(1)) if match else 10**6


def _insert_book_sorted(books: list, new_book: dict) -> None:
    key = (_band_start(new_book), str(new_book.get("id", "")))
    for i, book in enumerate(books):
        if isinstance(book, dict) and (_band_start(book), str(book.get("id", ""))) > key:
            books.insert(i, new_book)
            return
    books.append(new_book)


def apply_action(local_index: dict, action: Action) -> bool:
    """Apply one auto-apply (or accepted) action to the LOCAL index
    dict. Returns True if it landed."""
    if action.kind == "noop":
        return False
    if action.kind == "update":
        located = _locate_entry(local_index, action.ulid)
        if located is None or action.data is None:
            return False
        _, _, entry = located
        for field_name in action.fields:
            if field_name in action.data:
                entry[field_name] = action.data[field_name]
            else:
                # §6.2 rule 1: "update LOCAL entry in place from NEW" over
                # the synced fields — a synced field the payload dropped
                # must be removed locally too, or LOCAL never converges to
                # NEW and the same entry re-classifies as an update (and
                # counts toward the bulk guard) on every refresh.
                entry.pop(field_name, None)
        entry["arc_100"] = True
        return True
    if action.kind == "insert_chapter":
        if action.data is None:
            return False
        book = _find_target_book(local_index, action.entry_id)
        if book is None:
            return False
        _insert_chapter_sorted(book.setdefault("chapters", []), action.data)
        return True
    if action.kind == "insert_book":
        if action.data is None:
            return False
        books = local_index.get("books")
        if books is None:
            books = local_index.setdefault("books", [])
        _insert_book_sorted(books, action.data)
        return True
    if action.kind == "delete":
        located = _locate_entry(local_index, action.ulid)
        if located is None:
            return False
        container, i, _ = located
        container.pop(i)
        return True
    return False


_APPLY_ORDER = {"insert_book": 0, "insert_chapter": 1, "update": 2, "delete": 3}


def apply_actions(local_index: dict, actions: list[Action]) -> int:
    """Apply a (pre-cleared, escalation-free) batch. Books insert before
    their chapters; chapter deletes run before book deletes."""
    applied = 0
    ordered = sorted(
        (a for a in actions if a.kind != "noop"),
        key=lambda a: (
            _APPLY_ORDER.get(a.kind, 9),
            0 if (a.kind == "delete" and "-" in a.entry_id) else 1,
            a.entry_id,
        ),
    )
    for action in ordered:
        if apply_action(local_index, action):
            applied += action.entry_count
    return applied


# ---------------------------------------------------------------------------
# Index serialization (lifted from conform.py write_local_index)
# ---------------------------------------------------------------------------


def write_local_index(local_index: dict, original_md: str, path: Path, project_name: str) -> None:
    start = f"<!-- {project_name}-INDEX-START -->"
    end = f"<!-- {project_name}-INDEX-END -->"
    pattern = re.compile(
        rf"({re.escape(start)}\s*\n```yaml\n).*?(\n```\s*\n{re.escape(end)})",
        re.DOTALL,
    )
    new_yaml = yaml.safe_dump(local_index, sort_keys=False, allow_unicode=True)
    rewritten = pattern.sub(
        lambda m: m.group(1) + new_yaml.rstrip() + m.group(2),
        original_md,
        count=1,
    )
    path.write_text(rewritten, encoding="utf-8")


def build_snapshot(local_index: dict) -> list[dict]:
    """index_snapshot (BASE) = projection of every inherited LOCAL
    entry: enough fields to recompute LOCAL == BASE for both classes."""
    snapshot: list[dict] = []
    for entry in flatten_entries(local_index):
        if not entry.ulid or not entry.data.get("arc_100"):
            continue
        snap: dict[str, Any] = {"arc_100_ulid": entry.ulid}
        for field_name in ("id", "band", "title", "description", "status", "keywords"):
            if field_name in entry.data:
                snap[field_name] = _deep_copy(entry.data[field_name])
        snapshot.append(snap)
    return snapshot


def merge_snapshot_after_decisions(
    old_snapshot: list[dict],
    local_index: dict,
    verdicts: dict[str, str],
) -> list[dict]:
    """§6.4 step 3 + §6.2 triggers c/f: after a decision-apply, refresh
    BASE ONLY for the ULIDs in ``verdicts`` — the decisions that
    actually LANDED (apply_decisions: accepts applied + rejects
    recorded; a skipped accept is absent). All other entries keep their
    prior BASE value, so an inherited entry the human hand-edited
    (trigger c) or deleted (trigger f) between the escalation run and
    the decision run — or whose accept was skipped as stale — still
    escalates in the same-run reconcile. Rebuilding BASE from the whole
    LOCAL index would bake those interim edits in and auto-apply over
    them. Pure.

    Per landed ULID: present in LOCAL -> its current LOCAL projection
    (accept applied / reject kept at the divergent LOCAL value, §6.2);
    absent from LOCAL -> accept means an applied delete (drop from BASE),
    reject means a kept local deletion (retain the old BASE value so a
    later, different NEW re-fires trigger f).
    """
    local_snap = {
        str(s.get("arc_100_ulid") or ""): s for s in build_snapshot(local_index)
    }
    merged: list[dict] = []
    seen: set[str] = set()
    for item in old_snapshot:
        if not isinstance(item, dict):
            continue
        ulid = str(item.get("arc_100_ulid") or "")
        seen.add(ulid)
        if ulid not in verdicts:
            merged.append(_deep_copy(item))  # undecided: prior BASE, untouched
        elif ulid in local_snap:
            merged.append(local_snap[ulid])  # decided: the new applied state
        elif verdicts[ulid] == "accept":
            continue  # accepted delete: drop from BASE
        else:
            merged.append(_deep_copy(item))  # rejected deletion: keep BASE side
    for ulid in verdicts:
        if ulid not in seen and ulid in local_snap:
            merged.append(local_snap[ulid])  # accepted insert: now in BASE
    return merged


# ---------------------------------------------------------------------------
# state.yml read/write (§6.3, fail-closed shape guard)
# ---------------------------------------------------------------------------


def _empty_state() -> dict:
    return {
        "release_tag": "",
        "source_sha": "",
        "files": {},
        "index_snapshot": [],
        "diverged": {},
    }


def load_state(path: Path) -> tuple[dict | None, bool]:
    """Read + shape-guard state.yml. Returns (state, lost):
    (None, False) when absent; (empty defaults, True) when present but
    corrupt/malshaped — the lost-state degradation path (never trust a
    malformed BASE, never raise)."""
    if not path.is_file():
        return None, False
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError, UnicodeDecodeError):
        return _empty_state(), True
    if not isinstance(raw, dict):
        return _empty_state(), True
    state = _empty_state()
    for key in ("release_tag", "source_sha"):
        value = raw.get(key, "")
        if value is None:
            value = ""
        if not isinstance(value, str):
            return _empty_state(), True
        state[key] = value
    # §6.3 fail closed: an explicit null reads as the missing-key default
    # (matching the release_tag/source_sha handling above), but ANY other
    # wrong-typed value — INCLUDING falsy ones such as '' / false / 0 /
    # [] — is a shape violation routing the whole file to lost-state.
    files = raw.get("files")
    if files is None:
        files = {}
    if not isinstance(files, dict) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in files.items()
    ):
        return _empty_state(), True
    state["files"] = files
    snapshot = raw.get("index_snapshot")
    if snapshot is None:
        snapshot = []
    if not isinstance(snapshot, list) or not all(
        isinstance(item, dict) and item.get("arc_100_ulid") for item in snapshot
    ):
        return _empty_state(), True
    state["index_snapshot"] = snapshot
    diverged = raw.get("diverged")
    if diverged is None:
        diverged = {}
    if not isinstance(diverged, dict) or not all(
        isinstance(k, str) and isinstance(v, dict) for k, v in diverged.items()
    ):
        return _empty_state(), True
    state["diverged"] = diverged
    return state, False


def write_state(target: Path, state: dict, dry_run: bool) -> None:
    if dry_run:
        return
    path = contained_path(target, STATE_REL)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "release_tag": state.get("release_tag", ""),
        "source_sha": state.get("source_sha", ""),
        "synced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files": state.get("files", {}),
        "index_snapshot": state.get("index_snapshot", []),
        "diverged": state.get("diverged", {}),
    }
    path.write_text(
        yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Mirror file class (§6.5) + dated backups
# ---------------------------------------------------------------------------


@dataclass
class MirrorStats:
    synced: int = 0
    backed_up: int = 0
    removed: int = 0
    kept: int = 0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _backup(target: Path, rel: str, stamp: str, dry_run: bool) -> None:
    src = contained_path(target, rel)
    dst = contained_path(target, f"{BACKUPS_REL}/{stamp}/{rel}")
    if dry_run:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def walk_mirror_tree(source: Path) -> dict[str, Path]:
    """Map of payload-relative path -> absolute file under <source>/mirror."""
    mirror = source / "mirror"
    if not mirror.is_dir():
        raise SyncParseError(f"payload mirror tree not found: {mirror}")
    return {
        p.relative_to(mirror).as_posix(): p
        for p in sorted(mirror.rglob("*"))
        if p.is_file()
    }


def sync_mirror_tree(
    target: Path,
    payload_files: dict[str, Path],
    old_files: dict[str, str],
    stamp: str,
    dry_run: bool,
) -> tuple[dict[str, str], MirrorStats]:
    """One pass implementing the §6.5 seven-row table. With an empty
    old_files map this is also the (defensive) bootstrap copy: any
    pre-existing target file reads as locally-edited and is backed up
    before being overwritten. Returns (new files map, stats). The new
    files map contains exactly the payload's files — paths gone from
    the payload drop out (rows 4-6)."""
    new_files: dict[str, str] = {}
    stats = MirrorStats()
    for rel in sorted(payload_files):
        src = payload_files[rel]
        new_hash = sha256_file(src)
        new_files[rel] = new_hash
        tgt = contained_path(target, rel)
        old_hash = old_files.get(rel)
        if tgt.is_file():
            disk_hash = sha256_file(tgt)
            if disk_hash != old_hash:
                _backup(target, rel, stamp, dry_run)
                stats.backed_up += 1
                print(f"mirror: ~ {rel} (locally edited; backed up, then overwritten)")
            elif disk_hash == new_hash:
                stats.synced += 1
                continue  # already current
            if disk_hash != new_hash and not dry_run:
                shutil.copy2(src, tgt)
            stats.synced += 1
            if disk_hash == old_hash:
                print(f"mirror: ^ {rel} (refreshed)")
        else:
            if not dry_run:
                tgt.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, tgt)
            stats.synced += 1
            note = " (re-created; was deleted locally)" if rel in old_files else ""
            print(f"mirror: + {rel}{note}")
    for rel in sorted(old_files):
        if rel in payload_files:
            continue
        tgt = contained_path(target, rel)
        if not tgt.is_file():
            print(f"mirror: . {rel} (gone from disk and payload; retired from state)")
            continue
        disk_hash = sha256_file(tgt)
        _backup(target, rel, stamp, dry_run)
        stats.backed_up += 1
        if disk_hash == old_files[rel]:
            if not dry_run:
                tgt.unlink()
            stats.removed += 1
            print(f"mirror: - {rel} (removed from payload; backed up, then removed)")
        else:
            stats.kept += 1
            print(
                f"mirror: ! {rel} (payload removed this, but it was locally "
                "edited — backed up and KEPT on disk; upstream it or delete it)"
            )
    return new_files, stats


# ---------------------------------------------------------------------------
# Seed file class (phase 2b): copy-if-absent, in BOTH modes
# ---------------------------------------------------------------------------


@dataclass
class SeedStats:
    added: int = 0
    skipped: int = 0


def seed_class(source: Path, target: Path, dry_run: bool) -> SeedStats:
    """Deliver ``<source>/seed/`` by copy-if-absent (phase 2b §3.1),
    in BOTH bootstrap and refresh modes, relpath-preserving (P1 stores
    seed files under their FINAL target names; nothing is renamed
    here). For each file: containment-check the target path (2a's one
    write gate), then skip if ANY directory entry already exists there
    — ``os.path.lexists``, not ``exists()``: a dangling symlink counts
    as present, so ``copy2`` can never write *through* a link — else
    copy. An existing target is never overwritten and never backed up.
    Seed paths are NOT recorded in ``state.yml.files`` (project-owned
    after seeding; no refresh contract). A missing or empty ``seed/``
    is a clean no-op. Under dry-run, counts and prints but writes
    nothing."""
    stats = SeedStats()
    seed_root = source / "seed"
    if not seed_root.is_dir():
        return stats
    for src in sorted(seed_root.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(seed_root).as_posix()
        tgt = contained_path(target, rel)
        if os.path.lexists(tgt):
            stats.skipped += 1
            continue
        if not dry_run:
            tgt.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, tgt)
        stats.added += 1
        print(f"seed: + {rel}")
    return stats


# ---------------------------------------------------------------------------
# Doctor (phase 2b): presence-only toolchain checks + prepared commands
# ---------------------------------------------------------------------------

# (probe key, display label, prepared command printed when absent).
# The commands are PRINTED, never invoked — the doctor is the safe
# residue of the charter's cut guided installer.
_DOCTOR_CHECKS: tuple[tuple[str, str, str], ...] = (
    (
        "mkdocs",
        "docs build deps (mkdocs)",
        "python3 -m pip install --user --require-hashes -r requirements.txt",
    ),
    (
        "node",
        "Node (LikeC4 authoring, optional)",
        "install Node (≥ the LikeC4 toolchain's engines.node) via your "
        "platform's package manager",
    ),
    (
        "likec4",
        "LikeC4 toolchain (architecture/LikeC4/node_modules)",
        "( cd architecture/LikeC4 && npm ci --no-fund --no-audit )",
    ),
)


def doctor_report(probes: dict[str, bool]) -> list[str]:
    """Pure formatting of the doctor probes: present -> ``✓ <tool>``;
    absent -> ``→ <tool> not detected — run: <command>``. No I/O; a
    missing optional tool is a printed suggestion, never a failure —
    the doctor never alters the run's exit code."""
    lines: list[str] = []
    for key, label, command in _DOCTOR_CHECKS:
        if probes.get(key):
            lines.append(f"✓ {label}")
        else:
            lines.append(f"→ {label} not detected — run: {command}")
    return lines


def doctor(target: Path) -> dict[str, bool]:
    """Presence-only probes (phase 2b §3.1): no subprocess and no
    ``node --version`` — nothing to spawn, so the doctor can never
    hang, install, or traceback the sync. Node is presence-only by
    design (no version floor; the LikeC4 ``npm ci`` enforces
    ``engines.node`` itself at install time)."""
    try:
        import mkdocs  # noqa: F401  (presence probe only)

        has_mkdocs = True
    except ImportError:
        has_mkdocs = False
    return {
        "mkdocs": has_mkdocs,
        "node": shutil.which("node") is not None,
        "likec4": (target / "architecture/LikeC4/node_modules").is_dir(),
    }


# ---------------------------------------------------------------------------
# Decision file (§6.4): build, write, read, apply-on-next-run
# ---------------------------------------------------------------------------


def _escaped_entry_view(data: dict | None) -> tuple[dict | None, str | None]:
    """Escaped projection of an entry for decision-file cells. Returns
    (view, first_violation_or_None); malformed cells are sentinel-ized."""
    if data is None:
        return None, None
    view: dict[str, Any] = {}
    violation: str | None = None
    if data.get("arc_100_ulid"):
        view["arc_100_ulid"] = _safe_cell(data.get("arc_100_ulid"))
    if "arc_100" in data:
        view["arc_100"] = bool(data.get("arc_100"))
    for field_name in ("id", "band", "title", "description", "status"):
        if field_name in data:
            escaped = md_cell_escape(data[field_name])
            if isinstance(escaped, MalformedUpstream):
                view[field_name] = f"<malformed:{escaped.reason}>"
                violation = violation or f"{field_name}: {escaped.reason}"
            else:
                view[field_name] = escaped
    keywords = data.get("keywords")
    if isinstance(keywords, list):
        cells = []
        for item in keywords:
            escaped = md_cell_escape(item)
            if isinstance(escaped, MalformedUpstream):
                cells.append(f"<malformed:{escaped.reason}>")
                violation = violation or f"keywords: {escaped.reason}"
            else:
                cells.append(escaped)
        view["keywords"] = cells
    return view, violation


def build_decision_blocks(escalations: list[Escalation]) -> list[dict]:
    """Render escalations as decision blocks. Every upstream-sourced
    string passes md_cell_escape; a proposed entry with a failing field
    becomes a malformed_upstream decision (never raw into the file)."""
    blocks: list[dict] = []
    for esc in escalations:
        proposed, proposed_bad = _escaped_entry_view(esc.proposed)
        current, _ = _escaped_entry_view(esc.current)
        kind, action, reason = esc.kind, esc.action, esc.reason
        if proposed_bad and kind != "malformed_upstream":
            kind = "malformed_upstream"
            action = "none"
            reason = f"upstream field rejected ({proposed_bad}); was: {reason}"
        if kind == "malformed_upstream":
            reason += " — no safe accept exists; reject it or fix upstream"
        blocks.append(
            {
                "id": compute_decision_id(kind, esc.ulid, esc.local_ulid),
                "kind": kind,
                "ulid": esc.ulid,
                "action": action,
                "reason": _safe_cell(reason),
                "current": current,
                "proposed": proposed,
                "decision": None,
            }
        )
    return blocks


def write_decision_file(
    target: Path,
    blocks: list[dict],
    release_tag: str,
    source_sha: str,
    dry_run: bool,
) -> None:
    doc = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "release_tag": release_tag,
        "source_sha": source_sha,
        "decisions": blocks,
    }
    text = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True)
    if dry_run:
        print("--- decision-file preview (dry run; nothing written) ---")
        print(text, end="")
        print("--- end preview ---")
        return
    path = contained_path(target, PENDING_REL)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_pending(path: Path) -> list[dict]:
    """Parse + shape-guard the pending decision file (a trust input:
    yaml.safe_load only; fail closed on shape violations)."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError, UnicodeDecodeError) as exc:
        raise SyncParseError(f"pending decision file unreadable: {exc}") from exc
    if not isinstance(raw, dict) or not isinstance(raw.get("decisions"), list):
        raise SyncParseError(
            "pending decision file malformed (expected mapping with a 'decisions' list)"
        )
    decisions = [d for d in raw["decisions"] if isinstance(d, dict)]
    if len(decisions) != len(raw["decisions"]):
        raise SyncParseError("pending decision file malformed (non-mapping decision item)")
    return decisions


def _decision_value(block: dict) -> str:
    value = block.get("decision")
    return value.strip().lower() if isinstance(value, str) else ""


def apply_decisions(
    decisions: list[dict],
    local_index: dict,
    new_by_ulid: dict[str, Entry],
    diverged: dict[str, dict],
) -> tuple[int, int, list[str], dict[str, str]]:
    """Apply a fully-answered decision set to the LOCAL index dict (in
    memory). Accepts apply from the CURRENT payload (re-gated; skipped
    with a warning when stale). Rejects are recorded into ``diverged``
    keyed by ULID = the rejected NEW value ({'deleted': true} when the
    rejection was of an upstream deletion). Returns
    (accepted_applied, rejected_recorded, warnings, landed_verdicts).

    ``landed_verdicts`` maps ULID -> "accept"/"reject" for ONLY the
    decisions that actually landed: accepts applied + rejects recorded
    (rejects are never skipped). A skipped accept (stale payload entry,
    malformed content, target missing) applied nothing, so it is
    deliberately absent — its BASE entry must keep the prior value so
    the same-run reconcile genuinely re-escalates it (§6.4 step 3)."""
    accepted = 0
    rejected = 0
    warnings: list[str] = []
    landed_verdicts: dict[str, str] = {}
    insert_order = {"insert_book": 0, "insert_chapter": 1, "update": 2, "delete": 3}
    ordered = sorted(
        decisions, key=lambda d: insert_order.get(str(d.get("action") or ""), 9)
    )
    for block in ordered:
        ulid = str(block.get("ulid") or "")
        verdict = _decision_value(block)
        ident = block.get("id") or ulid or "?"
        if not ulid:
            warnings.append(f"decision {ident}: no ulid recorded; skipped")
            continue
        if verdict == "reject":
            new_e = new_by_ulid.get(ulid)
            if new_e is None:
                diverged[ulid] = {"deleted": True}
            else:
                fields = synced_fields_for(new_e.id)
                record = {
                    f: _deep_copy(new_e.data.get(f))
                    for f in fields
                    if f in new_e.data
                }
                record.setdefault("id", new_e.id)
                diverged[ulid] = record
            rejected += 1
            landed_verdicts[ulid] = "reject"
            print(f"decision: reject {ident} -> recorded in diverged")
            continue
        # accept
        action = str(block.get("action") or "none")
        if action == "none":
            warnings.append(
                f"decision {ident}: accept has no applicable action "
                "(malformed upstream content is never written); it will re-escalate"
            )
            continue
        if action == "delete":
            if ulid in new_by_ulid:
                warnings.append(
                    f"decision {ident}: stale accept (entry is back in the payload); "
                    "skipped — the refresh will re-evaluate"
                )
                continue
            if apply_action(local_index, Action(kind="delete", ulid=ulid, entry_id="")):
                accepted += 1
                landed_verdicts[ulid] = "accept"
                print(f"decision: accept {ident} -> deleted {ulid}")
            else:
                warnings.append(f"decision {ident}: entry already gone; nothing to delete")
            continue
        new_e = new_by_ulid.get(ulid)
        if new_e is None:
            warnings.append(
                f"decision {ident}: stale accept (entry no longer in the payload); skipped"
            )
            continue
        violation = entry_field_violation(new_e.data, include_chapters=(new_e.kind == "book"))
        if violation:
            warnings.append(
                f"decision {ident}: payload entry now malformed ({violation}); "
                "not applied — it will re-escalate"
            )
            continue
        fresh_view, _ = _escaped_entry_view(new_e.data)
        if block.get("proposed") is not None and fresh_view != block.get("proposed"):
            warnings.append(
                f"decision {ident}: stale accept (payload entry changed since "
                "escalation); skipped — the refresh will re-evaluate"
            )
            continue
        if action == "update":
            fields = synced_fields_for(new_e.id)
            landed = apply_action(
                local_index,
                Action(
                    kind="update",
                    ulid=ulid,
                    entry_id=new_e.id,
                    data=_deep_copy({k: v for k, v in new_e.data.items() if k != "chapters"}),
                    fields=fields,
                ),
            )
        elif action in ("insert_chapter", "insert_book"):
            kind_word = "chapter" if action == "insert_chapter" else "book"
            landed = apply_action(
                local_index,
                Action(
                    kind=action,
                    ulid=ulid,
                    entry_id=new_e.id,
                    data=_sanitized_insert(new_e.data, kind_word),
                ),
            )
        else:
            warnings.append(f"decision {ident}: unknown action {action!r}; skipped")
            continue
        if landed:
            accepted += 1
            landed_verdicts[ulid] = "accept"
            print(f"decision: accept {ident} -> {action} {new_e.id}")
        else:
            warnings.append(
                f"decision {ident}: accept could not be applied "
                "(target missing); it will re-escalate"
            )
    return accepted, rejected, warnings, landed_verdicts


# ---------------------------------------------------------------------------
# Bootstrap (index part lifted from conform.py bootstrap())
# ---------------------------------------------------------------------------


def _retarget_book00_links(md: str, config: Config) -> str:
    """Seed-time link fix. The upstream index (00-01) lives flattened at the
    standard's own ``docs_dir`` root, so its PROSE links to Book 00 chapters
    are sibling-relative (``](00-NN_*.md``). Seeded verbatim into the working
    index at ``<chapter_root>/01/01-01_*`` those break, because Book 00 lives a
    directory across at ``<chapter_root>/00/``. Rewrite the link targets to the
    relative path from the index's directory to ``<chapter_root>/00`` so they
    resolve in the downstream tree. The source stays sibling-relative (the
    standard's own red site is unaffected); only the seeded copy is retargeted.

    Touches ONLY prose OUTSIDE the index marker block — the YAML between the
    markers is (re)written from the entry dict by ``write_local_index`` and
    uses ``[BB-CC §N]`` citations, not file links. Pure.
    """
    index_dir = config.local_index_path.parent.as_posix()
    book00_dir = (config.local_chapter_root / "00").as_posix()
    prefix = posixpath.relpath(book00_dir, index_dir)
    if prefix in ("", "."):
        return md  # index sits beside Book 00 — sibling links already resolve
    link_re = re.compile(r"\]\((00-\d\d[^)\s#]*\.md)")

    def retarget(seg: str) -> str:
        return link_re.sub(lambda m: f"]({prefix}/{m.group(1)}", seg)

    start = f"<!-- {config.project_name}-INDEX-START -->"
    end = f"<!-- {config.project_name}-INDEX-END -->"
    si = md.find(start)
    ei = md.find(end)
    if si == -1 or ei == -1:
        return retarget(md)  # no marker block found — retarget the whole doc
    ej = ei + len(end)
    return retarget(md[:si]) + md[si:ej] + retarget(md[ej:])


def bootstrap_index(
    payload_md: str,
    payload_dict: dict,
    config: Config,
    target: Path,
    stamp: str,
    dry_run: bool,
) -> int:
    """Verbatim payload-index copy with the marker pair swapped to
    <project_name>-INDEX-*. The malformed gate ran before this (a
    failing field ABORTS bootstrap). Returns inherited entry count."""
    target_md = payload_md.replace(
        UPSTREAM_START, f"<!-- {config.project_name}-INDEX-START -->"
    ).replace(UPSTREAM_END, f"<!-- {config.project_name}-INDEX-END -->")
    # Retarget Book-00 prose links so they resolve from the working index's
    # location (the upstream source keeps its sibling-relative links).
    target_md = _retarget_book00_links(target_md, config)
    rel = config.local_index_path.as_posix()
    path = contained_path(target, rel)
    if path.is_file():
        _backup(target, rel, stamp, dry_run)
        print(f"index: ~ {rel} (pre-existing; backed up before bootstrap write)")
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        write_local_index(payload_dict, target_md, path, config.project_name)
    entries = [e for e in flatten_entries(payload_dict) if e.ulid]
    print(f"index: bootstrapped {len(entries)} entries into {rel}")
    return len(entries)


# ---------------------------------------------------------------------------
# Run flows
# ---------------------------------------------------------------------------


def read_release_meta(source: Path) -> tuple[str, str]:
    """Release metadata convention — see the module docstring."""
    meta = source / "payload.yml"
    if meta.is_file():
        try:
            raw = yaml.safe_load(meta.read_text(encoding="utf-8"))
        except (yaml.YAMLError, UnicodeDecodeError):
            print("WARNING: payload.yml unreadable; using release_tag=local", file=sys.stderr)
            return "local", ""
        if isinstance(raw, dict):
            return str(raw.get("release_tag") or "local"), str(raw.get("source_sha") or "")
    return "local", ""


def find_payload_index(payload_files: dict[str, Path]) -> str:
    """The payload index source: mirror/docs/00/00-01_*Inventory.md."""
    candidates = [
        rel
        for rel in payload_files
        if re.fullmatch(r"docs/00/00-01_.*Inventory\.md", rel)
    ]
    if len(candidates) != 1:
        raise SyncParseError(
            "expected exactly one payload index (mirror/docs/00/00-01_*Inventory.md); "
            f"found {len(candidates)}"
        )
    return candidates[0]


def _local_index_seeded(target: Path, config: Config) -> bool:
    """True when the local index exists and carries inherited entries —
    the 'clearly already seeded' test for lost-state degradation."""
    try:
        path = contained_path(target, config.local_index_path.as_posix())
    except PathEscapeError:
        return False
    if not path.is_file():
        return False
    try:
        local_dict = extract_yaml(
            path.read_text(encoding="utf-8"),
            f"<!-- {config.project_name}-INDEX-START -->",
            f"<!-- {config.project_name}-INDEX-END -->",
        )
    except (SyncParseError, OSError, UnicodeDecodeError):
        return False
    return any(
        e.ulid and e.data.get("arc_100") for e in flatten_entries(local_dict)
    )


def run_bootstrap(
    target: Path,
    source: Path,
    config: Config,
    payload_files: dict[str, Path],
    payload_md: str,
    payload_dict: dict,
    release_tag: str,
    source_sha: str,
    stamp: str,
    dry_run: bool,
) -> int:
    # Malformed gate over EVERY payload entry BEFORE any write — a
    # failing field aborts bootstrap naming the offending entry (§6.2).
    for entry in flatten_entries(payload_dict):
        violation = entry_field_violation(entry.data)
        if violation:
            print(
                f"ERROR: bootstrap aborted — payload entry {entry.kind} "
                f"{entry.id or entry.ulid or '?'} has a malformed field ({violation})",
                file=sys.stderr,
            )
            return 2
    files_map, stats = sync_mirror_tree(target, payload_files, {}, stamp, dry_run)
    seed_stats = seed_class(source, target, dry_run)
    applied = bootstrap_index(payload_md, payload_dict, config, target, stamp, dry_run)
    state = {
        "release_tag": release_tag,
        "source_sha": source_sha,
        "files": files_map,
        "index_snapshot": build_snapshot(payload_dict),
        "diverged": {},
    }
    write_state(target, state, dry_run)
    mode = "bootstrap (dry run)" if dry_run else "bootstrap"
    print(
        f"summary: mode={mode}; files synced={stats.synced} "
        f"backed_up={stats.backed_up} removed={stats.removed} kept={stats.kept}; "
        f"seeded {seed_stats.added} (skipped {seed_stats.skipped}); "
        f"index entries applied={applied} escalated=0"
    )
    return 0


def run_refresh(
    target: Path,
    source: Path,
    config: Config,
    payload_files: dict[str, Path],
    payload_dict: dict,
    state: dict,
    lost_state: bool,
    release_tag: str,
    source_sha: str,
    stamp: str,
    dry_run: bool,
) -> int:
    if lost_state:
        print(
            "WARNING: state.yml is missing or malformed — lost-state degradation: "
            "no BASE; every inherited difference will escalate and all mirror "
            "files read as locally edited",
            file=sys.stderr,
        )

    index_rel = config.local_index_path.as_posix()
    index_path = contained_path(target, index_rel)
    if not index_path.is_file():
        print(
            f"ERROR: refresh mode but local index missing at {index_rel} — "
            "on-disk state is inconsistent; not improvising a third mode",
            file=sys.stderr,
        )
        return 2
    local_md = index_path.read_text(encoding="utf-8")
    local_index = extract_yaml(
        local_md,
        f"<!-- {config.project_name}-INDEX-START -->",
        f"<!-- {config.project_name}-INDEX-END -->",
    )
    verify_ulid_coverage(local_index, side="local", require_arc_100=True)
    verify_ulid_coverage(payload_dict, side="payload", require_arc_100=False)
    new_by_ulid = index_entries_by_ulid(payload_dict)
    diverged: dict[str, dict] = _deep_copy(state.get("diverged") or {})

    # --- Decision lifecycle (§6.4): a pending file is handled FIRST ---
    pending_path = contained_path(target, PENDING_REL)
    if pending_path.is_file():
        decisions = load_pending(pending_path)
        unresolved = [d for d in decisions if _decision_value(d) not in _VALID_DECISIONS]
        if unresolved:
            print(
                f"{len(unresolved)} of {len(decisions)} decisions in {PENDING_REL} "
                "still need decision: accept | reject. Nothing was applied. "
                "Fill them in and re-run the same command."
            )
            return 1
        accepted, rejected, warnings, landed_verdicts = apply_decisions(
            decisions, local_index, new_by_ulid, diverged
        )
        for warning in warnings:
            print(f"WARNING: {warning}", file=sys.stderr)
        state["diverged"] = diverged
        # §6.4 step 3 + §6.2 triggers c/f: refresh BASE only for the
        # ULIDs whose decision actually LANDED (accepts applied +
        # rejects recorded). A whole-index rebuild here would bake any
        # interim hand edit (or deletion) of an UNDECIDED inherited
        # entry into BASE, and the same-run reconcile below would then
        # silently auto-apply over it instead of escalating. A SKIPPED
        # accept (stale / target missing) applied nothing, so it too
        # keeps its prior BASE value and genuinely re-escalates below.
        state["index_snapshot"] = merge_snapshot_after_decisions(
            state.get("index_snapshot") or [], local_index, landed_verdicts
        )
        if not dry_run:
            write_local_index(local_index, local_md, index_path, config.project_name)
            write_state(target, state, dry_run)
            archive = contained_path(target, f"{ARCHIVE_REL}/{stamp}.yml")
            archive.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pending_path, archive)
            pending_path.unlink()
            print(f"decision: archived to {ARCHIVE_REL}/{stamp}.yml")
        print(
            f"decision: applied accepts={accepted} rejects={rejected}; "
            "continuing refresh against the current payload"
        )

    # --- Mirror file class (independent of the index batch; §6.5) ---
    files_map, stats = sync_mirror_tree(
        target, payload_files, dict(state.get("files") or {}), stamp, dry_run
    )

    # --- Seed file class (phase 2b; also independent of the index batch):
    #     copy-if-absent, so a NEWLY-added upstream seed file reaches an
    #     existing adopter, while anything already on disk is untouched. ---
    seed_stats = seed_class(source, target, dry_run)

    # --- 3-way reconcile (atomic index batch; §6.2) ---
    result = reconcile_index(
        state.get("index_snapshot") or [], payload_dict, local_index, diverged
    )
    for ulid in result.diverged_drop:
        diverged.pop(ulid, None)
        print(f"index: diverged entry {ulid} re-opened (payload now proposes something new)")

    state["release_tag"] = release_tag
    state["source_sha"] = source_sha
    state["files"] = files_map
    state["diverged"] = diverged

    if result.escalations:
        for esc in result.escalations:
            print(f"index: escalate {esc.kind} {esc.ulid}: {_safe_cell(esc.reason)}")
        blocks = build_decision_blocks(result.escalations)
        write_decision_file(target, blocks, release_tag, source_sha, dry_run)
        # Apply ZERO index changes; mirror files synced; files map (NOT
        # index_snapshot) still updates (§6.2 atomic batch).
        write_state(target, state, dry_run)
        mode = "refresh (dry run)" if dry_run else "refresh"
        print(
            f"summary: mode={mode}; files synced={stats.synced} "
            f"backed_up={stats.backed_up} removed={stats.removed} kept={stats.kept}; "
            f"seeded {seed_stats.added} (skipped {seed_stats.skipped}); "
            f"index entries applied=0 escalated={len(result.escalations)}"
        )
        print(
            f"ACTION REQUIRED: review {PENDING_REL}, set each decision to "
            "accept or reject, then re-run this same command."
        )
        return 1

    applied = 0
    if any(a.kind != "noop" for a in result.actions):
        for action in result.actions:
            if action.kind != "noop":
                print(f"index: {action.kind} {action.entry_id} ({action.ulid})")
        applied = apply_actions(local_index, result.actions)
        if not dry_run:
            write_local_index(local_index, local_md, index_path, config.project_name)
    state["index_snapshot"] = build_snapshot(local_index)
    write_state(target, state, dry_run)
    mode = "refresh (dry run)" if dry_run else "refresh"
    print(
        f"summary: mode={mode}; files synced={stats.synced} "
        f"backed_up={stats.backed_up} removed={stats.removed} kept={stats.kept}; "
        f"seeded {seed_stats.added} (skipped {seed_stats.skipped}); "
        f"index entries applied={applied} escalated=0"
    )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="arc_sync",
        description=(
            "ARC-100 install + refresh from a local payload tree. Mode is "
            "implicit: .arc100/state.yml present means refresh, absent means "
            "bootstrap. No network access of any kind."
        ),
    )
    parser.add_argument(
        "--target", type=Path, default=Path("."), help="adopting repo root (default: .)"
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="payload root containing mirror/ (default: this script's clone root)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="classify and print everything; write nothing under --target",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="ARC-100-SYNC.config.yml",
        help="config path, resolved under --target",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")  # one run-level stamp
    target: Path = args.target
    source: Path = args.source
    dry_run: bool = args.dry_run

    try:
        if not target.is_dir():
            print(f"ERROR: --target is not a directory: {target}", file=sys.stderr)
            return 2
        config_path = contained_path(target, str(args.config))
        if not config_path.is_file():
            print(f"ERROR: config not found: {config_path}", file=sys.stderr)
            return 2
        config = load_config(config_path)
        # Fail-fast containment (security-critical): a hostile EXPLICIT
        # local_index_path override (e.g. ../escape.md) raises PathEscapeError
        # here — before any mirror/seed write runs. The DERIVED path is guarded
        # upstream by load_config's project_name shape gate (the fused filename
        # segment defeats post-interpolation containment for the derived case).
        contained_path(target, config.local_index_path.as_posix())

        payload_files = walk_mirror_tree(source)
        index_rel = find_payload_index(payload_files)
        if config.local_index_path.as_posix() in payload_files:
            print(
                "ERROR: local_index_path collides with a payload mirror path "
                f"({config.local_index_path}) — fix the config",
                file=sys.stderr,
            )
            return 2
        payload_md = payload_files[index_rel].read_text(encoding="utf-8")
        payload_dict = extract_yaml(payload_md, UPSTREAM_START, UPSTREAM_END)
        release_tag, source_sha = read_release_meta(source)

        state_path = contained_path(target, STATE_REL)
        state, lost = load_state(state_path)
        if state is None and not lost and _local_index_seeded(target, config):
            # Seeded repo with no state file: lost-state refresh, never a
            # clobbering bootstrap (§6.2 lost-state degradation).
            state, lost = _empty_state(), True

        if dry_run:
            print("arc-sync: DRY RUN — nothing will be written under --target")
        print(
            f"arc-sync: target={target} source={source} "
            f"release={release_tag} sha={source_sha or '(none)'}"
        )

        if state is None:
            pending = contained_path(target, PENDING_REL)
            if pending.is_file():
                print(
                    f"ERROR: {PENDING_REL} exists but the repo is unseeded — "
                    "remove or resolve it before bootstrapping",
                    file=sys.stderr,
                )
                return 2
            verify_ulid_coverage(payload_dict, side="payload", require_arc_100=False)
            code = run_bootstrap(
                target, source, config, payload_files, payload_md, payload_dict,
                release_tag, source_sha, stamp, dry_run,
            )
        else:
            code = run_refresh(
                target, source, config, payload_files, payload_dict, state, lost,
                release_tag, source_sha, stamp, dry_run,
            )
        # Doctor (phase 2b): printed at the end of EVERY run, after the
        # sync summary — informational only, never touches the exit code.
        print("Toolchain:")
        for line in doctor_report(doctor(target)):
            print(f"  {line}")
        return code
    except (SyncParseError, PathEscapeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERROR: filesystem failure: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
