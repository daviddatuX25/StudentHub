# SecureCAT — System Defense Speaker Notes (6-Slide Structure)

**File map:**
- These notes $\to$ `presentation-securecat.html` (6 slides with interactive simulator)
- Live demo script $\to$ `Demo-template.md` (Acts 1–9)

**Total time budget: ~10 minutes**
> Slide 1: Title & Registry · 0:20
> Slide 2: Context & The Problem · 1:30
> Slide 3: Proposed System & Component Map · 1:30
> Slide 4: Interactive Pipeline Simulation (Demo Transition) · 5:30 (including live app hand-off)
> Slide 5: System Comparisons & Boundaries · 0:45
> Slide 6: Development Roadmap & Conclusion · 0:25

---

## Slide 1 — Title & Registry · ⏱ 0:00–0:20

**Visual Cue:** Slide 1 displays the glowing green **SC** shield logo and the registry code `BSIT-CAP4-2026-SC-V2`.

**Verbal Script:**
> "Good morning, members of the panel. I am David Datu Sarmiento, and with me is Christine Lopez. We present **SecureCAT** — a Role-Based College Admission Testing System designed specifically for the Guidance and Registrar Offices here at ISPSC Tagudin. 
> 
> Our research focuses on how information assurance and security principles can be co-engineered into academic workflows. We address the systemic vulnerabilities of manual systems by implementing strict role-based access control, state-guarded workflows, and immutable audit logging."

**Action Cue:** Press `Space` or `ArrowRight` to advance on the word *"audit logging"*.

---

## Slide 2 — Context & The Problem · ⏱ 0:20–1:50

**Visual Cue:** Slide 2 displays the split view: a warning console log showing Excel errors on the left, and the two vulnerability cards on the right.

**Verbal Script:**
> "Let us look at the institutional context. Every year, hundreds of applicants pass through the Guidance and Registrar Offices for the College Admission Test. Under the current manual process, scheduling relies on spreadsheets, and exam room check-ins are verified by eyeballing an ID, creating impersonation risks. Furthermore, when scores are recorded, there is no audit trail showing who entered them.
> 
> As you can see in the simulated console log on the left, manual spreadsheets easily lead to overwritten schedules and untraced score modifications. SecureCAT addresses these vulnerabilities directly through digital identity check-in, isolated role boundaries, and permanent audit trails."

**Action Cue:** Gesture toward the warning logs, then advance to Slide 3.

---

## Slide 3 — Proposed System & Component Map · ⏱ 1:50–3:20

**Visual Cue:** Slide 3 shows the horizontal 5-phase gated pipeline on top, and the five compliance cards (Web, Mobile, AI/ML, IoT, Mapping) at the bottom.

**Verbal Script:**
> "To address these vulnerabilities, we design SecureCAT around a 5-phase role-gated pipeline. An applicant applies, a Test Admin schedules, a Proctor checks examinees in, a Registrar encodes, and a Counselor reviews and releases results. No role can perform actions outside their designated policy gate.
> 
> At the bottom, we map our implementation to the five capstone curriculum components. The Web application is built on Laravel 12 and Svelte 5. Mobile is covered by a responsive PWA. For AI/ML, we use a hallucination-free RAG AI Companion. For IoT, we integrate QR-based exam room verification. For Mapping, we use Leaflet.js to route examinees to their assigned rooms."

**Action Cue:** Point to the policy gate labels between the pipeline phases, then advance to Slide 4.

---

## Slide 4 — Interactive Pipeline Simulation (Live Demo) · ⏱ 3:20–8:50

**Visual Cue:** Slide 4 displays the interactive multi-surface simulator.

**Verbal Script:**
> "Before we switch to the active web browser windows, let us demonstrate the system's operational flow using this interactive simulator on the slide.
> 
> First, let's start the mock pipeline. The system registers David Datu. He can click these AI Companion presets to ask questions, returning context-grounded responses. On exam day, the proctor clicks 'Scan QR Code'. The laser scans, and David's status changes to Examining. After the exam, we input his scores. When we click 'Finalize and Lock', the score inputs disable. If an attacker attempts to modify them, Settle-level database triggers block it and log an immediate threat warning in the console. Finally, the counselor clicks 'Counselor Release' to publish the scores to the applicant portal.
> 
> Now, we will hand off from the slides to show you these exact screens in our running Laravel application."

**Action Cue:** Run the interactive simulator clicks on Slide 4, then switch to the browser window tabs for the actual live demonstration. Walk through Acts 1–9 from `Demo-template.md`. Once the live demo is complete, return to the slide presentation and advance to Slide 5.

---

## Slide 5 — System Comparisons & Boundaries · ⏱ 8:50–9:35

**Visual Cue:** Slide 5 displays the security comparison matrix table on the left, and the In-Scope/Out-of-Scope lists on the right.

**Verbal Script:**
> "Now that we have seen the running system, let us evaluate its security contributions. SecureCAT replaces visual ID checks with low-risk QR checks, and vulnerable spreadsheets with database-locked scores. It ensures non-repudiation with SQL write-once triggers, and replaces high office overhead with the RAG AI Companion.
> 
> To maintain project feasibility, we enforce clear boundaries: our scope covers the full administrative CAT lifecycle, while online exam delivery and payment processing are explicitly out of scope."

**Action Cue:** Point out the matrix comparison highlights, then advance to Slide 6.

---

## Slide 6 — Development Roadmap & Conclusion · ⏱ 9:35–10:00

**Visual Cue:** Slide 6 shows the completed roadmap milestones on the left, the automated and manual testing gates on the right, and the concluding system metrics at the bottom.

**Verbal Script:**
> "All five development phases are completed. We verified system reliability through 48 automated PHPUnit test cases covering role access and workflow transitions, alongside manual user acceptance testing.
> 
> Our system achieves three final metrics: four distinct role silos, a 100% complete audit log, and a 0% hallucination rate. SecureCAT proves that institutional security and usability can be co-engineered successfully. Thank you, and we welcome your questions."

**Action Cue:** End the slideshow and open the floor to the panel Q&A.

