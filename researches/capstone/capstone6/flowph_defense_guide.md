# FlowPH: A Dimension-Agnostic Government Funds Tracker and Citizen Watchdog Network — Canonical Knowledge Base and Title Defense Guide
*Capstone Title 6 · Public Finance Tech, Open Data Systems, and Auditable Visual Analytics*

---

## 0. Project Identity

| Field | Detail |
|---|---|
| **Working Title** | FlowPH: A Dimension-Agnostic Government Funds Tracker and Citizen Watchdog Network |
| **Domain** | Public Finance Technology (GovTech) · Information Visualization · Open Governance and Accountability Systems |
| **Core Thesis** | Existing government finance portals publish budget data in fragmented, static, and siloed CSV/PDF tables that prevent citizens and auditors from tracking the end-to-end flow of public funds. This opacity breeds mistrust and hides inefficiencies. **FlowPH** resolves this by modeling public finance as a structure-agnostic, transaction-level graph of money movement. By decoupling storage from rigid department hierarchies and leveraging dynamic dimension pivoting, it exposes the complete lineage of public money—from taxpayers to final suppliers—while validating every transaction against an immutable, publicly accessible Evidence Vault. |
| **Target Users** | Citizens, Investigative Journalists, Civil Society Organizations (CSOs), Department Finance Officers, and Commission on Audit (COA) Auditors |
| **Deployment Model** | Laravel Web Server + PostgreSQL Relational Engine + Redis cache and aggregation queue + D3.js interactive frontend |

**Hook Sentence:**
> "While national spending data remains buried in thousands of pages of unsearchable PDFs and disjointed CSV files, FlowPH tracks every single peso as a dynamic vector — letting citizens trace public funds directly from tax collections, through department allocations, to the exact contracts and receipts of private suppliers in real-time."

**Novelty Statement:**
Unlike the Department of Budget and Management's (DBM) existing systems (which only show top-down budget allocations) or open-data portals (which present static, disconnected tables), FlowPH introduces three novel contributions:
1. A **dimension-agnostic schema** that structures financial data from any government agency without requiring schema alterations.
2. A **dynamic dimension resolver** that automatically calculates paths for multi-tiered Sankey diagrams at runtime.
3. A **multi-state Evidence Verification Vault** that anchors transaction records to verified PDF contracts, geo-tagged site images, and independent COA audit reports.

---

## 1. The Core Defense Pitch (Slide Script)

*[2–3 minute oral delivery — speak confidently, maintain eye contact with each panel member]*

---

"Good morning, members of the panel. We present **FlowPH**, a web-based, dimension-agnostic budget transparency and money-movement visualization platform designed specifically so that citizens can see exactly where their taxes go. 

**The Scene of the Problem.** Today, if a citizen wants to know how the government spent the ₱5.7 Trillion national budget, they must download hundreds of separate Excel files from the DBM, match them with SEC filings of suppliers, and cross-reference them with scanned COA audit reports. There is no single system that links tax collection to agency allocation, down to final contractor disbursement. The data is intentionally siloed.

**The Solution Layer.** FlowPH breaks these silos by treating public money not as static columns, but as a directed graph. We do this through three core technical layers:
1. **The Storage Layer**: A unified three-table relational model (Flows, Dimensions, and Evidence) that stores all transactions, tags, and proof documents without rigid database migrations for different departments.
2. **The Interpretation Layer**: A dynamic resolver that takes complex user filters and calculates aggregations on the fly, rendering instant, multi-level Sankey diagrams.
3. **The Presentation Layer**: An intuitive frontend that guides the citizen from macro-level national charts down to micro-level evidence cards containing contracts, receipts, and photos.

**The Governance Advantage.** FlowPH moves beyond simple 'open data' by enforcing a strict verification pipeline. Transactions are tagged with explicit verification states: Fully Verified (supported by both receipts and COA clearance), Flagged (noting audit discrepancies), or Unverified. This introduces a structural mechanism of accountability, allowing citizen organizations to spot and audit discrepancies systematically.

Thank you. We are ready to take your questions."

---

## 2. Technical Architecture and Calculations

### 2.1 The Three-Table Unified Storage Model

To maintain perfect structural flexibility, FlowPH rejects department-specific tables. All agencies use the same three tables:

```
                  ┌──────────────────────────────┐
                  │            FLOWS             │
                  │  Stores the money vectors    │
                  └──────────────┬───────────────┘
                                 │
         ┌───────────────────────┴───────────────────────┐
         ▼ 1:N                                           ▼ 1:N
┌─────────────────┐                             ┌─────────────────┐
│ FLOW_DIMENSIONS │                             │  FLOW_EVIDENCE  │
│ Categorization  │                             │ Receipts, COA   │
│ tags (Region,   │                             │  contracts,     │
│ Agency, Program)│                             │ hashes, images  │
└─────────────────┘                             └─────────────────┘
```

#### 1. `FLOWS` (The Financial Vectors)
Stores the direct transfer of funds between entities:
* `id` (BIGINT, Primary Key)
* `from_entity` (VARCHAR: e.g., "Taxpayer", "National-Treasury", "DOH-Central")
* `to_entity` (VARCHAR: e.g., "DOH-Central", "DOH-Region4A", "ABC-Pharma-Inc")
* `amount` (DECIMAL(15,2): The exact monetary value)
* `flow_type` (ENUM: `collection`, `allocation`, `disbursement`)
* `flow_date` (DATE)
* `fiscal_year` (INT)
* `source_system` (VARCHAR: e.g., "BIR_API", "DOH_CSV")
* `raw_payload` (JSONB: Stores raw source payload for audit trails)

#### 2. `FLOW_DIMENSIONS` (The Explorable Schema-less Tags)
Stores key-value pairs linked to each flow, allowing infinite classification:
* `id` (BIGINT, Primary Key)
* `flow_id` (BIGINT, Foreign Key referencing `FLOWS.id`)
* `dimension_type` (VARCHAR: e.g., "sector", "region", "program", "tax_type", "contractor_sec")
* `dimension_value` (VARCHAR: e.g., "Health", "NCR", "Dengue Vaccination", "VAT", "SEC-998822")
* `depth_level` (INT: Determines order in the drill-down hierarchy)

#### 3. `FLOW_EVIDENCE` (The Trust Anchor)
Stores links and metadata of proof documents:
* `id` (BIGINT, Primary Key)
* `flow_id` (BIGINT, Foreign Key referencing `FLOWS.id`)
* `evidence_type` (ENUM: `contract`, `receipt`, `site_photo`, `audit_report`)
* `document_hash` (VARCHAR: SHA-256 hash of the original file to prevent tampering)
* `file_url` (VARCHAR: Remote link to government host or local S3 backup)
* `verification_source` (VARCHAR: e.g., "COA-Audit-2025", "SEC-Registry")
* `uploaded_at` (TIMESTAMP)

---

### 2.2 The Dynamic Dimension Resolver Algorithm

When a user views a Sankey diagram, the system must group and aggregate flows. The **Dimension Resolver** translates the active path into dynamic SQL:

```
Input: FiscalYear = 2025, ActiveFilters = {sector: "Health"}, GroupBy = "program"
```

The SQL generated dynamically:
```sql
SELECT 
    d2.dimension_value AS node_name,
    SUM(f.amount) AS total_amount,
    COUNT(f.id) AS transaction_count
FROM flows f
JOIN flow_dimensions d1 ON f.id = d1.flow_id
JOIN flow_dimensions d2 ON f.id = d2.flow_id
WHERE f.fiscal_year = 2025
  AND d1.dimension_type = 'sector' 
  AND d1.dimension_value = 'Health'
  AND d2.dimension_type = 'program'
GROUP BY d2.dimension_value
ORDER BY total_amount DESC;
```
This query maps the next layer of nodes dynamically without rigid foreign-key schemas.

---

### 2.3 Aggregation Engine and Indexing Strategy

To handle query response times under 100ms on millions of transaction records, FlowPH implements a **Materialized Aggregation Strategy**:

1. **GIN Indexing**: Built on the JSONB `raw_payload` in the `FLOWS` table for structural search flexibility.
2. **Composite B-Tree Indexes**: Created on `flow_dimensions(dimension_type, dimension_value, flow_id)` to speed up drill-down joins.
3. **Pre-computed Tables (`FLOW_AGGREGATES`)**:
   A cron job aggregates values nightly by common dimension combinations:
   $$\text{AggregateAmount} = \sum f.\text{amount} \quad \text{where} \quad d.\text{value} = X$$
   This enables the UI to load primary charts instantly.

---

### 2.4 Governance and The Multi-State Verification Matrix

A transaction on FlowPH can hold one of four verified status flags based on the existence and validation of supporting documentation:

$$\text{Verification State} = f(\text{Contracts}, \text{Receipts}, \text{COA Findings})$$

```
                   ┌─────────────────────────────┐
                   │    Is evidence complete?    │
                   └──────────────┬──────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼ Yes                           ▼ No
      ┌───────────────────────┐       ┌───────────────────────┐
      │  Any COA exceptions?  │       │  Any COA exceptions?  │
      └───────────┬───────────┘       └───────────┬───────────┘
            ┌─────┴─────┐                   ┌─────┴─────┐
        Yes ▼        No ▼               Yes ▼        No ▼
     ┌─────────┐ ┌───────────┐           ┌─────────┐ ┌───────────┐
     │ FLAGGED │ │ FULLY VER.│           │ FLAGGED │ │ UNVERIFIED│
     │  (Red)  │ │  (Green)  │           │  (Red)  │ │  (Gray)   │
     └─────────┘ └───────────┘           └─────────┘ └───────────┘
```

1. **Fully Verified (Green)**: Has uploaded contract, valid official receipt, and zero COA audit exceptions.
2. **Partially Verified (Yellow)**: Flow exists, but lacks either the receipt or contract document, and has no audit flags.
3. **Unverified (Gray)**: Only the raw transaction import exists; no verification documents uploaded yet.
4. **Flagged (Red)**: Audit exceptions registered by COA or document hash mismatch detected by the system.

---

## 3. Deep-Dive Technical Rebuttals (Mock Q and A)

### Category A: Architecture & Schema-less Validation

#### Q1: If you have a schema-less dimension system, how do you prevent users from entering garbage dimensions that break the visualization?
*   **Answer**: We enforce a **Source Registration Contract (SRC)**. While the database structure is flexible, each department registers their data adapter with a specific *Dimension Manifest* (a JSON configuration file). The manifest defines which dimension keys are valid (e.g., `region`, `tax_type`) and validates incoming values against official code sheets (e.g., ISO-3166 for regions, DBM codes for programs) before they are written. Inputs failing the manifest validation are quarantined in an import errors log.

### Category B: Security & Document Integrity

#### Q2: What prevents a corrupt department official from uploading fake evidence documents or altering files after they've been uploaded?
*   **Answer**: We implement **Evidence Hash Anchoring**. When a document is uploaded, the system generates a SHA-256 hash of the file payload in the background queue. This hash is written directly into `FLOW_EVIDENCE.document_hash`. Any attempt to alter the document on the host server will cause a mismatch against this hash, triggering a `FLAGGED` state on the UI. For full immutability, this hash can be anchored to a public ledger or distributed file registry (IPFS) in future iterations.

### Category C: Performance & Bulk Data Pipelines

#### Q3: How does the system handle massive transaction uploads from larger departments like the DPWH without crashing the server?
*   **Answer**: FlowPH uses an **Asynchronous Batch Pipeline**. When a department uploads a CSV file containing 100,000 transactions, the HTTP request only uploads the file to S3-compatible storage and creates a queued job via Laravel Queue (managed by Redis). The background worker splits the CSV into chunks of 1,000, inserts them using raw database bulk-insert statements (avoiding ORM overhead), and resolves dimensions in a single transaction blocks, preventing memory exhaust.

### Category D: Data Visualization & Sankey Pruning

#### Q4: Sankey diagrams become cluttered and unreadable when displaying thousands of nodes. How does FlowPH solve this visualization issue?
*   **Answer**: We apply **Progressive Aggregation and Node Pruning**. In the visualization engine, nodes that represent less than 2% of the active parent total are automatically grouped into a single "Other Agencies" or "Other Projects" node. Users can click this grouped node to expand it, or hover to see a summary. This prevents visual overload while preserving absolute transparency down to the single-peso level.

## 4. Component Coverage Map

| Layer | Component | Technologies | Purpose |
|---|---|---|---|
| **Web App** | Transparency Dashboard, Evidence Vault, Partner Admin Portal | Laravel 10, Livewire, Vanilla CSS | Core system routing, dashboard views, and department portal |
| **Mobile App** | Progressive Web App (PWA) | Service Workers, Web App Manifest | Lets citizens view budget flows and receive audit alerts on mobile |
| **Machine Learning / AI** | Outlier Anomaly Detector (Future Extension) | Python (Scikit-Learn / Isolation Forest) | Analyzes transaction dimensions to flag anomalous spending spikes |
| **IoT / Hardware** | Public Information Kiosk | Raspberry Pi 4 + Chromium kiosk mode | Physical terminal for local government halls to display transparency charts |
| **Data Visualization** | Interactive Sankey and Pivot Explorer | D3.js, ECharts, HTML5 Canvas | Renders the money flow diagrams and comparative bar charts |
| **Networking / Real-Time** | Dynamic Upload Pipeline | Redis 7, Laravel Queues | Processes large CSV uploads in background tasks without user timeout |

---

## 5. Scope and Delimitations

### In Scope
* Dynamic Sankey-based visualization of transaction paths.
* Dynamic Dimension Resolver supporting filters across unlimited nested layers.
* Unified three-table PostgreSQL database structure.
* Secure department portals with API key authentication for CSV uploads.
* Multi-state verification logic linking transactions to external document URLs.
* SHA-256 hashing of uploaded evidence files to prevent retro-active changes.
* Responsive web layouts and basic PWA support.

### Out of Scope
* Automatic OCR parsing of scanned paper invoices (uploads must use our CSV/API structures).
* Integration with the actual live BSP banking clearing loops (transactions are logged after clearing).
* Direct blockchain consensus writing (hashes are stored in DB, ledger integration is a future phase).
* Real-time push notifications to users for every single budget change (updates are compiled nightly).
