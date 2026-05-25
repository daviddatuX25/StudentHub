# SECURECAT
## A Role-Based College Admission Testing System for the Guidance and Registrar Offices at ISPSC Tagudin

---

**Group Members:**
- David Datu Sarmiento
- Christine Lopez

---

## 1. Introduction

### 1.1 Background of the Study

The College Admission Test (CAT) is the gateway through which prospective students enter ISPSC Tagudin. Every applicant goes through it. The volume, the stakes, and the coordination demands make it one of the most operationally complex tasks handled by the Guidance and Registrar Offices.

Traditionally, the entire CAT process runs on paper forms, manual scheduling across spreadsheets, and fragmented communication between applicants, proctors, and administrators. Lost forms, delayed results, and no single source of truth have long plagued the office. Staff manage applicant data across disconnected systems — spreadsheets, email threads, and handwritten rosters — with no unified view.

SecureCAT (Secure College Admission Testing) digitizes the entire pipeline: from the moment an applicant submits their form online, through exam scheduling, real-time proctoring, score entry, and result release. The system integrates Information Assurance and Security (IAS) principles to ensure confidentiality, integrity, availability, accountability, and non-repudiation of examination data. It modernizes traditional manual and paper-based admission testing processes by automating workflows, improving efficiency, and strengthening security controls within the institution.

### 1.2 Problem Statement

Current college admission testing processes face several critical issues:

1. **Manual and error-prone exam proctoring.** Paper-based attendance tracking is resource-intensive, leaves no verifiable record of who was actually in the exam room, and is susceptible to human error.

2. **Disconnected data management.** Staff manage applicant data across scattered spreadsheets, email threads, and handwritten rosters. There is no unified view, leading to lost forms, delayed results, and inconsistent records.

3. **Weak access control and lack of role separation.** Without proper role-based access control, unauthorized users may view or modify sensitive examination data, compromising data integrity.

4. **Risk of data tampering and absence of audit trails.** Without verification mechanisms and activity logging, there is no accountability for changes made to scores, statuses, or records.

5. **No intelligent support for applicant queries.** Between application submission and result release, applicants are left waiting and guessing, often emailing the office for updates — overloading staff with repetitive inquiries.

6. **Delays in scoring and result release.** Manual score computation and result generation introduce unnecessary turnaround time, reducing institutional responsiveness.

These problems compromise examination integrity, operational efficiency, and institutional credibility.

### 1.3 Objectives

#### General Objective

To develop SecureCAT — a role-based web application that streamlines the College Admission Test process at ISPSC Tagudin from applicant registration through exam scheduling, proctoring, scoring, and result release, grounded in Information Assurance and Security principles.

#### Specific Objectives

1. **Digitize applicant registration and application management** — Replace paper-based application intake with an online submission portal, enabling applicants to submit their data and course preferences digitally.

2. **Implement automated exam scheduling with room assignment** — Enable administrators to create exam sessions, assign rooms and proctors, and assign applicants to sessions without manual coordination.

3. **Enable real-time proctor attendance tracking** — Equip proctors with a live digital roster where they mark attendance in real-time on exam day, replacing paper-based roll calls.

4. **Automate score computation and result sheet generation** — Allow registrar administrators to input scores per aptitude area and generate result sheets automatically, eliminating manual computation errors.

5. **Provide role-based access control for all user types** — Enforce strict role-based permissions so each user (Registrar Administrator, Test Administrator, Proctor, Applicant) sees only what their role requires — nothing more.

6. **Deliver AI-powered applicant query support via AI Companion** — Provide a RAG-grounded AI chat widget that answers applicant questions from a curated ISPSC-specific knowledge base, offering 24/7 support without overloading office staff.

7. **Send real-time notifications for exam events and status updates** — Push email and in-app notifications for every status change — application acceptance, schedule assignment, score processing, and result release.

8. **Generate printable result sheets with counselor recommendations** — Enable counselors to write consultation summaries with recommended courses and release them deliberately to applicants, ensuring no premature disclosure.

---

## 2. Scope and Limitations

### 2.1 What the System Covers

The system covers the full administrative CAT pipeline:

- Online and walk-in application management (data intake, acceptance workflow, admission slip generation with QR code)
- Exam scheduling and room assignment (session creation, proctor assignment, applicant assignment, schedule publication)
- Proctor attendance tracking (real-time digital roster, attendance marking, session control)
- Score grading and result sheet generation (manual score input per aptitude area, session finalization, automated computation)
- AI Companion for applicant queries (RAG-grounded chat widget using ISPSC-specific knowledge base)
- Role-based access control (four distinct roles with policy-based authorization and route-level gates)
- Real-time notifications (email and in-app alerts for all status changes)
- Audit logging and activity tracking (non-repudiation — every action is recorded)
- Consultation summary release (counselor reviews scores, writes recommendations, and controls the moment of release)
- Applicant portal (self-service dashboard with status tracker, exam schedule view, result access, and AI Companion)

### 2.2 What the System Does Not Cover

The following are deliberately excluded from the approved scope:

- Physical exam materials handling (printing, distributing, and collecting exam papers)
- Face-to-face interview coordination
- Learning management system (LMS) functionality
- External API integrations (SIS, counseling systems)
- Payment processing
- Physical exam center infrastructure
- Online examination delivery (CAT at ISPSC is a physical paper-based exam; delivering it online requires a separate security and infrastructure review)
- Native mobile applications
- OMR auto-scoring (manual score input is the current approach; normalization engine deferred)
- QR code scanning for attendance (admission slip includes QR, but scanning is deferred; manual search is the MVP)

### 2.3 Target Users

SecureCAT serves four primary user roles, each with a role-filtered view of the system:

| Role | Description |
|------|-------------|
| **Registrar Administrator** | Encodes scores per aptitude area, finalizes grading sessions, writes consultation summaries, and releases results to applicants |
| **Test Administrator** | Creates and manages exam sessions, assigns rooms and proctors, assigns applicants to sessions, and publishes schedules |
| **Proctor** | Views assigned room roster, marks attendance in real-time on exam day, and logs exam submissions |
| **Applicant** | Submits applications online, tracks status through the portal, views exam schedules and QR code, accesses released results, and chats with the AI Companion |

Additionally, **Staff** review and process applications (accept or dismiss), and a **Super Admin** manages system configuration and user accounts.

---

## 3. System Demonstration

### 3.1 Step-by-Step Walkthrough

The following demonstrates the complete end-to-end lifecycle of SecureCAT — from application submission through result release.

---

#### Step 1: Login

**Staff/Admin Login:**
Staff and administrators log in through the secure authentication portal using their institutional email and password. Each role is directed to their role-specific dashboard upon login.

*[Insert PPT screenshot of staff/admin login page]*

**Applicant Portal Login:**
Applicants receive a setup email after their application is accepted. They set their password through a secure one-time link and then log in to the Applicant Portal.

*[Insert PPT screenshot of applicant login page]*

---

#### Step 2: Dashboard

**Registrar Administrator Dashboard:**
Displays grading sessions at various lifecycle stages (upcoming, in progress, finalized), pending consultation summaries, and quick-access to score entry.

*[Insert PPT screenshot of registrar dashboard]*

**Test Administrator Dashboard:**
Shows exam sessions with their current status (upcoming, active, completed), scheduling tools, and applicant assignment capabilities.

*[Insert PPT screenshot of test admin dashboard]*

**Proctor Dashboard:**
Displays the assigned exam session roster with examinee list, attendance status counters (present/absent/total), and real-time session controls.

*[Insert PPT screenshot of proctor dashboard]*

**Applicant Portal Dashboard:**
Shows the applicant's process status tracker (all stages from application to result release), exam schedule with countdown, and notification inbox.

*[Insert PPT screenshot of applicant portal dashboard]*

---

#### Step 3: Key Features

**Feature 1 — Application Submission & Acceptance:**

An applicant submits their application form online with personal data and three ranked course preferences. The system assigns a reference number immediately. Status is set to "pending" — no portal account exists yet.

Staff reviews the application in the staff dashboard, verifies documents, and clicks Accept. The moment the application is accepted:
- A portal account is auto-created for the applicant
- A setup email is triggered and sent to the applicant
- The applicant can now set their password and access the portal

*[Insert PPT screenshot of application form and staff review]*

---

**Feature 2 — Exam Scheduling & Room Assignment:**

The Test Administrator creates exam sessions by specifying date, time, room, and proctor. Accepted applicants are assigned to sessions. Once published, assigned applicants see their exam schedule in the portal — no separate notification needed.

The AI Scheduling Assistant provides context-aware support — it knows room capacities, current examinee loads, and unassigned applicants, helping administrators plan across multiple sessions.

*[Insert PPT screenshot of exam scheduling interface]*

---

**Feature 3 — Real-Time Proctor Attendance Tracking:**

On exam day, the assigned proctor opens the digital roster. They mark each applicant as Present or Absent in real-time. No paper roster needed — the system is the single source of truth for who entered the exam room.

In a real deployment, the proctor can also scan each applicant's QR code at the door for identity verification before marking them present.

*[Insert PPT screenshot of proctor attendance tracking]*

---

**Feature 4 — Score Grading & Session Finalization:**

After the exam, the Registrar Administrator opens the grading session. Scores are entered per applicant across six aptitude areas (SA, NA, VR, AR, LR, PSA). Once all scores are entered, the administrator finalizes the grading session.

Finalization locks the session — no further score edits are allowed. Every pre-finalization change is logged in the audit trail, ensuring accountability and non-repudiation.

*[Insert PPT screenshot of grading interface with score entry]*

---

**Feature 5 — Consultation Summary Release:**

The counselor reviews the finalized scores, writes a recommendation (suggested course and comments), and then explicitly releases the consultation summary to the applicant.

Release is deliberate, not automatic. The counselor controls the moment the applicant sees their result, preventing premature disclosure. Upon release, the applicant receives a notification and can immediately view their scores, recommended course, and counselor comments in the portal.

*[Insert PPT screenshot of consultation release and applicant result view]*

---

**Feature 6 — AI Companion:**

The AI Companion is a chat widget available to applicants in the portal. It is RAG-grounded — it only answers from a curated ISPSC-specific knowledge base. It cannot hallucinate admission policies it was not given.

Applicants can ask questions like "What does BSIT involve?" or "When is the next exam schedule?" and receive localized, accurate answers 24/7 without overloading the office staff.

*[Insert PPT screenshot of AI Companion chat interface]*

---

**Feature 7 — Real-Time Notifications:**

The system pushes email and in-app notifications at every critical status change:
- Application accepted
- Exam schedule assigned
- Score processing started
- Result released
- Exam day reminder (T-1 day)

*[Insert PPT screenshot of notification examples]*

---

**Feature 8 — Audit Log:**

Every action performed in SecureCAT is recorded in the audit log: application accepted, session finalized, scores entered, result released. No action is anonymous. This ensures non-repudiation and full accountability.

*[Insert PPT screenshot of audit log interface]*

---

### 3.2 Live Demo

*[Insert PPT slide images here for the live demo walkthrough]*

The live demo covers the complete end-to-end lifecycle:

1. **Application Lifecycle** — A live applicant submits their application; staff reviews and accepts it; the portal account is auto-created and a setup email is triggered.

2. **Exam Administration** — Test Admin schedules a session, assigns the proctor and room, and publishes it.

3. **Live Proctoring** — The proctor marks attendance in real-time on exam day.

4. **Grading and Release** — The registrar enters scores per aptitude area, finalizes the session, writes consultation summaries, and releases results. The applicant sees them immediately.

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Laravel 12, PHP 8.2+ |
| Database | MySQL 8.0+ |
| Frontend | Inertia.js v2 + Svelte 5 |
| Styling | TailwindCSS 4.x |
| Authorization | Laravel Policies + Route-level Gates (RBAC) |
| AI Companion | Mixedbread (RAG embeddings) + OpenRouter (multi-model LLM routing) |
| Notifications | Laravel Queue + Email (SMTP/SES) + In-app Alerts |
| Development | Claude Code with GSD Workflow (AI-assisted development) |
| Persistence | MySQL with migrations, seeders, and demo dataset |

---

*SecureCAT — One system, four roles, designed with security and accountability built in from the start.*
