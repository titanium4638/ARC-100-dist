---
title: 00-01 ARC-100 Index
arc_100_id: "00-01"
status: active
keywords: [arc-100, index, chapters, master, version, ata-100]
agent_summary: |
  The machine-parseable + human-readable master index of every ARC-100
  chapter. The YAML block between the ARC-100-INDEX-START and
  ARC-100-INDEX-END markers is the source of truth — agents extract
  the block by marker, never by file scan. Per-band prose follows the
  YAML block; substantive policy lives in 00-00_ARC-100_General.md.
prerequisites: ["00-00_ARC-100_General.md"]
companions: ["00-00_ARC-100_General.md"]
---

## 00-01 ARC-100 Index

> **What this chapter is.** The full chapter list for the ARC-100
> documentation system. The YAML block below — between the
> `ARC-100-INDEX-START` and `ARC-100-INDEX-END` markers — is the
> machine-parseable source of truth. Per-band prose after the block
> describes intent and reading order for human readers.
>
> **What this chapter is not.** A list of every chapter a project may
> ever need. ARC-100 lists only the chapters common to most networked
> applications. Project-specific chapters (e.g., a workflow engine's
> mutation pipeline; a code-scan tool's perspective registry) are
> allocated by the project's librarian into the unallocated slots
> below, without amending ARC-100 itself.
>
> **Source of truth.** This file. Agents read it by marker extraction;
> never read both copies of `00-01` and merge (see [`00-00_ARC-100_General.md` §00-00.9](00-00_ARC-100_General.md#00-009-active-version-copy-rule-for-00-01)).

### 00-01.1 — How to read this index

- **Status taxonomy** is defined in [§00-00.6](00-00_ARC-100_General.md#00-006-status-lifecycle).
- **Band structure** is defined in [§00-00.7](00-00_ARC-100_General.md#00-007-band-allocation).
- A `placeholder` entry means the chapter slot is reserved — no `.md`
  file exists at the ARC-100 path yet.
- An `active` entry means the file exists at the ARC-100 path under
  `docs/master/architecture/`.
- An entry tagged `(optional)` in the description is a chapter that
  many but not all networked applications will need. Skip the slot if
  the project does not require it; the number stays burned per ATA
  precedent.
- An entry tagged `(speculative)` is a forward-looking allocation
  that may or may not become real. It reserves the number so future
  planners do not re-allocate it.
- **Gaps are intentional.** Slot numbers absent from this index (e.g.,
  no book `42`, `43`, `44` in band 40-59) are deliberately left
  unallocated for project-specific use.
- **This index vs your project's index.** In an adopting project this
  file is a read-only mirror. The project's own table of contents is
  the **working index** at chapter `01-01`, which starts as an exact
  copy of this index at bootstrap and grows project-specific entries
  from there; `arc_100: true` marks which working-index entries are
  inherited from here. See
  [`00-00` §00-00.10.1](00-00_ARC-100_General.md#00-00101-one-standard-two-indexes).

### 00-01.2 — Index block

The YAML block is the source of truth. mkdocs renders it as a styled
code listing; agents extract it by the marker pair.

<!-- ARC-100-INDEX-START -->

```yaml
arc_100_version: "100.2"
active_version: null

bands:
  - range: "00-09"
    title: "Application"
    description: "The application's most fundamental identity — what it is, who it serves, why it exists. Topics in this band stand apart from technology choices and would remain true through a complete reimplementation in a different stack. Hosts the ARC-100 documentation-indexing system itself (Book 00, upstream-owned and body-synced) and the active project's documentation-system instance + project identity (Books 01–02, upstream-prescribed slot identity with project-authored body content). Books 03–09 open for project allocation."
    unallocated_book_slots: 7
  - range: "10-19"
    title: "Governance"
    description: "Glossary, roadmap, decisions, versioning policy. Process and governance docs that span the whole system."
    unallocated_book_slots: 6
  - range: "20-39"
    title: "Client"
    description: "Client-side / frontend / user-facing surface. Foundations, server communication, UI, rendering, browser-side concerns. Optional — not every system has a client."
    unallocated_book_slots: 17
  - range: "40-59"
    title: "Server"
    description: "Server-side / backend / engine. Transport, Application Programming Interface (API) contract, handlers, identity, runtime, audit. Optional — not every system has a server."
    unallocated_book_slots: 13
  - range: "60-79"
    title: "Data"
    description: "Schema, persistence, client hydration wire, asset data, audit data, identity data, migrations. Optional — not every system has persistent state."
    unallocated_book_slots: 13
  - range: "80-89"
    title: "Tooling"
    description: "The materials, instruments, and conventions used to build, validate, and integrate the application. Tooling chapters are contributor-facing — needed by anyone working on the system, never read by a user. Includes the development environment, lint, functional/performance/security testing, the repository, and the Continuous Integration (CI) pipeline."
    unallocated_book_slots: 3
  - range: "90-99"
    title: "Operations"
    description: "Cross-cutting operational concerns: observability, capacity, deployment, security, software composition analysis, compliance."
    unallocated_book_slots: 4

books:

  # =====================================================================
  # 00-09 — Application
  # =====================================================================

  - id: "00"
    arc_100: true
    arc_100_ulid: 01KRRRFNG8VB72WSCTYTE4NCSY
    title: "ARC-100 System"
    band: "00-09"
    description: "The documentation-indexing system itself: numbering, lifecycle, master/version split, agent rules, glossary, the mkdocs site that hosts it, comparisons against widely-cited external standards, and the synchronization system that keeps downstream <PROJECT>-100 instances in step with upstream."
    chapters:
      - id: "00-00"
        arc_100: true
        arc_100_ulid: 01KRRRFNG9Z2GN76SDXABGV961
        title: "General"
        status: "active"
        location: "master"
        description: "Canonical specification of the ARC-100 system: numbering, lifecycle, master/version split, agent rules."
        keywords: ["arc-100", "ata-100", "specification", "general"]
      - id: "00-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNG96P6KZHXZN2F7A60D
        title: "Index"
        status: "active"
        location: "master"
        description: "This file. Machine-parseable + human-readable index of every band, book, and chapter."
        keywords: ["arc-100", "index", "chapters"]
      - id: "00-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNG946YD5HE48J5KHF40
        title: "Glossary"
        status: "active"
        location: "master"
        description: "Glossary of terms for ARC-100 and preemptive indexing systems in general."
        keywords: ["arc-100", "glossary", "preemptive-indexing", "ata-100"]
      - id: "00-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNG926EMBDS895PJ8V0Z
        title: "Documentation Site"
        status: "active"
        location: "master"
        description: "Architecture of the mkdocs site that hosts these chapters: mkdocs.yml configuration, the YAML-driven index generator hook, the css/js customisations, the local-development VS Code task, and the minimal-change recipe for forking the site to another ARC-100 project."
        keywords: ["mkdocs", "documentation-site", "hosting", "hook", "vscode-tasks", "fork"]
      - id: "00-04"
        arc_100: true
        arc_100_ulid: 01KRRRFNG9ZA7F8A9MBY1H3B18
        title: "Standards Comparisons"
        status: "active"
        location: "master"
        description: "Comparison of ARC-100 to nine widely-cited industry standards covering architecture documentation, software engineering body of knowledge, IT service management, security maturity, and DevOps performance. Establishes each standard's intent and maintenance status, quantifies the topical overlap with ARC-100, and serves as the reference point for periodic re-evaluation via the reassess-standards-comparisons command."
        keywords: ["standards", "comparison", "arc42", "c4", "kruchten", "iso-42010", "swebok", "itil", "owasp-samm", "dora", "aws-well-architected"]
      - id: "00-05"
        arc_100: true
        arc_100_ulid: 01KRYVR57C69BW03FKQNTW90TR
        title: "Synchronization"
        status: "active"
        location: "master"
        description: "Architectural intent for ARC-100-SYNC — the portable toolkit that keeps an adopting <PROJECT>-100 documentation index in step with upstream ARC-100 over time. Documents the ULID-keyed identity model, the sync-and-rectify contract (deterministic auto-applied index diffs vs human-judgment-required escalations), the three operating modes (bootstrap, refresh, lost-state), the judgment surface (the YAML decision file, banner, librarian fill-in), the distribution model (a depth-1 clone of the public mirror run via arc_sync.py, mirror/seed file classes, two-axis versioning), the security posture, and the open architectural questions for review. Implementation is owned by the v2 phase plans in `versions/v2/implementation/` and the built tool `ARC-100-SYNC/scripts/arc_sync.py`."
        keywords: ["arc-100-sync", "sync", "synchronization", "ulid", "downstream", "clone", "supply-chain"]
      - id: "00-06"
        arc_100: true
        arc_100_ulid: 01KSE0GASHFB44EP78FVE2WDGP
        title: "Architectural Modeling"
        status: "active"
        location: "master"
        description: "How ARC-100 uses LikeC4 for architectural modeling: C4 model integration, agent-maintained diagrams, embedded per-chapter views, and the LikeC4 author/introspection skills distributed to downstream projects."
        keywords: ["architecture", "modeling", "c4", "likec4", "diagrams", "agent"]
      - id: "00-07"
        arc_100: true
        arc_100_ulid: 01KSXZEGBBFAK56AEW15316F5P
        title: "Getting Started"
        status: "active"
        location: "master"
        description: "Onboarding guide for adopting ARC-100 in a project: clone the public mirror and run the sync, post-sync setup, the first sync, where project docs go, the two agents, removal, and troubleshooting."
        keywords: ["getting-started", "clone", "onboarding", "adopt", "downstream", "sync", "likec4", "agents"]

  - id: "01"
    arc_100: true
    arc_100_ulid: 01KSG5QQXJS3H2QH0WQXPDRQN9
    title: "<NAME> System"
    band: "00-09"
    description: "The active project's documentation-system instance. Each project (ARC-100 itself, FLOW-100, CS-100, ...) fills in this book with its own General intro, comprehensive Index, Architectural Modeling specifics, Documentation Site configuration, and any project-specific Extensions. Slot identities are upstream-prescribed; bodies are project-authored. See §00-00.7.1 body-ownership clause and §00-00.7.2."
    chapters:
      - id: "01-00"
        arc_100: true
        arc_100_ulid: 01KSG5QQYJHEZHZWRKW31RWZAR
        title: "General"
        status: "placeholder"
        location: "master"
        description: "Project intro to the documentation-system instance. Body project-authored; slot identity upstream-prescribed."
        keywords: ["project", "system", "general"]
      - id: "01-01"
        arc_100: true
        arc_100_ulid: 01KSG5QQZJ933EXV89A5NP71A5
        title: "Index"
        status: "placeholder"
        location: "master"
        description: "Comprehensive navigation index for the project (Book 00 inherited entries + project allocations across all bands). Body project-authored; slot identity upstream-prescribed."
        keywords: ["project", "index", "navigation"]
      - id: "01-02"
        arc_100: true
        arc_100_ulid: 01KSG5QR0KGRPZ6DPAT8B51MNM
        title: "Architectural Modeling"
        status: "placeholder"
        location: "master"
        description: "Project's LikeC4 model, view styles, embedding conventions. Body project-authored; slot identity upstream-prescribed."
        keywords: ["project", "architecture", "likec4"]
      - id: "01-03"
        arc_100: true
        arc_100_ulid: 01KSG5QR1M4BX1XS970SJN2FM7
        title: "Documentation Site"
        status: "placeholder"
        location: "master"
        description: "Project's mkdocs configuration, hooks, theme overrides. Body project-authored; slot identity upstream-prescribed."
        keywords: ["project", "mkdocs", "site"]
      - id: "01-04"
        arc_100: true
        arc_100_ulid: 01KSG5QR2M1X8XJ412174MEJMT
        title: "Extensions"
        status: "placeholder"
        location: "master"
        description: "Project-specific enhancements that extend ARC-100 (custom templates, new conventions). Body project-authored; slot identity upstream-prescribed."
        keywords: ["project", "extensions"]

  - id: "02"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9JH2PD2J0VN533FM4
    title: "Philosophy"
    band: "00-09"
    description: "What the application is, who it's for, why it exists, and the cross-cutting design principles that shape every other architectural decision."
    chapters:
      - id: "02-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNG9KVF7QJF7DG29CKMP
        title: "Mission and Purpose"
        status: "placeholder"
        description: "What the application is at the highest level — the one-paragraph framing; how it differs from adjacent tools."
        keywords: ["philosophy", "mission", "overview"]
      - id: "02-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNG9KZEQG0JTAMSCW4JY
        title: "Business Problems"
        status: "placeholder"
        description: "The problems the application solves. The domain pain points motivating the work."
        keywords: ["business", "problem", "domain"]
      - id: "02-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNG99YBX090PAGZ8MEC1
        title: "Users and Personas"
        status: "placeholder"
        description: "Who the application is designed for — target verticals, organizational scale, user personas."
        keywords: ["users", "personas", "market"]
      - id: "02-04"
        arc_100: true
        arc_100_ulid: 01KRRRFNG9N8NV5DSJFDV3224A
        title: "Value Proposition"
        status: "placeholder"
        description: "How the application helps people — differentiation against adjacent tools, specific gains an adopter realizes."
        keywords: ["value", "differentiation"]
      - id: "02-05"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA2QT3ZR54HHHM6XC2
        title: "Design Principles"
        status: "placeholder"
        description: "Cross-cutting design principles that shape every other architectural decision."
        keywords: ["principles", "philosophy", "design"]
      - id: "02-06"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA0C921VPDX295B6SS
        title: "Requirements"
        status: "placeholder"
        description: "Functional and behavioural requirements for the application: elicitation method, traceability discipline, and the requirements registry. Anchored in SWEBOK's Software Requirements knowledge area (IEEE Computer Society, v4.0a 2025) as the canonical reference."
        keywords: ["requirements", "swebok", "elicitation", "traceability"]
      - id: "02-07"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA0NYNPKPE3T3YKS61
        title: "System Context"
        status: "placeholder"
        description: "The application's external boundary: external systems consumed, services hosted for external consumers, third-party APIs, data sources, and stakeholders interacting with the application. Anchored in arc42 §3 Context and Scope and the System Context level of Simon Brown's C4 model as canonical references. Distinct from 93-01 Trust Boundaries, which is the security view of the same context."
        keywords: ["system-context", "boundary", "arc42", "c4-model", "external-integrations"]
      - id: "02-08"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAWA773HBS8RP1F8TX
        title: "Quality Requirements"
        status: "placeholder"
        description: "Non-functional requirements: the application's quality attributes (performance, reliability, scalability, security, usability, maintainability) with concrete targets and the scenarios used to validate them. Anchored in arc42 §10 Quality Requirements and the ISO/IEC 25010 product-quality model as canonical references."
        keywords: ["quality-requirements", "nfr", "non-functional-requirements", "arc42", "iso-25010"]

  # =====================================================================
  # 10-19 — Governance
  # =====================================================================

  - id: "10"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9N8SMG3CCZX79FYDA
    title: "Glossary"
    band: "10-19"
    description: "Application domain vocabulary, distinct from the ARC-100 Glossary at 00-02 which covers documentation-system terminology only."
    chapters:
      - id: "10-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA6M8FW4P8501T7VEY
        title: "General Glossary"
        status: "placeholder"
        description: "Authoritative term glossary across all topics. The application's domain vocabulary."

  - id: "11"
    arc_100: true
    arc_100_ulid: 01KRRRFNG94FKTBFNFHP2KQQMN
    title: "Roadmap"
    band: "10-19"
    description: "Forward-looking architectural items and the out-of-scope register."
    chapters:
      - id: "11-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA2YFW1GCBDGXC8XW8
        title: "Roadmap"
        status: "placeholder"
        description: "Forward-looking architectural items."
      - id: "11-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA3JZRNWNJ7794ZP71
        title: "Out-of-Scope"
        status: "placeholder"
        description: "Items deliberately deferred per version."

  - id: "12"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9VSFNCC9H00Y13KFJ
    title: "Decisions"
    band: "10-19"
    description: "Architectural Decision Records (ADRs). Optional — adopt only if the project formalizes them."
    chapters:
      - id: "12-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAG8437NR40CXWXE5X
        title: "Architectural Decision Record (ADR) Index"
        status: "placeholder"
        description: "Index of ADRs and the rationale behind each. (optional)"

  - id: "13"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9HWDF64QCM4NZ742S
    title: "Versioning"
    band: "10-19"
    description: "Version lifecycle and the promote-version command contract."
    chapters:
      - id: "13-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGASCVHX957B2QE75W3
        title: "Version Lifecycle"
        status: "placeholder"
        description: "How a documentation version opens, lives, pauses, and closes. Distinct from code-release tagging, which lives in 86-06 Tagging and Releases."
      - id: "13-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA3XN08P8695B6T6BA
        title: "Promote-Version Contract"
        status: "placeholder"
        description: "The promote-version command contract."

  # =====================================================================
  # 20-39 — Client
  # =====================================================================

  - id: "20"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9YS26KF254EQB5BP2
    title: "Client Foundations"
    band: "20-39"
    description: "Overview, module structure, and build pipeline — the generic starting point for the client-side surface. Project-specific UI surfaces (panels, visualizations, designers, component libraries) land in unallocated slots above."
    chapters:
      - id: "20-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA6WWQW8B03NFH0A12
        title: "Overview"
        status: "placeholder"
        description: "Top-level client-side architecture. (optional)"
      - id: "20-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA29QWDN0FT2KDJWD3
        title: "Module Structure"
        status: "placeholder"
        description: "Client module/package layout and import conventions. (optional)"
      - id: "20-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA2M4TWWJH44TGPPZG
        title: "Build Pipeline"
        status: "placeholder"
        description: "Client build pipeline (bundler, transpiler, asset packaging). (optional)"
      - id: "20-04"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAP2GHG7Y9RNXAWJG7
        title: "State Management"
        status: "placeholder"
        description: "Client-side state model: store pattern (Redux/Pinia/signals/observable/event-bus), reactivity model, derivation rules, persistence and rehydration of state across page loads."
      - id: "20-05"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAJ606E4GZ1ADYJ11P
        title: "Routing"
        status: "placeholder"
        description: "URL ↔ view mapping, route guards, redirects, deep-link handling, history-stack discipline. (optional — applies to SPAs and any client with multiple views)"
      - id: "20-06"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAZAYBM475535PN793
        title: "Error Handling"
        status: "placeholder"
        description: "Client error surface: error boundaries, async error propagation from API/state/UI to a user-visible recovery path, uncaught-error capture for telemetry."
      - id: "20-07"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAV1SJCQM7W5XHNQJ3
        title: "Accessibility"
        status: "placeholder"
        description: "ARIA conventions, keyboard navigation, focus management, screen-reader compatibility, color-contrast policy."

  - id: "21"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9M15GYW874H89FY58
    title: "Server Communication"
    band: "20-39"
    description: "Client-side consumption of the server API: HTTP client wrapper, realtime channel subscriptions, auth surface on the client, retry/error normalization, response caching, optimistic updates. The server-side API contract lives in Book 42 API."
    chapters:
      - id: "21-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAZAZ3HKVYMH925CCY
        title: "HTTP Client"
        status: "placeholder"
        description: "HTTP client wrapper: base URL, default headers, request/response interceptors, serialization, content negotiation. (optional)"
      - id: "21-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAS47GVTQ65DRJGNGH
        title: "Realtime Channel"
        status: "placeholder"
        description: "WebSocket / SSE subscription lifecycle, reconnect strategy, message routing on the client. Companion to 41-01 WebSocket Transport. (optional)"
      - id: "21-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA5928QZDW8N9Q5Q75
        title: "Auth Surface"
        status: "placeholder"
        description: "Login state on the client, token storage choices and tradeoffs, refresh flow, logged-out UI states. Companion to 47-01 Authentication and 47-05 Sessions."
      - id: "21-04"
        arc_100: true
        arc_100_ulid: 01KRRRFNGASJEW316XM9Q71Q5T
        title: "Error Handling and Retry"
        status: "placeholder"
        description: "Retry policy (idempotency-aware), backoff, error normalization to a client-internal shape, surfacing transport errors vs application errors distinctly. Companion to 20-06 Error Handling."
      - id: "21-05"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA8S9EXDTX029XT4MV
        title: "Response Caching"
        status: "placeholder"
        description: "Cache-key shape, invalidation rules, stale-while-revalidate posture, cross-tab cache coordination, eviction policy. (optional)"
      - id: "21-06"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAMBGWD74782KGMN2Q
        title: "Optimistic Updates"
        status: "placeholder"
        description: "Optimistic-update discipline: predicted-state shape, rollback on server rejection, conflict detection when a concurrent change lands. (optional)"

  - id: "22"
    arc_100: true
    arc_100_ulid: 01KVRHKAJEFQSHPCDY8PRGKN0Y
    title: "Design"
    band: "20-39"
    description: "The application's design system: design intent and guidance for the application as a whole, detailed design intent for individual design topics, and the implementation architecture that realizes those design decisions in code — organized in three tiers (Foundations, Elements, Implementation). Optional — applications with a user interface."
    chapters:
      - id: "22-01"
        arc_100: true
        arc_100_ulid: 01KVRHKAKCWKEXPVH0TK8GP6M2
        title: "Design Language"
        status: "placeholder"
        description: "The unifying design language — the objectives, principles, and coherence rules that govern every other Design chapter."
        keywords: ["design-language", "design-philosophy", "tenets", "principles", "north-star", "foundation", "tier-1", "coherence", "accessibility-reference"]
      - id: "22-02"
        arc_100: true
        arc_100_ulid: 01KVRHKAMBCTDQNSWVA8J70ZNY
        title: "Brand"
        status: "placeholder"
        description: "Brand identity and personality expressed through design, carried consistently across every surface. Distinct from 02 Project Identity (mission, audience, value)."
        keywords: ["brand", "brand-identity", "personality", "positioning", "voice-and-character", "foundation", "tier-1", "logo", "wordmark"]
      - id: "22-03"
        arc_100: true
        arc_100_ulid: 01KVRHKAN88ENYTVKM498H0Y3A
        title: "Reserved (Tier-1 Foundation Headroom)"
        status: "placeholder"
        description: "Reserved. Held for a future cross-cutting design foundation that governs other chapters — not a bounded design facet."
        keywords: ["reserved", "headroom", "tier-1", "foundation", "cross-cutting", "unallocated", "do-not-assign-facet"]
      - id: "22-04"
        arc_100: true
        arc_100_ulid: 01KVRHKAP6MESXM8B94YGTGE3K
        title: "Reserved (Tier-1 Foundation Headroom)"
        status: "placeholder"
        description: "Reserved (second slot). Held for a future cross-cutting design foundation that governs other chapters — not a bounded design facet."
        keywords: ["reserved", "headroom", "tier-1", "foundation", "cross-cutting", "unallocated", "do-not-assign-facet"]
      - id: "22-05"
        arc_100: true
        arc_100_ulid: 01KVRHKAQ5P2MJMVF1QJXAFSPP
        title: "Typography"
        status: "placeholder"
        description: "Type families, scale, hierarchy, weight, measure, and the design objectives type serves. The visual half of language; cf. 22-06 Voice."
        keywords: ["typography", "type-system", "type-scale", "hierarchy", "leading", "measure", "legibility", "tier-2", "element"]
      - id: "22-06"
        arc_100: true
        arc_100_ulid: 01KVRHKAR2HP3Y27FJTR1Z55FF
        title: "Voice"
        status: "placeholder"
        description: "Tone of voice, terminology, and the application's microcopy approach. The verbal half of language; cf. 22-05 Typography."
        keywords: ["voice", "tone", "microcopy", "terminology", "ux-writing", "content-design", "tier-2", "element"]
      - id: "22-07"
        arc_100: true
        arc_100_ulid: 01KVRHKAS1XFFV92MJXD6DJ4EK
        title: "Color"
        status: "placeholder"
        description: "Palette, semantic color roles, usage, and light/dark variants. Contrast goals reference 20-07 Accessibility."
        keywords: ["color", "palette", "semantic-color", "color-roles", "theme-variants", "contrast", "tier-2", "element"]
      - id: "22-08"
        arc_100: true
        arc_100_ulid: 01KVRHKASZ85HY9NFP2PWA5MFY
        title: "Iconography"
        status: "placeholder"
        description: "The icon system — metaphors, family, style, and sizing conventions. Distinct from 22-21 Vectors, the SVG that renders icons."
        keywords: ["iconography", "icons", "icon-system", "visual-metaphor", "icon-grid", "icon-style", "tier-2", "element"]
      - id: "22-09"
        arc_100: true
        arc_100_ulid: 01KVRHKATYAFDHR6SPJ0PQF839
        title: "Imagery"
        status: "placeholder"
        description: "Photography, illustration, and art-direction style and intent. Distinct from 22-22 Assets (production and delivery of files)."
        keywords: ["imagery", "photography", "illustration", "art-direction", "image-style", "tier-2", "element"]
      - id: "22-10"
        arc_100: true
        arc_100_ulid: 01KVRHKAVXP65YV8475GGJXGB3
        title: "Layout"
        status: "placeholder"
        description: "Composition, grid, spacing and density scales, alignment, and responsive layout intent."
        keywords: ["layout", "composition", "grid", "spacing", "density", "alignment", "responsive-intent", "tier-2", "element"]
      - id: "22-11"
        arc_100: true
        arc_100_ulid: 01KVRHKAWVV08MAC86JQ48WP7P
        title: "Motion"
        status: "placeholder"
        description: "Animation and transition principles — choreography, easing, duration, and the intent of motion, including reduced-motion."
        keywords: ["motion", "animation", "transitions", "choreography", "easing", "duration", "reduced-motion", "tier-2", "element"]
      - id: "22-12"
        arc_100: true
        arc_100_ulid: 01KVRHKAXSEADB7GER623N27RT
        title: "Interactivity"
        status: "placeholder"
        description: "The intent of interactions — affordances, feedback, states, and gestures. Design intent, distinct from the client handlers in Book 20."
        keywords: ["interactivity", "interaction-design", "affordances", "feedback", "states", "gestures", "tier-2", "element"]
      - id: "22-20"
        arc_100: true
        arc_100_ulid: 01KVRHKAYQ49888F8GXVJEMHE2
        title: "Style"
        status: "placeholder"
        description: "The CSS architecture implementing the design: tokens, themes, file/module organization, state styling, and responsive rules. Distinct from 20-03 Build Pipeline."
        keywords: ["style", "css", "design-tokens", "themes", "css-architecture", "responsive-design", "breakpoints", "tier-3", "implementation"]
      - id: "22-21"
        arc_100: true
        arc_100_ulid: 01KVRHKAZNQGGJKH8S864P35XG
        title: "Vectors"
        status: "placeholder"
        description: "SVG and vector architecture — SVG-over-raster intent, inline vs sprite strategy, authoring, optimization, and rendering."
        keywords: ["vectors", "svg", "sprites", "inline-svg", "vector-optimization", "svg-over-raster", "tier-3", "implementation"]
      - id: "22-22"
        arc_100: true
        arc_100_ulid: 01KVRHKB0J8Z42T79H2GNMG7K9
        title: "Assets"
        status: "placeholder"
        description: "Production, formats, optimization, and delivery of non-vector design assets — images, fonts, logos, media. Distinct from 20-03 Build Pipeline."
        keywords: ["assets", "asset-management", "raster-images", "fonts-as-assets", "logo-files", "asset-pipeline", "optimization", "tier-3", "implementation"]

  # =====================================================================
  # 40-59 — Server
  # =====================================================================

  - id: "40"
    arc_100: true
    arc_100_ulid: 01KRRRFNG90RYW3PDM54CPQJ3J
    title: "Server Foundations"
    band: "40-59"
    description: "Top-level server architecture, boot sequence, and internal service decomposition."
    chapters:
      - id: "40-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA4B3AQ2JTPQGBPS0K
        title: "Overview"
        status: "placeholder"
        description: "Top-level server-side architecture. (optional)"
      - id: "40-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA1NE0YAM9D1MAGAQ7
        title: "Boot Sequence"
        status: "placeholder"
        description: "Server boot sequence and module load order. (optional)"
      - id: "40-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA57FEEBHMVQVDPKJF
        title: "Internal Services"
        status: "placeholder"
        description: "Decomposition of the server into internal services or subsystems: service boundaries, ownership, deploy units, and inter-service communication patterns. Service wire shapes — the message/payload formats exchanged between internal services — are documented within this chapter alongside the service architecture rather than as a separate chapter, since their conventions track the decomposition itself. Distinct from the client hydration wire (Book 62) and the published API wire (42-10). (optional)"

  - id: "41"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9T825H6HK1AMBZ2AB
    title: "Transport"
    band: "40-59"
    description: "HTTP, WebSocket, and internal-channel surfaces."
    chapters:
      - id: "41-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAW7EW1CNW81TC2AH2
        title: "WebSocket Transport"
        status: "placeholder"
        description: "WebSocket event handlers and envelope protocol. (optional)"
      - id: "41-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAJYWHKB11YH915VQ5
        title: "HTTP Surface"
        status: "placeholder"
        description: "Low-level HTTP routing layer: route registration, middleware chain, non-API surfaces (health checks, page serving, redirects, static assets). The published API contract — REST/GraphQL/gRPC shape, versioning, pagination, error envelope — lives in Book 42 API. (optional)"
      - id: "41-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAGXS94171756TWVXJ
        title: "Internal Channels"
        status: "placeholder"
        description: "IPC and internal-only channels for multi-process deployment. (optional)"

  - id: "42"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9V874ZJZ7QP7A31WP
    title: "Application Programming Interface (API)"
    band: "40-59"
    description: "The published API contract: surface style, versioning, error envelope, pagination, idempotency, rate limiting, machine authentication, webhooks, schema publication, and the wire catalog (curated subset of Book 62 wire shapes). Distinct from Book 41 Transport (the low-level routing layer) and consumed by Book 21 Server Communication on the client side."
    chapters:
      - id: "42-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA8XPNPQNF5AJV0QBE
        title: "API Surface Overview"
        status: "placeholder"
        description: "Chosen API style (REST / GraphQL / gRPC / JSON-RPC) and the rationale; resource model; URL/operation naming conventions; the public-vs-internal split."
      - id: "42-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA976K0KV1EXVF3455
        title: "Versioning and Deprecation"
        status: "placeholder"
        description: "Versioning scheme (URI version, media-type version, header version), deprecation policy, sunset cadence, communication channel for breaking changes."
      - id: "42-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAXTEXT5ZEMAG34Q9W
        title: "Error Envelope and Status Codes"
        status: "placeholder"
        description: "Error response shape, status-code mapping, machine-readable error codes, retryability hints, correlation IDs."
      - id: "42-04"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAM13XBZG2ER5K8A6J
        title: "Pagination, Filtering, Sorting"
        status: "placeholder"
        description: "Pagination model (offset/limit, cursor, page token), filter grammar, sort grammar, default and maximum page sizes."
      - id: "42-05"
        arc_100: true
        arc_100_ulid: 01KRRRFNGADAFVYBF7RG2YW4ZK
        title: "Idempotency and Safety Semantics"
        status: "placeholder"
        description: "Which operations are safe, idempotent, or neither; idempotency-key mechanism for unsafe operations; replay protection."
      - id: "42-06"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAWPXVNSJ8XSAC5MDJ
        title: "Rate Limiting and Throttling"
        status: "placeholder"
        description: "Per-principal and per-IP rate limits, burst allowance, throttle response shape, retry-after semantics, exemptions register."
      - id: "42-07"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAHSXMZE0PYC3YVGTV
        title: "Machine Authentication"
        status: "placeholder"
        description: "API tokens vs OAuth client credentials vs mTLS for machine clients, token lifecycle, scope model. Companion to 47 Identity and 93-02 Authentication."
      - id: "42-08"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAMY4WAKHMWWJ65Q3G
        title: "Webhooks"
        status: "placeholder"
        description: "Outbound API events: subscription model, delivery semantics (at-least-once vs exactly-once), retry policy, signature scheme, consumer-side verification contract. (optional)"
      - id: "42-09"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAQASFJWE0Y2NWWW2V
        title: "OpenAPI and Schema Publication"
        status: "placeholder"
        description: "Machine-readable schema artifact (OpenAPI / AsyncAPI / GraphQL SDL / .proto), generation cadence, distribution channel, consumer SDK strategy. (optional)"
      - id: "42-10"
        arc_100: true
        arc_100_ulid: 01KRRRFNGATCRJJTT2MPD8S14S
        title: "API Wire Catalog"
        status: "placeholder"
        description: "The curated, third-party-stable subset of wire shapes published as part of the API contract: which fields are guaranteed, which are deprecated, the public-vs-internal split, and the mapping back to the canonical wire shapes in Book 62 Client Hydration Wire. The conventions themselves — naming, primitives, null handling, unknown-field policy — are defined once in 62-01 and inherited here."

  - id: "47"
    arc_100: true
    arc_100_ulid: 01KRRRFNG968Z80J6MT2JDSENV
    title: "Identity"
    band: "40-59"
    description: "Authentication, authorization, Multi-Factor Authentication (MFA), federation, sessions. Companion to Book 65 Identity Data and 93 Security."
    chapters:
      - id: "47-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA4Z5D0XH44Z41ZVTA
        title: "Authentication"
        status: "placeholder"
        description: "Internal credentials and login flow."
      - id: "47-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGANTVTMCNDDSG4FCJE
        title: "Authorization"
        status: "placeholder"
        description: "Capability gating, IDOR avoidance, group-scoped permissions."
      - id: "47-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA6TEB3N9QPC4DWR1D
        title: "Multi-Factor Authentication (MFA)"
        status: "placeholder"
        description: "TOTP, WebAuthn, SMS, email MFA. (optional)"
      - id: "47-04"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAHCFP20NRSM25SQM2
        title: "Federation"
        status: "placeholder"
        description: "OAuth, SAML, OIDC providers. (optional)"
      - id: "47-05"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAKFAWV71FBWX5FDVJ
        title: "Sessions"
        status: "placeholder"
        description: "Session lifecycle, idle timeout, concurrent session caps, lockout."

  - id: "48"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9FDG9414039R23BAK
    title: "Audit"
    band: "40-59"
    description: "Audit-event capture at the application layer. The security posture for audit (what is logged, what must NEVER be logged, redaction contract) lives in 93-09."
    chapters:
      - id: "48-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAYS4RGYPGTK7V2A6E
        title: "Audit Trail"
        status: "placeholder"
        description: "Audit-event capture and timeline reconstruction. (optional)"

  - id: "53"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9C8C1Z78R9JT2RCJJ
    title: "Notifications"
    band: "40-59"
    description: "Event-driven user notifications."
    chapters:
      - id: "53-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA3KT92D9XRP2FYZGF
        title: "Overview"
        status: "placeholder"
        description: "Event-driven user notification surface (in-app, email, push). (optional)"

  - id: "54"
    arc_100: true
    arc_100_ulid: 01KRRRFNG90PJ9BWGBRKAKC4G9
    title: "Search"
    band: "40-59"
    description: "Server-side search infrastructure."
    chapters:
      - id: "54-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA35R9MVFV56Q7DF5P
        title: "Overview"
        status: "placeholder"
        description: "Server-side search infrastructure. (optional)"

  # =====================================================================
  # 60-79 — Data
  # =====================================================================

  - id: "60"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9EH09Z1SEVM3MRPQ2
    title: "Data Foundations"
    band: "60-79"
    description: "Top-level data model and schema conventions."
    chapters:
      - id: "60-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA02HSMHPGYJ50842X
        title: "Overview"
        status: "placeholder"
        description: "Top-level data model. (optional)"
      - id: "60-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA6NBNY2ZQSWE3M3W9
        title: "Schema Conventions"
        status: "placeholder"
        description: "Primary key conventions, naming conventions, timestamps. (optional)"

  - id: "61"
    arc_100: true
    arc_100_ulid: 01KRRRFNG91FZ1CAAM37MQQC8A
    title: "Persistence"
    band: "60-79"
    description: "Database engine choice and transaction patterns."
    chapters:
      - id: "61-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA566D6WG25B8D3J20
        title: "Database"
        status: "placeholder"
        description: "Primary persistence engine (RDBMS, NoSQL, etc.)."
      - id: "61-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGADCZZ58J9YC2FQ6DW
        title: "Transaction Patterns"
        status: "placeholder"
        description: "Transaction patterns and consistency guarantees."

  - id: "62"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9HYBVX0P7HN52VFHY
    title: "Client Hydration Wire"
    band: "60-79"
    description: "The full-fidelity data shape the privileged first-party client receives from the server and treats as its working in-memory model. Distinct from the API contract (Book 42), which publishes a curated third-party-facing subset. Defines naming conventions, primitives, projection rules from the persistence shape (Book 61), and the versioning discipline that lets clients hold state across deploys."
    chapters:
      - id: "62-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAPNTEV0CD5ZBECZD8
        title: "Wire Shape Conventions"
        status: "placeholder"
        description: "Field naming style, primitive encodings (dates, decimals, IDs), null vs missing semantics, unknown-field handling (strict reject vs forward-compat ignore), envelope/wrapping discipline. Applied consistently across HTTP responses, WebSocket payloads, and webhook bodies. Inherited by 42-10 API Wire Catalog and by 40-03 Internal Services."
      - id: "62-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA926C3MYPKKEJBRWK
        title: "Wire Shape Catalog"
        status: "placeholder"
        description: "The per-resource shape register: every typed payload the client receives and reasons against (Process, Order, Catalog, User, etc.). The catalog content is project-specific; this chapter defines the catalog format and the relationship between shape entries and the resources they hydrate."
      - id: "62-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGACD6C5SDFXK8ZDE82
        title: "Projection from Persistence"
        status: "placeholder"
        description: "How the at-rest schema (Book 61) maps to the at-wire shape: denormalization rules, computed and derived fields, graph traversal depth, embed-vs-reference decisions, server-side projection layer."
      - id: "62-04"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA5MG9A5PKASF1S8ET
        title: "Versioning and Migration"
        status: "placeholder"
        description: "How wire shapes evolve without breaking clients holding state across deploys: additive-change discipline, deprecation window, client-side handling of forward-compatible fields. Companion to 42-02 Versioning and Deprecation."
      - id: "62-05"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAM34BWKJ3SRPZ8458
        title: "Permission-Aware Redaction"
        status: "placeholder"
        description: "Viewer-role-driven field stripping: which fields are conditionally present based on the requester's permissions; what every consumer must treat as always-optional. Companion to 47-02 Authorization and 93-03 Authorization."

  - id: "63"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9ZBKG88CFQW0JRFQN
    title: "Assets"
    band: "60-79"
    description: "Document, image, and video asset storage and metadata."
    chapters:
      - id: "63-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAZA42QMY37RAEDJ2G
        title: "Storage"
        status: "placeholder"
        description: "Document, image, and video asset storage. (optional)"
      - id: "63-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAS3YKSYXAWV96VYMD
        title: "Metadata and Indexing"
        status: "placeholder"
        description: "Asset metadata (mime, size, source) and search indexing. (optional)"

  - id: "64"
    arc_100: true
    arc_100_ulid: 01KRRRFNG97P7NPBR8S5FRX7RQ
    title: "Audit Data"
    band: "60-79"
    description: "Audit-table schema, indexing, and retention. Companion to Book 48 Audit."
    chapters:
      - id: "64-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAHB9DTV3JAJCE929G
        title: "Tables"
        status: "placeholder"
        description: "Audit-table schema. (optional)"
      - id: "64-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAXJVCT8CV7BQQ2956
        title: "Indexing and Retention"
        status: "placeholder"
        description: "Indexing strategy and retention policy. (optional)"

  - id: "65"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9V1FZ0V2QHHG7ARB7
    title: "Identity Data"
    band: "60-79"
    description: "User, tenancy, credentials, MFA, and permissions schemas. Companion to Book 47 Identity."
    chapters:
      - id: "65-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAWWSNNB7X0NJTEB7V
        title: "User Data Model"
        status: "placeholder"
        description: "Core user identity table."
      - id: "65-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAWFE3JXVA40Y62HKQ
        title: "Tenancy Data Model"
        status: "placeholder"
        description: "Company, department, or organization tenancy structure. (optional)"
      - id: "65-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA1PGT8QCC4P31XA4X
        title: "Credentials"
        status: "placeholder"
        description: "Internal vs federated credentials data."
      - id: "65-04"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAFCYX91QABAMHN5XP
        title: "MFA Data"
        status: "placeholder"
        description: "MFA factor records, recovery codes, lockout state. (optional)"
      - id: "65-05"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAGE49EK6C2SJ405QK
        title: "Federated Identity Data"
        status: "placeholder"
        description: "Identity-provider records; mapping external IDs to internal users. Companion to 47-04 Federation. (optional)"
      - id: "65-06"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAQ4HH872QPM1G4YJR
        title: "Permissions"
        status: "placeholder"
        description: "Group definitions and scoping data. Companion to 47-02 Authorization."

  - id: "66"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9ZRTWQRCCPTHWZK3X
    title: "Migrations"
    band: "60-79"
    description: "Schema-evolution strategy and migration tooling."
    chapters:
      - id: "66-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAY0NQV2TBP4G2QB2M
        title: "Migration Strategy"
        status: "placeholder"
        description: "Schema-evolution strategy and tooling."

  # =====================================================================
  # 80-89 — Tooling
  # =====================================================================

  - id: "80"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9J9WFVMJ7M35W5JBG
    title: "Environment"
    band: "80-89"
    description: "Language, runtime, type system, project structure."
    chapters:
      - id: "80-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGACCHBN9V8CB3DRH3M
        title: "Language and Runtime"
        status: "placeholder"
        description: "Language, runtime version, and feature-set conventions."
      - id: "80-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA670319GQ0M9E4STT
        title: "Type System"
        status: "placeholder"
        description: "Type-checking strategy and conventions."
      - id: "80-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAV80WA8HSKXH0XNM8
        title: "Project Structure"
        status: "placeholder"
        description: "Top-level repo layout — the per-repo folder hierarchy and the language conventions that shape it. Companion to 86-02 Repository Topology, which owns the macro monorepo-vs-polyrepo decision that determines how many repos the layout is repeated across."

  - id: "81"
    arc_100: true
    arc_100_ulid: 01KRRRFNG99TFN2CX9B4H0945E
    title: "Linting"
    band: "80-89"
    description: "Lint, type-check, markdownlint, and other code-health static checks. Security-focused static analysis (SAST) lives in Book 84 Security Testing."
    chapters:
      - id: "81-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGASBGJZENQJ6ZBY891
        title: "Lint Configuration"
        status: "placeholder"
        description: "Lint rules and configuration."
      - id: "81-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGACYDDAC34JZGRTRN9
        title: "Type Checking"
        status: "placeholder"
        description: "Type-checking discipline and tooling."
      - id: "81-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAW874TR687JW8DE0H
        title: "Markdownlint"
        status: "placeholder"
        description: "Markdown lint rules and tooling."

  - id: "82"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9VP67N1A9JTGKB7N9
    title: "Functional Testing"
    band: "80-89"
    description: "Behavioral testing of the application across unit, integration, contract, and end-to-end levels, plus the helpers and coverage policy that support them. Performance and capacity testing live in Book 83 Performance Testing; security-flavored testing lives in Book 84 Security Testing."
    chapters:
      - id: "82-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAE1KN1PJVYPQGD9R3
        title: "Unit Testing"
        status: "placeholder"
        description: "Unit-level test discipline: scope, isolation, mocking policy, naming and structure conventions."
      - id: "82-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAART35PPWZSZ1Y2EQ
        title: "Integration Testing"
        status: "placeholder"
        description: "Tests that exercise multiple modules or cross process/database boundaries. Test-database posture and fixture scope."
      - id: "82-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAPTCYDS8A72R1EKB4
        title: "Contract Testing"
        status: "placeholder"
        description: "Provider/consumer contract tests at API and message-bus boundaries. Contract-storage location, drift detection."
      - id: "82-04"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAS7K1878J1A7HRH0D
        title: "End-to-end Testing"
        status: "placeholder"
        description: "Full-stack tests driving the assembled application from the outside (HTTP, browser, CLI). Run cadence, flake budget, environment provisioning."
      - id: "82-05"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAY1BT6C2371264E6Y
        title: "Test Helpers and Fixtures"
        status: "placeholder"
        description: "Shared test helpers, fixtures, in-memory test databases."
      - id: "82-06"
        arc_100: true
        arc_100_ulid: 01KRRRFNGANRQ98SXZWG3SW5XR
        title: "Coverage Targets"
        status: "placeholder"
        description: "Coverage policy and targets."

  - id: "83"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9R9GRBK8Y9GTT2FD3
    title: "Performance Testing"
    band: "80-89"
    description: "Capacity and performance testing methodology. The data those tests produce, and the assessments that consume it, live in Book 91 Capacity in band 90-99."
    chapters:
      - id: "83-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA5HGV6T3YRXKA4HF1
        title: "Capacity Testing"
        status: "placeholder"
        description: "Capacity testing methodology: synthetic at-scale dataset generation, soak-test cadence. Companion to 91-03 Capacity Assessments."
      - id: "83-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA89X6PAHVHDQTBWJD
        title: "Performance Benchmarks"
        status: "placeholder"
        description: "Performance benchmarking methodology: microbenchmarks, baseline tracking, regression detection. Companion to 91-02 Performance Tuning."

  - id: "84"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9C8J22NX1DZ7AJ4PR
    title: "Security Testing"
    band: "80-89"
    description: "Security-flavored testing of the application: static analysis with security rule packs, dynamic black-box probing, interactive instrumented testing, and human-driven penetration testing. Policy — what must be tested, severity thresholds, gating cadence — lives in 93-12 Security Testing Policy."
    chapters:
      - id: "84-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAW5MQQJZFDWMTG6MP
        title: "Static Application Security Testing (SAST)"
        status: "placeholder"
        description: "Source-code taint tracking, data-flow analysis, sink/source matching for security defects. Tool choice, rule curation, false-positive register, CI integration. Companion to 93-12 Security Testing Policy."
      - id: "84-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAQ5831V0X3DK15XNZ
        title: "Dynamic Application Security Testing (DAST)"
        status: "placeholder"
        description: "Black-box probing of a running application from the outside. Scanner choice, scope and authentication setup, scheduled vs gated runs. Companion to 93-12 Security Testing Policy."
      - id: "84-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA7T1XWK394GCQFS2B
        title: "Interactive Application Security Testing (IAST)"
        status: "placeholder"
        description: "Runtime instrumentation paired with the functional test suite to detect vulnerabilities during normal test execution. Companion to 93-12 Security Testing Policy."
      - id: "84-04"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA3AN84HMPFHKKBCJK
        title: "Penetration Testing"
        status: "placeholder"
        description: "Human-driven adversarial testing: scope, frequency, third-party engagement model, finding-triage workflow, retest cadence. Companion to 93-12 Security Testing Policy."

  - id: "85"
    arc_100: true
    arc_100_ulid: 01KRRRFNG90HD4P3XN6M7JDVWZ
    title: "Continuous Integration (CI)"
    band: "80-89"
    description: "Pre-commit/pre-push hooks and the CI/CD pipeline."
    chapters:
      - id: "85-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAY3BFEZ0T3QQTTWBP
        title: "Hooks"
        status: "placeholder"
        description: "Pre-commit and pre-push hooks. Companion to 86-04 Commit Conventions, whose rules these hooks enforce."
      - id: "85-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA4ZMTMS7HV8QGG0MY
        title: "Pipeline"
        status: "placeholder"
        description: "CI/CD pipeline. (optional)"

  - id: "86"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9TEZYNF5CXTX82AEY
    title: "Repository"
    band: "80-89"
    description: "The version-control container the project lives in, and the conventions that govern its day-to-day use: the Version Control System (VCS) and its host, repository topology, branching model, commit and review conventions, tagging and releases, and the security posture that protects the history. Companions: 80-03 Project Structure (per-repo layout), 85 Continuous Integration (CI) (which runs against every commit), and Book 93 Security (signing and protection)."
    chapters:
      - id: "86-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA99R2MNGNMXA614H9
        title: "Version Control System (VCS)"
        status: "placeholder"
        description: "VCS tool choice (git, Mercurial, jj), the host providing the canonical remote (GitHub, GitLab, Bitbucket, self-hosted), minimum required version, and the rationale for those choices. The conventions surrounding daily use of the tool live in 86-03, 86-04, and 86-05."
      - id: "86-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA6169YJRH9XNP8YWK
        title: "Repository Topology"
        status: "placeholder"
        description: "Monorepo vs polyrepo decision: the macro shape of how code is split across one or many repositories, and the implications for cross-cutting changes, CI, and release coordination. The per-repo internal folder layout lives in 80-03 Project Structure."
      - id: "86-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA2R7DCNM2M453ADHX
        title: "Branching Model"
        status: "placeholder"
        description: "The integration model the project follows — trunk-based development, GitHub Flow, GitFlow, or other. Branch-naming conventions, expected branch lifetime, integration cadence, and the relationship between branches and releases. Companion to 86-06 Tagging and Releases."
      - id: "86-04"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAWKKTQZFRJM6XGS5W
        title: "Commit Conventions"
        status: "placeholder"
        description: "Commit message format (Conventional Commits, semantic prefix, body structure), sign-off requirements, and co-author attribution. Mechanical enforcement via pre-commit hooks lives in 85-01 Hooks."
      - id: "86-05"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAGT3A2QAFEGFBAA0H
        title: "Merge and Review Policy"
        status: "placeholder"
        description: "Merge strategy (squash, rebase, merge commit), required reviewers and CODEOWNERS, pull/merge request template, and the policy distinction between blocking and advisory checks. Companion to 85-02 Pipeline, which runs the checks."
      - id: "86-06"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAE19JBTVDTE1MM4M7
        title: "Tagging and Releases"
        status: "placeholder"
        description: "Tag-naming convention, release artifact identification, and the mapping from a tag to a deployable build. Distinct from documentation-version tags managed under Book 13 Versioning."
      - id: "86-07"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAAEXG1QSRFJVVAPPZ
        title: "Signing and Branch Protection"
        status: "placeholder"
        description: "Commit and tag signing policy, branch protection rules (required reviewers, status checks, force-push posture), and repository access control. Companion to Book 93 Security."

  # =====================================================================
  # 90-99 — Operations
  # =====================================================================

  - id: "90"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9V1GHT1KNFJ39YQAC
    title: "Observability"
    band: "90-99"
    description: "Logging, metrics, tracing. Companion to 93-09 Logging and Audit."
    chapters:
      - id: "90-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGASG85FW0Q4D96R061
        title: "Logging"
        status: "placeholder"
        description: "Structured-logging conventions and audit-friendly redaction. Cross-references 93-09 Logging and Audit (security)."
      - id: "90-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAAC7AD7VVZ5R6JTAF
        title: "Metrics"
        status: "placeholder"
        description: "Application metrics surface. (optional)"
      - id: "90-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGARQ039X8CZDN6AXNW
        title: "Tracing"
        status: "placeholder"
        description: "Distributed tracing. (optional)"

  - id: "91"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9ZQVBGS7ZWQRP7Z4D
    title: "Capacity"
    band: "90-99"
    description: "Measurements, performance tuning, capacity assessments. Consumes data produced by Book 83 Performance Testing."
    chapters:
      - id: "91-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAD95QRYW96CMHEF5J
        title: "Measurements"
        status: "placeholder"
        description: "Empirical capacity data: row counts, payload sizes, throughput, compression timings."
      - id: "91-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAMZBSAVPY4994CV90
        title: "Performance Tuning"
        status: "placeholder"
        description: "Performance tuning workflow and historical findings. Companion to 83-02 Performance Benchmarks."
      - id: "91-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAY6M3726193PVW56R
        title: "Capacity Assessments"
        status: "placeholder"
        description: "Application-level capacity assessments — dated, scoped analyses that translate measurements and headroom estimates into action thresholds and migration triggers. Companion to 83-01 Capacity Testing."

  - id: "92"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9NHTVTBN3QESYMS73
    title: "Deployment"
    band: "90-99"
    description: "Cloud, on-prem, and self-contained build topologies."
    chapters:
      - id: "92-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAKVM9KPSZRGJX9KC8
        title: "Cloud Deployment"
        status: "placeholder"
        description: "Cloud-targeted deployment topology. (optional)"
      - id: "92-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAV7GTV0WFBHBRTCN8
        title: "On-Prem Deployment"
        status: "placeholder"
        description: "Self-contained on-premise deployment. (optional)"
      - id: "92-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA9MEEQB54M8S55DQ2
        title: "Self-Contained Build"
        status: "placeholder"
        description: "Build artifacts and bundling for air-gapped installs. (optional)"

  - id: "93"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9WXB0VXW245NSMM8D
    title: "Security"
    band: "90-99"
    description: "Trust boundaries, authn, authz, data-at-rest, data-in-transit, validation, secrets, supply chain, logging-and-audit, decisions, tenancy enforcement, client render safety, SQL execution, resource limits, and file/asset handling. Several chapters are optional — apply only those that match the project's surface."
    chapters:
      - id: "93-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA487BDG363Z9AAKT3
        title: "Trust Boundaries"
        status: "placeholder"
        description: "Where untrusted input crosses into trusted contexts; how trust is established at each boundary. Companion to 93-18 Threat Modeling, which produces the threat model that justifies the trust-boundary placement."
      - id: "93-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA3V0NB6D31EAHGJYT
        title: "Authentication"
        status: "placeholder"
        description: "Identity establishment, session token shape, password hashing, cookie flags, session expiry/rotation. Companion to 47-01."
      - id: "93-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAW5DKZMT2QZ6B4HJG
        title: "Authorization"
        status: "placeholder"
        description: "What an authenticated principal can do; capability gating; IDOR avoidance per request. Companion to 47-02."
      - id: "93-04"
        arc_100: true
        arc_100_ulid: 01KRRRFNGA77FZGWFAWE8KH9NY
        title: "Data at Rest"
        status: "placeholder"
        description: "Security posture of stored data: what is stored plaintext vs encrypted, key management, backup posture, secret material in DB."
      - id: "93-05"
        arc_100: true
        arc_100_ulid: 01KRRRFNGARXGTPGAXYF904JHF
        title: "Data in Transit"
        status: "placeholder"
        description: "TLS posture, transport-layer confidentiality and integrity."
      - id: "93-06"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAJ2G40ZKT3WHRSTPG
        title: "Validation and Encoding"
        status: "placeholder"
        description: "Field-level type/range/format validation and per-context output encoding."
      - id: "93-07"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAZDX75G7WQ9R832A0
        title: "Secrets"
        status: "placeholder"
        description: "Keys, tokens, env vars; secret-shape registry; what must never be logged."
      - id: "93-08"
        arc_100: true
        arc_100_ulid: 01KRRRFNGAPSR6Q5C3AWFXEYPY
        title: "Supply Chain"
        status: "placeholder"
        description: "Dependency policy stance: minimum maintainer count, minimum publish age, postinstall ban, license allow-list, lockfile-delta review, transitive-trust model. Policy only — the operational practice (component scanning, CVE-triage workflow, SBOM generation) lives in Book 95 Software Composition Analysis."
      - id: "93-09"
        arc_100: true
        arc_100_ulid: 01KRRRFNGBCHDYR9QR8N2Q082G
        title: "Logging and Audit"
        status: "placeholder"
        description: "What is logged, what must NEVER be logged, audit-trail expectations, redaction contract, audit-event taxonomy. Companion to 90-01 Logging and 48 Audit."
      - id: "93-10"
        arc_100: true
        arc_100_ulid: 01KRRRFNGBXT7QSG9R171QH2KR
        title: "Decisions and Rejections"
        status: "placeholder"
        description: "Security decisions taken and the alternatives rejected, with rationale."
      - id: "93-11"
        arc_100: true
        arc_100_ulid: 01KRRRFNGBKMF1YMH6DZ8FDDT5
        title: "Tenancy Enforcement"
        status: "placeholder"
        description: "The mechanism by which every server-side read or mutation re-derives tenant scope from the authenticated session and rejects any client-supplied tenancy key that disagrees. (optional — multi-tenant systems only)"
      - id: "93-12"
        arc_100: true
        arc_100_ulid: 01KRRRFNGBBKT0BST0JFEKW61W
        title: "Security Testing Policy"
        status: "placeholder"
        description: "What must be tested and how often: required test modes per application surface (SAST/DAST/IAST/Pen Test), severity thresholds that block merge or release, scheduled vs gated cadence, third-party engagement model. The how-to-execute lives in Book 84 Security Testing."
      - id: "93-13"
        arc_100: true
        arc_100_ulid: 01KRRRFNGB0SNHZFTWDT2JZ1GB
        title: "Client Render Safety"
        status: "placeholder"
        description: "XSS prevention; per-context encoding (text node / HTML attribute / SVG attribute / URL / JSON-in-script / CSS); SVG-specific attack surface; render-idiom safety register. (optional — applications with a client UI)"
      - id: "93-14"
        arc_100: true
        arc_100_ulid: 01KRRRFNGBB8D7ZS544EJD5AK4
        title: "SQL Execution"
        status: "placeholder"
        description: "Approved SQL execution shapes; ban on string-interpolated SQL; migration discipline (idempotency, no DROP on production DBs). (optional — applications using SQL)"
      - id: "93-15"
        arc_100: true
        arc_100_ulid: 01KRRRFNGBF9AQW68MKP9ZAH33
        title: "Resource Limits"
        status: "placeholder"
        description: "Availability discipline: unbounded loops/recursion register, regex length-cap rule (ReDoS), JSON.parse input-size cap, per-table query-result bounding, payload-cap policy."
      - id: "93-16"
        arc_100: true
        arc_100_ulid: 01KRRRFNGB6BW69WZ0HDK81T3Z
        title: "File and Asset Handling"
        status: "placeholder"
        description: "Upload, storage, and serve-back rules for user-supplied files. Magic-byte MIME verification, allowed-MIME register per feature, decompression budget, Content-Disposition escaping, no-execute-trusted serving. Companion to Book 63 Assets. (optional — applications that accept uploads)"
      - id: "93-17"
        arc_100: true
        arc_100_ulid: 01KRRRFNGBKYXYR4PXXDM4SGXJ
        title: "Runtime Application Self-Protection (RASP)"
        status: "placeholder"
        description: "Runtime instrumentation inside the application that detects and blocks attacks in production. Distinct from testing — RASP is a runtime defense alongside 93-15 Resource Limits and 93-09 Logging and Audit. (optional)"
      - id: "93-18"
        arc_100: true
        arc_100_ulid: 01KRRRFNGB6XMBWVW39ED7AK42
        title: "Threat Modeling"
        status: "placeholder"
        description: "Threat-modelling methodology for the application: assets, attack surfaces, threats, and mitigations. Anchored in OWASP SAMM Design: Threat Assessment as the maturity reference and the OWASP Threat Modeling project (STRIDE, PASTA, attack trees) as method references. Companion to 93-01 Trust Boundaries (the posture this model justifies) and Book 84 Security Testing (the validation arm)."
        keywords: ["threat-modeling", "stride", "pasta", "attack-surface", "owasp-samm", "owasp"]

  - id: "94"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9BD9RJJY0H6CAAQQT
    title: "Compliance"
    band: "90-99"
    description: "Data retention and regulated-data handling."
    chapters:
      - id: "94-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGBG3DA05ZZVYY8GXME
        title: "Data Retention"
        status: "placeholder"
        description: "Per-jurisdiction data retention and deletion policy. (optional)"
      - id: "94-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGBBD6QDSQKY7VV233E
        title: "Regulated Data"
        status: "placeholder"
        description: "PII, PHI, and other regulated-data handling for enterprise deployments. (optional)"

  - id: "95"
    arc_100: true
    arc_100_ulid: 01KRRRFNG9TMHXBV8ZDG9R7HYC
    title: "Software Composition Analysis"
    band: "90-99"
    description: "Operational practice of inspecting the third-party component inventory: NVD/CVE scanning, license allow-list enforcement, and customer-facing SBOM production. The dependency-acceptance policy itself lives in 93-08 Supply Chain."
    chapters:
      - id: "95-01"
        arc_100: true
        arc_100_ulid: 01KRRRFNGBWNTQKDTNH8ZRPX65
        title: "Vulnerabilities Detection"
        status: "placeholder"
        description: "Inventory of third-party components scanned against the National Vulnerabilities Database (NVD) for known CVEs. Scanner choice, scan cadence, severity thresholds, CVE-triage workflow, false-positive register, and remediation SLAs. Companion to 93-08 Supply Chain (policy)."
      - id: "95-02"
        arc_100: true
        arc_100_ulid: 01KRRRFNGBDPQ2X0RX9MXBC6YH
        title: "License Compliance"
        status: "placeholder"
        description: "Awareness of every component's license, mapped against the project's license allow-list (defined in 93-08). Copyleft-detection workflow, attribution-bundle generation, and the escalation path when a disallowed license is detected in a direct or transitive dependency."
      - id: "95-03"
        arc_100: true
        arc_100_ulid: 01KRRRFNGB9FY1343V3A25H8WK
        title: "Software Bill of Materials (SBOM)"
        status: "placeholder"
        description: "Concise machine-readable inventory of every open-source component the application ships with, in a format suitable for delivery to customers requesting an SBOM as part of their security review (CycloneDX or SPDX). Generation cadence, signing, distribution channel, and the customer-facing SBOM contract."
```

<!-- ARC-100-INDEX-END -->

### 00-01.3 — Per-band notes

#### Band 00-09 — Application

The application's most fundamental identity. Topics in this band
describe what the application is, who it serves, why it exists, and
the design principles that shape every downstream implementation
choice — concerns that would survive a complete reimplementation in a
different language, runtime, or stack.

Three books are allocated:

- **Book 00 — ARC-100 System.** The documentation-indexing system
  itself. Six chapters populated (`00-00 General`, `00-01 Index`,
  `00-02 Glossary`, `00-03 Documentation Site`, `00-04 Standards
  Comparisons`, `00-05 Synchronization`, `00-06 Architectural
  Modeling`).
- **Book 01 — \<NAME\> System.** The active project's own
  documentation-system instance. Five placeholder chapters
  (`01-00 General`, `01-01 Index`, `01-02 Architectural Modeling`,
  `01-03 Documentation Site`, `01-04 Extensions`); slot identities
  are upstream-prescribed and bodies are project-authored per
  §00-00.7.1.
- **Book 02 — Philosophy.** What the application is, who it's for,
  why it exists, what it requires of the world and of itself, what
  it interfaces with externally, what quality attributes it must
  meet, and the cross-cutting design principles that shape every
  other architectural decision. Eight chapters allocated as
  placeholders (`02-01 Mission and Purpose` through `02-08 Quality
  Requirements`); substance authored as the application's high-level
  framing matures.

7 book slots remain unallocated (Books 03–09). Future slots are
reserved for application-level concerns that are too cross-cutting
for any single domain band.

#### Band 10-19 — Governance

Application glossary, roadmap, decisions, versioning policy. Four
books allocated, all with placeholder chapters:

- **Book 10 — Glossary.** Application domain vocabulary (distinct
  from the ARC-100 Glossary at `00-02`, which covers documentation-
  system terminology only).
- **Book 11 — Roadmap.** Forward-looking architectural items and the
  out-of-scope register.
- **Book 12 — Decisions.** ADRs (optional — adopt only if the project
  formalizes architectural decision records).
- **Book 13 — Versioning.** Version lifecycle and the promote-version
  command contract.

#### Band 20-39 — Client

The client band is the most application-specific. ARC-100 allocates
three books:

- **Book 20 — Client Foundations.** Overview, module structure, build
  pipeline, state management, routing, error handling, accessibility.
- **Book 21 — Server Communication.** HTTP client wrapper, realtime
  channel, client-side auth surface, retry/error handling, response
  caching, optimistic updates. Consumes the API contract published in
  Book 42.
- **Book 22 — Design.** The application's visual and experiential
  design system, in three tiers: Foundations (the design language and
  brand that govern every other chapter), Elements (typography, voice,
  color, iconography, imagery, layout, motion, interactivity), and
  Implementation (style/CSS, vectors, assets). Optional — applies to
  any application with a user interface.

The remaining 17 book slots are deliberately unallocated — they are
where a project's application-specific UI surfaces (panels,
visualizations, designers, component libraries, etc.) will land.

A CLI tool, library, or static-site project may leave this band
empty entirely. A client that never talks to a server may skip
Book 21.

#### Band 40-59 — Server

Server foundations, transport, API contract, identity, audit, plus
forward-looking notification and search. Allocated books:

- **Book 40 — Server Foundations.** Top-level server architecture,
  boot sequence, and internal service decomposition. The Internal
  Services chapter (`40-03`) covers service boundaries and the
  service wire shapes between them.
- **Book 41 — Transport.** Low-level HTTP, WebSocket, and
  internal-channel surfaces. Book 41 owns *how bytes move*; Book 42
  owns *what the API says*.
- **Book 42 — API.** The published API contract: surface style,
  versioning, error envelope, pagination, idempotency, rate limiting,
  machine authentication, webhooks, schema publication.
- **Book 47 — Identity.** Authentication, authorization, MFA,
  federation, sessions.
- **Book 48 — Audit.** Audit-event capture (the *application* layer;
  the *security* posture is at 93-09).
- **Book 53 — Notifications.** Event-driven user notifications.
- **Book 54 — Search.** Server-side search infrastructure.

13 book slots unallocated. Project-specific server topics (workflow
runtime, billing, mutation pipelines, room models, etc.) land in
those gaps.

A library or static-site project may leave this band empty.

#### Band 60-79 — Data

Data foundations, persistence, client hydration wire, asset data,
audit data, identity data, migrations. Allocated books:

- **Book 60 — Data Foundations.** Top-level data model and schema
  conventions.
- **Book 61 — Persistence.** Database engine and transaction patterns.
- **Book 62 — Client Hydration Wire.** The full-fidelity data shape
  the privileged first-party client receives and treats as its
  working in-memory model. Distinct from the curated third-party
  subset published as the API contract (42-10).
- **Book 63 — Assets.** Document, image, and video asset storage and
  metadata.
- **Book 64 — Audit Data.** Audit-table schema, indexing, retention.
  Companion to Book 48 Audit.
- **Book 65 — Identity Data.** User, tenancy, credentials, MFA,
  permissions schemas. Companion to Book 47 Identity.
- **Book 66 — Migrations.** Schema-evolution strategy and tooling.

**Three kinds of wire** are distinguished in the index, intentionally:
the *client hydration wire* (Book 62) is the full-fidelity shape the
privileged first-party client treats as its working model; the
*API wire* (42-10) is the curated, third-party-stable subset published
as part of the API contract; the *service wire* between internal
services is documented within 40-03 Internal Services alongside the
service architecture, since its conventions track the decomposition
itself.

13 book slots unallocated. Project-specific data topics (parameter
schemas, type-object patterns, billing data, etc.) land in those gaps.

A stateless library may leave this band empty.

#### Band 80-89 — Tooling

The materials, instruments, and conventions used to build, validate,
and integrate the application. Tooling chapters are contributor-facing:
a contributor needs them to work on the system, while a user of the
system never reads them. Topics in this band are technology-bound and
would be rewritten under a complete reimplementation — distinguishing
them from the Application band (00-09), whose topics stand independent
of the chosen stack.

Seven books allocated:

- **Book 80 — Environment.** Language, runtime, type system, project
  structure.
- **Book 81 — Linting.** Lint, type-check, markdownlint, and other
  code-health static checks. Security-focused static analysis (SAST)
  lives in Book 84.
- **Book 82 — Functional Testing.** Unit, integration, contract, and
  end-to-end testing, plus the helpers/fixtures and coverage policy
  that support them.
- **Book 83 — Performance Testing.** Capacity testing and performance
  benchmarking methodology.
- **Book 84 — Security Testing.** SAST, DAST, IAST, and penetration
  testing. The policy layer — what must be tested, severity thresholds,
  gating cadence — lives in `93-12 Security Testing Policy`.
- **Book 85 — CI.** Pre-commit/pre-push hooks and CI/CD pipeline.
- **Book 86 — Repository.** The version-control container and the
  conventions that govern its day-to-day use: VCS choice and hosting,
  repository topology (monorepo vs polyrepo), branching model, commit
  conventions, merge/review policy, tagging and releases, and signing
  and branch protection. Sits as the first tool in the developer
  pipeline that every other Book 80–85 instrument hooks into.
  Companion to 80-03 Project Structure, Book 85 CI, and Book 93
  Security.

**Capacity- and performance-testing chapters** live in Book 83
(`83-01 Capacity Testing`, `83-02 Performance Benchmarks`) rather than
Book 91 so that all testing methodology stays co-located in band
80-89. The data those tests produce, and the assessments that consume
it, live in Book 91 in band 90-99 (`91-01 Measurements`, `91-02
Performance Tuning`, `91-03 Capacity Assessments`).

#### Band 90-99 — Operations

Observability, capacity, deployment, security, software composition
analysis, compliance. Six books allocated:

- **Book 90 — Observability.** Logging, metrics, tracing.
- **Book 91 — Capacity.** Measurements, performance tuning, capacity
  assessments.
- **Book 92 — Deployment.** Cloud, on-prem, self-contained build
  topologies.
- **Book 93 — Security.** Seventeen chapters covering trust
  boundaries, authn, authz, data-at-rest, data-in-transit, validation,
  secrets, supply chain, logging-and-audit, decisions, tenancy
  enforcement, security testing policy, client render safety, SQL
  execution, resource limits, file/asset handling, and runtime
  application self-protection (RASP). Several are tagged `(optional)`
  — apply only the chapters that match the project's surface (e.g.,
  93-13 Client Render Safety applies only to applications with a
  client UI; 93-14 SQL Execution applies only to applications using
  SQL; 93-17 RASP applies only if you operate runtime instrumentation).
  The policy/practice partition with Book 84 Security Testing: 93-12
  *Security Testing Policy* defines what must be tested and the
  severity gates; Book 84 covers how the tests are run.
- **Book 94 — Compliance.** Data retention and regulated-data handling.
- **Book 95 — Software Composition Analysis.** The operational
  practice of inspecting the application's third-party component
  inventory: vulnerability detection against the NVD, license-allow-list
  enforcement and copyleft surveillance, and customer-facing SBOM
  production. **Policy/practice partition:** the dependency-acceptance
  *policy* (minimum maintainer count, license allow-list, postinstall
  ban, lockfile-delta review, transitive-trust model) lives in `93-08
  Supply Chain`; Book 95 covers the *operational mechanics* — the
  scanner, the triage workflow, and the SBOM artifact.

4 book slots unallocated.

### 00-01.4 — Project-specific allocation guidance

When a project adopts ARC-100, the librarian allocates project-specific
chapters into unallocated slots without amending ARC-100 itself. Two
patterns are normal:

- **New chapter in an existing ARC-100 book.** Example: a project's
  authentication system uses passkeys; allocate `47-06 Passkeys` as a
  new chapter under existing book `47 Identity`. The book and band
  inherit ARC-100; only the chapter is project-specific.
- **New book in an unallocated slot.** Example: a workflow-engine
  project allocates `42 Room Model` and `43 Mutation Pipeline` in the
  unallocated 40-59 server band. The band inherits ARC-100; the books
  are project-specific.

The librarian halts at any proposal that would require a new band
(see §00-00.7); band changes are reserved for ARC-100.2.

### 00-01.5 — Pointers

- **System spec**: [`00-00_ARC-100_General.md`](00-00_ARC-100_General.md)
- **Glossary**: [`00-02_ARC-100_Glossary.md`](00-02_ARC-100_Glossary.md)

---

> **Maintenance.** Only the librarian may add or modify entries
> in the YAML block. Manual hand-editing of the YAML is forbidden.
> Prose sections (00-01.1, 00-01.3, 00-01.4, 00-01.5) may be edited
> by mkdocs-related agents or by humans before the librarian is wired
> in; the librarian leaves prose alone.
