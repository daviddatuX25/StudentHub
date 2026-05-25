# CollabAcad: An Institutional Forum and Real-Time Event Management System with Segmented Weighted Voting and Anonymous Feedback Channels — Canonical Knowledge Base & Title Defense Guide
*Capstone Title 2 · Real-Time Web Systems, Collaborative Platforms, and Participatory Data Analytics*

---

## 0. Project Identity

| Field | Detail |
|---|---|
| **Working Title** | CollabAcad: An Institutional Forum and Real-Time Event Management System with Segmented Weighted Voting and Anonymous Feedback Channels |
| **Domain** | Real-Time Web Systems · Participatory Democracy Platforms · Institutional Communication Infrastructure |
| **Core Thesis** | Legacy messaging platforms (e.g., Facebook Messenger Group Chats) fail institutional communication by conflating personal and professional boundaries, silencing minority department voices through raw-count voting, and offering no safe anonymous discourse channels. CollabAcad resolves all three using WebSocket-driven real-time architecture, a normalized weighted voting algorithm, and a managed anonymity layer with keyword-based toxicity interception. |
| **Target Users** | Students, Faculty, Department Administrators, Student Government Officers — across all colleges/departments of the institution |
| **Deployment Model** | Hybrid: Institution-hosted Node.js/Express server (on-premise or private VPS) + PostgreSQL relational store + Redis pub/sub for real-time event fanout + React/Next.js frontend |

**Hook Sentence:**
> "While students drown in Messenger notifications and student councils vote in raw headcounts that silence CTE against CAS, CollabAcad delivers a purpose-built institutional commons — where every voice is mathematically equalized, every event is broadcast in real-time, and every honest concern can be raised without fear."

**Novelty Statement:**
Unlike generic platforms such as Google Classroom (LMS-only, no horizontal peer discourse) or Facebook Groups (no equity controls, no segmentation, personal-boundary violations), CollabAcad introduces three novel engineering contributions:
1. A **department-normalized weighted voting formula** that corrects for population asymmetry across academic units.
2. A **Socket.IO event broadcast system** with a role-aware subscription model (admin push → student pull) that eliminates the polling overhead of traditional announcement systems.
3. A **managed anonymous posting layer** with configurable forum-level anonymity toggles and a pre-publication keyword filter pipeline — enforcing safe discourse without surrendering moderation accountability.

---

## 1. The Core Defense Pitch (Slide Script)

*[2–3 minute oral delivery — speak confidently, maintain eye contact with each panel member]*

---

"Good morning, panel. My name is [Name], and I am presenting **CollabAcad** — a real-time institutional forum and event management platform designed specifically to replace the fragmented, inequitable, and boundary-violating communication infrastructure currently held together by informal Facebook Messenger group chats.

**The Problem Layer.** Three pain points define our institution's communication failure. First, announcements are buried in personal Messenger GCs — teachers are forced to use private phones for official school business. Second, student government votes count raw numbers — a 1,200-student college will always outvote a 300-student college, even on issues that affect them equally. Third, students have no safe channel to raise genuine concerns — fear of judgment silences legitimate academic discourse.

**The Solution Layer.** CollabAcad addresses each failure point with a distinct engineered system:

- Layer 1 — **Live Event Broadcast Engine**: Built on Socket.IO over WebSockets, administrators push real-time announcements, pinned FAQs, and live ticker alerts to all subscribed clients within under 200 milliseconds, with no page refresh required.

- Layer 2 — **Segmented Weighted Voting System**: Our voting module applies a department-normalized weight formula: $W = \frac{V}{P} \times 100$, where $V$ is departmental yes-votes and $P$ is departmental population. This produces a percentage-based equity score per unit, aggregated into a final institutional result — ensuring CTE's 300 students carry proportional voice against CAS's 1,200.

- Layer 3 — **Managed Anonymous Feedback Channels**: Forum administrators may toggle anonymous mode per thread. Before publication, all anonymous posts pass through a server-side keyword filter array. Flagged posts are held for admin review. Admins retain a de-anonymization table in a separate, access-controlled database schema, visible only to system administrators under justifiable circumstances.

**Hardware and Infrastructure Constraints.** The system runs entirely on institution-controlled infrastructure — no student data leaves to third-party consumer platforms. WebSocket connections are maintained via a Redis pub/sub fanout layer, decoupling the Socket.IO emission from the HTTP application server to support horizontal scaling.

**Cache Coherence Model.** Real-time vote tallies are cached in Redis with a write-through policy — every vote write simultaneously updates PostgreSQL (durable store) and Redis (hot cache). The frontend polls the Redis snapshot via a server-sent event stream, ensuring no client displays a stale vote count beyond a 500ms window.

This is not a basic CRUD application. CollabAcad is a distributed, real-time, equity-aware institutional communication system. Thank you."

---

## 2. System Architecture Deep-Dive

### 2.1 Streaming Pipeline & Real-Time Event Broadcast Engineering

**WebSocket Connection Lifecycle:**

```
Client Browser
  └─► HTTP Upgrade Request (ws://)
        └─► Socket.IO Handshake (Polling → WebSocket upgrade)
              └─► Namespace Assignment: /events | /forums | /voting
                    └─► Room Subscription by Role (admin | faculty | student | org-officer)
                          └─► Redis Pub/Sub Channel Fanout
                                └─► Emission to all subscribed sockets in room
```

**End-to-End Latency Budget (Target: <300ms for announcements):**

| Stage | Component | Budget |
|---|---|---|
| Client Event Trigger | Admin clicks "Broadcast" | ~5ms |
| HTTP → WS Upgrade (first connection) | Socket.IO handshake | ~50ms |
| Server-Side Processing | Express middleware + validation | ~10ms |
| Redis Pub/Sub Fanout | Channel publish → subscriber receive | ~5ms |
| Socket.IO Emission to Room | Node.js event loop dispatch | ~10ms |
| Client-Side Re-render | React state update → DOM diff | ~20ms |
| **Total** | | **~100ms (well within budget)** |

**Frame packetization for live ticker:**
- Ticker events are packaged as JSON payloads: `{ type: "TICKER", payload: { message, priority, timestamp, authorRole } }`
- Priority field (`HIGH | NORMAL | LOW`) governs client-side rendering: HIGH events interrupt current view with a modal overlay; NORMAL events append to ticker banner; LOW events queue to notification bell.

### 2.2 Hardware-Inspired Memory Hierarchy (Caching Architecture)

| Tier | Name | Technology | Contents | Eviction Policy |
|---|---|---|---|---|
| **L1** | Hot Session Cache | Redis (in-memory) | Active vote tallies, live ticker queue, online user presence map | LRU + TTL (30-second expiry for vote snapshots) |
| **L2** | Working Application Cache | Redis (persistent RDB snapshot) | Forum thread metadata, event schedules, user session tokens | Write-through; evicted on session expiry |
| **L3** | Long-Term Durable Store | PostgreSQL | All posts, votes, user records, audit logs, anonymization table | Append-only for audit; soft-delete for posts |

**Information Salience Metric for Pinned Post Prioritization ($V_{gold}$):**

For ranking pinned forum posts in the event board, we define a salience score:

$$V_{gold} = \frac{\sum_{k=1}^{K} \alpha_k \cdot r_k}{\sum_{k=1}^{K} \alpha_k}$$

Where:
- $K$ = number of engagement signals (views, replies, reactions, saves)
- $r_k$ = raw engagement count for signal $k$
- $\alpha_k$ = signal weight ($\alpha_{reply} = 0.4,\ \alpha_{view} = 0.1,\ \alpha_{reaction} = 0.3,\ \alpha_{save} = 0.2$)

Posts with $V_{gold}$ below a rolling 48-hour median threshold are demoted from the pinned board. This governs the L1 Redis sorted set that drives the live event feed.

### 2.3 Asynchronous Multi-Service Orchestration

Four decoupled backend services operate in parallel, communicating via Redis Pub/Sub channels:

| Service | Responsibility | Redis Channel | Stack |
|---|---|---|---|
| **Event Broadcast Service** | Ingests admin announcements, publishes to role-segmented rooms | `channel:broadcast:{role}` | Node.js + Socket.IO |
| **Vote Aggregation Service** | Receives individual votes, applies weight formula, emits live tally updates | `channel:vote:tally` | Node.js + Bull queue |
| **Anonymity Moderation Service** | Pre-screens anonymous posts via keyword filter, routes to admin review queue if flagged | `channel:anon:review` | Node.js + `bad-words` / custom regex |
| **Notification Delivery Service** | Fans out bell notifications to individual user sockets | `channel:notify:{userId}` | Node.js + Socket.IO |

**Redis Schema (Key Patterns):**

```
vote:poll:{pollId}:dept:{deptCode}:raw       → Integer (raw vote count)
vote:poll:{pollId}:dept:{deptCode}:weighted  → Float (W = V/P * 100)
vote:poll:{pollId}:result                    → Sorted Set (deptCode → W score)
event:ticker:queue                           → Redis List (LPUSH on broadcast, RPOP on display)
session:{userId}                             → Hash (socketId, role, deptCode, lastSeen)
anon:review:queue                            → Redis List (pending moderation)
```

### 2.4 Semantic Cache Coherence Protocol (Software-Defined MESI for Vote State)

To prevent race conditions where two students in the same department submit a vote simultaneously and corrupt the tally, we apply a software-defined MESI coherence model on the vote cache entry:

| State | Symbol | Meaning | Trigger |
|---|---|---|---|
| **Modified** | M | Vote tally updated in Redis; PostgreSQL write pending | User casts vote; Redis incremented, DB write queued |
| **Exclusive** | E | Single active write lock on dept vote block; no other service writing | Bull job acquires lock before processing batch |
| **Shared** | S | Multiple readers (dashboards, frontend clients) consuming tally snapshot | Read-only clients connected to SSE stream |
| **Invalid** | I | Cached tally expired (TTL hit) or poll closed; must re-fetch from PostgreSQL | Poll deadline passes or admin closes vote |

Implementation: Redis `SET vote:lock:{pollId}:{deptCode} 1 EX 5 NX` (atomic lock, 5-second expiry) enforces the Exclusive state before any write. Failure to acquire lock routes the vote to the Bull retry queue.

### 2.5 Weighted Voting Formula — Formal Derivation

**Base Departmental Weight:**

$$W_d = \frac{V_d}{P_d} \times 100$$

Where $W_d$ is the weighted participation score (0–100) for department $d$, $V_d$ is the count of "Yes" votes from department $d$, and $P_d$ is the total registered population of department $d$.

**Institutional Aggregate Score:**

$$W_{inst} = \frac{1}{|D|} \sum_{d \in D} W_d$$

Where $D$ is the set of all participating departments. This arithmetic mean of departmental scores gives each department equal institutional weight regardless of population.

**Example:**

| Department | Population ($P_d$) | Yes Votes ($V_d$) | $W_d$ |
|---|---|---|---|
| CAS | 1,200 | 800 | 66.67 |
| CTE | 300 | 240 | 80.00 |
| CBM | 450 | 200 | 44.44 |
| CCS | 350 | 280 | 80.00 |

$$W_{inst} = \frac{66.67 + 80.00 + 44.44 + 80.00}{4} = 67.78$$

Without weighting, CAS's 800 votes dominate. With weighting, CTE's 80% participation score carries equal institutional weight to CAS's 66.67%.

**Multi-Objective Constraint:** The system enforces a minimum quorum threshold $Q$:

$$Q_d = \frac{V_d}{P_d} \geq 0.30 \quad \forall d \in D_{required}$$

Departments below 30% participation are flagged as "low quorum" and their $W_d$ is displayed with a warning indicator on the dashboard.

---

## 3. Four Critical Defense Arguments

### Argument 1: Latency

> **The Attack:** "WebSockets are overkill for a school forum. Why not just use AJAX polling every few seconds? This adds unnecessary complexity."

> **The Rebuttal:** "AJAX polling at 5-second intervals introduces a worst-case 5,000ms delay for critical announcements — imagine a fire drill broadcast delayed by 5 seconds because a poll cycle just completed. Socket.IO's persistent WebSocket connection delivers sub-200ms latency for all event types. The complexity is justified precisely because institutional announcements are time-sensitive. Furthermore, Socket.IO's fallback to long-polling on restricted networks means we lose nothing — it gracefully degrades."

**Defensive Proofs:**
- WebSocket persistent connection eliminates TCP handshake overhead on every message vs. HTTP polling's per-request cost.
- Socket.IO room-based targeting ensures broadcast only reaches subscribed role groups — no unnecessary fanout to irrelevant clients.
- Redis pub/sub decouples socket emission from HTTP request handling, preventing event loop blocking on the Node.js application server.

---

### Argument 2: Vote Integrity / Context Bloat

> **The Attack:** "What stops a student from voting 10 times? And storing per-department vote counts in Redis seems redundant with PostgreSQL."

> **The Rebuttal:** "Vote integrity is enforced at three layers: session authentication (JWT token bound to userId), server-side idempotency check (PostgreSQL unique constraint on `userId + pollId`), and Redis atomic increment with lock acquisition. The redundancy between Redis and PostgreSQL is intentional — it's a write-through cache pattern, not duplication. Redis serves the live dashboard; PostgreSQL is the audit trail. They serve different consistency requirements at different time scales."

**Defensive Proofs:**
- `UNIQUE(user_id, poll_id)` database constraint is the final arbitrator — no duplicate vote can persist even if the application layer fails.
- JWT expiry + server-side session validation prevents session-hijacking replay attacks.
- Bull job queue serializes concurrent votes from the same department, preventing TOCTOU race conditions on the Redis counter.

---

### Argument 3: State Desynchronization (Anonymous Moderation)

> **The Attack:** "If anonymous posts are held in a review queue, what if the admin never reviews them? And isn't storing the real identity a privacy violation?"

> **The Rebuttal:** "The review queue has a configurable SLA — unreviewed posts older than 24 hours trigger an admin notification. For the identity question: the de-anonymization table is stored in a separate PostgreSQL schema with role-based access control, accessible only to system administrators with logged audit trails. This mirrors the legal framework of court-ordered de-anonymization — the identity exists but is sealed. No faculty member or peer can access it. This is architecturally equivalent to how anonymous tip lines operate in law enforcement."

**Defensive Proofs:**
- PostgreSQL row-level security (RLS) policies restrict `anon_identity` schema reads to `role = superadmin` only.
- Every de-anonymization access is recorded in an immutable audit log table.
- The keyword filter intercepts posts before they enter the queue — most toxic content never reaches human review.

---

### Argument 4: Empirical Verification

> **The Attack:** "How will you prove this actually works better than Messenger? What metrics will you use for evaluation?"

> **The Rebuttal:** "We will conduct a mixed-methods evaluation with two tracks. Technical benchmarks: end-to-end WebSocket latency measured under 50-concurrent-user load using k6 load testing, compared against a baseline AJAX polling implementation. User-centric metrics: a NASA-TLX cognitive load survey administered to 30 student respondents split across experimental (CollabAcad) and control (Messenger GC) groups. We hypothesize significantly lower Task Load Index scores for the CollabAcad group, particularly in the Mental Demand and Frustration dimensions."

**Defensive Proofs:**
- Quantitative: k6 load test will generate a latency percentile report (P50, P95, P99) for both systems.
- Qualitative: SUS (System Usability Scale) score target ≥ 70 (above industry average for acceptable usability).
- Equity validation: We will run a simulation with synthetic department population data to verify that $W_{inst}$ produces correct equity normalization across 5 varied population distributions.

---

## 4. Component Coverage Map

| Layer | Component | Technologies | Purpose |
|---|---|---|---|
| **Web App** | Forum, Event Board, Vote Dashboard | Next.js 14 (App Router), React 18, TailwindCSS | Primary user interface for all roles |
| **Mobile App** | Progressive Web App (PWA) | Next.js PWA plugin, Web Push API, Service Workers | Mobile access + push notifications without native app store |
| **Machine Learning / AI** | Keyword Filter, Toxicity Screening | `bad-words` npm package + custom regex corpus + optional Perspective API integration | Pre-publication content moderation for anonymous posts |
| **IoT / Hardware** | On-Premise Server Deployment | Ubuntu 22.04 LTS VPS or institution server + Nginx reverse proxy | Keeps all data within institutional boundary |
| **Data Visualization** | Live Vote Charts, Participation Heatmaps | Chart.js / Recharts, D3.js (department participation map) | Real-time tally display; segmented analytics dashboard |
| **Networking / Real-Time** | WebSocket Event Bus | Socket.IO 4.x, Redis 7 (Pub/Sub + Sorted Sets + Lists), Bull 4.x job queue | Sub-200ms event delivery; decoupled service messaging |

---

## 5. Scope & Delimitations

### In Scope
- Institutional forum with threaded discussion (departments, organizations, public boards)
- Live Event Broadcast with Socket.IO (admin push → role-segmented rooms)
- Real-time ticker banner and pinned announcement overlay
- Segmented weighted voting with live Chart.js dashboard
- Managed anonymous posting with keyword filter and admin review queue
- Role-based access control (Student, Faculty, Org Officer, Dept Admin, Sys Admin)
- PostgreSQL relational schema with Redis caching layer
- Progressive Web App (mobile-responsive, installable)
- Admin de-anonymization with audit logging

### Out of Scope
- Native iOS/Android application (PWA covers mobile; native build is out of timeline)
- AI-generated meeting summaries or transcription (not in project thesis)
- Integration with external LMS platforms (Google Classroom, Moodle)
- Real-money transaction processing (no payment gateway)
- Video/audio streaming (text and structured data only)
- External social media cross-posting

---

## 6. Dynamic UI Rendering & Shneiderman Taxonomy

The CollabAcad interface applies Ben Shneiderman's **"Overview First, Zoom and Filter, Details-on-Demand"** paradigm across all primary views:

| Shneiderman Stage | CollabAcad UI Implementation | Data Layer |
|---|---|---|
| **Overview First** | Event Board homepage renders all active events/polls as summary cards (title, dept tag, time remaining, participation %) | Redis sorted set of $V_{gold}$ scores drives card ranking |
| **Zoom** | Clicking a poll card expands a department-segmented bar chart (real-time via SSE stream) | Redis `vote:poll:{id}:result` sorted set |
| **Filter** | Dropdown filters narrow results by Department, Organization, or Event Type | PostgreSQL `WHERE dept_code IN (...)` with indexed query |
| **Details-on-Demand** | Hovering over a department bar reveals tooltip: raw count, population, $W_d$ score, quorum status | Computed on-demand from Redis + PostgreSQL join |

For the Forum view:
- **Overview**: Thread list sorted by $V_{gold}$ salience score
- **Filter**: Tag-based filtering (Academic, Administrative, Feedback, Anonymous)
- **Details-on-Demand**: Thread expansion loads full reply chain, author badges, and (for admins) moderation flags

---

## 7. Infrastructure Topology

```
┌─────────────────────────────────────────────────────────┐
│                  INSTITUTION NETWORK BOUNDARY            │
│                                                         │
│  ┌──────────────┐    ┌─────────────────────────────┐   │
│  │   Nginx      │    │     Node.js App Server       │   │
│  │  Reverse     │───►│  (Express + Socket.IO)       │   │
│  │  Proxy       │    │  Port: 3000                  │   │
│  │  Port: 80/443│    └──────────┬──────────────────┘   │
│  └──────────────┘               │                       │
│                          ┌──────▼──────┐                │
│                          │  Redis 7    │                │
│                          │  Pub/Sub    │                │
│                          │  + Cache    │                │
│                          │  Port: 6379 │                │
│                          └──────┬──────┘                │
│                                 │                       │
│                    ┌────────────▼──────────┐            │
│                    │    PostgreSQL 15       │            │
│                    │    Primary Store       │            │
│                    │    Port: 5432          │            │
│                    └───────────────────────┘            │
│                                                         │
│  VRAM / Memory Budget (Moderation Service):             │
│  - Node.js heap: ~256MB per process                     │
│  - Redis working set: ~512MB (vote cache + sessions)    │
│  - PostgreSQL shared_buffers: ~1GB                      │
│  - Total institution server RAM target: ≥4GB            │
└─────────────────────────────────────────────────────────┘

Client Connections:
  Student Browser ──(WSS)──► Nginx ──► Socket.IO Server
  Mobile PWA ──(HTTPS)──► Nginx ──► Next.js SSR
  Admin Panel ──(WSS)──► Nginx ──► Socket.IO /admin namespace
```

---

## 8. Technical Mock Q&A: Deep-Dive (24 Questions)

### Category A: Real-Time Architecture & WebSockets

#### Q1: Why Socket.IO instead of raw WebSockets or Server-Sent Events?
*   **Answer**: Socket.IO provides automatic fallback to long-polling for clients behind restrictive firewalls (common in institution networks), built-in room/namespace management that maps perfectly to our role-segmented broadcast model, and heartbeat/reconnection logic that prevents silent disconnections. Raw WebSockets would require us to reimplement all of this. SSE is unidirectional — our system requires bidirectional event exchange (client votes → server; server tallies → client).

#### Q2: How does your system handle 500 simultaneous voters on the same poll?
*   **Answer**: Votes are enqueued via a Bull job queue backed by Redis. The queue serializes concurrent writes per department using Redis atomic locks (`SET NX EX`). Each Bull worker processes votes in FIFO order. The Socket.IO emission of updated tallies is batched — rather than emitting on every single vote, the aggregation service emits every 500ms via a debounce window, preventing broadcast storms.

#### Q3: What happens when the Redis server goes down during a live vote?
*   **Answer**: The Node.js app server has a Redis connection retry strategy (exponential backoff, max 5 retries). If Redis is unavailable, the vote submission falls through to a direct PostgreSQL write with an application-level mutex. The live dashboard degrades gracefully to a 5-second AJAX polling fallback. The Bull queue persists jobs to Redis AOF — if Redis restarts with AOF enabled, no votes are lost.

#### Q4: How does your Socket.IO namespace design prevent cross-department data leaks?
*   **Answer**: Each socket is assigned to a room on connection: `socket.join(`dept:${deptCode}`)`. Admin broadcasts targeting CAS students emit only to `room:dept:CAS`. Vote tally emissions are scoped to `room:poll:{pollId}` which all participants join. No emission crosses room boundaries; the Socket.IO server enforces this at the event routing layer.

### Category B: Weighted Voting

#### Q5: Prove that your weighted formula is resistant to ballot stuffing by a large department.
*   **Answer**: Under $W_d = \frac{V_d}{P_d} \times 100$, increasing $V_d$ (votes cast) while $P_d$ is fixed only moves $W_d$ toward 100 — the maximum gain is bounded. A department with 1,200 students achieving 100% participation scores $W_d = 100$. A department with 300 students achieving 80% participation scores $W_d = 80$. The institutional aggregate $W_{inst}$ gives each department equal weight in the mean. Flooding votes from CAS cannot exceed $W_{CAS} = 100$, which is then averaged with all other departments.

#### Q6: What is the quorum threshold and how is it enforced?
*   **Answer**: $Q_d = V_d / P_d \geq 0.30$. This is checked after the poll closes. Departments below quorum are flagged visually on the dashboard with a "Low Participation" badge. Their $W_d$ is included in $W_{inst}$ but displayed with a confidence warning. The panel can configure whether sub-quorum departments are excluded from the final count — this is a system administration setting.

#### Q7: Why arithmetic mean for $W_{inst}$ and not weighted mean by department size?
*   **Answer**: A weighted mean by department size reintroduces population bias — larger departments would have greater influence on the final aggregate, defeating the equity goal. The arithmetic mean treats each department as an equal institutional actor, which aligns with the political science principle of equal representation per constituency, not proportional representation.

#### Q8: Could a department with very few voters (e.g., 5 out of 10) distort the aggregate?
*   **Answer**: Yes — this is the small-department noise problem. Our quorum threshold of 30% mitigates this: a department with only 5 registered members needs at least 2 votes to be considered. For very small sub-units, administrators can configure minimum absolute vote thresholds (e.g., $V_d \geq 10$) before including the department in the aggregate. This is exposed as a poll configuration option.

### Category C: Anonymous Moderation

#### Q9: What keyword filter approach do you use and how do you prevent filter evasion?
*   **Answer**: We use a layered approach: a base `bad-words` npm package corpus, supplemented by a custom Filipino/Tagalog slur dictionary curated for the local institutional context. Filter evasion (l33tspeak, character substitution like "b*tch") is addressed by normalizing input before comparison: strip non-alphabetic characters, map common substitutions (@ → a, 3 → e), then run the filter on the normalized string. This is not foolproof — it is a first-pass gate, not a final arbitrator.

#### Q10: How is the de-anonymization table protected from unauthorized access?
*   **Answer**: The `anon_identity` table resides in a separate PostgreSQL schema (`private`). Row-level security policy: `CREATE POLICY anon_admin_only ON private.anon_identity USING (current_user = 'sysadmin')`. Application-layer middleware additionally requires a secondary OTP confirmation before any admin UI triggers a de-anonymization lookup. All lookups are recorded in an immutable audit log via a PostgreSQL trigger.

#### Q11: What is the legal basis for storing anonymous identities at all?
*   **Answer**: The system's terms of use — agreed to at account registration — disclose that anonymous posts are pseudonymous, not truly anonymous, and that identity may be revealed to system administrators under circumstances of demonstrated harm or institutional policy violation. This mirrors standard anonymous reporting system disclosures. The stored identity is the institution-assigned student/faculty ID — no additional PII beyond what the institution already holds.

### Category D: Data Visualization & UI

#### Q12: How does your live chart update without the page refreshing?
*   **Answer**: The frontend subscribes to a Socket.IO event: `socket.on('vote:update', (data) => updateChart(data))`. The Chart.js instance is updated via `chart.data.datasets[0].data = newWeightedScores; chart.update('active')`. This triggers a smooth animation interpolation between the old and new bar heights — no DOM reload, no HTTP request.

#### Q13: How does Shneiderman's taxonomy apply to your segmented vote dashboard?
*   **Answer**: The overview level shows all departments as a single stacked bar chart of aggregate $W_{inst}$. The zoom level allows clicking a department bar to expand a sub-chart of section-level participation within that department. The filter level lets the admin select specific sections or date ranges. Details-on-demand are triggered by hovering any bar, revealing the raw count, population, $W_d$, and quorum status in a tooltip. This three-level drill-down mirrors Shneiderman's information-seeking mantra precisely.

### Category E: Security & Privacy

#### Q14: How do you prevent SQL injection in vote submissions?
*   **Answer**: All database queries use parameterized statements via the `pg` Node.js driver: `client.query('INSERT INTO votes (user_id, poll_id, choice) VALUES ($1, $2, $3)', [userId, pollId, choice])`. No string concatenation of user input into SQL. Additionally, input is validated server-side with `zod` schema validation before any database interaction.

#### Q15: How is JWT authentication implemented and what are the expiry policies?
*   **Answer**: Access tokens: 15-minute expiry, stored in memory (React state). Refresh tokens: 7-day expiry, stored in an `httpOnly`, `Secure`, `SameSite=Strict` cookie. On access token expiry, the frontend silently requests a new access token using the refresh token. On refresh token expiry, the user is redirected to login. Socket.IO connections validate the JWT on the initial handshake via a middleware: `io.use((socket, next) => { verifyJWT(socket.handshake.auth.token, next) })`.

#### Q16: What happens if a student tries to access another department's vote data via API manipulation?
*   **Answer**: Every API endpoint enforces authorization: `if (req.user.deptCode !== requestedDeptCode && req.user.role !== 'admin') return res.status(403).json({ error: 'Forbidden' })`. Department-scoped data is filtered at the query level using the authenticated user's `deptCode` from their JWT payload — the client cannot override this.

### Category F: Database Design

#### Q17: What is your PostgreSQL schema for the voting module?
*   **Answer**: ```sql
CREATE TABLE polls (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  created_by UUID REFERENCES users(id),
  closes_at TIMESTAMPTZ,
  quorum_threshold FLOAT DEFAULT 0.30,
  status TEXT CHECK (status IN ('draft','active','closed'))
);

CREATE TABLE votes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  poll_id UUID REFERENCES polls(id),
  user_id UUID REFERENCES users(id),
  dept_code TEXT REFERENCES departments(code),
  choice BOOLEAN NOT NULL,
  cast_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(poll_id, user_id)
);

CREATE TABLE departments (
  code TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  population INTEGER NOT NULL
);
```

#### Q18: How do you compute $W_d$ efficiently at scale in PostgreSQL?
*   **Answer**: ```sql
SELECT
  v.dept_code,
  COUNT(*) FILTER (WHERE v.choice = TRUE) AS yes_votes,
  d.population,
  ROUND((COUNT(*) FILTER (WHERE v.choice = TRUE)::FLOAT / d.population) * 100, 2) AS W_d
FROM votes v
JOIN departments d ON v.dept_code = d.code
WHERE v.poll_id = $1
GROUP BY v.dept_code, d.population;
```
This query runs in O(n) where n is total votes cast. For the live dashboard, Redis caches the result snapshot, so this SQL runs only on cache miss or poll close.

### Category G: Scalability & Load

#### Q19: What is your estimated maximum concurrent user capacity?
*   **Answer**: A single Node.js + Socket.IO server on a 2-core/4GB instance handles approximately 10,000 concurrent WebSocket connections per Socket.IO documentation benchmarks. For a typical Philippine institution (2,000–5,000 students), a single server is sufficient. Horizontal scaling via multiple Node.js instances + Redis adapter for Socket.IO (all instances sharing one Redis pub/sub bus) handles growth.

#### Q20: How does your system behave under a DDoS attack on the voting endpoint?
*   **Answer**: Nginx rate limiting: `limit_req_zone $binary_remote_addr zone=vote:10m rate=5r/s` — each IP is limited to 5 vote requests per second. Additionally, each authenticated vote is idempotency-checked: a second submission for the same `(user_id, poll_id)` pair is rejected at the PostgreSQL unique constraint before processing. Cloudflare or institution firewall WAF handles volumetric attacks at the network layer.

### Category H: Testing & Evaluation

#### Q21: What testing strategy do you use for the weighted voting formula?
*   **Answer**: Unit tests (Jest): 15 test cases covering edge conditions — all votes from one department, zero votes, single-member departments, exactly 30% quorum, 100% participation. Integration tests: Supertest against the `/api/polls/:id/results` endpoint with seeded database data. Formula validation: synthetic dataset with known ground-truth outputs compared against computed $W_d$ and $W_{inst}$ values.

#### Q22: How will you measure if the system actually reduces communication friction?
*   **Answer**: Pre/post survey design: 30 participants from existing Messenger GC users, split 15/15. Control group continues using Messenger GC for 2 weeks. Experimental group uses CollabAcad. NASA-TLX administered after each week. Primary hypothesis: CollabAcad group reports significantly lower Frustration and Mental Demand subscale scores. Secondary metric: time-to-information (how long it takes a student to find a specific announcement) measured via screen recording analysis.

#### Q23: What is your SUS score target and how will you administer the survey?
*   **Answer**: Target: SUS ≥ 70 (industry benchmark for "acceptable" usability; ≥ 85 is "excellent"). Survey administered via Google Forms after a 30-minute structured usability session where participants complete 5 predefined tasks (post a forum reply, cast a vote, find an announcement, toggle anonymous mode, check vote results). SUS is a 10-item Likert scale — scoring is standardized and validated.

#### Q24: How do you validate that your anonymity filter works correctly?
*   **Answer**: Test corpus: 200 hand-labeled posts (100 toxic, 100 clean) including common Filipino slurs, English profanity, l33tspeak variants, and benign posts that contain flaggable substrings (e.g., "assess" containing "ass"). Compute precision and recall of the filter on this labeled corpus. Target: Precision ≥ 0.85 (low false positive rate — clean posts not incorrectly blocked), Recall ≥ 0.80 (most toxic posts caught). False negatives (missed toxic posts) are acceptable given the human review queue as a backstop.

---

## 9. Difficulty Acknowledgment & Roadmap

**Three Genuinely Difficult Components:**

1. **Redis + Socket.IO Horizontal Scaling**: Configuring the Socket.IO Redis adapter correctly so multiple Node.js instances share the same pub/sub bus without duplicate emissions is non-trivial. This requires understanding of Redis cluster vs. sentinel vs. standalone deployment tradeoffs.

2. **Weighted Vote Race Condition Prevention**: The MESI-inspired locking protocol using Redis `SET NX EX` is correct in theory but requires careful testing under concurrent load to ensure no vote is silently dropped during lock contention.

3. **Anonymous Moderation UX Balance**: The admin review queue must be fast enough that legitimate anonymous posts aren't buried for days, but the keyword filter must be aggressive enough to catch toxic content before it enters the queue. Tuning this threshold is an empirical problem requiring iteration on real institutional language data.

**Three-Phase Execution Roadmap:**

| Phase | Timeline | Deliverables | Success Criteria |
|---|---|---|---|
| **Phase 1: Core Infrastructure** | Weeks 1–4 | PostgreSQL schema, Next.js scaffolding, JWT auth, basic forum CRUD, Socket.IO connection | Forum posts persist; WebSocket connection stable under 10 concurrent users |
| **Phase 2: Real-Time Features** | Weeks 5–9 | Live Event Broadcast, Weighted Voting with Redis cache, Anonymous Posting with keyword filter | Sub-300ms broadcast latency; correct $W_d$ computation on 5 test departments; anonymous posts intercepted at 80% recall |
| **Phase 3: Analytics & Evaluation** | Weeks 10–14 | Chart.js live dashboard, Shneiderman drill-down UI, NASA-TLX evaluation, k6 load testing, documentation | SUS ≥ 70; P95 latency < 500ms at 50 concurrent users; panel-ready defense documentation |

---

## 10. Summary System Matrix

| Layer | Technology | Standard / Compliance | Privacy Mitigation |
|---|---|---|---|
| Frontend Framework | Next.js 14 (App Router) | WCAG 2.1 AA | No PII in client-side state beyond session token |
| Real-Time Transport | Socket.IO 4.x over WSS | RFC 6455 (WebSocket) | TLS encryption of all WS traffic; JWT auth on handshake |
| HTTP API | Express.js REST | RESTful conventions | Rate limiting; input validation via zod; CORS restricted to institution domain |
| Job Queue | Bull 4.x + Redis | FIFO + retry semantics | Vote data serialized, not logged in plaintext |
| Cache Layer | Redis 7 | LRU + TTL eviction | No raw PII in Redis; only anonymized vote counts and session tokens |
| Primary Database | PostgreSQL 15 | ACID compliance | Row-level security; separate schema for anonymization table |
| Authentication | JWT (RS256) | RFC 7519 | httpOnly cookie for refresh token; memory-only for access token |
| Content Moderation | Custom keyword filter + `bad-words` | Institution AUP | Flagged posts isolated to admin-only review queue |
| Mobile Access | Next.js PWA | W3C PWA specification | Service worker scope restricted to institution domain |
| Infrastructure | Ubuntu 22.04 + Nginx | On-premise / private VPS | All data remains within institution network boundary |

---

## 11. Complete Technology Stack Reference

| Category | Technology | Version | Purpose |
|---|---|---|---|
| Frontend Framework | Next.js | 14.x (App Router) | SSR + client-side React SPA |
| UI Library | React | 18.x | Component-based UI |
| Styling | TailwindCSS | 3.x | Utility-first CSS |
| Real-Time Client | Socket.IO Client | 4.x | WebSocket event subscription |
| Charts | Chart.js + react-chartjs-2 | 4.x | Live vote visualization |
| Form Validation | React Hook Form + Zod | 7.x / 3.x | Client-side + shared schema validation |
| Backend Runtime | Node.js | 20.x LTS | Server-side JavaScript |
| HTTP Framework | Express.js | 4.x | REST API routing |
| WebSocket Server | Socket.IO | 4.x | Real-time event bus |
| Job Queue | Bull | 4.x | Async vote processing |
| Cache / Pub-Sub | Redis | 7.x | Hot cache + inter-service messaging |
| Database | PostgreSQL | 15.x | Relational durable store |
| ORM / Query Builder | node-postgres (`pg`) | 8.x | Parameterized SQL |
| Authentication | jsonwebtoken | 9.x | JWT generation + verification |
| Password Hashing | bcryptjs | 2.x | Secure credential storage |
| Content Filter | bad-words | 3.x + custom corpus | Anonymous post toxicity screening |
| Input Validation | zod | 3.x | Server-side schema enforcement |
| Load Testing | k6 | 0.50.x | WebSocket + HTTP load simulation |
| Unit Testing | Jest + Supertest | 29.x / 6.x | API + formula unit tests |
| Process Manager | PM2 | 5.x | Node.js clustering + auto-restart |
| Reverse Proxy | Nginx | 1.24.x | SSL termination + rate limiting |
| OS | Ubuntu | 22.04 LTS | Server operating system |
