# FlowPH — Presentation Source (Capstone 6)

**Format:** 6 slides + live interactive playground | **Total time:** 10 minutes
**Audience:** Thesis panel (Public Administration and Information Technology Panel)
**Style:** Government Gold and Transparent Teal (glassmorphic dark UI, gold outlines, teal visualization nodes, dynamic canvas particle connections)
**Source of truth:** `flowph_defense_guide.md` (defense guide) + `flowph.md` (ground document)

> **Timing Budget (10 min)**
> - Slide 1: Title and Tagline (The Anchor) · 0:30
> - Slide 2: The Opaque Ledger (The Scene and Hook) · 1:30
> - Slide 3: Proposed Web-Based Solution Architecture (Proposed Architecture) · 2:00
> - Slide 4: Tech Stack and Component Map (Implementation Shape) · 1:30
> - Slide 5: Governance and Verification Simulator (Research Rigor) · 3:00
> - Slide 6: Scope, Boundaries and Timeline (Execution Plan) · 1:30

---

## Slide 1 — Title (30 sec)

| Element | Content |
|---------|---------|
| Logo Mark | **FΦ** (FlowPH symbol in Gold and Teal with intersecting flows) |
| Tagline | Title Defense · 2026 |
| Title | **FlowPH: Dimension-Agnostic Government Funds Tracker and Citizen Watchdog Network** |
| Subtitle | A decoupled financial lineage pipeline and community monitoring network for tracing government expenditures from national allocations down to supplier disbursements. |
| Core Focus | Establishing financial lineage, structural flexibility, and citizen auditing vectors |

**Speaker Script:**
> "Good morning, distinguished members of the panel. We present **FlowPH** — a platform built specifically so that citizens can see exactly where their taxes go. 
> 
> FlowPH solves the structural opacity of government spending by modeling budget data not as isolated, static tables, but as a continuous, verifiable, and dimension-agnostic graph of money movement. 
> 
> We turn static numbers into visible vectors, giving citizens and auditors the tools to trace public funds from tax collections directly to the contracts of private suppliers."

**Cue:** Project title card on screen; allow the panel to anchor the title.

---

## Slide 2 — The Opaque Ledger (90 sec)

**Layout:** Split screen. Left: A graphic showing fragmented folders, Excel sheets, and unsearchable PDF reports. Right: Three core problem pillars.

* **Pillar 1: Siloed Infrastructure**: Budget data is scattered across DBM, DOH, and DPWH sites with completely different structures.
* **Pillar 2: Linear Blind Spots**: Citizens can see what money was allocated to an agency, but they cannot see which private vendor received that money and for what project.
* **Pillar 3: The Proof Vacuum**: Published transactions lack direct, tamper-proof links to actual vouchers, receipts, or COA audit results.

**Speaker Script:**
> "Let us look at the reality of public spending analysis. If a citizen wants to audit a public health project today, they are met with what we call 'The Opaque Ledger'. 
> 
> First, they must extract numbers from disjointed CSV and Excel sheets across different agency portals. 
> 
> Second, these sheets only show top-level numbers—they stop at the department boundaries, hiding who actually got paid. 
> 
> Third, there is no way to verify if these payments are legitimate because there are no direct links to receipts or audit reports. 
> 
> Current systems fail because they hide the flow. FlowPH changes this by unifying data into an explorable, transaction-level vector graph."

**Cue:** Slide transitions with fade-in for each problem pillar.

---

## Slide 3 — Decoupled Ingestion and Dimension-Agnostic Storage Strategy (120 sec)

**Layout:** Strategic Data Flow Blueprint showing three decoupled domains: Ingestion (Scraped Sources and Adapters), Storage (Dimension-Agnostic Core), and Presentation (Resolver Engine and Client Canvas).

* **The Ingestion Adapter Layer:** Standardizes scraped data (DBM Excel sheets, PhilGEPS CSVs, DPWH Project Portals, and COA PDFs) before database insertion, protecting the core schema from source modifications.
* **Resilient Storage Core:** Decouples records from rigid government hierarchies using three stable tables (`FLOWS`, `FLOW_DIMENSIONS`, `FLOW_EVIDENCE`). Zero SQL migrations are required when departments re-organize or introduce new reporting metrics.
* **Dynamic Translation Engine:** The Laravel-based Dimension Resolver aggregates and pivots variables on the fly, feeding a standardized node-link structure directly to the client browser.

**Speaker Script:**
> "Distinguished panel, the core challenge of open-government portals is that scraped data is chaotic, siloed, and frequently changes shape. To solve this, FlowPH implements a decoupled, three-layer strategic architecture.
> 
> First, our Ingestion Adapter Layer acts as a buffer. It absorbs the formatting chaos of scraped PDFs, XLS files, and HTML tables, translating raw files into normalized vectors without touching our database structure.
> 
> Second, our Storage Core uses a dimension-agnostic schema. Rather than creating fragile tables for each department, we store all financial vectors in one Flows table, and map key-value metadata in a Dimensions table. If the government rolls out a new spending category—like Sustainable Development Goals or Calamity Funding—we don't run complex SQL database migrations. We simply append tag rows.
> 
> Third, our Interpretation Resolver translates client filters on the fly into clean node-link structures, letting our frontend canvas draw an unbroken visual chain of custody from taxpayer collections down to private suppliers."

**Cue:** Highlight the Adapter block on the left and the stable 3-table storage block in the center to show separation of concerns.

---

## Slide 4 — Web Framework, Scale and Performance Map (90 sec)

**Layout:** 2x2 matrix outlining the strategic engineering choices that support GovTech scaling and real-time visualization.

| System Layer | Selected Technology | Strategic Capability and Purpose |
|---|---|---|
| **API and Security** | **Laravel (PHP)** | Secure department API gates, source origin validation, and ingestion queue management. |
| **Transaction Engine** | **PostgreSQL** | Dynamic dimension grouping using composite index querying and JSONB raw payload auditing. |
| **Concurrency and Cache** | **Redis** | Background processing of large scraped batches; caching of pre-computed aggregations for instant page loads. |
| **Visual Canvas** | **D3.js / Vanilla JS** | Client-side rendering of multi-tiered Sankey diagrams, preserving smooth CSS transitions during drill-downs. |

**Speaker Script:**
> "To execute this strategic model, we selected a highly performant GovTech stack. 
> 
> Laravel manages our ingestion queue and secures our department APIs, ensuring that only validated data sources enter the pipeline.
> 
> PostgreSQL acts as our relational engine, using composite indexes on dimension values to perform multi-level aggregations in under 100 milliseconds. We store 100% of the raw scraped source row in a JSONB column, providing a complete data-lake audit trail.
> 
> Redis handles asynchronous batch importing, preventing server timeouts during bulk uploads of government files, while our client canvas uses D3.js to render animated Sankey paths that help users intuitively understand complex allocations."

**Cue:** Point out the separation between raw write operations (Redis queue) and visual read queries (indexed database tables).

---

## Slide 5 — The Strategic Auditing and Citizen Watchdog Network (180 sec)

**Layout:** Live interactive dashboard demonstration showcasing the citizen-agent auditing loop.
*   **Left Canvas: Dynamic Flow Pivot-Explorer**. Toggles for different dimensions (Sector, Agency, Program, Contractor). Selecting them dynamically recalculates weights and redraws the Sankey lines in real-time.
*   **Right Panel: Ingestion Sandbox and Watchdog Evidence Vault**. Shows the auditing check cards:
    -   **Update Alerts and Staging Diff:** Displays a preview of scraped update files compared to live database rows.
    -   **AI Watchdog Indicators:** Auto-flags transactions indicating shell corporate patterns (newly registered suppliers winning large tenders) or standard pricing exceptions (unit cost markups).
    -   **Evidence Anchors:** Dynamic uploads of user geotagged photos or receipts, cryptographically hashed and linked to the database vector.

**Speaker Script:**
> "Data without proof is just numbers. In Slide 5, we demonstrate the core of our platform: **The Strategic Auditing Loop and Citizen Watchdog Network**.
> 
> When our automated scrapers detect updates on legacy government portals, or when partner APIs push records via webhooks, the data enters an **Ingestion Staging Gate**. Admins and civil society receive alert diffs to review changes before committing them.
> 
> Once committed, our **AI Watchdog Agents** scan the Postgres transaction vectors. If the AI detects an anomaly—like a 300% markup on standard asphalt or a massive disbursement to a supplier registered only last week—it auto-flags the flow and alerts local watchdogs.
> 
> Subscribed citizen watchdogs act as ground verifiers, uploading physical photos or receipts. These uploads are hashed, anchored, and instantly shift the flow status to **'Flagged'**. Finally, the AI compiler aggregates these inputs into a structured **COA-Ready Audit Dossier** to trigger official audits, turning a passive dashboard into an active, crowdsourced accountability loop."

**Cue:** Click on a transaction node, open the Watchdog Evidence Card, toggle the AI alert exception, and show the flow line changing color.

---

## Slide 6 — Scope, Boundaries and Timeline (90 sec)

**Layout:** 2-column division. Left: In-scope vs. Out-of-scope. Right: Phase roadmap and difficulty acknowledgement.

| Project Boundaries | Development Roadmap |
|--------------------|---------------------|
| **In Scope:**<br>· Unified 3-table relational schema<br>· Dynamic dimension resolver logic<br>· D3.js dynamic Sankey visual engine<br>· Ingestion Staging Sandbox and Review dashboard<br>· Legacy hash-based HTML scrapers and Partner webhooks<br>· AI Watchdog anomaly detection triggers<br>· Evidence Vault with SHA-256 integrity | **Phase 1: Ingestion and API Gates (Weeks 1-4)**<br>· DB setup and synonym mapping<br>· Legacy scrapers and partner webhooks<br>· Ingestion staging review panel<br><br>**Phase 2: Resolver and Viz (Weeks 5-8)**<br>· Dimension resolver logic<br>· D3.js Sankey explorer integration<br><br>**Phase 3: Watchdogs and Evidence (Weeks 9-12)**<br>· AI anomaly detection rules<br>· Evidence hashing and upload pipeline<br>· AI audit report compiler |
| **Out of Scope:**<br>· Automated PDF OCR text recognition<br>· Real-time bank clearing hooks<br>· Consensus blockchain ledger | **Difficulty Rating: High**<br>· *Key Challenges:* Dynamic SQL join optimization, AI anomaly classification accuracy, and file integrity validation. |

**Speaker Script:**
> "To conclude, our execution scope is strictly bounded. We implement the unified storage, legacy scrapers, partner webhooks, the staging gate, D3 visualizations, and the AI Watchdog monitoring rules. We exclude automated OCR scans and blockchain networks to ensure immediate reliability.
> 
> Development spans 12 weeks: starting with ingestion and the staging review panel in Phase 1, moving to visual rendering in Phase 2, and concluding with the AI Watchdogs and Evidence Vault compiling in Phase 3.
> 
> This represents a highly sophisticated, AI-augmented transparency framework. Thank you, panel. We are now open for your questions."

**Cue:** Open the floor for panel questions. Keep Slide 5 visible in case they request a demo.
