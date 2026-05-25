**IAS**

**SecureCAT**

System Architecture & Developer Reference

*Computerized Admission & Testing System*

| Document Type | System Architecture Reference |
| --- | --- |
| Version | 2.0 — Rev 2 |
| Status | Draft — For Development Expansion |
| Classification | Internal — Technical |
| Date | 2026 |
| Owner | IAS Development Team |

**CONFIDENTIAL — INTERNAL USE ONLY**

# Revision History

| Version | Date | Author | Description |
| --- | --- | --- | --- |
| 1.0 | 2026 | IAS Team | Initial architecture — 5 core phases |
| 2.0 | 2026 | IAS Team | Added Applicant Portal, Notification Engine, Auth flow |
| - | 2026 | IAS Team | Answered the Open Question and Design Decisions |

# Table of Contents

# 1. Executive Summary

SecureCAT is the Computerized Admission and Testing system created as part of the IAS (Information Assurance and Security) academic project. It digitizes and coordinates the full lifecycle of student admission — from initial application through to examination, grading, and counselor-guided course consultation — across two institutional offices: the Registrar and the Guidance and Registrar Offices.

This document serves as the canonical technical reference for system architects and developers. It defines the system boundary, component interfaces, data flows, actor roles, and non-functional requirements. Sections are structured to support incremental elaboration: each module is described at the architectural level with placeholder subsections for detailed design during implementation.

| Key Design Constraints The system spans two organizational units with separate staff roles and responsibilities. Applicants are external actors with limited, controlled access via a web portal. All applicant-visible data is gated through explicit staff or counselor release actions. The system must support both on-the-spot and pre-booked application workflows. |
| --- |

# 2. System Overview

## 2.1 System Boundary

SecureCAT is a standalone admission pipeline system created for the IAS academic project. It does not replace or replicate the existing institutional SIS (Student Information System) or the dedicated Counseling System used by the Guidance and Registrar Offices. Integration points with those systems are noted where relevant.

| Attribute | Value |
| --- | --- |
| System Name | SecureCAT |
| Academic Project | IAS (Information Assurance and Security) — the academic subject that prompted the creation of SecureCAT |
| Version Documented | 2.0 |
| Primary Language | [TBD by implementation team] |
| Deployment Target | [TBD — on-premise / cloud] |
| Access Model | Role-based, web-based interfaces + applicant web portal |
| Authentication | Staff: institutional SSO / Admin accounts. Applicants: email + password, OTP fallback |
| Data Residency | [TBD — institutional data governance policy applies] |

## 2.2 Organizational Units

SecureCAT is operated across two offices with distinct responsibilities:

| Office | Phases Owned | Primary Actors | Notes |
| --- | --- | --- | --- |
| Registrar Office | Phase 1 (Application), Phase 2 (Scheduling) | Staff, Admin | Manages applicant intake and exam logistics |
| Guidance and Registrar Offices | Phase 3 (Examination), Phase 4 (Grading), Phase 5 (Consultation) | Proctor, Grader, Counselor | Manages exam execution and result counseling |

## 2.3 High-Level Component Map

The system is composed of five sequential core phases plus two cross-cutting subsystems:

| Component | Type | Color Code | Owned By |
| --- | --- | --- | --- |
| Application Interface | Core Phase 1 | #C8401A | Registrar |
| Scheduling Interface | Core Phase 2 | #1A5FC8 | Registrar |
| Examination Interface | Core Phase 3 | #1A9C55 | Guidance |
| Grading Interface | Core Phase 4 | #8B2AC8 | Guidance |
| Consultation & Analytics Interface | Core Phase 5 | #C87A1A | Guidance |
| Applicant Portal | Cross-cutting | #0D7C7C | System-wide |
| Notification Engine | Cross-cutting | #B5860D | System-wide |

# 3. Actors & Roles

Six distinct actor roles interact with SecureCAT. Each role is mapped to a specific organizational unit and has access only to the interfaces relevant to their function.

| Actor | Office | Interface(s) | Responsibilities |
| --- | --- | --- | --- |
| Applicant | External | Application Interface, Exam Interface, Applicant Portal | Submits application, takes examination, views portal for schedule, status, and consultation summary |
| Staff | Registrar Office | Application Interface | Processes and validates applications, issues admission receipts, triggers account provisioning on acceptance |
| Admin | Registrar Office | Scheduling Interface | Configures exam schedule using AI assistant, assigns rooms and proctors, sets score release countdown date, resets applicant portal accounts |
| Proctor | Guidance and Registrar Offices | Examination Interface | Monitors exam session in real-time, logs attendance and submission events |
| Grader | Guidance and Registrar Offices | Grading Interface | Inputs scores via OMR or manual entry, applies normalization, triggers processing notification |
| Counselor | Guidance and Registrar Offices | Consultation & Analytics Interface | Reviews heatmaps and decision support output, overrides auto-recommendations, adds written comments, explicitly releases consultation summary to applicant |

| Note on Role Boundaries Registrar Staff and Admin are separate roles — Staff handles per-applicant processing; Admin handles scheduling configuration and system settings. Guidance Proctor, Grader, and Counselor may be the same physical person but are distinct roles within the system. Applicants are never given access to staff-facing interfaces. |
| --- |

# 4. Core Phase Specifications

Each phase is described with its interface, inputs, outputs, actors, features, and the specific problems it addresses. Each phase subsection includes a [Developer Notes] block for implementation-time elaboration.

| P1 | PHASE 1 — Appointment & Application |
| --- | --- |

| Interface | Application Interface |
| --- | --- |
| Location | Registrar Office (on-site + web) |
| Actors | Applicant (submitter), Staff (processor) |
| Input Data | Applicant personal data, courses offered, application date windows |
| Output | Admission Receipt (document + digital record); Account Provisioning trigger |
| Office Owner | Registrar |

### 4.1.1 Features

Appointment Booking

Applicants schedule a visit slot to prevent crowding and long wait times.

On-the-Spot Application

Walk-in application capture without pre-booking, for flexibility.

Application Lookup

Staff can search and retrieve any application by reference number, name, or date.

Account Provisioning on Acceptance

When staff marks an application as accepted, the system auto-creates an applicant portal account linked to the email provided. No password is set at this stage — a setup email is dispatched.

### 4.1.2 Problems Addressed

**Long wait times and crowding** at the registrar counter during peak admission periods.

**No-show appointments** reducing throughput efficiency.

**Fragmented paper-based records** making lookup and audit difficult.

**Manual account creation** delay between acceptance and portal access.

| Developer Notes — Phase 1 [Expand During Implementation] Define applicant data schema: required fields, optional fields, file attachments (e.g., ID scans). Specify appointment booking logic: slot duration, max per day, overbooking rules. Define acceptance workflow: who can accept, approval levels, rejection handling. Account provisioning: token expiry window for setup email, password policy, OTP flow. Admission receipt format: PDF generation spec, fields to include, digital signature/QR code. |
| --- |

| P2 | PHASE 2 — Exam Scheduling |
| --- | --- |

| Interface | Scheduling Interface |
| --- | --- |
| Location | Registrar Office (admin-only) |
| Actors | Admin |
| Input Data | Available rooms (capacity, location), available proctors, applicant list from Phase 1, datetime windows |
| Output | Finalized and published exam schedule; score release target date |
| Office Owner | Registrar |

### 4.2.1 Features

AI Schedule Management Assistance

AI-assisted schedule generation that resolves room conflicts, matches room capacity to applicant count, and distributes proctors efficiently across sessions.

Room-Capacity Matching

Prevents over-assignment by checking room capacity against registered applicant count per session.

Proctor Allocation

Assigns proctors to rooms, checking for conflicts and ensuring minimum coverage per room.

Score Release Date Setting

Admin sets the target score release date, which is surfaced as a live countdown in the Applicant Portal.

Schedule Publication & Notification Trigger

Publishing the schedule auto-triggers the Notification Engine to dispatch schedule assignment notifications to all affected applicants.

### 4.2.2 Problems Addressed

**Room/venue conflicts** from manual double-booking.

**Capacity mismatches** where rooms are assigned more applicants than they can accommodate.

**Inefficient manual proctor allocation** creating over- or under-staffed sessions.

| Developer Notes — Phase 2 [Expand During Implementation] Define AI assistant scope: rule-based constraint solver vs. ML model vs. hybrid. Room entity schema: id, name, building, floor, capacity, facilities (projector, AC, etc.). Proctor assignment rules: max rooms per proctor, minimum proctor-to-applicant ratio. Schedule publication state machine: Draft → Review → Published. Define rollback/edit policy: can a published schedule be edited after notifications are sent? Score release date: how is it stored, who can change it, what happens if changed after countdown started? |
| --- |

| P3 | PHASE 3 — Examination |
| --- | --- |

| Interface | Examination Interface |
| --- | --- |
| Location | Exam venue (on-site, per assigned room) |
| Actors | Proctor (monitor), Applicant (examinee) |
| Input Data | Published schedule, applicant roster per room |
| Output | Timestamped attendance records, submission logs, real-time session state |
| Office Owner | Guidance and Registrar Offices |

### 4.3.1 Features

Attendance Logging

Proctor marks attendance per applicant at session start. Timestamps are recorded and immutable.

Submission Logging

Proctor logs each exam paper submission (per applicant, timestamped, with proctor signature/confirmation). Generates a verifiable submission record.

Real-Time Session Monitoring

Session status visible to authorized supervisors: how many present, how many submitted, session elapsed time.

### 4.3.2 Problems Addressed

**Disputed submissions**: timestamped, proctor-confirmed records provide evidence in case of disputes.

**Proxy examinees**: attendance logging tied to admission receipt and identity verification.

**Inaccurate manual attendance** sheets that are error-prone and hard to audit.

**No real-time visibility** into session progress for supervisors.

| Developer Notes — Phase 3 [Expand During Implementation] Define identity verification method at attendance: QR code scan, manual ID check, biometric (future). Specify submission log schema: applicant_id, proctor_id, timestamp, paper_id, status. Define what "real-time monitoring" means technically: polling interval, websocket, or SSE. Clarify session state machine: Not Started → In Progress → Submission Phase → Closed. Data retention policy for attendance/submission records (used in dispute resolution). |
| --- |

| P4 | PHASE 4 — Marking & Grading |
| --- | --- |

| Interface | Grading Interface |
| --- | --- |
| Location | Guidance and Registrar Offices |
| Actors | Grader |
| Input Data | Submission records from Phase 3, answer keys, scoring rubrics |
| Output | Normalized/converted scores per applicant, graded results record |
| Office Owner | Guidance and Registrar Offices |

### 4.4.1 Features

Auto OMR Input (Beta)

Optical Mark Recognition for scanning multiple-choice answer sheets. Flagged as Beta — results must be reviewed before finalization.

Manual Grade Input Interface

Fallback and override interface for graders to input or correct scores manually per applicant.

Score Normalization / Conversion

Configurable normalization rules to convert raw scores to standard scales (e.g., percentile, T-score, or program-specific cutoffs).

Processing Notification Trigger

Starting a grading session auto-triggers a notification to applicants that scores are being processed.

### 4.4.2 Problems Addressed

**Excessive manual workload** from paper-based marking at scale.

**Scoring inconsistency and human error** in manual tabulation.

**Long result wait times** due to sequential, manual grading workflows.

**Fragmented record-keeping**: scores stored digitally alongside submission evidence.

| Developer Notes — Phase 4 [Expand During Implementation] OMR integration spec: scanner hardware requirements, image format, confidence threshold for auto-reject. Define normalization rule engine: who configures rules, per-program rules vs. global, versioning. Grading session state machine: Open → In Progress → Review → Finalized. Audit trail: every score change logged with grader ID, timestamp, before/after values. OMR Beta policy: what percentage error rate is acceptable before requiring full manual review? |
| --- |

| P5 | PHASE 5 — Results & Consultation |
| --- | --- |

| Interface | Consultation & Analytics Interface |
| --- | --- |
| Location | Guidance and Registrar Offices / Covered Court (consultation sessions) |
| Actors | Counselor (release), Applicant (recipient) |
| Input Data | Graded results from Phase 4, historical enrollment data, course quota data |
| Output | Released Consultation Summary (status + counselor comments + recommended course(s)) |
| Office Owner | Guidance and Registrar Offices |

### 4.5.1 Features

Real-Time Course Distribution Heatmap

Visual representation of how applicants are distributed across courses based on current scores and preferences. Highlights courses nearing quota or dangerously under-enrolled.

Decision Support

System-generated course recommendation per applicant based on score profile and current course vacancy. Counselor can override the recommendation before release.

Score Data & Statistics per Course

Per-course score distribution, pass rates, and applicant count summaries to support counselor decision-making.

Counselor Override & Comment

Counselor can modify the auto-generated recommendation and append written notes before releasing to the applicant.

Gated Release to Applicant

Nothing is visible to the applicant until the counselor explicitly triggers a release. Release auto-fires a notification (email + in-app).

### 4.5.2 Problems Addressed

**No historical benchmarking**: counselors lack context on how similar applicant profiles have performed in specific programs historically.

**No big-picture enrollment context**: no real-time view of which departments are nearing quota or under-enrolled.

**Subjective course placement** without data to support the counselor's recommendation.

| Developer Notes — Phase 5 [Expand During Implementation] Decision support algorithm: rules-based (score thresholds) vs. ML model — define scope for v1. Heatmap data model: course_id, enrolled_count, quota, applicant_score_distribution. Counselor release workflow: Draft → Counselor Review → Override/Comment → Released. What does "release" do atomically? Update applicant record + trigger notification + log counselor ID + timestamp. Historical data source: where does past enrollment/performance data come from? Manual import, SIS integration? Define what the applicant sees exactly: plain status, or formatted summary PDF? |
| --- |

# 5. Applicant Portal

The Applicant Portal is a web-based interface accessible to accepted applicants. It provides read-only visibility into their admission progress and serves as the delivery channel for counselor-released results. It does not allow applicants to modify any data — all data shown is system-generated or staff-released.

## 5.1 Authentication & Account Lifecycle

| Stage | Trigger | Actor | Details |
| --- | --- | --- | --- |
| Account Created | Staff marks application as Accepted | System (auto) | Account record created. Email stored from application. No password set. |
| Setup Email Sent | Account creation event | System (auto) | Email with time-limited password setup link dispatched. |
| Password Set | Applicant clicks setup link | Applicant | First-time login screen. Password policy enforced. OTP option available. |
| Portal Access Granted | Password successfully set | System | Dashboard unlocked. All available surfaces rendered. |
| Account Reset | Admin action or OTP request | Admin / System | Admin can reset password or resend setup link. OTP provides self-service fallback. |

| Developer Notes — Auth [Expand During Implementation] Token expiry window for setup link: recommend 48–72 hours for admission context. Password policy: minimum length, complexity requirements, bcrypt/argon2 hashing. OTP delivery method: email OTP only, or SMS fallback? Session management: JWT vs. server-side sessions, expiry duration, refresh strategy. Rate limiting on login attempts and OTP requests. |
| --- |

## 5.2 Portal Surfaces

The portal dashboard exposes four distinct surfaces, each fed by data from a specific pipeline stage:

### 5.2.1 Process Status Tracker

A detailed, timestamped pipeline view showing the applicant's current stage across all phases.

| Stage | Triggered By | Timestamp Source |
| --- | --- | --- |
| Application Submitted | Application form submission | Phase 1 — submission event |
| Application Accepted | Staff marks accepted | Phase 1 — acceptance event |
| Exam Schedule Assigned | Admin publishes schedule | Phase 2 — publication event |
| Examination Completed | Proctor closes session | Phase 3 — session close event |
| Scores Being Processed | Grader starts grading session | Phase 4 — session open event |
| Consultation Released | Counselor releases summary | Phase 5 — release event |

### 5.2.2 My Exam Schedule

| Data Shown | Room name, building, floor, assigned date, time slot, proctor name (optional) |
| --- | --- |
| Populated When | Admin publishes schedule in Phase 2 |
| Visibility | Shown immediately on publication — no gating required |
| Notification | Email + in-app alert fires on population |

### 5.2.3 Score Release Countdown

| Data Shown | Target release date (set by admin), live countdown (days, hours, minutes) |
| --- | --- |
| Set By | Admin — manual, via Scheduling Interface |
| Visibility | Hidden until admin sets a date. Countdown updates if date is revised. |
| Notification | Email + in-app alert fires when admin sets or revises the date |

### 5.2.4 Consultation Summary

| Data Shown | Status (Done / Pending), counselor written comments, recommended course(s) |
| --- | --- |
| Gated By | Counselor must explicitly release before applicant can see any content |
| Locked State | Surface visible but content hidden with "Pending" status until released |
| Notification | Email + in-app alert fires on counselor release action |
| Override Visible | Applicant sees final recommendation only — not the system's original suggestion |

| Developer Notes — Portal Surfaces [Expand During Implementation] Define portal data API: does each surface poll independently or is there a unified dashboard endpoint? Real-time vs. polling: consider WebSocket for status tracker updates during active phases. Consultation summary: deliver as structured JSON (rendered in portal) or as a generated PDF attachment? Accessibility requirements for the portal (WCAG 2.1 AA recommended for public-facing tools). Mobile responsiveness: portal is web-based — define minimum viewport support. |
| --- |

# 6. Notification Engine

The Notification Engine is a cross-cutting subsystem that dispatches event-driven communications to applicants via two channels: email and in-portal alerts. It is triggered by defined system events — some automatic, some requiring explicit staff action.

## 6.1 Notification Event Matrix

| Event | Trigger Type | Triggered By | Channels | Content Summary |
| --- | --- | --- | --- | --- |
| Exam Schedule Assigned | Automatic | Schedule publication (Phase 2) | Email + In-App | Room, date, time, building |
| Exam Day Reminder | Automatic | T-1 day before exam date (scheduled job) | Email + In-App | Schedule recap, venue details |
| Scores Being Processed | Automatic | Grader opens grading session (Phase 4) | Email + In-App | Confirmation scores are in processing |
| Score Release Countdown Set | Manual | Admin sets release date (Phase 2) | Email + In-App | Target date, countdown link |
| Consultation Released | Manual | Counselor releases summary (Phase 5) | Email + In-App | Prompt to view portal summary |

## 6.2 Engine Architecture

At minimum, the Notification Engine requires:

Event Queue

Decouples event producers (phase interfaces) from notification dispatch. Prevents blocking on delivery failures.

Recipient Resolver

Maps event context (e.g., schedule_id, grading_session_id) to the correct set of applicant recipients.

Template Selector

Maps event type to the appropriate email template and in-app alert copy.

Email Dispatcher

Handles SMTP/transactional email delivery, retries, and delivery status tracking.

In-App Alert Store

Persists unread notifications for display in the portal dashboard notification inbox.

| Developer Notes — Notification Engine [Expand During Implementation] Queue technology: synchronous (simple) vs. async queue (Redis/Bull, RabbitMQ, etc.) — define based on volume. Email provider: SMTP relay, SendGrid, Mailgun, or institutional mail server? Template management: hardcoded vs. template engine (Handlebars, Mjml, etc.). Delivery failure handling: retry policy, dead-letter queue, alert to admin on repeated failure. In-app alert read/unread state: stored per-user, cleared on view or explicit dismiss? Exam day reminder: requires a scheduled job/cron — define scheduler approach. Unsubscribe/opt-out: required for email (CAN-SPAM / local equivalent compliance)? |
| --- |

# 7. Data Flows

This section documents the key data handoffs between phases and subsystems. Each flow entry describes what data moves, from where to where, under what condition, and the format/channel.

## 7.1 Core Pipeline Flow

| From | To | Data Transferred | Condition |
| --- | --- | --- | --- |
| Phase 1 — Application | Phase 2 — Scheduling | Accepted applicant list (IDs, names, contact) | On acceptance decision by Staff |
| Phase 2 — Scheduling | Phase 3 — Examination | Published schedule (room assignments, timeslots, proctors) | On schedule publication by Admin |
| Phase 3 — Examination | Phase 4 — Grading | Submission records (applicant_id, paper_id, timestamp) | On session close by Proctor |
| Phase 4 — Grading | Phase 5 — Consultation | Normalized scores per applicant | On grading session finalization by Grader |
| Phase 5 — Consultation | Applicant Portal | Released summary (status, comments, courses) | On explicit release by Counselor |

## 7.2 Portal Data Feeds

| Source | Portal Surface | Update Trigger |
| --- | --- | --- |
| Phase 1 events | Process Status Tracker | Application submitted / accepted events |
| Phase 2 — Schedule pub | My Exam Schedule | Schedule publication event |
| Phase 2 — Release date | Score Release Countdown | Admin sets release date |
| Phase 3/4/5 events | Process Status Tracker | Session close / grading start / consultation release |
| Phase 5 — Release | Consultation Summary | Counselor release action |

## 7.3 Notification Event Sources

| Source Event | Phase | Notification Fired |
| --- | --- | --- |
| Schedule published | Phase 2 | Exam Schedule Assigned |
| Exam date = tomorrow | Phase 2 | Exam Day Reminder (via scheduled job) |
| Grading session opened | Phase 4 | Scores Being Processed |
| Admin sets release date | Phase 2 | Score Release Countdown Set |
| Counselor releases summary | Phase 5 | Consultation Released |

| Developer Notes — Data Flows [Expand During Implementation] Define the canonical data format for each inter-phase transfer: JSON schema, database foreign keys, or event payloads. Clarify whether phase-to-phase transfer is synchronous (direct DB write) or event-driven (pub/sub). Data consistency: what happens if Phase 3 closes before Phase 2 data is fully available? Define audit/event log schema: every state transition should be logged with actor_id, timestamp, and context. |
| --- |

# 8. Non-Functional Requirements

The following non-functional requirements are defined at an architectural level. Specific acceptance criteria should be elaborated per requirement during sprint planning.

| ID | Category | Requirement | Priority | Status |
| --- | --- | --- | --- | --- |
| NFR-01 | Security | All applicant data must be transmitted over TLS 1.2+ | High | TBD |
| NFR-02 | Security | Passwords must be hashed using bcrypt or Argon2 with appropriate cost factor | High | TBD |
| NFR-03 | Security | Role-based access control enforced at API layer — not only UI layer | High | TBD |
| NFR-04 | Security | Session tokens must expire and support forced invalidation by Admin | High | TBD |
| NFR-05 | Performance | Portal dashboard must load within 3 seconds under normal load | Medium | TBD |
| NFR-06 | Performance | Notification dispatch must complete within 60 seconds of trigger event | Medium | TBD |
| NFR-07 | Availability | System must support planned maintenance windows with < 2 hours unplanned downtime/month | Medium | TBD |
| NFR-08 | Auditability | All state-change events must be written to an immutable audit log | High | TBD |
| NFR-09 | Auditability | Submission and attendance records must be tamper-evident | High | TBD |
| NFR-10 | Scalability | System must support concurrent use by all registered applicants in a single batch | Medium | TBD |
| NFR-11 | Accessibility | Applicant Portal must meet WCAG 2.1 AA accessibility guidelines | Medium | TBD |
| NFR-12 | Data Retention | Graded results and submission records must be retained per institutional data policy | High | TBD |

# 9. Integration Points

SecureCAT operates alongside existing institutional systems. The following integration points are identified at the architectural level. Integration contracts should be elaborated during design.

| External System | Integration Type | Direction | Data Exchanged | Status |
| --- | --- | --- | --- | --- |
| Dedicated Counseling System (Guidance and Registrar Offices) | Planned future integration | Outbound from SecureCAT | Consultation summaries, applicant scores | Future / Not in Scope v1 |
| Student Information System (SIS) | Planned future integration | Bidirectional | Accepted applicant records, enrollment confirmations | Future / Not in Scope v1 |
| Institutional Email Server / SMTP | Required | Outbound | Transactional notification emails | Required for v1 |
| OMR Scanner Hardware | Required (Phase 4) | Inbound to SecureCAT | Scanned answer sheet images | Beta — define spec |

| Note on Future Integrations Integration with the Guidance and Registrar Offices Dedicated Counseling System is a planned long-term enhancement. Integration with SIS for enrollment confirmation is planned but not in scope for v1. These integrations should be designed with adapter patterns so they can be added without refactoring core phases. |
| --- |

# 10. Open Questions & Design Decisions

The following items require resolution before or during detailed design. Assign an owner and target resolution date(changed to answer section) for each prior to sprint planning.

| ID | Question | Phase/Area | Owner | Answers |
| --- | --- | --- | --- | --- |
| OQ-01 | What is the primary technology stack (frontend framework, backend language, database)? | All | Arch Lead | Laravel + Inertia.js + Svelte + shadcn-svelte + MySQL |
| OQ-02 | On-premise or cloud deployment? Affects data residency, scaling, and backup strategy. | Infra | Infra Lead | Hostinger; On-prem (dev) |
| OQ-03 | What is the definition of "AI" in the scheduling assistant — rules engine or ML model? | Phase 2 | Dev Lead | Use of Third party model AI api; |
| OQ-04 | OMR integration: what scanner hardware is available? Define image format and API. | Phase 4 | Phase 4 Dev | Use OMRChecker or other third party solution; that can utilize phone camera |
| OQ-05 | Decision support in Phase 5: rules-based for v1, or ML from inception? | Phase 5 | Dev Lead | Rules based (manual counselor input) |
| OQ-06 | Historical data for decision support: manual CSV import, or SIS API? | Phase 5 | Arch Lead | Defer; for future; |
| OQ-07 | Notification email: institutional SMTP, or third-party transactional provider? | Notify | Infra Lead | Third party/cloud infra; custom if in dev mode |
| OQ-08 | Consultation summary delivery: structured HTML in portal, or generated PDF? | Phase 5 | UX Lead | Structured HTML/JSON rendered in portal (Amazon SES used for email notifications) |
| OQ-09 | What is the session token expiry duration for applicant portal? | Portal | Sec Lead | Standard session expiry (TBD — to be defined during implementation) |
| OQ-10 | Does the system need to support multiple concurrent admission batches (cohorts)? | All | Arch Lead | No |

# 11. Glossary

| Term | Definition |
| --- | --- |
| IAS | Information Assurance and Security — the academic subject that prompted the creation of SecureCAT. SecureCAT is a standalone system developed as part of this academic project. |
| SecureCAT | Computerized Admission & Testing — the admission pipeline module documented here. |
| Applicant | An external individual who has submitted an application for admission. |
| Admission Receipt | The official document issued to an accepted applicant, containing their reference number and triggering account provisioning. |
| OMR | Optical Mark Recognition — automated scanning of multiple-choice answer sheets. |
| Heatmap | In context: a visual representation of applicant-to-course distribution, highlighting capacity utilization. |
| Decision Support | System-generated course recommendation based on applicant score profile and current enrollment context. |
| Normalization | Conversion of raw exam scores to a standardized scale (e.g., percentile, T-score) for fair comparison. |
| Gated Release | A content release that requires explicit action by an authorized user (counselor) before the recipient (applicant) can view it. |
| OTP | One-Time Password — a single-use code used for account recovery or alternative authentication. |
| TLS | Transport Layer Security — encryption protocol for data in transit. |
| RBAC | Role-Based Access Control — permissions assigned to roles, not individuals. |
| SIS | Student Information System — institutional system of record for enrolled students. |

# 12. Document Control

| Document Title | SecureCAT — System Architecture & Developer Reference |
| --- | --- |
| Document ID | IAS-SecureCAT-ARCH-001 |
| Version | 2.0 |
| Status | Draft — For Development Expansion |
| Classification | Internal — Technical |
| Owner | IAS Development Team |
| Review Cycle | On major architectural change or phase completion |
| Last Updated | 2026 |
| Next Review | [TBD] |

## 12.1 How to Use This Document

**This document is structured as a living architecture reference. The intended workflow:**

Read Sections 1–3 for system context and actor mapping.

Use Section 4 per phase during detailed design — fill in the [Developer Notes] callouts.

Resolve Open Questions (Section 10) before sprint planning for each phase (already done).

Update the Revision History (page 2) on every structural change.

Treat Section 8 (NFRs) as acceptance criteria stubs — elaborate each item with measurable thresholds.

*Sections 5, 6, and 7 (Portal, Notifications, Data Flows) should be reviewed whenever a phase boundary changes or a new integration is added.*
