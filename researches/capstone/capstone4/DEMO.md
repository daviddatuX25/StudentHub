# SecureCAT v2 — Defense Demo Guide

> **ISPSC Tagudin Thesis Panel Defense**
> Full lifecycle walkthrough: application → account setup → exam → scoring → results → portal

---

## What is SecureCAT?

SecureCAT v2 is a web-based **College Admission Test (CAT) Management System** for ISPSC Tagudin. It digitizes the entire CAT pipeline:

1. **Applicants** submit online and track their status through a secure portal
2. **Staff** review and accept applications
3. **Admins** schedule exam sessions, assign applicants to rooms, and manage academic years
4. **Proctors** manage attendance and exam submission in real-time
5. **Registrar Administrators** enter scores, finalize grading, and release consultation summaries
6. **Applicants** view results, counselor recommendations, and chat with an AI companion

**Tech stack:** Laravel 12 · Svelte 5 · Inertia.js · MySQL · Laravel Reverb (WebSockets)

---

## Quick Setup (run before the defense)

```bash
# One command — migrates fresh, seeds foundation + demo data, prints session IDs
php artisan demo:setup
```

> **Requires:** `DEMO=true` in `.env`. See Troubleshooting if you see "DEMO is not enabled."

**Expected output includes:**
```
Applications: 20        Exam sessions: 4
Applicants:   12        Rooms:         4

Session IDs (use these in URLs):
  ID 1  | <date>  | completed  | Main Building / Room 101
  ID 2  | <date>  | completed  | Academic Building / Room 201
  ID 3  | today   | published  | Main Building / Room 102
  ID 4  | <date>  | published  | Vocational Building / Lab Room 1
```

Note the Session IDs — you will use them in URLs during the demo.

---

## Pre-Flight Checklist (30 min before defense)

- [ ] Run `php artisan demo:setup` — verify counts and note session IDs
- [ ] Open **Browser A** (Staff/Admin) — start at `http://localhost:8000`
- [ ] Open **Browser B** (Applicant Portal) — keep blank for now
- [ ] Open **Mailpit tab** — `http://localhost:8025`
- [ ] Copy the **Live Submission Data** below (paste into `/apply` during Step 1)
- [ ] Confirm `php artisan serve` is running
- [ ] (Optional) If Google OAuth configured — verify Sign-In button at `/login`

---

## The Big Picture: What's Already Seeded

| Session | Date | Status | What it demonstrates |
|---------|------|--------|----------------------|
| **Session A** | 14 days ago | `completed` + results released | Fully finalized — show grading + released consultation results |
| **Session B** | 5 days ago | `completed` + grading in progress | Partial scores entered — complete grading live, then release |
| **Session C** | **Today** | `published` | Live attendance marking by proctor |
| **Session D** | 5 days from now | `published` | Upcoming session — assign applicants live |

---

## Demo Flow

---

## ACT 1 — Application Lifecycle (~5 min)

> *"Let's follow an applicant from their very first interaction with the system."*

---

### Step 0: Home Page — Set the Scene (30 seconds)

**Browser A → `http://localhost:8000/`**

- Open the home page — *"This is the public entry point of SecureCAT."*
- Applicants arrive here to submit. Staff access is via `/login`.

---

### Step 1: Live Application Submission (public — no login)

**Browser A → `http://localhost:8000/apply`**

*"Any student can submit an application online. No account needed."*

Fill in the form with this data:

| Field | Value |
|-------|-------|
| First Name | Geraldine |
| Last Name | Santos |
| Birthdate | 2006-05-20 |
| Sex | Female |
| Email | `geraldine.santos@ispsc-demo.local` |
| Phone | 09171009021 |
| Address | 456 Rizal St. |
| City | Tagudin |
| Province | Ilocos Sur |
| Zip | 2714 |
| Course Preference 1 | BSIT |
| Course Preference 2 | BSCS |
| Course Preference 3 | BSDS |

**After submitting:**
- Success page shows reference number (e.g., `ISPSC-2026-0021`)
- Application is `pending` — no portal account yet

---

### Step 2: Staff Reviews & Accepts Applications

**Browser A — Login:** `maria@securecat.local` / `password`
**URL:** `http://localhost:8000/applications`

1. Applications list — show statuses: pending, accepted, dismissed
2. Open **Geraldine Santos** (just submitted) — show details
3. Click **Accept** → confirm
   - Portal account is created automatically
   - Setup email is triggered
4. Also show: **Carlos Vargas** (dismissed — "Did not appear") and **Rodolfo Lacsamana** (incomplete docs — "Missing PSA birth certificate")

*"Staff process applications digitally. Every action is logged for audit."*

---

### Step 3: Account Setup via Mailpit

**Mailpit tab → `http://localhost:8025`**

1. Show the setup email for Geraldine Santos — it arrived the moment she was accepted
2. Open the email — copy/click the setup link
3. **Browser B** → paste the setup link
4. Set a password (use `password` for simplicity)
5. Submit → lands on the applicant portal dashboard

**Portal shows:** *"Your application has been accepted. You are currently awaiting exam scheduling."*

*"The applicant gets a setup email the moment staff accepts. Zero manual steps — one click and they're in."*

6. Say: *"We'll come back to explore the portal features after the exam cycle."*

---

## ACT 2 — Exam Administration (~5 min)

> *"Now let's see how admins manage the exam pipeline."*

---

### Step 4: Admin — Sessions Overview

**Browser A — Login:** `josefina@securecat.local` / `password`
**URL:** `http://localhost:8000/admin/test-scheduling`

1. Show 4 sessions at different lifecycle stages
2. Point out Session C (today — `published`) and Session D (upcoming)
3. Open Session A (completed) — show it's closed and finalized

*"The admin sees the full pipeline at a glance — what's upcoming, in progress, and completed."*

---

### Step 5: Assign Applicants to Session D

**Browser A (same login)**

1. Open **Session D** (upcoming, 5 days from now)
2. Click **Assign Applicants / Examinees**
3. Show the list of accepted/unassigned applicants: Natividad, Virgilio, Erlinda
4. Assign them to Session D

*"Admins control which examinees go to which session — useful when managing multiple rooms and dates."*

---

### Step 6: AI Scheduling Assistant *(bonus — impressive)*

**Browser A (same login) → Test Scheduling**

1. Click the **AI Scheduling Assistant** button
2. Type: *"How many applicants are still unassigned?"* or *"Suggest a schedule for remaining applicants."*
3. Show the AI response

*"The assistant is context-aware — it knows your rooms, capacity, and current examinee load."*

---

## ACT 3 — Live Exam (~3 min)

> *"Session C is happening today. Let's watch the proctor work in real-time."*

---

### Step 7: Proctor — Mark Attendance Live

**Browser A — Login:** `eduardo@securecat.local` / `password`
**URL:** `http://localhost:8000/proctor/sessions/{SESSION_C_ID}`

*(Use the Session C ID from `php artisan demo:setup` output)*

1. Open Session C examinee list
2. **Point out:** Lorena Tamayo is already marked **Present** (pre-seeded)
3. Live demo actions:
   - **Roberto Libed** → Mark **Present** ✓
   - **Maribel Pagulayan** → Mark **Present** ✓
   - **Arturo Madriaga** → Mark **Absent** ✗
4. Show present count updating

*"Proctors mark attendance in real-time. No paper rosters — the system is the single source of truth."*

---

## ACT 4 — Scoring & Release (~5 min)

> *"Session B was completed 5 days ago. The registrar administrator finishes grading and releases results."*

---

### Step 8: Complete Session B Grading

**Browser A — Login:** `analiza@securecat.local` / `password`
**URL:** `http://localhost:8000/grading/sessions/{SESSION_B_GRADING_ID}`

*(Grading session ID = navigate to grading from the session B exam session)*

1. Open Session B grading — status: **In Progress**
2. **Point out:** SA, NA, VR scores already entered — 3 of 6 domains done
3. Open **Rowena Ballesteros** → Enter remaining scores:

   | Domain | Score |
   |--------|-------|
   | AR | 15 |
   | LR | 14 |
   | PSA | 13 |

4. Save Rowena's scores
5. Open **Danilo Espiritu Jr.** → Enter:

   | Domain | Score |
   |--------|-------|
   | AR | 17 |
   | LR | 16 |
   | PSA | 15 |

6. Save Danilo's scores
7. Click **Finalize Grading** → confirm

*"Scores are entered per aptitude area. Finalization locks the session — no further edits."*

---

### Step 9: Release Consultation Summaries

**Browser A (same login)**
**URL:** `http://localhost:8000/release`

1. Open Release Management — shows **pending** summaries for Rowena and Danilo
   - Note: course and notes fields are **blank** — filled live here
2. Open **Rowena Ballesteros**:
   - Recommended course: **BSIT**
   - Counselor comments: *"Good aptitude scores overall. Recommended for BSIT based on SA and VR performance."*
   - Click **Release**
3. Open **Danilo Espiritu Jr.**:
   - Recommended course: **BSCS**
   - Counselor comments: *"Strong numerical ability. Recommended for BSCS."*
   - Click **Release**

> **f2f shortcut:** If time is tight, skip counselor comments and use **Bulk Release**. Say: *"In practice, counselors review scores before releasing — we'll skip that step for time."*

*"Release management is deliberate — counselors review scores before applicants see results. Prevents premature disclosure."*

---

## ACT 5 — Portal Reveal (~4 min)

> *"Now let's see what just happened on the applicant's side — immediately after that release."*

---

### Step 10: Rowena Sees Her Just-Released Result

**Browser B → `http://localhost:8000/login`**
**Login:** `rowena.ballesteros@ispsc-demo.local` / `password`

1. Dashboard shows result status: **Released**
2. Recommended course: **BSIT**
3. Counselor comments visible

*"Rowena's result was released 30 seconds ago. No delay, no batch job — the system is live."*

---

### Step 11: Juan Views Session A Results

**Browser B → `http://localhost:8000/login`**
**Login:** `juan.agustin@ispsc-demo.local` / `password`

1. Dashboard shows Session A result — **Released**
2. Full scores per aptitude area, counselor comments, recommended course: **BSIT**

*"Session A was finalized days ago. Applicants can view results any time after release — no office visit needed."*

---

### Step 11B: AI Companion *(bonus — impressive)*

**Browser B (same login as Juan)**
**URL:** `http://localhost:8000/portal/ai-companion`

1. Ask: *"What does BSIT involve?"* or *"What do my scores mean?"*
2. Show contextual AI response (ISPSC-aware)

*"The AI companion is configured with ISPSC-specific knowledge — it gives relevant, localized answers."*

---

### Step 12: Lorena Checks Today's Exam

**Browser B → `http://localhost:8000/login`**
**Login:** `lorena.tamayo@ispsc-demo.local` / `password`

1. Dashboard shows Session C — **Published** (today's exam)
2. Shows: room (Main Building / Room 102), time (9:00 AM – 11:00 AM), proctor name

*"Once the admin publishes a session, assigned examinees immediately see their exam details — no separate notification needed."*

---

## ACT 6 — Admin Tools *(bonus, ~3 min)*

> *"Finally, let's look at what the super admin sees."*

---

### Step 13: View Session A Finalized Results

**Browser A — Login:** `analiza@securecat.local` / `password`
**URL:** `http://localhost:8000/grading/sessions/{SESSION_A_GRADING_ID}`

Show the 3 score profiles:

| Applicant | SA | NA | VR | AR | LR | PSA | Outcome |
|-----------|----|----|----|----|----|----|---------|
| Juan Carlo Agustin | 22 | 20 | 21 | 17 | 20 | 16 | High — BSIT |
| Maricel Dacumos | 14 | 13 | 15 | 10 | 13 | 11 | Borderline — BSCS |
| Reynaldo Soriano | 8 | 9 | 7 | 6 | 8 | 7 | Low — retake advised |

*"The system supports three outcomes — pass with recommendation, borderline, and retake advised."*

---

### Step 14: Print Result Sheets

**Browser A (same login) → Session A print view**

1. Show result sheet preview for Juan — formatted with scores per domain
2. Click **Print** (browser print dialog)

*"All printable outputs are generated from live data — no manual formatting."*

---

### Step 15: Staff Login — Both Methods

**Browser A → `http://localhost:8000/login`**

- **Method A:** `maria@securecat.local` / `password` → email + password login
- **Method B *(if configured)*:** Google Sign-In button → one-click with institutional Google account

---

### Step 16: Audit Logs

**Browser A — Login:** `admin@securecat.local` / `password`
**URL:** `http://localhost:8000/admin/logs`

1. Full audit trail of everything done during the demo
2. Filter by user — show Maria's accepts
3. Export to CSV

*"Every state-changing action is logged with user, timestamp, and before/after values — full traceability."*

---

### Step 17: System Settings

**Browser A (same login)**
**URL:** `http://localhost:8000/admin/settings`

- AI Companion toggle, release mode settings
- *"System behavior is configurable without touching code."*

---

## Timing Guide

| Act | Core | With bonus |
|-----|------|-----------|
| Act 1 — Application Lifecycle | ~5 min | — |
| Act 2 — Exam Administration | ~4 min | +2 min AI scheduler |
| Act 3 — Live Exam | ~3 min | — |
| Act 4 — Scoring & Release | ~5 min | — |
| Act 5 — Portal Reveal | ~4 min | +2 min AI companion |
| Act 6 — Admin Tools | — | ~3 min |
| **Total** | **~21 min** | **~28 min** |

---

## Credentials Reference

### Staff Accounts

| Role | Email | Password | Primary Demo Steps |
|------|-------|----------|--------------------|
| `super_admin` | `admin@securecat.local` | `password` | Audit logs, settings, users |
| `admin` | `josefina@securecat.local` | `password` | Sessions, scheduling, AI assistant |
| `staff` | `maria@securecat.local` | `password` | Application review & acceptance |
| `proctor` | `eduardo@securecat.local` | `password` | Attendance marking (Session C) |
| `registrar_administrator` | `analiza@securecat.local` | `password` | Grading, scoring, result release |

### Applicant Portal Accounts

| Name | Email | Password | Portal Status |
|------|-------|----------|---------------|
| Juan Carlo Agustin | `juan.agustin@ispsc-demo.local` | `password` | Session A — result **released** ✓ |
| Maricel Dacumos | `maricel.dacumos@ispsc-demo.local` | `password` | Session A — result **released** ✓ |
| Reynaldo Soriano | `reynaldo.soriano@ispsc-demo.local` | `password` | Session A — result **released** ✓ |
| Rowena Ballesteros | `rowena.ballesteros@ispsc-demo.local` | `password` | Session B — release live in Step 9 |
| Danilo Espiritu Jr. | `danilo.espiritu@ispsc-demo.local` | `password` | Session B — release live in Step 9 |
| Lorena Tamayo | `lorena.tamayo@ispsc-demo.local` | `password` | Session C — today's exam |
| Roberto Libed | `roberto.libed@ispsc-demo.local` | `password` | Session C — pending attendance |
| Maribel Pagulayan | `maribel.pagulayan@ispsc-demo.local` | `password` | Session C — pending attendance |
| Arturo Madriaga | `arturo.madriaga@ispsc-demo.local` | `password` | Session C — pending attendance |
| Natividad Ramirez | `natividad.ramirez@ispsc-demo.local` | `password` | Accepted — unassigned |
| Virgilio Castillo | `virgilio.castillo@ispsc-demo.local` | `password` | Accepted — unassigned |
| Erlinda De Vera | `erlinda.devera@ispsc-demo.local` | `password` | Accepted — unassigned |

> **Note:** 8 additional applicants (pending, dismissed, incomplete docs) have **no portal account** — access is granted only after staff acceptance.

---

## Pre-Seeded Data Summary

### Applications (20 total)

| Status | Count | Notes |
|--------|-------|-------|
| `accepted` | 12 | Portal accounts created, assigned to sessions |
| `pending` | 4 | Nestor, Imelda, Ferdinand, Rosalinda — awaiting staff review |
| `dismissed` | 2 | Carlos, Analiza — "Did not appear for appointment" |
| `incomplete_documents` | 2 | Rodolfo (missing PSA), Teresita (missing Form 138) |

### Sessions

| Session | Date | Room | Status | Examinees |
|---------|------|------|--------|-----------|
| Session A | Today − 14 days | Main Building / Room 101 | `completed` | Juan, Maricel, Reynaldo |
| Session B | Today − 5 days | Academic Building / Room 201 | `completed` | Rowena, Danilo |
| Session C | **Today** | Main Building / Room 102 | `published` | Lorena *(present)*, Roberto, Maribel, Arturo |
| Session D | Today + 5 days | Vocational Building / lab Room 1 | `published` | *(empty — assign live in Step 5)* |

### Consultation Summaries

| Applicant | Status | Recommendation |
|-----------|--------|----------------|
| Juan Carlo Agustin | `released` | BSIT — *"Excellent performance"* |
| Maricel Dacumos | `released` | BSCS — *"Borderline scores"* |
| Reynaldo Soriano | `released` | BSIT — *"Low scores. Advised to retake."* |
| Rowena Ballesteros | `pending` | *(enter live in Step 9 — BSIT)* |
| Danilo Espiritu Jr. | `pending` | *(enter live in Step 9 — BSCS)* |

---

## Test Suite

```bash
# Run the DefenseDemoSeeder integration tests
php artisan test --compact tests/Feature/DefenseDemoSeederTest.php

# Run a specific test
php artisan test --compact tests/Feature/DefenseDemoSeederTest.php --filter=session_a

# Run full suite
php artisan test --compact
```

**Expected:** All DefenseDemoSeeder tests PASS.

---

## Google Sign-In Setup (optional — for Step 15)

Add to `.env`:

```ini
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

Restart: `php artisan serve`. The Sign-In button appears on the Staff tab. Without these values, the button is silently hidden.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "DEMO is not enabled" | Add `DEMO=true` to `.env`, then re-run |
| "Database empty / counts wrong" | Re-run: `php artisan demo:setup` |
| "Login fails for staff" | Verify seeder ran — check `users` table for `maria@securecat.local` |
| "Portal login fails" | Only accepted applicants have portal accounts — check application status |
| "Session C has wrong examinees" | Re-run `php artisan demo:setup` — idempotent via `updateOrCreate` |
| "Google button not showing" | Check `.env` for `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` |
| "AI Companion not responding" | Check `OPENAI_API_KEY` or configured AI provider in `.env` |
| "Mailpit has no emails" | Confirm `MAIL_MAILER=smtp` and `MAIL_PORT=1025` in `.env` |
