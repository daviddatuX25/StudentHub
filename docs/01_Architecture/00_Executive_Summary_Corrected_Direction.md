# StudentHub — Corrected Direction Brief

*Synthesized from the developer direction questionnaire. This document corrects the research assumptions and reframes what we're actually building, for whom, and in what order.*

---

## 1. What This Project Actually Is

StudentHub is a **campus-deployed, coin-operated WiFi vending platform with an intranet PaaS layer**, initiated by the developer in coordination with the SSC governor. It is:

- An **Income-Generating Project (IGP)** under the student body
- A **developer's learning project** — specifically for agentic development, Linux server management, and full-stack infrastructure work
- A **legacy project** — something to leave behind at ISPSC Tagudin that continues working after the developer graduates
- **Not a capstone** (capstone is separate), but potentially a side project that proves the same skills

The project is currently **pre-institutional** — the SSC is aligned but no formal pitch has been made to admin, IT, or finance yet.

---

## 2. Corrections to the Research Documents

### 2.1 The Credit System Framing Is Too Restrictive

The research framed the platform credits entirely as a BSP-compliant closed-loop workaround to avoid legal exposure. **This is overly cautious and limits the platform's actual vision.**

**Corrected framing:** The platform should support **real monetary collection** for student-run applications, but scoped under campus-authorized policies — meaning collection is legal as long as it goes through the proper paperwork and approvals the campus already requires for any monetary activity. The platform's role is to **augment and enforce those existing policies technically**, not to replace them or circumvent them.

Practically: if a student org wants to use a platform app to collect payments for an event, they get the campus approval first (as they would anyway), then the platform flags their app as collection-authorized. The platform doesn't become a bank — it becomes an enforcement layer for approvals that already exist.

This means:
- The "non-cashable credits only" constraint from the research is **not absolute** — it's a default safe mode, not a design ceiling
- Platform credits remain the default unit, but authorized apps can transact in real peso value under campus policy
- P2P transfers stay prohibited (still correct from research)
- The platform's responsibility is **policy enforcement + audit trail**, not monetary gatekeeping

### 2.2 Textbee / SMS Gateway — Remove from Scope

Textbee (self-hosted Android SMS) is **cut entirely from scope**. It introduces a hardware dependency that is fragile to maintain and hard to debug in isolation. OTP and account recovery will be handled via other means — either email (if campus SMTP is accessible) or admin-assisted reset via the dashboard. This can be revisited only if a future developer team wants to pick it up.

### 2.3 Intranet "Sidequests" Are Platform Slots, Not Built Apps

The research described intranet apps (Moodle, e-library, etc.) as things the dev team would build. **Corrected:** the developer's role is to build the **PaaS hosting layer** (via Coolify on Proxmox), not the apps themselves. The apps are:
- Either existing campus systems (MIS, e-library) that get routed through the Walled Garden
- Or apps built by other student developers on top of the platform API in the future

The demo app(s) built by the developer are just proofs-of-concept to show the platform can host things — not core deliverables.

### 2.4 ISP Line — Not Resolved Yet

The campus has an ISP line, but **sharing it requires policy approval** which hasn't been pursued. A dedicated line contracted by the SSC is the cleaner path but also requires budget and coordination. This is an **open decision** that needs to be resolved during the pitch process — it cannot be assumed in the architecture.

**For development and testing purposes:** the developer's own home/dorm internet line is sufficient. The architecture doesn't change based on which ISP line is used.

### 2.5 NTC Compliance — Deferred, Not Ignored

The developer is aware of NTC requirements and intends to comply, but it is **not a development priority right now**. It becomes relevant at pitch time or at deployment — not during the build phase. Flag it in the pitch deck when that time comes.

---

## 3. Corrected Architecture Decisions

### 3.1 Host Machine — Proxmox

**Decision: Proxmox hypervisor on x86 Mini PC.**

Rationale:
- More room to learn — the dev wants to grow into infrastructure, not just code
- Network segmentation is cleaner and more visible
- Coolify (the PaaS layer) can be spun up as a separate VM/container without interfering with the routing VM
- Easier to rebuild components independently if something breaks

**Development environment:** The developer's Windows machine with a spare drive can run Proxmox for testing. This is the immediate path forward — no hardware procurement needed to start.

**Production hardware target:** ~₱20,000 org budget. A used Dell Optiplex or HP EliteDesk Mini (i5, 8th gen) + PoE switch + 1–2 TP-Link Omada APs is achievable within that budget.

### 3.2 Routing VM — OPNsense or OpenWrt x86

Inside Proxmox, a dedicated routing VM handles:
- WAN/LAN separation
- DHCP via dnsmasq
- The openNDS captive portal
- iptables / nftables for Walled Garden enforcement

The developer has **never run openNDS**, so this is a learning milestone — not a known quantity. This needs to be prototyped early, even in a basic VM-to-VM setup, before any app layer is built. **This is the first real technical risk.**

### 3.3 App VM — Ubuntu Server + Coolify + Docker

A separate VM on Proxmox runs:
- Coolify (open-source PaaS, Heroku-like, manages Docker deployments via a UI)
- Laravel app (admin dashboard, user ledger, session management, API)
- Node.js container (MQTT subscriber, ndsctl bridge)
- Mosquitto (MQTT broker)
- PostgreSQL

Coolify handles the Docker orchestration with a GUI, which reduces the iptables-conflict risk of managing raw Docker networking on the same host as the router.

### 3.4 Backend Stack — Hybrid Laravel + Node.js (as researched, confirmed)

- **Node.js container:** MQTT subscriber only. Receives coin pulse from ESP32, validates HMAC signature, calls Laravel API or directly executes ndsctl auth.
- **Laravel:** Everything else. Ledger, user accounts, admin dashboard, Walled Garden API, app authorization layer.

The developer is **comfortable with Laravel** and can learn Node.js for the narrow MQTT-only use case. This split is the right call.

### 3.5 MAC Randomization — Token Architecture, Deferred Testing

The browser token + cookie architecture from the research is **accepted as the direction** but is not going to be fully validated until a test environment is running. The developer correctly noted that this needs live testing to confirm behavior. JuanFi's codebase can serve as reference for how an existing open-source project handles this problem.

**For now:** accept the architecture as proposed. Build it. Test it on a real device. Adjust when edge cases surface.

### 3.6 Session Pause/Resume — Phase 1 Priority

Confirmed as a **must-have in Phase 1**, not a deferrable feature. The BinAuth script approach from openNDS (intercepting deauth events, calculating residual time, crediting back the ledger) is the implementation path.

### 3.7 Named Accounts + Anonymous Access

**Both required from Phase 1:**
- Anonymous users get a browser token automatically — drop coins, get internet, no registration needed
- Named accounts (Student ID + PIN) unlock: discounts, multi-device session transfer, balance recovery
- Visitors and canteen staff use anonymous mode
- Named account creation is optional and user-initiated

---

## 4. What the Walled Garden Actually Serves

The Walled Garden (intranet access before or without paying for external internet) serves two purposes:

1. **Infrastructure access:** The captive portal splash page itself must always be reachable — this is just how captive portals work
2. **PaaS-hosted apps:** Apps running on the Coolify VM are reachable through the Walled Garden. Whether a student pays to use a specific app depends on **how that app is configured in the admin panel** — not on a blanket free-for-all policy.

**Corrected from earlier assumption:** Not all PaaS-hosted apps are free. The platform supports three access tiers per app, configured by the admin:

- **Free / Walled Garden open** — accessible to anyone connected to the LAN, no credits required (e.g., campus announcements board, e-library)
- **Platform-credit gated** — requires the student to spend platform credits to use (e.g., a print queue app, a tutoring booking system)
- **Policy-authorized monetary collection** — app is permitted to collect real peso value, contingent on campus approval paperwork being on file

This access tier is set per-app in the admin dashboard. No manual iptables config needed each time — the platform manages its own routing allowlist via the API, and the Walled Garden rules are updated programmatically when an app's tier changes.

The iptables / DOCKER-USER chain rules allow traffic to the Coolify VM subnet at the network level, but the **application-layer gating** (who can use what) is enforced by the Laravel API — not by the firewall alone. External internet still requires openNDS authorization (i.e., payment).

---

## 5. Scope Definition by Phase

### Phase 1 — The Vending Machine (Build Now)
- Proxmox + OPNsense/OpenWrt VM setup
- openNDS captive portal on LAN interface
- ESP32 + coin acceptor → MQTT → Node.js → ndsctl auth flow
- Laravel ledger: anonymous token accounts, coin credit, session debit
- Session pause/resume via BinAuth + ndsctl deauth
- Named account registration (Student ID + PIN)
- Student discount logic tied to named accounts
- Admin dashboard: session monitor, manual refund, credit grant
- Walled Garden routing rules for Coolify VM subnet

### Phase 1.5 — Platform Readiness (Build After Phase 1 Works)
- Coolify VM setup and demo app deployment
- Platform API for third-party app credit debit/authorization
- App registration flow (student orgs apply to use the platform)
- Policy enforcement layer for monetization-authorized apps
- Xendit webhook integration for GCash/PayMaya top-up (UI built in Phase 1, wired up here)

### Phase 2+ — Institutional and Scale (After Pitch Succeeds)
- Campus MIS / e-library integration into Walled Garden
- Multi-AP deployment and network segmentation
- Reporting for CHED CMO 20 (25% admin share calculation)
- NTC compliance documentation
- Delegation to other developers

---

## 6. Timeline Strategy — Big Bang Research First

**The approach:** Max out the two-week AI subscription window on deep, exhaustive research and documentation — producing a research and architecture output so solid, complete, and playbook-ready that development can proceed confidently afterward even without AI assistance at the same intensity. This also becomes the pitch artifact: a document thorough enough that the SSC governor, IT program head, and admin can trust the developer knows what they're doing.

**What "big bang research" means here:**
- Every major technical decision gets a researched answer, not an assumption
- Every unresolved question from the OQ list gets a dedicated research pass
- The output is a **deployment playbook** — step-by-step enough that another developer could pick it up later
- Feature completeness is benchmarked against real existing PisoWifi software (WiFi5soft, AdoPiSoft, etc.)
- Hardware choices are verified with real Philippine market availability and pricing
- The architecture diagram is fully resolved — no "TBD" nodes

**Development starts after** the research phase produces a document you're confident pitching with. The skeleton sprint happens after, not during, the research window.

---

## 7. Open Research Areas — ✅ ALL RESOLVED OR DEFERRED

*Note: The questions originally listed here formed the basis for the Phase 1.5 Research Epics. As of May 2026, **all technical questions have been fully researched and resolved**, and the architecture is finalized. Non-technical business questions have been deferred to the pitch phase.*

### Technical Questions (Resolved)
*   **openNDS on Ubuntu 24.04 compatibility** → **Resolved in Epic 1.** We chose OpenWrt instead. (See `01_Proxmox_and_Networking_Foundation.md` and `02_Network\01_Captive_Portal_and_Session_Mechanics.md`)
*   **OPNsense vs OpenWrt x86 in Proxmox** → **Resolved in Epic 1.** OpenWrt was selected because it natively supports the openNDS package. (See `01_Proxmox_and_Networking_Foundation.md`)
*   **Coolify + Docker networking conflicts** → **Resolved in Epic 1.** We isolated routing (VM1) from Docker apps (VM2) to prevent Traefik from bypassing the captive portal. (See `01_Proxmox_and_Networking_Foundation.md`)
*   **Feature parity benchmarking** → **Resolved in Epic 6.** Fully cataloged against AdoPiSoft, PisoFi, LPB, JuanFi, and WiFi5soft. (See `05_Frontend_Identity\01_Software_Architecture_and_Commercial_Parity.md`)
*   **Bill acceptor integration & Power relays** → **Resolved in Epic 3.** Researched pulse/serial interfaces and relay logic. (See `03_Hardware\01_Vending_Hardware_and_BOM.md`)
*   **MAC randomization evidence** → **Resolved in Epic 6.** Analyzed competitors; verified that the cookie-first architecture is the correct architectural fix. (See `05_Frontend_Identity\01_Software_Architecture_and_Commercial_Parity.md`)
*   **App access tier management** → **Resolved in Epic 6.** Designed a Traefik `forwardAuth` middleware architecture that offloads auth to Laravel without proxying heavy traffic. (See `05_Frontend_Identity\01_Software_Architecture_and_Commercial_Parity.md`)
*   **Proxmox on a consumer Windows PC** → **Resolved in Epic 1.** Selected nested virtualization via VMware Workstation to avoid risky dual-booting. (See `01_Architecture\01_Proxmox_and_Networking_Foundation.md`)

### Business & Compliance Questions (Deferred to Pitch Phase)
These non-technical items (Track 7) will be addressed when preparing the pitch deck for the ISPSC administration:
1.  **ISP line decision** (Shared campus line vs. dedicated SSC line)
2.  **Campus policy on student org monetary collection** (Paperwork and accounting rules)
3.  **CHED CMO 20 pitch strategy** (Framing the 25% admin share as a benefit)

