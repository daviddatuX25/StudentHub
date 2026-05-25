# SecureCAT: A Role-Based College Admission Testing System

**Capstone Project — ISPSC Tagudin · 2026**

**Group Members:**
- David Datu Sarmiento
- Christine Lopez

---

## 1. Introduction

### Background of the Study

The College Admission Test (CAT) is the gateway through which prospective students enter ISPSC Tagudin. Every applicant goes through it. The volume, the stakes, and the coordination demands make it one of the most operationally complex tasks in the Guidance and Registrar Offices.

Traditionally, this entire process runs on paper forms, manual scheduling across spreadsheets, and fragmented communication between applicants, proctors, and administrators. Lost forms, delayed results, and no single source of truth plague the workflow.

Current admission testing processes face several issues:
- Manual and paper-based application handling
- Weak access control and lack of role separation — anyone with the file can edit
- Risk of data tampering and unauthorized access
- Inaccurate identity verification during examinations — verified by eyeballing an ID
- Absence of audit trails for accountability — tampering goes unnoticed
- Delays in scoring and result release — applicants wait weeks with no updates

These problems compromise examination integrity, operational efficiency, and institutional credibility.

### Problem Statement

ISPSC Tagudin's College Admission Testing process suffers from three core problems:

1. **Manual exam proctoring** — It is error-prone, resource-intensive, and leaves no verifiable record of who was actually in that exam room. Identity is verified by visual inspection alone, with impersonation risk.

2. **Disconnected data management** — Staff manage applicant data across spreadsheets, email threads, and handwritten rosters. There is no unified view, and changes in one place are not reflected in others.

3. **Zero applicant support between submission and results** — Applicants are left waiting, guessing, and emailing the office for updates. There is no channel for self-service information.

These issues result in lost forms, delayed results, no accountability for changes, and a poor applicant experience.

### Objectives

**General Objective**

To develop SecureCAT — a role-based web application that streamlines the full College Admission Testing pipeline from registration through result release, grounded in Information Assurance and Security (IAS) principles.

**Specific Objectives**

1. Digitize applicant registration and automate exam scheduling with room assignment.
2. Enable real-time proctor attendance tracking and automate score computation.
3. Enforce role-based access control (RBAC) to secure applicant and examination data.
4. Implement QR-based identity verification on examination day.
5. Prevent data tampering through audit logging and verification mechanisms.
6. Deliver AI-powered applicant query support via the AI Companion.
7. Push real-time notifications for every status change.
8. Generate printable result sheets with counselor recommendations.

Each objective is implemented and testable.

---

## 2. Scope and Limitations

### What the System Covers

SecureCAT covers the full administrative CAT pipeline:

- Online and walk-in application management
- Exam scheduling and room assignment
- QR code generation and validation for exam entry
- Real-time proctor attendance tracking on exam day
- Score encoding and automated computation per aptitude area
- Result sheet generation with counselor consultation summaries
- Deliberate release management — the counselor controls when the applicant sees their result
- Role-based access control (4 roles with role-filtered views)
- Real-time notifications with two-tier sound system (toast + audio)
- AI Companion — RAG-grounded chat widget for applicant self-service
- Audit logging and activity tracking for non-repudiation
- Workflow state machine — Scheduled → Active → Completed transitions with state guards

### What the System Does NOT Cover

The following are deliberately excluded per the approved proposal:

- Online examination delivery — CAT at ISPSC is a physical paper exam; delivering it online requires a separate security and infrastructure review
- Payment processing
- Native mobile applications
- Advanced analytics and AI-based recommendations
- Physical exam materials handling
- Face-to-face interview coordination
- LMS functionality
- External API integrations
- Physical infrastructure management

### Target Users

Four user roles operate the system. Each role sees only what they need — nothing more.

| Role | Description |
|------|-------------|
| **Administrator** | Manages system configuration, approves applicants, configures schedules, releases results |
| **Test Administrator** | Manages exam sessions, assigns proctors and rooms, publishes sessions, has AI scheduling assistant |
| **Proctor** | Scans QR codes on exam day, marks attendance in real-time, runs exam-day workflow |
| **Applicant** | Submits application online, tracks status, views exam schedule and QR code, views results, chats with AI Companion |

---

## 3. System Demonstration

### Step-by-Step Walkthrough

#### Login

SecureCAT enforces role-based access from the first interaction. Each user logs in with their credentials and is directed to a role-specific dashboard.

- **Staff/Admin** accounts access the administrative backend with full visibility into applications, scheduling, grading, and audit logs.
- **Proctor** accounts access only the exam session roster for their assigned room.
- **Applicant** accounts access the portal — their personal status, schedule, QR code, results, and AI Companion.

<!-- INSERT IMAGE: Login page screenshot here -->

#### Dashboard

Each role sees a different dashboard tailored to their responsibilities:

- **Admin Dashboard** — KPI cards showing application counts, active sessions, pending grades, and released results. Full navigation sidebar for all administrative functions.
- **Test Admin Dashboard** — Exam session overview at different lifecycle stages (Scheduled, Active, Completed, Finalized). Room and proctor assignment controls.
- **Proctor Dashboard** — Current session roster with attendance status. QR scanner interface.
- **Applicant Portal** — Application status tracker, exam schedule with QR code, result card with counselor recommendations.

<!-- INSERT IMAGE: Admin dashboard screenshot here -->
<!-- INSERT IMAGE: Applicant portal dashboard screenshot here -->

#### Key Features

**1. Application Lifecycle**

Applicants submit through a public form — no login required. Staff reviews each application digitally, accepts or dismisses with documented reasons. On acceptance, a portal account is auto-created and a setup email is triggered. The applicant can then log in to track their status.

<!-- INSERT IMAGE: Public application form screenshot here -->
<!-- INSERT IMAGE: Staff application review screenshot here -->

**2. Exam Session Workflow**

Test Administrators create exam sessions, assign rooms, proctors, and examinees. Sessions follow a state machine: Scheduled → Active → Completed → Finalized. Each transition is guarded — sessions cannot skip states. Once finalized, no further score edits are allowed.

<!-- INSERT IMAGE: Exam session management screenshot here -->

**3. QR-Based Identity Verification**

Each applicant receives a unique QR code tied to their assignment. On exam day, the proctor scans the QR at the door — the system verifies identity before marking them present. This eliminates impersonation risk.

<!-- INSERT IMAGE: Applicant QR code screenshot here -->
<!-- INSERT IMAGE: Proctor scanning interface screenshot here -->

**4. Real-Time Proctor Attendance**

The proctor marks attendance live during the exam. No paper roster. The system is the single source of truth for who entered the room. Absent and present statuses are recorded in real-time.

<!-- INSERT IMAGE: Proctor attendance roster screenshot here -->

**5. Grading and Score Finalization**

The Registrar Administrator encodes scores per aptitude area (six domains: SA, NA, VR, AR, LR, PSA). Finalization locks the session permanently — no further edits. Every score change before finalization is logged in the audit trail.

<!-- INSERT IMAGE: Grading interface screenshot here -->

**6. Result Release with Counselor Recommendations**

Release is deliberate, not automatic. The counselor reviews scores, writes a course recommendation and comments, then releases. The applicant sees their result immediately upon release — no office visit required.

<!-- INSERT IMAGE: Release management screenshot here -->
<!-- INSERT IMAGE: Applicant result view screenshot here -->

**7. AI Companion**

A RAG-grounded chat widget available to applicants in the portal. It answers ISPSC-specific questions about courses, admission policies, and exam procedures from a curated knowledge base. It cannot hallucinate information it was not given.

<!-- INSERT IMAGE: AI Companion chat screenshot here -->

**8. Audit Trail**

Every critical action is logged — application accepted, session finalized, scores entered, result released. No action in SecureCAT is anonymous. Immutable history for non-repudiation.

<!-- INSERT IMAGE: Audit log screenshot here -->

**9. Real-Time Notifications**

Status changes trigger toast notifications with a two-tier sound system (chime for informational, alert for urgent). Notifications are role-filtered and accessible from a mobile-friendly dropdown.

<!-- INSERT IMAGE: Notification interface screenshot here -->

### Live Demo

<!-- INSERT PPT IMAGES FOR LIVE DEMO SECTION BELOW -->

*The live demonstration walks through the complete end-to-end lifecycle of the system:*

**Act 1 — Application Submission** (2 min)
- Public home page → application form
- Live applicant fills and submits
- Reference number assigned, status: Pending

<!-- INSERT IMAGE: Demo Act 1 screenshot here -->

**Act 2 — Staff Review & Acceptance** (3 min)
- Staff reviews pending applications
- Accepts the applicant → portal account auto-created
- Setup email triggered → applicant sets password
- Applicant logs into portal, sees: "Awaiting Exam Scheduling"

<!-- INSERT IMAGE: Demo Act 2 screenshot here -->

**Act 3 — Exam Session Scheduling** (2 min)
- Test Admin views sessions at different lifecycle stages
- Assigns examinees to upcoming session
- Applicants see their schedule in the portal immediately

<!-- INSERT IMAGE: Demo Act 3 screenshot here -->

**Act 4 — Proctor Marks Attendance** (2.5 min)
- Session is today — proctor opens the roster
- Marks applicants Present or Absent in real-time
- QR verification at the door confirms identity

<!-- INSERT IMAGE: Demo Act 4 screenshot here -->

**Act 5 — Registrar Grades Scores** (3.5 min)
- Scores entered per aptitude area (6 domains)
- Finalization locks the session — no further edits
- Every pre-finalization change is logged

<!-- INSERT IMAGE: Demo Act 5 screenshot here -->

**Act 6 — Result Release** (3 min)
- Counselor writes recommendation and comments
- Clicks Release — applicant sees result immediately
- No premature disclosure; counselor controls the moment

<!-- INSERT IMAGE: Demo Act 6 screenshot here -->

**Act 7 — Audit Log** (1 min)
- Every action performed is recorded
- Application accepted, session finalized, scores entered, result released
- Non-repudiation by design

<!-- INSERT IMAGE: Demo Act 7 screenshot here -->

---

*That is SecureCAT end-to-end — from application to result release. One system, four roles, designed with security and accountability built in from the start.*
