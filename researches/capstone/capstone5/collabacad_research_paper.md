# Theoretical Foundations and Architectural Design of CollabAcad: A Real-Time Institutional Forum System with Equity-Normalized Participatory Voting and Managed Anonymous Discourse

**Abstract**

Contemporary Philippine higher education institutions rely predominantly on consumer-grade social networking platforms — principally Facebook Messenger — for institutional communication, event dissemination, and student participatory processes. This practice introduces three structurally documented failures: the conflation of personal and professional communication boundaries among faculty stakeholders, the systematic suppression of minority department voices in raw-count voting structures, and the absence of psychologically safe anonymous discourse channels. This paper presents the theoretical foundations and architectural design of *CollabAcad*, a purpose-built, institution-hosted real-time forum and event management system addressing all three failure modes. Drawing from Weiser's (1991) ubiquitous computing paradigm, Dillenbourg's (2002) orchestration graph framework, and Shneiderman's (1996) visual information-seeking taxonomy, CollabAcad introduces three novel engineering contributions: a Socket.IO-based role-segmented broadcast architecture, a department-normalized weighted voting algorithm formally grounded in participatory democracy theory, and a managed anonymity layer with pre-publication toxicity interception. Evaluation will employ a mixed-methods framework combining technical load benchmarks (k6) and human-centric cognitive load measurement (NASA-TLX), targeting a System Usability Scale score exceeding the 70-point industry threshold.

**Keywords:** real-time web systems; participatory platforms; weighted voting; institutional communication; anonymous discourse; WebSockets; collaborative technology

---

## 1. Introduction

The proliferation of consumer social networking platforms within institutional contexts represents a well-documented infrastructural compromise. When Philippine universities and colleges adopt Facebook Messenger Group Chats as de facto administrative communication infrastructure, they inherit a platform designed for interpersonal social exchange — not institutional governance, participatory decision-making, or confidential discourse. The consequences are multifold and structurally predictable.

First, boundary violation: Venkatesh and Brown (2001) established that technology appropriation within organizational contexts is governed by social influence norms. When faculty members are implicitly required to use personal social media accounts for professional communication, the resulting boundary collapse generates measurable affective distress and role-identity conflict (Mazmanian, Orlikowski, & Yates, 2013). Second, representational inequity: raw-count majority voting in heterogeneously sized organizational sub-units systematically suppresses minority constituencies, a phenomenon documented across organizational behavior literature (Arrow, 1963; Dahl, 1956). A college of 1,200 students will arithmetically dominate a college of 300 students in any unweighted participatory process. Third, discourse suppression: Ackerman (2000) identifies the fundamental "social-technical gap" in collaborative systems — the engineering failure to accommodate the social complexity of discourse norms, including the documented human need for psychologically safe anonymous expression (Kiesler, Siegel, & McGuire, 1984).

CollabAcad is presented as a theoretically grounded architectural response to these three failure modes, implemented within the constraints and affordances of modern real-time web infrastructure.

---

## 2. Theoretical Foundations

### 2.1 Ubiquitous Computing and Context-Aware Institutional Platforms

Mark Weiser's seminal vision of ubiquitous computing (1991) proposed the displacement of discrete computing devices by seamlessly embedded, context-responsive computational environments. While Weiser's original formulation concerned physical embedding, subsequent scholarship has extended the paradigm to software architecture. Abowd and Mynatt (2000) reframe ubiquitous computing as the design of systems that exhibit *proactive contextual responsiveness* — systems that adapt their behavior to the current situational context of the user without requiring explicit parameterization.

Anind Dey's (2001) formal definition of context as "any information that can be used to characterize the situation of an entity" provides the operational grounding for CollabAcad's role-aware broadcast architecture. In CollabAcad, the relevant context dimensions are: user role (Student, Faculty, Department Administrator, Student Government Officer, System Administrator), organizational affiliation (department code, college), and temporal situational state (active event, closed poll, pending moderation). These context dimensions directly govern the system's behavioral outputs — broadcast targeting, voting eligibility, anonymity permissions, and dashboard rendering.

**Comparative Analysis: Traditional Platforms vs. CollabAcad**

| Feature Dimension | Facebook Messenger GC | Google Classroom | CollabAcad |
|---|---|---|---|
| Context Awareness | None (flat broadcast) | Course-scoped only | Role + department + event-state aware |
| Real-Time Push | Mobile notification only | None (polling) | WebSocket sub-200ms broadcast |
| Boundary Separation | None (personal accounts) | Partial (Google account) | Institution-issued identity only |
| Voting / Participation | None | None | Weighted, segmented, real-time |
| Anonymous Discourse | None | None | Managed, auditable, filtered |
| Data Sovereignty | Facebook servers | Google servers | Institution-controlled on-premise |
| Semantic Metadata | None | Course tags only | Dept code, role, event type, salience score |

This comparative mapping demonstrates that CollabAcad occupies a structural gap unaddressed by both general-purpose social platforms and purpose-built learning management systems.

### 2.2 Real-Time Collaborative Architecture and WebSocket Event Routing

The theoretical basis for CollabAcad's real-time event broadcast layer is grounded in the Reactive Systems architectural paradigm (Boner et al., 2014), which prescribes that distributed systems should be *responsive* (consistent low latency), *resilient* (failure tolerance), *elastic* (adaptive under load), and *message-driven* (asynchronous communication). The WebSocket protocol (Fette & Melnikov, 2011; RFC 6455) provides the transport substrate enabling persistent, full-duplex communication channels between institution server and client browsers, eliminating the polling overhead that characterizes HTTP-based notification systems.

Socket.IO's room-based namespace architecture maps directly onto CollabAcad's context model. Each authenticated socket connection is assigned to rooms corresponding to the user's role and department affiliation: `dept:{code}` and `role:{roleName}`. Event emissions are scoped to specific rooms, implementing what Dourish and Bellotti (1992) term *awareness filtering* — the selective routing of shared workspace events to relevant stakeholders, preventing information overload while maintaining operational awareness.

**End-to-End Latency Composition:**

The theoretical minimum latency for a broadcast event is governed by:

$$L_{total} = L_{server} + L_{redis} + L_{socket} + L_{render}$$

Where $L_{server}$ is application processing time (~10ms), $L_{redis}$ is pub/sub fanout latency (~5ms), $L_{socket}$ is Socket.IO emission overhead (~10ms), and $L_{render}$ is client-side React reconciliation (~20ms). The theoretical total is approximately 45ms — well within the 200ms perceptual threshold established by Nielsen (1993) for "immediate" system response.

### 2.3 Participatory Democracy Theory and Equity-Normalized Voting

The mathematical foundations of CollabAcad's weighted voting module are grounded in the literature on proportional representation and deliberative democracy (Lijphart, 1999; Rawls, 1971). The central theoretical problem is the majority tyranny inherent in unweighted voting across constituencies of unequal size. Arrow's Impossibility Theorem (1963) establishes that no voting system can simultaneously satisfy all fairness criteria; however, within a constrained institutional context, department-level normalization represents a principled compromise that maximizes inter-departmental equity.

**Formal Definition of the Weighted Participation Score:**

For department $d$ participating in poll $p$, the weighted participation score $W_d$ is defined as:

$$W_d = \frac{V_d}{P_d} \times 100$$

Where $V_d \in \mathbb{Z}^+$ denotes the count of affirmative votes cast by registered members of department $d$, and $P_d \in \mathbb{Z}^+$ denotes the total registered membership population of department $d$. The resulting $W_d \in [0, 100]$ represents the departmental participation rate as a percentage, normalized to the department's own population — independent of inter-departmental population disparities.

**Institutional Aggregate Score:**

The institutional consensus metric $W_{inst}$ is computed as the arithmetic mean of all departmental weighted scores across the participating department set $D$:

$$W_{inst} = \frac{1}{|D|} \sum_{d \in D} W_d$$

The arithmetic mean assigns equal institutional weight to each department regardless of population, operationalizing the principle that each academic unit constitutes an equal deliberative actor within the institutional polity — analogous to equal state representation in bicameral legislative structures.

**Quorum Constraint:**

To prevent low-participation outliers from distorting the aggregate, a minimum quorum threshold $Q$ is enforced:

$$Q_d = \frac{V_d}{P_d} \geq \tau_Q, \quad \tau_Q = 0.30$$

Departments satisfying $Q_d < \tau_Q$ are flagged for low participation. System administrators may configure whether sub-quorum departments are excluded from the aggregate computation or retained with a confidence penalty.

**Theoretical Validation — Population Disparity Simulation:**

Consider a five-department institution with the following composition:

| Dept | $P_d$ | $V_d$ | Raw Share | $W_d$ | $W_{inst}$ Contribution |
|---|---|---|---|---|---|
| CAS | 1,200 | 840 | 50.1% of raw votes | 70.00 | 14.00 |
| CTE | 300 | 255 | 15.2% | 85.00 | 17.00 |
| CBM | 450 | 180 | 10.7% | 40.00 | 8.00 |
| CCS | 350 | 280 | 16.7% | 80.00 | 16.00 |
| CED | 280 | 120 | 7.2% | 42.86 | 8.57 |
| **Total** | **2,580** | **1,675** | — | — | **63.57** |

Under unweighted raw counting, CAS's 840 votes constitute 50.1% of all votes cast, effectively granting CAS majority unilateral control. Under the weighted formula, CAS contributes 70.00 to the average — identical in computational status to CTE's 85.00. The institutional aggregate of 63.57 reflects a genuine cross-departmental consensus rather than a population-weighted majority preference.

### 2.4 Anonymous Discourse Theory and Managed Pseudonymity

Kiesler et al. (1984) demonstrated that computer-mediated communication channels featuring reduced social cues — including anonymity — produce measurable increases in uninhibited expression, both prosocial (willingness to raise legitimate concerns) and antisocial (hostile or toxic expression). This empirical duality defines the architectural challenge of anonymous forum design: maximizing the prosocial benefits of uninhibited expression while minimizing antisocial harm.

Friedman and Nissenbaum (1996) introduce the concept of *value-sensitive design* — the systematic consideration of human values in technology development. CollabAcad's managed anonymity architecture operationalizes value-sensitive design through a three-layer framework:

1. **Presentation Layer**: Posts appear to peers without author attribution — preserving the psychological safety benefit of anonymity.
2. **Moderation Layer**: Pre-publication keyword filtering intercepts high-probability toxic content before peer exposure — reducing antisocial harm.
3. **Accountability Layer**: The de-anonymization table, stored in an access-controlled database schema with immutable audit logging, preserves institutional accountability without surfacing identity to unauthorized parties.

This tripartite structure instantiates what Nissenbaum (2010) terms *contextual integrity* — information flows appropriately when they match the norms of the context in which information is shared. Anonymous posts flow appropriately to peers (presentation) and to system administrators under specified conditions (accountability), but not to arbitrary faculty or student observers.

---

## 3. System Architecture

### 3.1 Layered Service Decomposition

CollabAcad's backend decomposes into four asynchronously orchestrated services communicating via Redis Pub/Sub channels, a pattern consistent with the microservices architectural style (Newman, 2015) adapted for single-institution deployment scale:

- **Event Broadcast Service**: Consumes administrator-authored announcements and emits role-segmented Socket.IO events to subscribed client rooms.
- **Vote Aggregation Service**: Processes individual vote submissions via a Bull job queue, computes $W_d$ per department, and emits live tally snapshots to poll subscriber rooms.
- **Anonymity Moderation Service**: Intercepts anonymous post submissions, applies the keyword filter pipeline, routes flagged content to the admin review queue, and publishes cleared posts to the forum service.
- **Notification Delivery Service**: Fans out per-user bell notifications via Socket.IO to individual user socket rooms.

### 3.2 Hardware-Inspired Cache Hierarchy

The caching architecture applies a three-tier memory hierarchy model analogous to CPU cache design:

| Tier | Technology | Contents | Latency | Eviction |
|---|---|---|---|---|
| L1 (Hot) | Redis in-memory | Active vote tallies, ticker queue, presence map | ~1ms | LRU + 30s TTL |
| L2 (Working) | Redis RDB snapshot | Session tokens, event metadata, thread manifests | ~5ms | Write-through; session expiry |
| L3 (Durable) | PostgreSQL | All posts, votes, audit logs, anonymization table | ~10ms | Append-only (audit); soft-delete (posts) |

The **Information Salience Score** $V_{gold}$ governs L1 sorted set ordering for the event feed:

$$V_{gold} = \frac{\sum_{k=1}^{K} \alpha_k \cdot r_k}{\sum_{k=1}^{K} \alpha_k}$$

Where engagement signals $k \in \{\text{view}, \text{reply}, \text{reaction}, \text{save}\}$ carry weights $\alpha = \{0.1, 0.4, 0.3, 0.2\}$ respectively. Posts with $V_{gold}$ below the rolling 48-hour median are demoted from the pinned board — implementing a recency-and-engagement-aware replacement policy.

### 3.3 Semantic Cache Coherence for Vote State

Concurrent vote submissions targeting the same departmental tally introduce data race conditions under naive implementation. CollabAcad applies a software-defined coherence protocol modeled after the MESI cache coherence framework:

| State | Condition | Implementation |
|---|---|---|
| Modified (M) | Vote written to Redis; PostgreSQL write pending | Redis atomic increment; Bull job enqueued |
| Exclusive (E) | Single write lock held on dept vote block | `SET lock:{pollId}:{deptCode} NX EX 5` |
| Shared (S) | Multiple dashboard clients reading tally snapshot | SSE stream consumers reading Redis sorted set |
| Invalid (I) | Poll closed or TTL expired | Redis key deleted; re-fetch from PostgreSQL |

---

## 4. Visual Information Architecture and Shneiderman's Taxonomy

Shneiderman's (1996) Visual Information-Seeking Mantra — *"Overview first, zoom and filter, then details-on-demand"* — provides the structural framework for CollabAcad's analytics dashboard design. The three-stage mantra maps to the vote dashboard as follows:

| Shneiderman Stage | CollabAcad Implementation | Data Source |
|---|---|---|
| Overview | Aggregate $W_{inst}$ displayed as a single gauge; all departments shown as color-coded horizontal bars | Redis sorted set: `vote:poll:{id}:result` |
| Zoom | Click on a department bar to expand section-level participation sub-chart | PostgreSQL GROUP BY section_code query |
| Filter | Dropdown: filter by department, date range, poll type | Parameterized PostgreSQL WHERE clause with indexes |
| Details-on-Demand | Hover tooltip: $V_d$, $P_d$, $W_d$, quorum status, timestamp of last vote | Computed join: Redis snapshot + departments table |

Shneiderman's taxonomy of data types (1996) maps to CollabAcad's content structures as follows:

| Shneiderman Type | CollabAcad Manifestation | Visualization |
|---|---|---|
| One-Dimensional | Vote tallies per department (ordered list) | Horizontal bar chart (Chart.js) |
| Two-Dimensional | Participation heatmap (dept × time) | D3.js grid heatmap |
| Temporal | Vote cast timestamps over poll duration | Line chart: votes per hour |
| Network | Forum reply threading (parent–child relationships) | Nested tree view (React recursive component) |

---

## 5. Collaborative Orchestration and Role-Aware Rendering

Dillenbourg's (2002) orchestration graphs provide a formal notation for representing the coordination of collaborative activities across participants with heterogeneous roles and responsibilities. In CollabAcad, the orchestration graph maps to a role-aware socket subscription model:

```
[System Administrator]
  └── Namespace: /admin
       ├── Emit: broadcast:all, broadcast:dept:{code}
       └── Receive: moderation:queue:update, vote:anomaly:alert

[Faculty / Department Admin]
  └── Namespace: /faculty
       ├── Emit: event:create, poll:create, post:moderate
       └── Receive: broadcast:all, broadcast:role:faculty

[Student / Org Officer]
  └── Namespace: /student
       ├── Emit: vote:cast, post:create, post:anonymous
       └── Receive: broadcast:all, broadcast:dept:{code}, vote:tally:update
```

Each role receives a distinct rendered dashboard state — the Dillenbourg "decoupled visual state" principle applied to web UI design. Administrators see the moderation queue and de-anonymization controls. Faculty see event management and poll creation interfaces. Students see the forum feed, live vote tallies, and their individual voting history.

---

## 6. Evaluation Framework

### 6.1 Technical Benchmarks

Technical evaluation will employ k6 load testing simulating 50 concurrent users across three scenarios: (1) simultaneous broadcast reception, (2) concurrent vote submission (same poll, multiple departments), and (3) mixed forum posting and voting. Metrics collected: WebSocket connection establishment time, event delivery latency (P50, P95, P99), vote computation correctness under concurrency, and Redis hit rate during peak load.

Target criteria:

| Metric | Target |
|---|---|
| P95 Broadcast Latency | < 300ms |
| P95 Vote Tally Update Latency | < 500ms |
| Vote Correctness (concurrent) | 100% (zero duplicate votes persisted) |
| Redis Cache Hit Rate | > 90% during active poll |
| $W_d$ Formula Accuracy | 100% match against ground-truth computations |

### 6.2 Human-Centric Usability Evaluation

Human-centric evaluation will employ two validated instruments:

**NASA-TLX (Task Load Index):** A 6-dimension workload assessment covering Mental Demand, Physical Demand, Temporal Demand, Performance, Effort, and Frustration (Hart & Staveland, 1988). Administered to 30 participants (15 experimental: CollabAcad; 15 control: Facebook Messenger GC) after a structured 2-week usage period. Primary hypothesis: CollabAcad participants report significantly lower scores on the Mental Demand and Frustration subscales (p < 0.05, two-tailed t-test).

**System Usability Scale (SUS):** A 10-item standardized usability questionnaire (Brooke, 1996). Administered after a 30-minute structured task session comprising 5 predefined tasks. Target: SUS ≥ 70 (acceptable threshold); aspirational target ≥ 85 (excellent).

**Anonymous Filter Evaluation:** A 200-post labeled corpus (100 toxic, 100 benign) including Filipino/Tagalog slurs, English profanity, l33tspeak variants, and benign posts containing flaggable substrings. Filter performance evaluated on Precision and Recall:

$$\text{Precision} = \frac{TP}{TP + FP} \geq 0.85$$

$$\text{Recall} = \frac{TP}{TP + FN} \geq 0.80$$

---

## 7. Conclusion

CollabAcad presents a theoretically grounded architectural response to documented failures in Philippine institutional communication infrastructure. By synthesizing Weiser's ubiquitous computing paradigm, Arrow's participatory democracy theory, Dillenbourg's orchestration graph framework, and Shneiderman's visual information-seeking taxonomy into a coherent real-time web system, CollabAcad advances the state of practice in institutional collaborative platforms beyond both consumer social networks and generic learning management systems. The three novel contributions — Socket.IO role-segmented broadcast, department-normalized weighted voting, and managed pseudonymous discourse — address structurally distinct failure modes with architecturally distinct solutions. Evaluation will provide empirical validation across both technical performance dimensions and human-centric usability dimensions, producing a replicable assessment framework for future institutional platform deployments.

---

## Works Cited

Abowd, G. D., & Mynatt, E. D. (2000). Charting past, present, and future research in ubiquitous computing. *ACM Transactions on Computer-Human Interaction, 7*(1), 29–58.

Ackerman, M. S. (2000). The intellectual challenge of CSCW: The gap between social requirements and technical feasibility. *Human–Computer Interaction, 15*(2–3), 179–203.

Arrow, K. J. (1963). *Social choice and individual values* (2nd ed.). Yale University Press.

Boner, J., Farley, D., Kuhn, R., & Thompson, M. (2014). *The reactive manifesto* (v2.0). reactivemanifesto.org.

Brooke, J. (1996). SUS: A "quick and dirty" usability scale. In P. W. Jordan, B. Thomas, B. A. Weerdmeester, & I. L. McClelland (Eds.), *Usability evaluation in industry* (pp. 189–194). Taylor & Francis.

Dahl, R. A. (1956). *A preface to democratic theory*. University of Chicago Press.

Dey, A. K. (2001). Understanding and using context. *Personal and Ubiquitous Computing, 5*(1), 4–7.

Dillenbourg, P. (2002). Over-scripting CSCL: The risks of blending collaborative learning with instructional design. In P. A. Kirschner (Ed.), *Three worlds of CSCL* (pp. 61–91). Open Universiteit Nederland.

Dourish, P., & Bellotti, V. (1992). Awareness and coordination in shared workspaces. In *Proceedings of the 1992 ACM Conference on Computer-Supported Cooperative Work* (pp. 107–114). ACM.

Fette, I., & Melnikov, A. (2011). *The WebSocket protocol* (RFC 6455). IETF.

Friedman, B., & Nissenbaum, H. (1996). Bias in computer systems. *ACM Transactions on Information Systems, 14*(3), 330–347.

Hart, S. G., & Staveland, L. E. (1988). Development of NASA-TLX (Task Load Index): Results of empirical and theoretical research. *Advances in Psychology, 52*, 139–183.

Kiesler, S., Siegel, J., & McGuire, T. W. (1984). Social psychological aspects of computer-mediated communication. *American Psychologist, 39*(10), 1123–1134.

Lijphart, A. (1999). *Patterns of democracy: Government forms and performance in thirty-six countries*. Yale University Press.

Mazmanian, M., Orlikowski, W. J., & Yates, J. (2013). The autonomy paradox: The implications of mobile email devices for knowledge professionals. *Organization Science, 24*(5), 1337–1357.

Newman, S. (2015). *Building microservices: Designing fine-grained systems*. O'Reilly Media.

Nielsen, J. (1993). *Usability engineering*. Academic Press.

Nissenbaum, H. (2010). *Privacy in context: Technology, policy, and the integrity of social life*. Stanford University Press.

Rawls, J. (1971). *A theory of justice*. Harvard University Press.

Shneiderman, B. (1996). The eyes have it: A task by data type taxonomy for information visualizations. In *Proceedings of the 1996 IEEE Symposium on Visual Languages* (pp. 336–343). IEEE.

Venkatesh, V., & Brown, S. A. (2001). A longitudinal investigation of personal computers in homes: Adoption determinants and emerging challenges. *MIS Quarterly, 25*(1), 71–102.

Weiser, M. (1991). The computer for the 21st century. *Scientific American, 265*(3), 94–104.
