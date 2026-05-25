# CollabAcad — Presentation Source (Capstone 5)

**Format:** 6 slides + live interactive playground | **Total time:** 10 minutes
**Audience:** Thesis panel (Institutional IT & Administration Services)
**Style:** Academic Indigo & Social Coral (classic serif headings, modern sans interfaces, reactive node network background)
**Source of truth:** `collabacad_defense_guide.md` (defense guide) + `collabacad_research_paper.md` (research paper)

> **Timing Budget (10 min)**
> - Slide 1: Title & Tagline (The Anchor) · 0:30
> - Slide 2: The Mess vs. The Solution (The Hook) · 1:30
> - Slide 3: Proposed Architecture (The Shape) · 2:00
> - Slide 4: Tech Stack & Component Map (Housekeeping) · 1:30
> - Slide 5: Equity & Anonymity Mechanics (Research Rigor) · 3:00
> - Slide 6: Scope, Roadmap & Difficulty (Execution Plan) · 1:30

---

## Slide 1 — Title (30 sec)

| Element | Content |
|---------|---------|
| Logo Mark | **CA** (Indigo/Coral emblem with intersecting nodes) |
| Tagline | Capstone Project · Title Defense · 2026 |
| Title | **CollabAcad** |
| Subtitle | An Institutional Forum and Real-Time Event Management System with Segmented Weighted Voting and Anonymous Feedback Channels |
| Core Focus | Solving structural equity, boundary collapse, and discourse suppression in campus communication |

**Speaker Script:**
> "Good [morning/afternoon], distinguished members of the panel. I am [Name], and together with my co-researchers, we present **CollabAcad**. 
> 
> Our project is a purpose-built, real-time institutional forum and event management platform designed to replace the fragmented and boundary-violating communication practices currently held together by consumer-grade messaging networks like Facebook Messenger group chats. 
> 
> Through Socket.IO-based real-time event broadcasting, department-normalized voting weights, and a managed anonymity layer, we establish an institutional commons that respects boundaries, enforces mathematical representation, and guarantees psychological safety."

**Cue:** Advance slide on the words *"psychological safety"* to maintain momentum.

---

## Slide 2 — The Mess vs. The Solution (90 sec)

**Layout:** Two unequal columns. Left: "The Status Quo (Messenger GCs)" in muted crimson styling. Right: "The CollabAcad Resolution" in vibrant indigo and coral styling. One-to-one problem-solution alignment.

| The Status Quo (Consumer GCs) | The CollabAcad Resolution |
|--------------------------------|----------------------------|
| **Boundary Collapse:** Official work and announcements clutter personal accounts, causing high cognitive load and teacher distress. | **Role-Segmented Channels:** Separate workspaces for faculty, student government, and student roles, respecting personal boundaries. |
| **Representative Inequity:** Student votes use raw counts, allowing large colleges (e.g., CAS's 1,200) to arithmetically drown out small ones (e.g., CTE's 300). | **Segmented Weighted Voting:** Normalizes votes by department population, ensuring equitable democratic representation for all colleges. |
| **Discourse Suppression:** Students fear academic retaliation or peer judgment, silencing honest feedback on administrative or curricular issues. | **Managed Anonymity:** Pre-publication keyword filtering keeps posts clean while keeping student identities sealed and audit-logged. |

**Speaker Script:**
> "Let's address the reality of campus communication today. When we rely on Facebook Messenger for official school operations, we inherit three structural failures.
> 
> First, boundary collapse. Faculty members are forced to use personal accounts for work, resulting in round-the-clock notifications and identity strain. CollabAcad resolves this with role-segmented workspaces.
> 
> Second, raw majority voting. A student government vote on student fees is arithmetically dominated by CAS's 1,200 students, leaving CTE's 300 students completely powerless. CollabAcad introduces a department-normalized weighted voting algorithm.
> 
> Third, discourse suppression. Students stay silent on structural issues due to fear of peer judgment or administrative backlash. CollabAcad provides managed anonymous feedback channels where identity is securely sealed and audited, while server-side keyword filters prevent abuse."

**Cue:** Point to the red-to-green mapping. Transition to Slide 3.

---

## Slide 3 — Proposed Architecture (120 sec)

**Layout:** Large architectural diagram showing the WebSocket stream, data persistence tiers, and cache synchronization loops.

```
[ Client (React/Next.js) ]
       │  ▲
       │  │ (1) WS Handshake: ws://collabacad.edu/events
       ▼  │ (2) Real-Time Announcements / Ticker Streams (Socket.IO)
[ Node.js / Express Server & Socket.IO Engine ]
       │                                 ▲
       ├─► (3) Cache Update (Write)      │ (4) Pub/Sub Event Fanout
       ▼                                 │
[ Redis L1/L2 Caches ] ◄─────────────────┘
       │
       ▼ (5) Durable Write-Through (Async Batch)
[ PostgreSQL DB (L3) ]
```

**Speaker Script:**
> "CollabAcad is not a simple CRUD application. It is a distributed real-time platform. This diagram outlines our three-tier memory architecture.
> 
> At the top, clients connect via WebSockets to namespaces like `/events` or `/voting`. 
> 
> To achieve a latency under 100 milliseconds for active streams, we implement a memory hierarchy inspired by hardware cache structures. 
> 
> **L1** is our Hot Session Cache in Redis, holding active vote tallies and the real-time ticker queue. 
> **L2** is our Working Application Cache in Redis, managing session tokens and metadata. 
> **L3** is our long-term durable store in PostgreSQL.
> 
> Cache coherence is governed by a software-defined MESI protocol using atomic Redis locks. This prevents simultaneous vote writes from causing race conditions, ensuring data consistency even under high concurrency."

**Cue:** Trace the arrow from the Client to Redis to PostgreSQL.

---

## Slide 4 — Tech Stack & Component Map (90 sec)

**Layout:** Structured grid showing the technologies and how they map to regulatory requirements for BSIT capstone compliance.

| System Layer | Selected Technology | Compliance Component Map |
|---|---|---|
| **Frontend Web** | **React / Next.js** (Tailwind CSS) | Interactive dashboards, live event feed, and voting modules. |
| **Real-Time Engine** | **Socket.IO** (Node.js) | Under 100ms push notification delivery and live tickers without page refresh. |
| **Hot Cache** | **Redis Pub/Sub** | Decouples WebSocket emission from API logic to support horizontal scaling. |
| **Relational Store** | **PostgreSQL** | Strict relational mapping for audit trails, voter rolls, and forum records. |
| **Moderation Engine** | **Regex Pipeline + Perspective API** | Pre-publication toxicity screening and keyword moderation for anonymous threads. |

**Speaker Script:**
> "To execute this design, we selected a modern, highly performant stack. 
> 
> The application is powered by Next.js and React on the frontend, ensuring responsive web layouts. 
> 
> The real-time messaging pipeline is driven by Node.js and Socket.IO. We run Redis as a pub/sub event fanout to separate server processing from network emissions, which allows the system to scale horizontally. 
> 
> For data storage, PostgreSQL provides the relational integrity needed for voter registration and audit logging. 
> 
> Finally, the moderation engine uses a custom regex pipeline with optional Perspective API integration to sanitize anonymous submissions before they are broadcast."

**Cue:** Move quickly past the tech list, emphasizing that the components are chosen for performance and reliability.

---

## Slide 5 — Equity & Anonymity Mechanics (180 sec)

**Layout:** Live interactive playground. 
- Left panel: **Segmented Weighted Voting Simulator**. Sliders let panelists adjust votes and populations for two departments (e.g. CAS and CTE) and compare the Unweighted Raw Count (where the CAS majority dominates the outcome) to the Normalized Weighted Score (where voices are balanced).
- Right panel: **Managed Anonymity Toxicity Filter**. A text entry field where typing toxic words (e.g. "cheat", "scam", "stupid") triggers real-time keyword flagging, demonstrating the pre-publication screening queue.

**Equations displayed:**
$$W_d = \frac{V_d}{P_d} \times 100$$
$$W_{inst} = \frac{1}{|D|} \sum_{d \in D} W_d$$

**Speaker Script:**
> "Let's demonstrate the mathematical and security mechanisms that ground our research. 
> 
> On the left, we show the **Segmented Weighted Voting Simulator**. If we have a large college like CAS with 1,200 students, and a small college like CTE with 300 students—a raw headcount vote of 600 CAS students will easily crush 240 CTE students, representing a 71% raw majority for CAS's preference. 
> 
> However, our algorithm normalizes participation per department population. As you can see on the simulator, CAS has a 50% participation weight, whereas CTE has an 80% participation weight. In our equity-normalized score, CTE's voice is protected, and the institutional result is 65% in favor of participation, adjusting for size asymmetry.
> 
> On the right, we show the **Managed Anonymity pipeline**. When a student posts anonymously, the text is screened in real-time. If you type a restricted keyword, the system flags it immediately and diverts it to the admin review queue. To ensure accountability, the true voter identity is written into a separate PostgreSQL schema protected by Row-Level Security, accessible only to super-administrators under audited conditions, mirroring judicial de-anonymization protocols."

**Cue:** Interact with the sliders and type a flagged word into the filter box to show the real-time feedback.

---

## Slide 6 — Scope, Roadmap & Difficulty (90 sec)

**Layout:** 2-column division. Left: In-scope vs. Out-of-scope. Right: Phase roadmap and difficulty acknowledgement.

| Project Boundaries | Development Roadmap |
|--------------------|---------------------|
| **In Scope:**<br>· Role-based auth (Admin, Faculty, Officer, Student)<br>· Socket.IO live tickers & event posts<br>· Department-normalized polls & quorum alerts<br>· Keyword-filtered anonymous chat channels<br>· PostgreSQL database audit logging | **Phase 1: Core Infra (Weeks 1-4)**<br>· Database schema & Next.js setup<br>· WebSocket namespaces & authentication<br><br>**Phase 2: App & Voting (Weeks 5-8)**<br>· Weighted voting algorithm & lock checks<br>· Real-time ticker & notification delivery<br><br>**Phase 3: Moderation & Audit (Weeks 9-12)**<br>· Pre-publication regex queue & RLS setup<br>· Load benchmarks (k6) & SUS validation |
| **Out of Scope:**<br>· Third-party chat clients (Messenger integration)<br>· Native iOS/Android apps<br>· SMS/Email gateways (keeps data local) | **Difficulty Rating: Moderate-High**<br>· *Key Challenges:* Socket connection stability, cache synchronization locks, and Row-Level Security isolation. |

**Speaker Script:**
> "We conclude with our execution parameters. 
> 
> Our scope is strictly bounded: we implement the institutional web application, the live WebSocket event stream, the weighted voting engine, and the audited anonymity schema. We explicitly exclude third-party chat integrations and native mobile apps to keep student data secure and localized.
> 
> We are approaching development in three distinct phases: infrastructure setup, followed by application and voting modules, and finally moderation controls and system benchmarks. 
> 
> We rate this project as moderate-to-high difficulty due to the state synchronization requirements between Redis and PostgreSQL under load, but we are confident that our architectural plan addresses these risks. 
> 
> Thank you, panel. We are now open for your questions."

**Cue:** Stand by for questions. Keep the interactive playground on Slide 5 accessible in case the panel wants to test it during Q&A.
