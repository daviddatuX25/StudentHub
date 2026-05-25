# SecureCAT — Presentation Source (6-Slide Structure)

**Format:** 6 slides including live simulator | **Total time:** 10 minutes
**Audience:** Thesis panel (ISPSC Guidance and Registrar Offices)
**Style:** Emerald green cybersecurity, sharp contrast, structured wireframes
**Source of truth:** `SecureCAT Capstone Research Grounding.md` + `presentation-securecat.html`

> **Timing Budget (10 min)**
> Slide 1: Title & Registry · 0:20
> Slide 2: Context & The Problem · 1:30
> Slide 3: Proposed System & Component Map · 1:30
> Slide 4: Interactive Pipeline Simulation (Live Demo Transition) · 5:30
> Slide 5: System Comparisons & Boundaries · 1:00
> Slide 6: Development Roadmap & Conclusion · 0:30

---

## Slide 1 — Title & Registry (20 sec)

| Element | Content |
|---------|---------|
| Registry Code | `BSIT-CAP4-2026-SC-V2` |
| Title | **SecureCAT** |
| Subtitle | A Role-Based College Admission Testing System for the Guidance and Registrar Offices at ISPSC Tagudin |
| Highlights | Role-Gated Admission Pipeline & Immutable Audit Logging (RBAC) |
| Branding | **SC** logo mark in a glowing cybersecurity shield |

**Speaker Script:**
> "Good morning, members of the panel. We present **SecureCAT** — a Role-Based College Admission Testing System designed for the Guidance and Registrar Offices of ISPSC Tagudin. Our project modernizes the admission pipeline by implementing key Information Assurance and Security principles — specifically role-based access control, state-guarded workflow transitions, and immutable audit logging — to ensure data integrity and absolute accountability."

**Cue:** Advance to Slide 2 as you transition to the problem.

---

## Slide 2 — Context & The Problem (90 sec)

**Layout:** Split layout — left shows institutional context and simulated warning log console; right lists the primary vulnerability cards.

### Left Half — Institutional Hook & Reality
- **Scene Hook:** *"A proctor glances at a student ID card at the testing room door. Weeks later, anomalies emerge in the scoring spreadsheets with no trail."*
- **Context:** Admission testing at ISPSC Tagudin processes hundreds of applicants annually. Currently, it runs on manual spreadsheet encoding, visual ID verification, and disconnected paper rosters, presenting substantial data integrity and impersonation risks.
- **Log Simulation:** Warning console showing duplicate room schedules, untraced score modifications, and failed audit trail checks.

### Right Half — Core Vulnerability Cards
1. **Identity Verification Gaps:** Room check-in is purely visual. Impersonation risks are high without a digital link between the registered online profile and the physical examinee.
2. **Disconnected Data & No Audit:** Roster sheets exist in isolated silos. Scores can be modified in spreadsheets without access tracking or cryptographic constraints.

**Speaker Script:**
> "The College Admission Test is the entry gateway for all ISPSC students, yet the current manual process is highly vulnerable. Real-world proctoring relies on visual check-ins, allowing impersonation risks. Staff copy data between separate spreadsheets, and score changes happen without any log showing who made them or why. Our mock console logs represent these exact warnings: duplicate room bookings and untraced score edits. SecureCAT replaces this vulnerable, paper-heavy approach with an automated, secure pipeline."

**Cue:** Point to the warnings on the mock console log, then advance to Slide 3.

---

## Slide 3 — Proposed System & Component Map (90 sec)

**Layout:** Top row shows the 5-phase role-gated pipeline; bottom row shows the 5 curriculum compliance cards.

### Top — 5-Phase Gated Pipeline
- **P1: Apply** (Applicant role / Guest policy)
- **P2: Schedule** (Test Admin role / TestAdmin policy)
- **P3: Exam** (Proctor role / Proctor policy)
- **P4: Encode** (Registrar Admin role / Registrar policy)
- **P5: Release** (Counselor role / Counselor policy)

### Bottom — Curriculum Component Map
1. **Web (Laravel + Svelte):** Laravel 12 backend with Svelte 5 Inertia.js v2 SPA. Enforces policy gates server-side.
2. **Mobile (PWA Portal):** Responsive applicant portal optimized for mobile screens using Tailwind CSS v4.
3. **AI/ML (RAG Engine):** Mixedbread embeddings + confidence threshold to answer applicant queries without hallucination.
4. **IoT (QR Verification):** Cryptographically generated QR codes scanned at room entry points to record examinee attendance.
5. **Mapping (Venue Maps):** Leaflet.js mapping module routing applicants directly to their assigned examination rooms.

**Speaker Script:**
> "Here is our solution. We structure SecureCAT as a 5-phase pipeline, where every phase transition is strictly gated by role-based policy rules. Applicants apply, Test Admins schedule, Proctors check examinees in, Registrars encode grades, and Counselors write recommendations and release results. 
>
> To satisfy our curriculum constraints, we map these phases across five technical components: Laravel 12 and Svelte 5 for the Web app, a responsive PWA for Mobile, a hallucination-free RAG AI Companion for ML, QR code verification at the door for IoT, and Leaflet.js venue mapping for the Mapping component."

**Cue:** Trace the pipeline flow from left to right, then advance to the Live Demo on Slide 4.

---

## Slide 4 — Interactive Pipeline Simulation (Live Demo) (5 min 30 sec)

**Layout:** Four-quadrant interactive dashboard simulating the entire SecureCAT ecosystem.

### Quadrants
1. **Applicant Portal:** Displays applicant card (David Datu, Ref: SC-2026-981), registration status, QR code, and RAG AI Companion presets.
2. **Proctor Scanner Terminal:** Simulates a barcode scanner with a green swiping laser and check-in confirmation audio.
3. **Registrar & Counselor Panel:** Score input fields (Math, English, Science, Abstract) with locks and deliberate release trigger buttons.
4. **System Security Logs:** Console running real-time append-only security logs logging RBAC blocks and state updates.

**Demo Sequence:**
1. **Initialize:** Click "Start Mock Pipeline Demo" to trigger user registration in logs.
2. **RAG QA:** Ask AI Companion presets (e.g., "Passing Rate?") to display similarity score and context-grounded response.
3. **QR Check-in:** Scan the applicant QR code to watch state advance to `Examining` with a high-pitched scanner chime.
4. **Grading & Finalization:** Input mock scores, click "Finalize & Lock". Verify inputs become disabled. Attempting a simulated unauthorized edit displays an immediate red threat warning in the console.
5. **Deliberate Release:** Click "Counselor Release" to publish scores to the Applicant card.

**Speaker Script:**
> "We will now transition to the live demonstration. To show the interaction between these four distinct roles, we have built a self-contained, interactive multi-surface simulator directly on this slide. We can trace David Datu's application. We can query the AI Companion, scan the QR code to check him in, record and lock his scores, and trigger a counselor release. Let's step through this workflow now, and then look at the active web application."

**Cue:** Perform the simulation steps on-screen, then switch to the actual running Laravel application windows.

---

## Slide 5 — System Comparisons & Boundaries (60 sec)

**Layout:** Split column — left shows the comparison matrix; right details the scope boundaries.

### Left — Security Comparison Matrix
| Security Pillar | Manual Process | SecureCAT |
|-----------------|----------------|--------------|
| **Identity Verification** | None (Visual ID check) | Low-risk (QR-based scan) |
| **Score Modifications** | Vulnerable (Excel sheets) | Locked (DB constraint gate) |
| **Non-Repudiation Audit**| Zero event logs | Immutable (SQL write-once trigger) |
| **Applicant Support** | High office overhead | 24/7 RAG AI Companion |
| **Disclosure Control** | Immediate / Uncontrolled | Deliberate counselor release |

### Right — Scope Boundaries
- **In Scope:** Online/Walk-in review, scheduling & room assignment, QR check-in & score locking, counselor recommendations, hallucination-free RAG chat.
- **Out of Scope:** Online exam delivery (exams remain paper-based), fee collections, native App Store builds, automated enrollment decisions.

**Speaker Script:**
> "To validate the contribution of our system, we compare it against the manual process. SecureCAT addresses every security gap: QR codes replace simple visual checks, database-level locks replace vulnerable spreadsheets, and SQL triggers log every single modification. 
> 
> Furthermore, we establish strict scope boundaries. We handle the entire administrative workflow, but exam delivery itself remains paper-based, and payment processing is out of scope."

**Cue:** Gesture across the comparison columns to highlight the security enhancements, then advance to Slide 6.

---

## Slide 6 — Development Roadmap & Conclusion (30 sec)

**Layout:** Left side shows the development timeline; right side shows verification gates and final system metrics.

### Left — Development Roadmap
- **Timeline:** Phases 1–5 are fully completed, including database design, scheduling, QR check-in, score finalization triggers, and OpenRouter RAG integration.

### Right — Quality Verification Gates
- **PHPUnit Automated Tests:** 48 test cases verifying role-access blocks (403), sequential workflow state-guards, and edit-prevention database triggers.
- **User Acceptance Testing (UAT):** Target SUS score of $\ge 80$ evaluated with 30 key roles, demonstrating 100% role separation.

### Bottom — Conclusion & Metrics
- **4 Role Silos:** Absolute separation of access boundaries.
- **100% Audit Logs:** No untraced actions.
- **0% AI Hallucination:** Confidence-gated knowledge responses.

**Speaker Script:**
> "In conclusion, SecureCAT is fully built and verified. Our development roadmap is complete. We have verified the system through 48 automated PHPUnit test cases and manual UAT evaluations. The metrics speak for themselves: four distinct role silos, a 100% complete audit log, and a 0% hallucination rate for the AI Companion. SecureCAT proves that security and usability can be successfully co-engineered into academic workflows. Thank you, and we are open for your questions."

**Cue:** Conclude the presentation and invite panel questions.

