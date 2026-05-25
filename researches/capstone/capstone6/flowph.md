# **FlowPH: Complete System Architecture**
*Full-Spanning Blueprint for Budget Transparency System*

---

## **Table of Contents**

### **Part I: System Foundation**
1. [System Vision and Core Principles](#1-system-vision--core-principles)
2. [The Big Picture: How Everything Connects](#2-the-big-picture-how-everything-connects)
3. [The Three-Layer Mental Model](#3-the-three-layer-mental-model)

### **Part II: Data Architecture**
4. [Core Data Model (The Foundation)](#4-core-data-model-the-foundation)
5. [Dimension System (What Makes It Flexible)](#5-dimension-system-what-makes-it-flexible)
6. [Aggregation Strategy (What Makes It Fast)](#6-aggregation-strategy-what-makes-it-fast)
7. [Data Lifecycle (Birth to Archive)](#7-data-lifecycle-birth-to-archive)

### **Part III: Integration Architecture**
8. [Adapter Layer (Chaos to Order)](#8-adapter-layer-chaos-to-order)
9. [Data Import Pipeline](#9-data-import-pipeline)
10. [Source Registration System](#10-source-registration-system)

### **Part IV: User Experience Architecture**
11. [The User Journey Map](#11-the-user-journey-map)
12. [State Management (How the App Thinks)](#12-state-management-how-the-app-thinks)
13. [Visualization Engine](#13-visualization-engine)
14. [Evidence and Verification Layer](#14-evidence--verification-layer)

### **Part V: System Intelligence**
15. [Smart Defaults and Personalization](#15-smart-defaults--personalization)
16. [Search and Discovery](#16-search--discovery)
17. [Anomaly Detection (Future)](#17-anomaly-detection-future)

### **Part VI: Technical Infrastructure**
18. [API Architecture](#18-api-architecture)
19. [Performance Strategy](#19-performance-strategy)
20. [Security Model](#20-security-model)
21. [Deployment Architecture](#21-deployment-architecture)

### **Part VII: Scaling and Evolution**
22. [MVP to Full System Roadmap](#22-mvp-to-full-system-roadmap)
23. [Multi-Department Scaling](#23-multi-department-scaling)
24. [Future Extensions](#24-future-extensions)

---

# **Part I: System Foundation**

## **1. System Vision and Core Principles**

### **What FlowPH Actually Is**

FlowPH is **NOT**:
- ❌ A database of all government data
- ❌ A replacement for existing systems
- ❌ A fixed schema application

FlowPH **IS**:
- ✅ A **flow visualization layer** over existing systems
- ✅ A **dimension-agnostic explorer** that adapts to any structure
- ✅ A **progressive disclosure interface** for public money

### **Core Design Principles**

**Principle 1: Flow-First, Structure-Agnostic**
```
We don't model departments.
We model MONEY MOVEMENT.
Everything else is metadata.
```

**Principle 2: User Intent, Not System Structure**
```
Users explore by asking questions:
  "Where does health spending go?"
NOT by navigating rigid trees:
  "Click Health → Click Programs → Click..."
```

**Principle 3: Source Truth Stays at Source**
```
We don't own the data.
We aggregate, visualize, verify.
Original documents stay with departments.
```

**Principle 4: Progressive Disclosure**
```
Show simple first.
Reveal complexity on demand.
Never overwhelm casual users.
```

---

## **2. The Big Picture: How Everything Connects**

### **The Complete System Map**

```
┌─────────────────────────────────────────────────────────────────┐
│                         CITIZENS (Users)                         │
│                  "Where does my money go?"                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Pie Charts   │  │  Bar Charts  │  │  Flow Lists  │         │
│  │ Interactive  │  │  Comparisons │  │  Evidence    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EXPLORATION ENGINE                           │
│  ┌────────────────────────────────────────────────┐            │
│  │  State Manager: Tracks user journey            │            │
│  │  Dimension Resolver: "What can user see next?" │            │
│  │  Aggregator: Sums money by dimension           │            │
│  └────────────────────────────────────────────────┘            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER (3 Tables)                       │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐│
│  │  FLOWS          │  │  FLOW_DIMENSIONS │  │  FLOW_EVIDENCE ││
│  │  (Money moves)  │  │  (What/Where)    │  │  (Proof)       ││
│  └─────────────────┘  └──────────────────┘  └────────────────┘│
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  FLOW_AGGREGATES (Pre-computed for speed)               │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INTEGRATION LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ BIR Adapter  │  │ DPWH Adapter │  │ DOH Adapter  │         │
│  │ (CSV/API)    │  │ (Excel/API)  │  │ (PDF/API)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA SOURCES                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │     BIR      │  │     DPWH     │  │     DOH      │         │
│  │  (Tax Data)  │  │  (Projects)  │  │  (Health)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Local Govt  │  │   Treasury   │  │     DBM      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### **Data Flow (Following One Transaction)**

```
1. BIR collects VAT from NCR Retail
   → BIR system records: ₱1.2M collected
   
2. BIR uploads to FlowPH (CSV or API)
   → "Date, Region, TaxType, Industry, Amount"
   
3. BIR Adapter processes:
   → Creates FLOW record: BIR-NCR → National-Treasury, ₱1.2M
   → Creates DIMENSIONS: [region:NCR, tax_type:VAT, industry:Retail]
   
4. FlowPH stores in database
   → FLOWS table gets new record
   → FLOW_DIMENSIONS table gets 3 linked records
   
5. Nightly aggregation runs
   → Pre-computes: "VAT in NCR = ₱1.2M"
   → Stores in FLOW_AGGREGATES for fast queries
   
6. Citizen visits FlowPH
   → Sees: "Tax collections: ₱500B total"
   → Clicks "VAT" → Sees "NCR: ₱1.2M"
   → System queries aggregates (instant response)
```

---

## **3. The Three-Layer Mental Model**

Think of FlowPH as three distinct layers stacked on top of each other:

### **Layer 1: STORAGE (The Truth)**

**What it does:** Stores raw facts about money movement

**Key components:**
- Flow records (who paid whom, when, how much)
- Dimensions (tags that make flows explorable)
- Evidence (links to proof)

**Analogy:** Library shelves storing books

**Never changes structure** - always the same 3 tables

---

### **Layer 2: INTERPRETATION (The Brain)**

**What it does:** Understands what users want and translates to queries

**Key components:**
- State manager (remembers user's journey)
- Dimension resolver (figures out "what's next")
- Aggregator (adds up money by category)

**Analogy:** Librarian who knows where everything is

**Adapts to user intent** - same engine, different results

---

### **Layer 3: PRESENTATION (The Face)**

**What it does:** Shows information in understandable ways

**Key components:**
- Charts (pie, bar, line)
- Lists (flows, evidence)
- Filters (region, date, amount)

**Analogy:** Book recommendations display

**Changes based on context** - desktop vs mobile, casual vs power user

---

### **How Layers Communicate**

```
USER ACTION:
  Clicks "Health" slice on pie chart
  
PRESENTATION LAYER says to INTERPRETATION:
  "User wants to see Health spending breakdown"
  
INTERPRETATION LAYER says to STORAGE:
  "Give me all flows where dimension_value = 'Health'"
  "Then tell me what other dimensions those flows have"
  
STORAGE LAYER responds:
  "Found 1,234 flows totaling ₱20B"
  "They have dimensions: region, department, program"
  
INTERPRETATION LAYER decides:
  "User should see breakdown by region (most logical next step)"
  
PRESENTATION LAYER renders:
  New pie chart showing regions
```

---

# **Part II: Data Architecture**

## **4. Core Data Model (The Foundation)**

### **The Three Essential Tables**

#### **Table 1: FLOWS (The Core Truth)**

**Purpose:** Every movement of money is ONE flow record

**Fields Explained:**

| Field | What It Means | Example |
|-------|---------------|---------|
| `id` | Unique identifier | 12345 |
| `from_entity` | Where money came from | "BIR-NCR" |
| `to_entity` | Where money went | "National-Treasury" |
| `amount` | How much moved | 1200000 |
| `flow_type` | Kind of movement | "collection", "allocation", "disbursement" |
| `flow_date` | When it happened | 2025-01-15 |
| `fiscal_year` | Budgeting period | 2025 |
| `source_system` | Who reported it | "BIR_API", "DPWH_MANUAL" |
| `raw_data` | Original data (JSON) | `{"tax_type": "VAT", ...}` |

**Example Records:**

```
Flow #1:
  from: "Taxpayers-NCR-Retail"
  to: "BIR-NCR"
  amount: 1,200,000
  type: "collection"
  date: 2025-01-15
  raw_data: {"tax_type": "VAT", "or_number": "12345"}

Flow #2:
  from: "National-Treasury"
  to: "DPWH"
  amount: 50,000,000
  type: "allocation"
  date: 2025-02-01
  raw_data: {"budget_line": "Infrastructure-2025"}

Flow #3:
  from: "DPWH"
  to: "ABC-Construction-Corp"
  amount: 30,000,000
  type: "disbursement"
  date: 2025-03-10
  raw_data: {"project": "Road-Widening-Calamba", "contract": "CON-2025-123"}
```

**Key Insight:**  
Notice `raw_data` is flexible JSON. We can store ANYTHING the source provides without changing the table structure.

---

#### **Table 2: FLOW_DIMENSIONS (What Makes It Explorable)**

**Purpose:** Tags that let users navigate flows

**Fields Explained:**

| Field | What It Means | Example |
|-------|---------------|---------|
| `id` | Unique identifier | 67890 |
| `flow_id` | Links to FLOWS table | 12345 |
| `dimension_type` | Category of tag | "region", "tax_type", "project" |
| `dimension_value` | Actual tag value | "NCR", "VAT", "Road-Widening" |
| `level` | Order for drilling down | 1, 2, 3 |

**Example: How Flow #1 Gets Tagged**

```
Flow #1 (BIR collection) creates these dimensions:

Dimension #1:
  flow_id: 12345
  dimension_type: "region"
  dimension_value: "NCR"
  level: 1

Dimension #2:
  flow_id: 12345
  dimension_type: "tax_type"
  dimension_value: "VAT"
  level: 2

Dimension #3:
  flow_id: 12345
  dimension_type: "industry"
  dimension_value: "Retail"
  level: 3
```

**Why This Works:**

```
User explores:
  1. "Show me VAT" → Filter where dimension_value = "VAT"
  2. "Where in VAT?" → Show other dimensions (region, industry)
  3. "NCR VAT" → Filter where region AND VAT
  4. "From which industry?" → Show industry breakdown
```

---

#### **Table 3: FLOW_EVIDENCE (Proof Links)**

**Purpose:** Connect flows to supporting documents

**Fields:**

| Field | What It Means | Example |
|-------|---------------|---------|
| `id` | Unique identifier | 111 |
| `flow_id` | Links to FLOWS | 12345 |
| `evidence_type` | Kind of proof | "document", "photo", "contract" |
| `external_url` | Where proof lives | "https://bir.gov.ph/docs/..." |
| `description` | What it is | "Official Receipt #12345" |
| `uploaded_at` | When added | 2025-01-15 |

**Example:**

```
Flow #3 (DPWH payment) has evidence:

Evidence #1:
  flow_id: 12345
  evidence_type: "contract"
  external_url: "https://dpwh.gov.ph/contracts/CON-2025-123.pdf"
  description: "Signed contract with ABC Construction"

Evidence #2:
  flow_id: 12345
  evidence_type: "photo"
  external_url: "https://dpwh.gov.ph/photos/road-before.jpg"
  description: "Road condition before construction"
```

---

### **How Tables Work Together (Complete Example)**

**Scenario:** DPWH pays contractor for NCR road project

```
FLOWS TABLE:
┌─────┬─────────┬────────────────────┬───────────┬──────────────┐
│ id  │ from    │ to                 │ amount    │ flow_type    │
├─────┼─────────┼────────────────────┼───────────┼──────────────┤
│ 999 │ DPWH    │ ABC-Construction   │ 30000000  │ disbursement │
└─────┴─────────┴────────────────────┴───────────┴──────────────┘

FLOW_DIMENSIONS TABLE:
┌─────┬─────────┬────────────────┬─────────────────────┬───────┐
│ id  │ flow_id │ dimension_type │ dimension_value     │ level │
├─────┼─────────┼────────────────┼─────────────────────┼───────┤
│ 1   │ 999     │ sector         │ Infrastructure      │ 1     │
│ 2   │ 999     │ department     │ DPWH                │ 2     │
│ 3   │ 999     │ region         │ NCR                 │ 3     │
│ 4   │ 999     │ project        │ Road-Widening-2025  │ 4     │
│ 5   │ 999     │ contractor     │ ABC-Construction    │ 5     │
└─────┴─────────┴────────────────┴─────────────────────┴───────┘

FLOW_EVIDENCE TABLE:
┌─────┬─────────┬────────────────┬───────────────────────────────┐
│ id  │ flow_id │ evidence_type  │ external_url                  │
├─────┼─────────┼────────────────┼───────────────────────────────┤
│ 1   │ 999     │ contract       │ https://.../contract.pdf      │
│ 2   │ 999     │ photo          │ https://.../before.jpg        │
│ 3   │ 999     │ inspection     │ https://.../audit-report.pdf  │
└─────┴─────────┴────────────────┴───────────────────────────────┘
```

**User Journey with This Data:**

```
1. User sees: "Infrastructure: ₱500B"
   → Query: SUM(amount) WHERE dimension_value = 'Infrastructure'
   
2. User clicks, sees: "DPWH: ₱300B"
   → Query: SUM(amount) WHERE Infrastructure AND DPWH
   
3. User clicks, sees: "NCR: ₱80B"
   → Query: SUM(amount) WHERE Infrastructure AND DPWH AND NCR
   
4. User clicks, sees: "Road Widening 2025: ₱30M"
   → Query: SUM(amount) WHERE all above + Road-Widening-2025
   
5. User clicks, sees: "ABC Construction: ₱30M"
   → Shows flow #999
   → Shows 3 evidence links
   → User can click to view contract, photos, audit
```

---

## **5. Dimension System (What Makes It Flexible)**

### **The Problem Dimensions Solve**

**Without dimensions (rigid hierarchy):**
```
Budget
  └─ Department
      └─ Program
          └─ Project
              └─ Contract
```
**Problem:** What if a department doesn't have "programs"? System breaks.

**With dimensions (flexible tagging):**
```
Flow can have ANY combination:
  - [sector, department, project]
  - [region, tax_type, industry]
  - [program, beneficiary, payment_type]
  - [anything the source provides]
```

---

### **Dimension Types by Department**

**BIR (Tax Collection):**
```
Common dimensions:
  - region (NCR, Region IV-A, ...)
  - tax_type (VAT, Income Tax, ...)
  - industry (Retail, Manufacturing, ...)
  - collection_channel (eFPS, Bank, OTC)
```

**DPWH (Infrastructure):**
```
Common dimensions:
  - region (NCR, Region IV-A, ...)
  - project_type (Road, Bridge, Building)
  - project (Road-Widening-2025, ...)
  - contractor (ABC Construction, ...)
```

**DOH (Health):**
```
Common dimensions:
  - program (Vaccination, Hospital Modernization, ...)
  - region (NCR, ...)
  - facility (Hospital, Clinic, ...)
  - beneficiary_type (Children, Elderly, ...)
```

**COA (Audit):**
```
Common dimensions:
  - audit_program (Financial, Performance, ...)
  - case_reference (AUDIT-2025-001, ...)
  - finding_type (Irregularity, Deficiency, ...)
```

---

### **Dimension Levels (Order of Exploration)**

**Concept:** Levels guide users from broad → specific

**Example: DPWH Flow**

```
Level 1: sector = "Infrastructure"
  ↓
Level 2: department = "DPWH"
  ↓
Level 3: region = "NCR"
  ↓
Level 4: project = "Road-Widening-2025"
  ↓
Level 5: contractor = "ABC-Construction"
  ↓
(END - show evidence)
```

**Important:** Levels are **suggestions**, not rules.

User can jump:
- Infrastructure → Region (skip department)
- Infrastructure → Project (skip department AND region)

System adapts.

---

### **Dimension Configuration Table**

**Purpose:** Departments define their dimension structure

**Table: DIMENSION_CONFIGS**

| Field | Meaning | Example |
|-------|---------|---------|
| `source_system` | Which department | "BIR_API" |
| `dimension_type` | Dimension name | "region" |
| `display_label` | User-friendly name | "Geographic Region" |
| `sort_order` | Preferred sequence | 1, 2, 3 |
| `is_geographic` | Maps related? | true/false |

**Example: BIR Configuration**

```
Config #1:
  source_system: "BIR_API"
  dimension_type: "region"
  display_label: "Region"
  sort_order: 1
  is_geographic: true

Config #2:
  source_system: "BIR_API"
  dimension_type: "tax_type"
  display_label: "Tax Type"
  sort_order: 2
  is_geographic: false

Config #3:
  source_system: "BIR_API"
  dimension_type: "industry"
  display_label: "Industry Sector"
  sort_order: 3
  is_geographic: false
```

**What System Does With This:**

```
User viewing BIR data sees:
  1. "Explore by Region" (sort_order: 1)
  2. "Explore by Tax Type" (sort_order: 2)
  3. "Explore by Industry" (sort_order: 3)

If is_geographic = true → show map option
```

---

## **6. Aggregation Strategy (What Makes It Fast)**

### **The Performance Problem**

**Naive approach (slow):**
```sql
-- User wants: "Health spending in NCR"
SELECT SUM(amount)
FROM flows f
JOIN flow_dimensions fd1 ON f.id = fd1.flow_id
JOIN flow_dimensions fd2 ON f.id = fd2.flow_id
WHERE fd1.dimension_value = 'Health'
  AND fd2.dimension_value = 'NCR'
```

**At 1 million flows:** 5-10 seconds ❌  
**Users will leave.**

---

### **Solution: Pre-Aggregate Everything**

**Table: FLOW_AGGREGATES**

| Field | Meaning | Example |
|-------|---------|---------|
| `id` | Unique identifier | 1 |
| `fiscal_year` | Year | 2025 |
| `flow_type` | Collection/spending | "disbursement" |
| `dimension_path` | Filter combination | "sector:Health\|region:NCR" |
| `total_amount` | Pre-computed sum | 8000000000 |
| `flow_count` | Number of flows | 1234 |
| `last_updated` | Freshness indicator | 2025-03-15 02:00:00 |

**Example Records:**

```
Record #1:
  dimension_path: "sector:Health"
  total_amount: 20000000000
  flow_count: 5432
  
Record #2:
  dimension_path: "sector:Health|region:NCR"
  total_amount: 8000000000
  flow_count: 1234
  
Record #3:
  dimension_path: "sector:Health|region:NCR|program:Vaccination"
  total_amount: 2000000000
  flow_count: 456
```

---

### **Fast Query (milliseconds)**

```sql
-- User wants: "Health in NCR"
SELECT total_amount, flow_count
FROM flow_aggregates
WHERE dimension_path = 'sector:Health|region:NCR'
  AND fiscal_year = 2025
```

**Response time:** <50ms ✅

---

### **When Aggregates Update**

**Strategy 1: Nightly Batch (Recommended for MVP)**
```
Every night at 2 AM:
  1. Delete old aggregates
  2. Regenerate from FLOWS table
  3. Takes 10-30 minutes (acceptable off-peak)
```

**Strategy 2: On Data Import**
```
When new flows imported:
  1. Update only affected aggregates
  2. Faster but more complex
```

**Strategy 3: Real-time (Future)**
```
On every flow insert:
  1. Update aggregates immediately
  2. Requires queue system
```

**MVP uses Strategy 1.**

---

### **Aggregate Generation Logic (Pseudo)**

```
FOR each fiscal_year:
  FOR each flow_type:
    
    // Level 0: Total
    AGGREGATE: SUM(amount) WHERE fiscal_year AND flow_type
    STORE: dimension_path = ""
    
    // Level 1: Single dimensions
    FOR each dimension_type:
      FOR each dimension_value:
        AGGREGATE: SUM(amount) WHERE dimension_value
        STORE: dimension_path = "type:value"
    
    // Level 2: Two dimensions
    FOR each combination of 2 dimensions:
      AGGREGATE: SUM(amount) WHERE dim1 AND dim2
      STORE: dimension_path = "type1:value1|type2:value2"
    
    // Level 3+: Three or more (if needed)
    ...
```

**Result:** All possible combinations pre-computed.

---

## **7. Data Lifecycle (Birth to Archive)**

### **Phase 1: Data Arrives**

```
Source → FlowPH
```

**Inputs:**
- API call from department
- Manual CSV upload
- Scheduled data pull
- Email attachment (parsed)

**Where it goes:** Staging area (temporary table)

---

### **Phase 2: Validation**

```
Raw Data → Validation Engine → Accept/Reject
```

**Checks:**
1. Required fields present (amount, date, from, to)
2. Amount is positive number
3. Date is valid and reasonable
4. No duplicate flows (same amount, date, entities)
5. Source system registered

**If validation fails:**
- Rejected flows logged
- Admin notified
- Source can review and resubmit

---

### **Phase 3: Transformation**

```
Valid Raw Data → Adapter → Normalized Flows + Dimensions
```

**Adapter extracts:**
- Core flow (from, to, amount, date)
- Dimensions (region, type, category, etc.)
- Evidence links (if provided)
- Raw original (stored as-is in JSON)

**Output:**
- 1 record in FLOWS
- N records in FLOW_DIMENSIONS (N = number of tags)
- M records in FLOW_EVIDENCE (M = number of documents)

---

### **Phase 4: Storage**

```
Normalized Data → Database Tables
```

**Transaction ensures:**
- Flow saved successfully
- All dimensions saved
- All evidence saved
- Or nothing saved (rollback if error)

**Immediately available for:**
- Search
- Filtering
- Evidence viewing

**Not yet available for:**
- Aggregated charts (needs nightly update)

---

### **Phase 5: Aggregation**

```
New Flows → Nightly Batch → Updated Aggregates
```

**Happens:** 2 AM every night

**Process:**
1. Identify flows added since last run
2. Compute new aggregates
3. Replace old aggregates
4. Mark timestamp

**Next morning:** Users see updated charts instantly

---

### **Phase 6: Archival (Long-term)**

```
Old Flows → Archive Storage → Query on Demand
```

**When:** After 3+ years

**What happens:**
- Moved to archive database
- Still accessible via "Historical Data" option
- Not included in default queries
- Keeps main database fast

**Never deleted** - audit trail permanent

---

### **Complete Lifecycle Diagram**

```
┌──────────────┐
│ Data Source  │ (BIR, DPWH, etc.)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Staging    │ (Temporary holding)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Validation  │ (Check quality)
└──────┬───────┘
       │
       ├─[PASS]─────────────┐
       │                    │
       ▼                    ▼
┌──────────────┐    ┌──────────────┐
│ Adapter      │    │ Rejection Log│
│ (Transform)  │    │ (Review)     │
└──────┬───────┘    └──────────────┘
       │
       ▼
┌──────────────┐
│  Database    │ (FLOWS, DIMENSIONS, EVIDENCE)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Aggregation │ (Nightly at 2 AM)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  User Access │ (Fast queries)
└──────┬───────┘
       │
       ▼ (After 3 years)
┌──────────────┐
│   Archive    │ (Historical access)
└──────────────┘
```

---

# **Part III: Integration Architecture**

## **8. Adapter Layer (Chaos to Order)**

### **Why Adapters Exist**

**Problem:** Every department has different data formats

**BIR sends:**
```csv
CollectionDate,TaxCategory,RegionCode,IndustryType,TotalAmount
2025-01-15,VAT,1300,RTL,1200000
```

**DPWH sends:**
```excel
Project Name: Road Widening - Calamba
Region: IV-A (CALABARZON)
Contract Amount: ₱50,000,000.00
Contractor: ABC Construction Corporation
```

**COA sends:**
```pdf
AUDIT REPORT NO. 2025-031
Subject: Legal Fees - Department of Audit
Amount: Five Million Pesos (PHP 5,000,000.00)
```

**Solution:** One adapter per source format

---

### **Adapter Architecture**

```
┌──────────────────────────────────────────────┐
│            ADAPTER INTERFACE                  │
│  (What every adapter must implement)         │
│                                               │
│  parse(file) → returns:                      │
│    - Array of normalized flows               │
│    - Array of dimensions for each flow       │
│    - Array of evidence links (optional)      │
└──────────────────────────────────────────────┘
                    ▲
                    │
        ┌───────────┼───────────┐
        │           │           │
┌───────┴──────┐ ┌──┴─────────┐ ┌─┴───────────┐
│ BIR Adapter  │ │DPWH Adapter│ │ COA Adapter │
│              │ │            │ │             │
│ Handles:     │ │ Handles:   │ │ Handles:    │
│ - CSV        │ │ - Excel    │ │ - PDF       │
│ - Region code│ │ - Money fmt│ │ - Text scan │
│ - Tax types  │ │ - Projects │ │ - Cases     │
└──────────────┘ └────────────┘ └─────────────┘
```

---

### **Adapter Responsibilities (Each Adapter)**

**Step 1: READ source data**
```
- Open file (CSV, Excel, PDF)
- Parse rows/entries
- Handle encoding issues
- Detect headers
```

**Step 2: VALIDATE basic structure**
```
- Required columns present?
- Data types reasonable?
- No completely empty rows?
```

**Step 3: EXTRACT money flow**
```
- Identify: who paid
- Identify: who received
- Identify: how much
- Identify: when
```

**Step 4: DETERMINE dimensions**
```
- Map source fields → dimension types
- Example: "RegionCode" → dimension "region"
- Example: "TaxCategory" → dimension "tax_type"
```

**Step 5: PRESERVE original**
```
- Store entire row as JSON
- So we never lose information
```

**Step 6: RETURN normalized structure**
```
- Flow object
- Dimensions array
- Evidence array (if any)
```

---

### **Example: BIR Adapter (Detailed)**

**Input CSV:**
```csv
CollectionDate,TaxCategory,RegionCode,IndustryType,TotalAmount,ORNumber
2025-01-15,VAT,1300,RTL,1200000,OR-2025-12345
```

**Adapter Logic (Pseudo):**

```
FUNCTION parse_bir_csv(file):
  
  rows = read_csv(file)
  results = []
  
  FOR EACH row IN rows:
    
    // Extract core flow
    flow = {
      from_entity: "Taxpayer-" + row.IndustryType + "-" + map_region(row.RegionCode),
      to_entity: "BIR-" + map_region(row.RegionCode),
      amount: parse_number(row.TotalAmount),
      flow_type: "collection",
      flow_date: parse_date(row.CollectionDate),
      fiscal_year: extract_year(row.CollectionDate),
      source_system: "BIR_CSV_IMPORT",
      raw_data: json_encode(row)
    }
    
    // Extract dimensions
    dimensions = [
      {
        dimension_type: "region",
        dimension_value: map_region(row.RegionCode),
        level: 1
      },
      {
        dimension_type: "tax_type",
        dimension_value: row.TaxCategory,
        level: 2
      },
      {
        dimension_type: "industry",
        dimension_value: map_industry(row.IndustryType),
        level: 3
      }
    ]
    
    // Extract evidence (if available)
    evidence = [
      {
        evidence_type: "official_receipt",
        external_url: "https://bir.gov.ph/verify/" + row.ORNumber,
        description: "Official Receipt " + row.ORNumber
      }
    ]
    
    results.append({
      flow: flow,
      dimensions: dimensions,
      evidence: evidence
    })
  
  RETURN results


// Helper: Region code → Name
FUNCTION map_region(code):
  IF code == "1300": RETURN "NCR"
  IF code == "0400": RETURN "Region IV-A"
  // etc.


// Helper: Industry code → Name
FUNCTION map_industry(code):
  IF code == "RTL": RETURN "Retail"
  IF code == "MFG": RETURN "Manufacturing"
  // etc.
```

**Output (Normalized):**

```
Flow:
  from_entity: "Taxpayer-Retail-NCR"
  to_entity: "BIR-NCR"
  amount: 1200000
  flow_type: "collection"
  flow_date: 2025-01-15
  raw_data: {"CollectionDate": "2025-01-15", ...}

Dimensions:
  [
    { type: "region", value: "NCR", level: 1 },
    { type: "tax_type", value: "VAT", level: 2 },
    { type: "industry", value: "Retail", level: 3 }
  ]

Evidence:
  [
    { type: "official_receipt", url: "...", description: "..." }
  ]
```

---

### **Adding a New Department (Process)**

**Scenario:** LGU Calamba wants to join FlowPH

**Step 1: Analyze their data**
```
- What format? (Excel)
- What fields? (Date, Program, Amount, Beneficiary)
- What structure? (One row per disbursement)
```

**Step 2: Create adapter**
```
File: app/Adapters/CalambaLGUAdapter.php

Implements: FlowAdapter interface

Maps their fields:
  - "Program" → dimension "program"
  - "Beneficiary" → to_entity
  - "Date" → flow_date
```

**Step 3: Register adapter**
```
Config file:
  'calamba_lgu' => Calam baLGUAdapter::class
```

**Step 4: Test with sample data**
```
- Import 10 test records
- Verify flows created correctly
- Check dimensions appear right
- Confirm charts work
```

**Step 5: Production**
```
- LGU uploads real data
- Adapter processes automatically
- Data appears in FlowPH
```

**Time needed:** 2-4 hours per new department (once system built)

---

## **9. Data Import Pipeline**

### **The Complete Import Flow**

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA IMPORT PIPELINE                          │
└─────────────────────────────────────────────────────────────────┘

Step 1: RECEIVE
├─ API endpoint receives POST with file
├─ Or admin uploads via web interface
└─ Or scheduled job fetches from source

Step 2: STORE TEMPORARILY
├─ Save to /storage/imports/pending/
└─ Generate unique import ID

Step 3: IDENTIFY ADAPTER
├─ Check file extension
├─ Check source parameter
└─ Load appropriate adapter

Step 4: VALIDATE FILE
├─ Is file readable?
├─ Is format correct?
├─ Are required columns present?
└─ Log any issues

Step 5: PARSE AND TRANSFORM
├─ Adapter reads file
├─ Transforms to normalized format
├─ Extracts flows + dimensions
└─ Generates preview (first 10 records)

Step 6: REVIEW (Optional for manual uploads)
├─ Admin sees preview
├─ Can reject if looks wrong
└─ Can approve to continue

Step 7: IMPORT TO DATABASE
├─ Begin transaction
├─ Insert flows
├─ Insert dimensions
├─ Insert evidence
├─ Commit transaction
└─ Mark import as successful

Step 8: POST-PROCESSING
├─ Move file to /storage/imports/completed/
├─ Log import details
├─ Send notification
└─ Queue for aggregation update

Step 9: AGGREGATION
├─ Nightly job picks up
├─ Recalculates affected aggregates
└─ Data now appears in charts
```

---

### **Import Modes**

**Mode 1: API Import (Automated)**
```
Department system → Posts to FlowPH API → Immediate import

Use case: BIR daily collections, real-time updates
Frequency: Hourly or daily
Approval: Automatic (if validation passes)
```

**Mode 2: Manual Upload (Admin)**
```
Admin uploads file → Reviews preview → Approves → Import

Use case: One-time data, historical imports, LGU data
Frequency: As needed
Approval: Manual review
```

**Mode 3: Scheduled Pull (Automated)**
```
FlowPH fetches from source → Imports automatically

Use case: Departments with public APIs/FTP
Frequency: Daily at set time
Approval: Automatic
```

---

### **Error Handling**

**During Parse:**
```
Problem: Unrecognized column name
Action: Skip that column, log warning, continue
Result: Import succeeds, admin notified of skipped data
```

**During Validation:**
```
Problem: Negative amount detected
Action: Reject that specific row
Result: Import other rows, log rejected ones
Admin can review and fix source data
```

**During Database Insert:**
```
Problem: Duplicate flow detected
Action: Rollback transaction
Result: No partial import, preserve data integrity
Admin notified to check for duplicate submission
```

**Complete Failure:**
```
Problem: Adapter crashes
Action: Catch error, preserve file
Result: Import marked as failed
Admin can retry or debug
```

---

## **10. Source Registration System**

### **What "Registering a Source" Means**

Before a department can send data, they must be registered in FlowPH.

**Why:**
- System knows which adapter to use
- System knows which dimensions to expect
- System can attribute data correctly
- System can validate appropriately

---

### **Source Registry Table**

**Table: DATA_SOURCES**

| Field | Meaning | Example |
|-------|---------|---------|
| `id` | Unique ID | 1 |
| `source_code` | Short identifier | "BIR_API" |
| `source_name` | Display name | "Bureau of Internal Revenue" |
| `adapter_class` | Which adapter | "BIRAdapter" |
| `import_mode` | How they send data | "api", "manual", "scheduled" |
| `api_key` | For API imports | "abc123..." |
| `is_active` | Currently working | true/false |
| `last_import_at` | Last successful import | 2025-03-14 |

**Example Records:**

```
Source #1:
  source_code: "BIR_API"
  source_name: "Bureau of Internal Revenue"
  adapter_class: "BIRAdapter"
  import_mode: "api"
  is_active: true

Source #2:
  source_code: "DPWH_MANUAL"
  source_name: "Department of Public Works"
  adapter_class: "DPWHAdapter"
  import_mode: "manual"
  is_active: true

Source #3:
  source_code: "CALAMBA_LGU"
  source_name: "City of Calamba"
  adapter_class: "CaIambaLGUAdapter"
  import_mode: "scheduled"
  is_active: true
```

---

### **Registration Process**

**Step 1: Department Applies**
```
Contact FlowPH team
Provide sample data
Explain their structure
```

**Step 2: FlowPH Analyzes**
```
Review data format
Identify dimensions
Design adapter
Estimate implementation time
```

**Step 3: Adapter Development**
```
Create adapter class
Write mapping logic
Test with sample data
```

**Step 4: Registration**
```
Add to DATA_SOURCES table
Generate API key (if needed)
Configure scheduled pull (if needed)
```

**Step 5: Training and Go-Live**
```
Train department staff
Test live import
Monitor first few imports
Handle any issues
```

---

# **Part IV: User Experience Architecture**

## **11. The User Journey Map**

### **Persona 1: Casual Citizen**

**Goal:** "I just want to know where my taxes go"

**Journey:**

```
Entry → Homepage
  Sees: "Total Budget: ₱100B"
  Sees: Pie chart (Health, Infrastructure, Education, Defense)
  
Action: Clicks "Health" (curiosity)
  Sees: "Health: ₱20B"
  Sees: Regional breakdown pie chart
  
Action: Clicks "NCR" (where they live)
  Sees: "Health in NCR: ₱8B"
  Sees: Program breakdown
  
Action: Satisfied, leaves
  
Time spent: 2 minutes
Learned: Where health spending in their region goes
```

---

### **Persona 2: Journalist**

**Goal:** "I'm investigating hospital modernization spending"

**Journey:**

```
Entry → Homepage
  
Action: Uses search → "hospital modernization"
  Sees: List of all flows mentioning it
  Sees: Total amount across all regions
  
Action: Filters by "NCR" and "2024"
  Sees: ₱4B spent in NCR during 2024
  Sees: Breakdown by hospital
  
Action: Clicks specific hospital → "PGH Modernization"
  Sees: ₱500M allocated
  Sees: List of contracts
  Sees: Evidence links
  
Action: Downloads contract PDF
  Sees: Contractor details
  Cross-references with other sources
  
Action: Exports data to CSV for analysis
  
Time spent: 30 minutes
Outcome: Story lead with evidence
```

---

### **Persona 3: NGO Auditor**

**Goal:** "Track infrastructure spending in Region IV-A"

**Journey:**

```
Entry → Saved Filter ("Infrastructure-Region4A")
  (They've been monitoring this for months)
  
Sees: Dashboard showing:
  - Total spent this year: ₱15B
  - Compared to last year: +12%
  - Top projects by amount
  - Recent disbursements (last 7 days)
  
Action: Reviews new disbursements
  Checks evidence for completeness
  Flags 2 contracts without supporting docs
  
Action: Exports monthly report
  Sends to team
  
Time spent: 15 minutes (regular check-in)
Outcome: Monitoring compliance
```

---

### **Common User Needs (All Personas)**

| Need | How FlowPH Serves It |
|------|---------------------|
| Quick overview | Homepage pie chart, total amounts |
| Drill down | Progressive clicking through dimensions |
| Find specific | Search + filters |
| Verify | Evidence links, source attribution |
| Compare | Side-by-side regions, years, programs |
| Export | CSV download, print-friendly views |
| Track changes | "New this week", comparison to prior period |
| Share | Shareable URLs, embed charts |

---

## **12. State Management (How the App Thinks)**

### **What "State" Means**

**State** = What the app remembers about the user's current session

**Includes:**
- Which filters are active
- What view they're in (chart/list)
- Which fiscal year they're viewing
- What they've clicked on
- Their exploration path

---

### **State Structure**

```javascript
{
  // Core state
  fiscalYear: 2025,
  flowType: "spending",  // or "collection"
  viewMode: "chart",     // or "list", "comparison"
  
  // User's exploration path
  filters: [
    { dimension: "sector", value: "Health" },
    { dimension: "region", value: "NCR" }
  ],
  
  // What they're currently seeing
  currentAggregation: {
    totalAmount: 8000000000,
    flowCount: 1234,
    breakdown: [
      { dimension: "program", value: "Hospital Modernization", amount: 4000000000 },
      { dimension: "program", value: "Vaccination", amount: 2000000000 },
      // ...
    ]
  },
  
  // What they can do next
  availableDimensions: ["program", "department", "facility"],
  
  // History for back button
  previousStates: [
    { filters: [] },  // National view
    { filters: [{ dimension: "sector", value: "Health" }] }  // Sector view
  ]
}
```

---

### **State Transitions (What Happens When User Acts)**

**User Action: Clicks "Health" in pie chart**

```
Before:
  filters: []
  currentView: "National overview"

System processes:
  1. Add filter: { dimension: "sector", value: "Health" }
  2. Save previous state to history
  3. Query aggregates WHERE sector = Health
  4. Find available next dimensions
  5. Render new chart

After:
  filters: [{ dimension: "sector", value: "Health" }]
  currentView: "Health sector breakdown"
  totalAmount: 20000000000
  availableDimensions: ["region", "department", "program"]
```

---

**User Action: Clicks "Back"**

```
Before:
  filters: [{ dimension: "sector", value: "Health" }]
  previousStates: [{ filters: [] }]

System processes:
  1. Pop last state from history
  2. Restore that state
  3. Requery data
  4. Re-render

After:
  filters: []
  currentView: "National overview"
  (Back to where they started)
```

---

**User Action: Changes fiscal year to 2024**

```
Before:
  fiscalYear: 2025
  filters: [{ dimension: "sector", value: "Health" }]

System processes:
  1. Update fiscalYear to 2024
  2. Keep same filters
  3. Requery aggregates for 2024
  4. Re-render with 2024 data

After:
  fiscalYear: 2024
  filters: [{ dimension: "sector", value: "Health" }]
  (Same view, different year)
  
Note: Can now compare 2024 vs 2025 side-by-side
```

---

### **State Persistence**

**URL-Based State (Shareable)**
```
https://flowph.gov.ph/explore?year=2025&sector=Health&region=NCR

Benefits:
  - Users can bookmark
  - Can share with others
  - Back button works naturally
```

**Session Storage (Temporary)**
```
Stores:
  - Search history
  - Recent views
  - Preferences (chart type)

Clears when browser closed
```

**User Preferences (Permanent, if logged in)**
```
Stores:
  - Saved filters
  - Favorite dimensions
  - Default view mode
  - Notification settings

Persists across sessions
```

---

## **13. Visualization Engine**

### **Chart Types and When to Use**

**Pie Chart**
```
Best for: Showing part-to-whole at current level
Use when: User has filtered to a category and wants to see breakdown
Example: "Health spending by region"

Limitations: Max 8-10 slices (combine small ones into "Other")
```

**Bar Chart (Horizontal)**
```
Best for: Comparing many categories
Use when: More than 10 items, or long labels
Example: "Top 20 projects by spending"

Benefit: Easy to read labels, good for rankings
```

**Line Chart**
```
Best for: Showing trends over time
Use when: Comparing multiple fiscal years or periods
Example: "Health spending 2020-2025"

Benefit: Shows growth/decline clearly
```

**Treemap**
```
Best for: Hierarchical data with size
Use when: Want to show multiple levels at once
Example: "All departments, programs, and projects sized by budget"

Benefit: Dense information, impressive visualization
```

**List/Table**
```
Best for: Detailed data, final endpoints
Use when: At deepest level, showing actual flows
Example: "Individual payments to contractors"

Benefit: Precise numbers, sortable, exportable
```

---

### **Visualization Rules**

**Rule 1: Default to Simplest**
```
Start with: Pie chart (most intuitive)
Offer: Switch to bar chart, list view
Let user: Choose what they prefer
```

**Rule 2: Progressive Detail**
```
Level 1: Just amounts and labels
Level 2: Add percentages
Level 3: Add trend indicators (↑ vs last year)
Level 4: Add evidence counts
```

**Rule 3: Color Coding**
```
Collection flows: Green tones
Spending flows: Blue tones
Warnings/issues: Yellow/red
No political party colors
```

**Rule 4: Responsive**
```
Desktop: Full pie chart with legend
Tablet: Compact chart, collapsible legend
Mobile: Simplified chart or list view
```

---

### **Chart Interaction Patterns**

**On Hover:**
```
Show tooltip:
  - Label: "Health"
  - Amount: "₱20,000,000,000"
  - Percentage: "20% of total"
  - Flow count: "5,432 transactions"
```

**On Click:**
```
If not at deepest level:
  → Drill down, apply filter, show next level
  
If at deepest level:
  → Show flow list and evidence
```

**On Right-Click (or long press mobile):**
```
Context menu:
  - "View details"
  - "Compare with another region"
  - "Export this data"
  - "Share this view"
```

---

## **14. Evidence and Verification Layer**

### **Types of Evidence**

**Document Evidence**
```
Type: PDF, Word, Excel files
Examples: Contracts, budgets, invoices, receipts
Storage: External URL (department server, cloud)
Display: Link with icon, opens in new tab
```

**Visual Evidence**
```
Type: Photos, videos
Examples: Project site photos, before/after, progress
Storage: External URL or CDN
Display: Thumbnail gallery, lightbox on click
```

**Audit Evidence**
```
Type: Audit reports, inspection reports
Examples: COA findings, third-party audits
Storage: External URL
Display: Special icon, flagged importance
```

**Blockchain Evidence (Future)**
```
Type: Transaction hash
Purpose: Proof of immutability
Display: Hash + link to explorer
```

---

### **Evidence Display UI**

**At Flow Level:**
```
┌──────────────────────────────────────────────────┐
│ Payment to ABC Construction Corp - ₱30,000,000  │
│                                                   │
│ Evidence (3 documents):                          │
│                                                   │
│ 📄 Contract Agreement                            │
│    https://dpwh.gov.ph/contracts/CON-2025-123    │
│    Uploaded: 2025-02-01                          │
│    [View] [Download]                             │
│                                                   │
│ 📷 Project Site Photo - Before                   │
│    [thumbnail]                                    │
│    [View Full Size]                              │
│                                                   │
│ ✅ COA Audit Report                              │
│    Status: No findings                           │
│    [View Report]                                 │
└──────────────────────────────────────────────────┘
```

---

### **Verification Indicators**

**Full Verification:**
```
✅ All evidence provided
✅ Audit completed, no issues
✅ Hash verified (if blockchain enabled)

Display: Green checkmark, "Fully Verified"
```

**Partial Verification:**
```
⚠️ Some evidence missing
✅ Audit completed, minor findings

Display: Yellow warning, "Partially Verified - 2 documents pending"
```

**Unverified:**
```
❌ No evidence provided
❌ Audit pending or not applicable

Display: Gray icon, "Unverified - Evidence pending"
```

**Flagged:**
```
🚩 Audit found issues
🚩 Evidence conflicts with reports

Display: Red flag, "Review Required - See audit findings"
```

---

### **Evidence Upload Process (For Departments)**

```
Step 1: Department logs into portal
Step 2: Navigates to specific flow/project
Step 3: Clicks "Upload Evidence"
Step 4: Selects evidence type
Step 5: Uploads file or provides URL
Step 6: Adds description
Step 7: Submits

System processes:
  - Validates file (size, type)
  - Creates evidence record
  - Links to flow(s)
  - Notifies admin
  - Updates verification status
```

---

# **Part V: System Intelligence**

## **15. Smart Defaults and Personalization**

### **Smart Defaults (No Login Required)**

**Default Fiscal Year:**
```
Show: Current fiscal year
If past Q4: Show next year (upcoming budget)
User can change: Yes, dropdown selector
```

**Default View:**
```
First-time visitor: National overview pie chart
Returning visitor: Resume where they left off (session storage)
```

**Default Sort:**
```
Charts: Largest slice first (clockwise)
Lists: Highest amount first
Tables: Most recent date first
```

**Default Region (if geolocation enabled):**
```
User in NCR: Suggest "View NCR spending"
User in Laguna: Suggest "View Region IV-A spending"
Note: Never force, just suggest
```

---

### **Personalization (If User Has Account)**

**Saved Filters:**
```
User can save:
  - "My region's health spending"
  - "Infrastructure in CALABARZON"
  - "Education budget tracking"

Benefits:
  - One-click access
  - Email alerts when updated
  - Share with team
```

**Dashboard:**
```
User creates custom dashboard:
  - Top 3 filters as widgets
  - Recent changes in tracked areas
  - Evidence status updates
```

**Notifications:**
```
User chooses:
  - Email me when new flows in [filter]
  - Alert me if amount changes >10%
  - Notify when evidence uploaded
```

---

## **16. Search and Discovery**

### **Search Types**

**Quick Search (Global)**
```
User types: "vaccination"

System searches:
  - Dimension values (program names, project names)
  - Flow descriptions (from raw_data)
  - Evidence titles

Returns:
  - All flows mentioning "vaccination"
  - Grouped by department
  - Total amount across all
```

**Advanced Search**
```
Filters:
  - Amount range: ₱1M - ₱10M
  - Date range: Jan 2025 - Mar 2025
  - Flow type: Disbursements only
  - Region: NCR
  - Has evidence: Yes

Returns:
  - Matching flows
  - Can export results
```

**Natural Language Search (Future)**
```
User asks: "How much did we spend on roads in Laguna last year?"

System interprets:
  - "roads" → dimension project_type = "Road"
  - "Laguna" → dimension region = "Region IV-A", province = "Laguna"
  - "last year" → fiscal_year = 2024
  - "how much" → SUM(amount)

Returns:
  - Total amount
  - Breakdown by project
  - Trend vs previous year
```

---

### **Discovery Features**

**"Explore Similar"**
```
User viewing: "Hospital Modernization in NCR - ₱4B"

System suggests:
  - "Hospital Modernization in other regions"
  - "Other health programs in NCR"
  - "NCR spending in other sectors"
```

**"Compare"**
```
User can compare:
  - This year vs last year
  - NCR vs Region IV-A
  - Program A vs Program B

Shown as:
  - Side-by-side charts
  - Difference percentages
  - Trend arrows
```

**"What Changed"**
```
Homepage widget shows:
  - "New this week: 234 flows, ₱5.2B"
  - "Largest new payment: ₱500M to..."
  - "Evidence added: 45 documents"
```

---

## **17. Anomaly Detection (Future)**

### **What to Detect**

**Unusual Amounts:**
```
Flag if:
  - Payment 5x higher than average for this project type
  - Payment in round numbers (₱5M, ₱10M - might be estimate)
  - Payment to same entity multiple times in one day
```

**Missing Evidence:**
```
Flag if:
  - Flow >₱1M has no evidence after 30 days
  - Contract mentioned but no contract document
  - Audit required but no audit report
```

**Pattern Breaks:**
```
Flag if:
  - Region's spending suddenly increases 50%
  - New contractor appears with large contract
  - Spending drops to zero unexpectedly
```

### **How to Handle Flags**

```
System does NOT accuse anyone of wrongdoing

Instead:
  - Marks flow with ⚠️ icon
  - Shows reason: "Payment significantly higher than similar projects"
  - Allows department to explain
  - Allows admin to dismiss if explained

Purpose: Aid oversight, not replace it
```

---

# **Part VI: Technical Infrastructure**

## **18. API Architecture**

### **API Endpoints Overview**

```
PUBLIC (No Auth Required):
  GET  /api/v1/flows/aggregate         - Get aggregated data
  GET  /api/v1/flows/search            - Search flows
  GET  /api/v1/dimensions/available    - Get explorable dimensions
  GET  /api/v1/evidence/{flowId}       - Get evidence for flow

DEPARTMENT (API Key Required):
  POST /api/v1/flows/import            - Submit flows
  GET  /api/v1/flows/status/{importId} - Check import status

ADMIN (Token Required):
  POST /api/v1/sources/register        - Register new source
  POST /api/v1/aggregates/rebuild      - Trigger aggregation
  GET  /api/v1/imports/history         - View import log
```

---

### **Key Endpoint Examples**

**GET /api/v1/flows/aggregate**
```json
Request:
{
  "fiscal_year": 2025,
  "flow_type": "spending",
  "filters": [
    { "dimension": "sector", "value": "Health" },
    { "dimension": "region", "value": "NCR" }
  ],
  "group_by": "program"
}

Response:
{
  "total_amount": 8000000000,
  "flow_count": 1234,
  "breakdown": [
    {
      "dimension": "program",
      "value": "Hospital Modernization",
      "amount": 4000000000,
      "percentage": 50,
      "flow_count": 456
    },
    {
      "dimension": "program",
      "value": "Vaccination",
      "amount": 2000000000,
      "percentage": 25,
      "flow_count": 234
    }
  ],
  "available_next_dimensions": ["facility", "supplier"]
}
```

---

**POST /api/v1/flows/import** (Department submits data)
```json
Request:
Headers: X-API-Key: [department's key]

Body:
{
  "source": "BIR_API",
  "flows": [
    {
      "from": "Taxpayer-Retail-NCR",
      "to": "BIR-NCR",
      "amount": 1200000,
      "date": "2025-01-15",
      "flow_type": "collection",
      "dimensions": [
        { "type": "region", "value": "NCR" },
        { "type": "tax_type", "value": "VAT" }
      ],
      "evidence": [
        {
          "type": "official_receipt",
          "url": "https://bir.gov.ph/verify/OR-12345"
        }
      ]
    }
  ]
}

Response:
{
  "import_id": "IMP-2025-001234",
  "status": "processing",
  "flows_received": 1,
  "estimated_completion": "2025-03-15T10:05:00Z"
}
```

---

### **Rate Limiting**

```
Public endpoints:
  - 1000 requests/hour per IP
  - Enough for normal browsing

Department API:
  - 10,000 requests/hour per API key
  - Allows bulk imports

Search API:
  - 100 requests/minute per IP
  - Prevents scraping abuse
```

---

### **API Versioning**

```
Current: /api/v1/...

Future: /api/v2/...

Strategy:
  - v1 supported for 2 years after v2 launch
  - Deprecation warnings in response headers
  - Migration guide provided
```

---

## **19. Performance Strategy**

### **Performance Targets**

```
Homepage load: <2 seconds
Chart render: <500ms
Search results: <1 second
Aggregation query: <100ms
Import processing: <5 minutes per 10K flows
```

---

### **Optimization Techniques**

**Database Level:**
```
1. Indexes on:
   - flows.fiscal_year
   - flows.flow_type
   - flow_dimensions.dimension_value
   - flow_dimensions.flow_id

2. Partitioning:
   - Partition flows table by fiscal_year
   - Older years can be archived

3. Aggregates:
   - Pre-compute all common combinations
   - Update nightly, not on every query
```

**Application Level:**
```
1. Caching:
   - Cache aggregates for 1 hour
   - Cache dimension configs (rarely change)
   - Cache search results for 5 minutes

2. Lazy Loading:
   - Load evidence only when user clicks
   - Load next dimension options on demand

3. Pagination:
   - Flow lists show 50 at a time
   - Infinite scroll for mobile
```

**Frontend Level:**
```
1. Code Splitting:
   - Load chart libraries only when needed
   - Split by route (explore vs search vs admin)

2. Asset Optimization:
   - Compress images
   - Minify JS/CSS
   - Use CDN for static assets

3. Progressive Loading:
   - Show skeleton while loading
   - Load critical content first
   - Lazy load images
```

---

### **Scaling Strategy**

**Vertical Scaling (First):**
```
Current: 4 CPU, 8GB RAM
When needed: 8 CPU, 16GB RAM
Handles: ~10M flows, ~1000 concurrent users
```

**Horizontal Scaling (Later):**
```
Add: Read replicas for database
Add: Load balancer for web servers
Add: Separate aggregation server
Handles: 100M+ flows, 10K+ concurrent users
```

---

## **20. Security Model**

### **Data Security**

**At Rest:**
```
- Database encrypted (AES-256)
- Backups encrypted
- API keys hashed
```

**In Transit:**
```
- HTTPS only (TLS 1.3)
- API calls over HTTPS
- No plain HTTP allowed
```

**Access Control:**
```
Public: Can view, search, export
Departments: Can import their own data only
Admins: Can manage sources, view logs, rebuild aggregates
```

---

### **Input Validation**

```
All inputs validated:
  - Amount must be positive number
  - Date must be valid, not future
  - Dimensions must match registered types
  - File uploads: size limit, type whitelist

SQL Injection: Prevented by ORM (Laravel Eloquent)
XSS: Escaped output, CSP headers
CSRF: Token required for state-changing operations
```

---

### **Privacy Considerations**

```
NO personal data collected:
  - No taxpayer names
  - No personal IDs
  - No addresses beyond city/province level

Aggregation prevents identification:
  - Minimum group size: 10 flows
  - Suppress if <10 (show "Less than 10")

Evidence reviewed:
  - Admin checks for accidental PII before publishing
  - Can redact if needed
```

---

## **21. Deployment Architecture**

### **Deployment Stack**

```
┌───────────────────────────────────────────┐
│           USERS (Citizens)                │
└──────────────┬────────────────────────────┘
               │ HTTPS
               ▼
┌───────────────────────────────────────────┐
│      CDN (Static Assets)                  │
│      - Images, JS, CSS                    │
└──────────────┬────────────────────────────┘
               │
               ▼
┌───────────────────────────────────────────┐
│      Load Balancer                        │
└──────────────┬────────────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│ Web Server 1│ │ Web Server 2│
│ (Laravel)   │ │ (Laravel)   │
└──────┬──────┘ └──────┬──────┘
       │               │
       └───────┬───────┘
               ▼
┌───────────────────────────────────────────┐
│      Database (PostgreSQL)                │
│      - Primary (writes)                   │
│      - Replica (reads)                    │
└──────────────┬────────────────────────────┘
               │
               ▼
┌───────────────────────────────────────────┐
│      File Storage (S3-compatible)         │
│      - Import files                       │
│      - Export files                       │
└───────────────────────────────────────────┘
```

---

### **MVP Deployment (Simpler)**

```
Single Server:
  - Web server (Nginx)
  - Application (Laravel)
  - Database (PostgreSQL)
  - Queue worker (for imports)

Cost: ~$50-100/month (DigitalOcean, Linode)
Capacity: 1M flows, 100 concurrent users
```

---

### **Backup Strategy**

```
Database:
  - Daily full backup (retained 30 days)
  - Hourly incremental backup (retained 7 days)
  - Weekly archive backup (retained 1 year)

Code:
  - Git repository (GitHub/GitLab)
  - Tagged releases

Files:
  - Replicated to secondary region
  - Versioning enabled
```

---

# **Part VII: Scaling and Evolution**

## **22. MVP to Full System Roadmap**

### **Phase 1: MVP (Months 1-3)**

**Scope:**
```
✅ 3-table data model implemented
✅ 1-2 fake data sources (BIR, DPWH simulated)
✅ Basic pie chart + drill-down
✅ Flow list view
✅ Evidence links display
✅ Manual CSV upload
✅ Aggregation (nightly batch)
✅ Search (basic keyword)

❌ No real department integrations yet
❌ No user accounts
❌ No blockchain
❌ No advanced anomaly detection
```

**Deliverable:** Working demo with realistic fake data

---

### **Phase 2: Pilot (Months 4-6)**

**Scope:**
```
✅ One real department integration (suggest: LGU)
✅ Department portal for uploads
✅ API endpoint for automated imports
✅ Evidence upload feature
✅ Comparison view (year-over-year)
✅ Export to CSV
✅ Mobile-responsive UI
✅ Performance optimization

Stretch goals:
✅ 2-3 additional LGU partners
✅ User accounts (for saved filters)
```

**Deliverable:** Live system with real data from pilot partner

---

### **Phase 3: Scale (Months 7-12)**

**Scope:**
```
✅ 5-10 department/LGU integrations
✅ Advanced search
✅ Saved filters and dashboards
✅ Email notifications
✅ Audit trail / change log
✅ Admin panel improvements
✅ API documentation
✅ Developer portal (for departments)

Stretch goals:
✅ Anomaly detection (basic)
✅ Blockchain verification (pilot)
```

**Deliverable:** Production-ready platform with multiple active departments

---

### **Phase 4: National (Year 2+)**

**Scope:**
```
✅ National government adoption
✅ All major departments onboarded
✅ Advanced analytics and insights
✅ Public API for researchers
✅ Mobile app
✅ Multi-language support
✅ Blockchain fully integrated
✅ AI-powered anomaly detection
✅ Predictive insights
```

**Deliverable:** Nationwide transparency platform

---

##  **23. Multi-Department Scaling**

### **When You Have 10+ Departments**

**Challenge 1: Adapter Proliferation**
```
Problem: 50 departments = 50 adapters?

Solution: Standardized templates
  - "CSV Standard Template" (most use this)
  - "Excel Standard Template"
  - Custom adapter only if truly unique

Result: 80% use templates, 20% custom
```

**Challenge 2: Dimension Explosion**
```
Problem: 500+ unique dimension types across all departments

Solution: Dimension mapping layer
  - "project" vs "programa" vs "project_name" → all map to "project"
  - System knows they're equivalent
  - User sees consistent language

Result: ~50 standardized dimensions, infinite variations handled
```

**Challenge 3: Data Quality Variance**
```
Problem: Some departments pristine, others messy

Solution: Quality scoring
  - Each department gets data quality score (0-100)
  - Based on: completeness, timeliness, evidence provision
  - Displayed alongside their data
  - Monthly quality report sent

Result: Departments improve to avoid low scores
```

---

### **Governance Model**

**Steering Committee:**
```
Members:
  - DBM (Budget lead)
  - COA (Audit lead)
  - DTI (Tech support)
  - Civil society reps (2-3)
  - FlowPH technical team

Meets: Quarterly

Decides:
  - New department priorities
  - Standard updates
  - Policy issues
```

**Technical Working Group:**
```
Members:
  - Technical reps from each department
  - FlowPH dev team

Meets: Monthly

Decides:
  - API specifications
  - Data format standards
  - Integration schedules
```

---

## **24. Future Extensions**

### **Natural Language Interface**

```
User asks: "How much did we spend on education in Laguna last year?"

System:
  1. Parses intent (spending, education sector, Laguna, 2024)
  2. Translates to filters
  3. Queries aggregates
  4. Generates answer: "₱500M was spent on education in Laguna during 2024"
  5. Offers: "Would you like to see the breakdown by program?"
```

---

### **Predictive Analytics**

```
Use case: Budget planning

System analyzes:
  - Historical spending patterns
  - Seasonal trends
  - Regional growth rates

Predicts:
  - "Based on trends, Health sector will need ₱25B in 2026 (up from ₱20B)"
  - "NCR infrastructure backlog requires ₱15B investment"

Helps: DBM in budget allocation decisions
```

---

### **Citizen Participation Features**

```
Feature: Community Feedback

Citizens can:
  - Flag questionable flows
  - Submit evidence they find
  - Suggest audit priorities
  - Vote on transparency priorities

COA/departments:
  - Review flagged items
  - Respond to concerns
  - Update evidence based on citizen submissions
```

---

### **Integration with Other Systems**

```
Connect to:
  - PhilGEPS (procurement data)
  - LandBank/DBP (disbursement verification)
  - SEC (contractor verification)
  - DTI (business registration checks)

Benefits:
  - Auto-verify contractor legitimacy
  - Cross-reference procurement vs payments
  - Detect discrepancies automatically
```

---

### **Open Data Ecosystem**

```
Provide:
  - Public API (free, rate-limited)
  - Bulk data downloads (monthly)
  - Data dictionary and documentation
  - Sample code and tutorials

Enable:
  - Researchers to analyze trends
  - Media to create visualizations
  - NGOs to build monitoring tools
  - Startups to create value-added services

Result: Thriving transparency ecosystem
```

---

# **FINAL SUMMARY**

## **What You've Built (Conceptually)**

A **flow-first, dimension-agnostic, exploration-driven** public transparency platform that:

1. **Accepts** chaotic, varied government data
2. **Transforms** it into standardized money flows
3. **Tags** flows with flexible dimensions
4. **Aggregates** for instant performance
5. **Visualizes** through progressive disclosure
6. **Verifies** with evidence links
7. **Scales** to any number of departments without schema changes

---

## **Why This Architecture Wins**

✅ **Flexible:** No rigid hierarchy, adapts to any department  
✅ **Fast:** Pre-aggregated queries, <100ms response  
✅ **Intuitive:** Users explore by asking questions, not navigating trees  
✅ **Scalable:** 3-table core never changes, handles millions of flows  
✅ **Verifiable:** Evidence-first design builds trust  
✅ **Realistic:** Doesn't require perfect data or full control  
✅ **Future-proof:** Easy to add departments, dimensions, features  

---

## **You're Ready When You Can Explain:**

✅ Why flows have "from" and "to" (and what happens at endpoints)  
✅ How dimensions make rigid hierarchies unnecessary  
✅ Why aggregates solve the performance problem  
✅ How adapters handle data chaos  
✅ How users explore without getting lost  
✅ Why this scales better than traditional approaches  

---

**Next Step: Pick one thing to implement first.**

What do you want to build:
1. **The 3 tables + sample data** (prove the data model)
2. **One adapter** (prove we can import varied data)
3. **Basic visualization** (prove the exploration UI)
4. **The state machine** (prove the user journey)

Tell me which, and I'll give you the exact implementation plan for that piece.
