# SecureCAT — Defense Demo Script

**Format:** Live walkthrough · End-to-end lifecycle
**Total budget:** ~21 min core flow (+7 min bonus acts)
**Two browser windows only** — you switch accounts within Browser A

> **Read this like a stage play.**
> `>` lines are what you say aloud.
> *Italics* are stage directions — skip them if behind on time, never skip the spoken lines.
> **⏱** marks are cumulative time targets from demo start.

---

## Pre-Demo Launch (30 min before walking on stage)

```bash
# From the project root — does everything in one go
bash demo-launch.sh
```

This script:
1. Runs `npm run build`
2. Runs `php artisan demo:setup` (fresh demo seed)
3. Starts `php artisan serve` on port 8000
4. Starts `php artisan queue:listen`
5. Starts ngrok → reads the public URL → injects it into **Slide 4** (Live Demo slide) as a clickable link + QR code
6. Serves the slides on port 9090 and opens them in your browser

> If `demo-launch.sh` fails, run these manually:
> ```bash
> npm run build && php artisan demo:setup
> php artisan serve &  php artisan queue:listen &
> ```

---

## Pre-Demo: 2-Window Browser Setup

Open **exactly two browser windows** before you walk on stage.

### Browser A — Staff / Admin Window
This window handles every staff-side action. Switch accounts between tabs within this window.

| Act | Account | Route |
|-----|---------|-------|
| Acts 1–2 | `maria@securecat.local` / `password` | `/applications` |
| Acts 3–4 | `josefina@securecat.local` / `password` | `/admin/test-scheduling` |
| Act 5 | `eduardo@securecat.local` / `password` | `/proctor` |
| Acts 6–7 | `analiza@securecat.local` / `password` | `/grading` |
| Act 9 (bonus) | `admin@securecat.local` / `password` | `/admin/logs` |

**Tip:** Pre-log into each account in a separate tab. Switch tabs, not windows.

### Browser B — Applicant Portal Window
This window stays on the portal. Switch applicant accounts as the demo progresses.

| Act | Account | What they see |
|-----|---------|---------------|
| Act 2 | Geraldine Santos (new) | Account setup link via Mailpit |
| Act 6 | `lorena.tamayo@ispsc-demo.local` | Session C — today's exam |
| Act 7 | `rowena.ballesteros@ispsc-demo.local` | Just-released result |
| Act 7 | `juan.agustin@ispsc-demo.local` | Session A result + AI Companion |

---

## Pre-Demo Checklist

- [ ] `bash demo-launch.sh` completed without errors
- [ ] Database seeded — note the Session IDs printed in terminal
- [ ] Browser A: tabs open, each staff account pre-logged-in
- [ ] Browser B: ready at `http://localhost:8000/portal/login`
- [ ] Mailpit open at `http://localhost:8025` in a spare tab
- [ ] Slide 4 shows ngrok URL + QR code (visible to audience)
- [ ] Zoom at 110% on projector
- [ ] Notification sound: audible but not loud
- [ ] Close Slack, email, Discord — no surprise popups
- [ ] This script open on a second monitor or printed — **never on the projector**

---

## Interface Introduction (Slide 3 — speak before switching to live demo)

*Navigate to Slide 3 of the presentation deck. Point at each interface card as you describe it.*

> "Before I show you the live system, let me orient you on who sees what."

> "SecureCAT has six distinct interfaces, each locked to a specific role."

*Point left-to-right, top row first:*

> "The **public** — no login needed. Any student can submit an application at the Apply page."

> "**Staff** reviews those applications, accepts or dismisses them. The moment they accept, the portal account is auto-created and a setup email is sent."

> "**Admin and Test Admin** schedule exam sessions, assign rooms and examinees. They also have an AI scheduling assistant."

*Bottom row:*

> "**Proctor** — on exam day they mark attendance live and verify identity with each applicant's unique QR code."

> "**Registrar Administrator** encodes scores after the exam and releases the consultation summary to each applicant."

> "And the **Applicant Portal** — the student's view. They track their status, see their exam schedule and QR code, view their results, and can chat with the AI Companion."

> "One backend. Six role-filtered views. Let me show you the full lifecycle now."

*Navigate to Slide 4 — the demo slide with the ngrok URL and QR code.*

> "The system is already live at this address." *(point at the URL and QR on screen)* "You can open it on your phone right now."

*Switch to Browser A. Begin Act 1.*

---

## Act 1 — Application Submission · ⏱ 0:00–2:00

**Browser A → `http://localhost:8000/`**

> "This is the public home page. No login required. Any student starts here."

**Browser A → `http://localhost:8000/apply`**

> "The application form. I'll fill this in with a live applicant right now."

*Fill — pre-memorize these values, do NOT think on stage:*

| Field | Value |
|-------|-------|
| First Name | Geraldine |
| Last Name | Santos |
| Email | `geraldine.santos@ispsc-demo.local` |
| Birthdate | 2006-05-20 |
| Sex | Female |
| Course 1/2/3 | BSIT / BSCS / BSDS |

*Click Submit.*

> "Reference number assigned immediately. Status is `pending` — no portal account yet. She cannot log in until a staff member accepts her."

**⏱ If over 2:00, skip filling birthdate and course fields.**

---

## Act 2 — Staff Reviews & Accepts · ⏱ 2:00–5:00

**Browser A → `maria@securecat.local` tab → `/applications`**

> "This is the Staff view. Maria sees every application — pending, accepted, dismissed."

*Show the list briefly.*

> "Here's Geraldine Santos — just submitted. Here's Carlos Vargas — dismissed, did not appear for appointment. Rodolfo Lacsamana — incomplete documents, missing PSA birth certificate."

> "Staff handles this digitally. Every action goes to the audit log."

*Open Geraldine Santos → click **Accept**.*

> "The moment I accept — portal account is created automatically and a setup email is triggered."

**Mailpit tab → `http://localhost:8025`**

> "Here's her setup email. One click and she sets her password."

*Open the setup link in Browser B → set password (`password`) → submit.*

> "She's in the portal. Status: Awaiting Exam Scheduling."

*Show portal dashboard briefly, then close.*

> "We'll come back to the applicant side after the exam cycle."

**⏱ If over 5:00, skip Mailpit — just say the email was triggered.**

---

## Act 3 — Admin Schedules Sessions · ⏱ 5:00–7:00

**Browser A → `josefina@securecat.local` tab → `/admin/test-scheduling`**

> "Admin switches to exam scheduling. Four sessions at different lifecycle stages."

*Point at the four session cards.*

> "Session A — completed two weeks ago, results already released. Session B — completed five days ago, grading in progress. Session C — today, actively running. Session D — five days out, upcoming."

*Open Session D.*

> "Let me assign some examinees to this upcoming session."

*Click **Assign Applicants** → assign Natividad Ramirez, Virgilio Castillo, Erlinda De Vera.*

> "Accepted applicants appear here immediately. Once assigned, they see their exam schedule in the portal — no separate notification needed."

**⏱ Target: 7:00 total.**

---

## Act 4 — AI Scheduling Assistant *(bonus — +1:30)*

**Browser A (same josefina) → Test Scheduling page → AI Scheduling Assistant button**

*Type:* `How many applicants are still unassigned?`

> "The assistant is context-aware — it knows our rooms, capacity, and current examinee load. Useful for planning across multiple sessions."

---

## Act 5 — Proctor Marks Attendance Live · ⏱ 7:00–9:30

**Browser A → `eduardo@securecat.local` tab → `/proctor/sessions/{SESSION_C_ID}`**

*(Session C ID was printed by `demo:setup` in the terminal)*

> "Session C is today. Eduardo is the assigned proctor. He opens the roster."

*Show examinees — Lorena Tamayo already marked Present.*

> "Lorena is pre-marked present — she arrived early. Now I'll mark the others live."

- Roberto Libed → **Present** ✓
- Maribel Pagulayan → **Present** ✓
- Arturo Madriaga → **Absent** ✗

> "Real-time. No paper roster. The system is the single source of truth for who entered that room."

> "In a real deployment, Eduardo scans each applicant's QR at the door — the system verifies identity before marking them present. That's our identity layer."

**⏱ Target: 9:30 total.**

---

## Act 6 — Registrar Grades Session B · ⏱ 9:30–13:00

**Browser A → `analiza@securecat.local` tab → `/grading` → open Session B**

> "Session B finished five days ago. Analiza, the Registrar Administrator, is finishing the scoring now."

*Show grading status: **In Progress**. Point at already-entered domains (SA, NA, VR).*

> "Three of six aptitude areas are already scored. I'll enter the remaining three now."

*Open Rowena Ballesteros → enter:*

| Domain | Score |
|--------|-------|
| AR | 15 |
| LR | 14 |
| PSA | 13 |

*Save. Open Danilo Espiritu Jr. → enter:*

| Domain | Score |
|--------|-------|
| AR | 17 |
| LR | 16 |
| PSA | 15 |

*Save. Click **Finalize Grading** → confirm.*

> "Scores entered per aptitude area — six domains total. Finalization locks the session. No further edits. Every score change before this point was logged."

**⏱ If over 13:00, enter only Rowena's scores and skip Danilo.**

---

## Act 7 — Release Consultation Summaries · ⏱ 13:00–16:00

**Browser A (same analiza) → `/release`**

> "Release management. Rowena and Danilo's summaries are pending. The counselor reviews scores and writes a recommendation before the applicant sees anything."

*Open Rowena Ballesteros:*
- Recommended course: **BSIT**
- Comments: `Good aptitude scores overall. Recommended for BSIT based on SA and VR performance.`
- Click **Release**

*Open Danilo Espiritu Jr.:*
- Recommended course: **BSCS**
- Comments: `Strong numerical ability. Recommended for BSCS.`
- Click **Release**

> "Deliberate release — not automatic. The counselor controls the moment the applicant sees their result. No premature disclosure."

**Browser B → login as `rowena.ballesteros@ispsc-demo.local`**

> "Rowena's result was just released — thirty seconds ago. She sees it immediately."

*Show dashboard: Released, BSIT, counselor comments.*

**Browser B → login as `juan.agustin@ispsc-demo.local`**

> "Juan was in Session A, finalized two weeks ago. He can view his result any time — no office visit."

*Show his scores per aptitude area.*

> "That's the full lifecycle. Application → scheduling → exam → grading → release. One system, six roles, end to end."

**⏱ If over 16:00, show only Rowena's result and skip Juan.**

---

## Act 8 — AI Companion *(bonus — +2:00)*

**Browser B (still as Juan) → `/portal/ai-companion`**

*Ask:* `What does BSIT involve?`

> "The AI Companion is grounded in ISPSC-specific knowledge — localized answers for this campus, not a generic chatbot."

---

## Act 9 — Audit Log · ⏱ 16:00–17:00

**Browser A → `admin@securecat.local` tab → `/admin/logs`**

> "Finally — accountability. Every action we just performed is recorded here: application accepted, session finalized, scores entered, result released. Non-repudiation by design."

*Scroll once. Do not read entries aloud.*

> "No action in SecureCAT is anonymous."

---

## Closing (back to slides) · ⏱ 17:00

*Alt+Tab back to the presentation deck.*

> "That's SecureCAT end-to-end. We'll take your questions."

---

## Recovery Plan

| Problem | What to do |
|---------|-----------|
| `demo-launch.sh` fails | Run `php artisan serve`, `php artisan queue:listen`, `php artisan demo:setup` manually in separate terminals |
| Login fails for staff | Use the pre-logged-in tab — never re-login on stage |
| Notification doesn't appear | Say *"notifications are queued"* and navigate to the notifications table directly |
| AI Companion slow or timeout | Say *"this is a live model call"* and show a pre-captured screenshot |
| Whole demo crashes | Go to Slide 3 on the presentation, narrate the interface tour verbally without the live app |
| Slide 4 missing ngrok URL | Open `http://localhost:8000` directly in Browser A — explain the local URL to the panel |

---

## Post-Demo Reset

```bash
php artisan demo:setup   # idempotent — safe to re-run between panel groups
```

---

## Credentials Quick-Reference

### Browser A — Staff Accounts

| Role | Email | Password |
|------|-------|----------|
| Staff | `maria@securecat.local` | `password` |
| Admin / Test Admin | `josefina@securecat.local` | `password` |
| Proctor | `eduardo@securecat.local` | `password` |
| Registrar Admin | `analiza@securecat.local` | `password` |
| Super Admin | `admin@securecat.local` | `password` |

### Browser B — Applicant Accounts

| Name | Email | Password | When |
|------|-------|----------|------|
| Geraldine Santos | `geraldine.santos@ispsc-demo.local` | `password` | Act 2 — created live |
| Lorena Tamayo | `lorena.tamayo@ispsc-demo.local` | `password` | Act 6 — today's exam |
| Rowena Ballesteros | `rowena.ballesteros@ispsc-demo.local` | `password` | Act 7 — result released live |
| Danilo Espiritu Jr. | `danilo.espiritu@ispsc-demo.local` | `password` | Act 7 — result released live |
| Juan Carlo Agustin | `juan.agustin@ispsc-demo.local` | `password` | Act 7 — already released |
| Maricel Dacumos | `maricel.dacumos@ispsc-demo.local` | `password` | Act 7 (optional) |

