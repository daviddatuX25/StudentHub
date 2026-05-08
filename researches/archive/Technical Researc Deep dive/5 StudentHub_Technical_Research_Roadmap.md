# StudentHub — Technical Research Roadmap (Expanded)

*Master guide for the pre-development research phase. Every section below represents an unresolved technical unknown that must be definitively answered before writing production code. Each research topic includes the problem statement, specific questions to answer, known risks, decision criteria, and the expected deliverable.*

*Source documents: Research #1 (Technical Deep Dive), #2 (Architecture & Feasibility), #3 (Platform Completeness), #4 (Corrected Direction Brief).*

---

## 🧭 Strategy Overview

StudentHub is a **campus-deployed, coin-operated WiFi vending platform with an intranet PaaS layer**, running on a Proxmox hypervisor. The system consolidates routing, captive portal, application hosting, and financial ledger onto a single x86 mini PC.

**Why research-first matters:** The architecture stacks multiple open-source systems (Proxmox → OpenWrt/OPNsense → openNDS → Docker → Coolify → Traefik → Laravel + Node.js) that each aggressively manipulate Linux networking. A single misconfiguration in the `iptables` chain order can silently bypass the captive portal — giving free internet to everyone. Every layer must be validated before code is written.

**Research execution order:** Epic 1 → Epic 2 → Epic 3 → Epic 4 → Epic 5 → Epic 6 → Track 7. Each epic produces a standalone research report saved to `/researches/`.

---

## 🟢 Epic 1: Development Environment & Hypervisor Foundation

*Dependency: None. This is the absolute starting point.*
*Objective: Get a working Proxmox lab on the developer's existing hardware so every subsequent research topic can be validated hands-on.*

### 1.1 Proxmox on the Developer's Windows Machine

**Problem:** The developer's primary machine runs Windows. We need Proxmox VE running locally without purchasing dedicated hardware yet.

**Questions to answer:**
- Can Proxmox run stably inside VMware Workstation or VirtualBox via nested virtualization? What are the known performance penalties and compatibility issues (VT-x passthrough, nested VT-d)?
- Is dual-booting Proxmox on a second SSD/partition the better path? What's the risk to the existing Windows install?
- Can the WR840N router (already owned) be flashed to pure bridge/AP mode and connected to the Proxmox host's physical NIC to simulate real WiFi clients?
- What's the minimum RAM/CPU allocation needed for a functional 3-VM Proxmox lab (Gateway VM + App VM + DB LXC)?

**Known risks:**
- Nested virtualization may not support PCIe/NIC passthrough, limiting network testing fidelity.
- Single-NIC setups require VLAN trunking through one physical port — needs managed switch or software bridge.

**Decision criteria:** Stability over 48 hours of continuous operation, ability to run at least 3 VMs simultaneously, real WiFi client connectivity.

**Deliverable:** Step-by-step setup guide with exact Proxmox version, VM allocations, and network bridge configuration.

---

### 1.2 Routing VM: OPNsense vs. OpenWrt x86

**Problem:** VM1 must handle WAN/LAN routing, DHCP, VLAN termination, and host the openNDS captive portal daemon. Two viable candidates exist.

**Questions to answer:**
- What is the RAM/CPU footprint of each under idle and 100-client NAT load?
- Which has native, maintained package support for openNDS? (OpenWrt has `opkg` packages; OPNsense uses FreeBSD ports — does openNDS even compile on FreeBSD?)
- Which provides a better web GUI for a developer who has never administered a routing OS?
- How does each handle 802.1Q VLAN subinterfaces inside a Proxmox virtio NIC?
- Which has better community documentation for "router-on-a-stick" deployments inside Proxmox specifically?

**Known risks:**
- OPNsense is FreeBSD-based. openNDS is Linux-native. Running openNDS on OPNsense may require cross-compilation or may not work at all.
- OpenWrt x86 has a minimal default UI (LuCI) that may confuse beginners, but it's far more lightweight.

**Decision criteria:** openNDS compatibility is the hard gate. Whichever OS runs openNDS natively and reliably wins. Resource footprint is the tiebreaker.

**Deliverable:** Comparison table with benchmarks. Final recommendation with rationale.

---

### 1.3 openNDS Compatibility & FAS Architecture

**Problem:** openNDS is the captive portal engine. Its Forwarding Authentication Service (FAS) must reliably intercept traffic, redirect to the Laravel portal, and execute `ndsctl auth` commands. Multiple unknowns exist.

**Questions to answer:**
- Does openNDS compile cleanly on Ubuntu 24.04 LTS? (Research #4 flagged this as unverified.)
- If openNDS runs inside the OpenWrt VM (VM1), how does the Laravel backend (in VM2) execute `ndsctl auth` commands across the VM boundary? SSH tunnel? REST API wrapper? Unix socket forwarding?
- Which FAS level (1, 2, or 3) should we target? Research #1 noted that FAS Level 3 (HTTPS) may cause iOS Captive Portal Assistant to choke on self-signed certs on a local IP.
- How does openNDS interact with the `iptables-nft` translation layer on modern Ubuntu? Research #1 warned against mixing `iptables-legacy` and `iptables-nft`.
- What is the exact openNDS config needed to whitelist the Docker bridge subnet (172.18.0.0/16) as a Walled Garden?

**Known risks:**
- If openNDS lives in VM1 but the backend lives in VM2, the `ndsctl` binary won't be locally available in VM2. This is a critical integration gap.
- iOS Captive Portal Assistant (CNA) has notoriously unpredictable behavior with HTTP redirects on non-standard ports.

**Decision criteria:** openNDS must successfully redirect a real iPhone and Android device to the portal page, and `ndsctl auth` must grant internet access within 2 seconds.

**Deliverable:** Working openNDS configuration file. Documented FAS level choice. Cross-VM `ndsctl` execution strategy.

---

### 1.4 Coolify + Docker + Firewall Coexistence

**Problem:** Docker, Traefik (via Coolify), and openNDS all manipulate `iptables`. They will fight for control of the FORWARD chain.

**Questions to answer:**
- How exactly does Coolify's embedded Traefik modify `iptables`? Does it use the same `DOCKER-USER` chain pattern, or does it inject its own chains?
- If the routing VM (VM1) handles all captive portal enforcement, does the App VM (VM2) even need `iptables` awareness of openNDS? Or is the network isolation between VMs sufficient?
- What DOCKER-USER rules are needed in VM2 to prevent Docker containers from bypassing VM1's captive portal via direct WAN access?
- Can Coolify's Traefik be configured to listen only on the VLAN 30 interface, preventing it from accidentally exposing services on VLAN 10?
- Research #3 flagged: "NAT reflection rules" — what specific OpenWrt config is needed so that portal requests from VLAN 10 correctly reach Docker containers on VLAN 30?

**Known risks:**
- Docker daemon restarts flush and rebuild `iptables` rules, potentially overwriting custom DOCKER-USER entries (Research #1, Problem Area 2).
- Coolify auto-updates may silently change Traefik's networking behavior.

**Decision criteria:** After a `systemctl restart docker` on VM2, unauthenticated clients on VLAN 10 must still be blocked from external internet AND still be able to reach the captive portal page.

**Deliverable:** Complete `iptables` rule set for both VM1 and VM2. Systemd persistence strategy. Test protocol.

---

### 1.5 VLAN Architecture & Virtual Bridge Design

**Problem:** The system requires at least 4 VLANs (Student WiFi, Admin, Intranet Apps, Proxmox Management) all trunked through potentially a single physical NIC.

**Questions to answer:**
- How to configure Proxmox's `vmbr0` and `vmbr1` virtual bridges for a single-NIC vs. dual-NIC mini PC?
- What managed switch is needed to terminate VLANs to physical access points? Verify the TP-Link Omada SG2008P supports 802.1Q trunking with PVID assignment.
- How does the OpenWrt VM act as "router-on-a-stick" across VLANs 10, 20, 30, and 99?
- What Netplan or `/etc/network/interfaces` config is needed on the Proxmox host itself?

**Known risks:**
- Single-NIC VLAN trunking creates a bandwidth bottleneck — all inter-VLAN traffic passes through one gigabit link.
- Misconfigured PVID on the switch can leak student traffic into the management VLAN.

**Deliverable:** Complete VLAN topology diagram. Proxmox bridge config. Switch port assignment table.

---

## 🟡 Epic 2: Network Services & Session Mechanics

*Dependency: Epic 1 (need a working Proxmox lab to test).*
*Objective: Validate every component of the captive portal session lifecycle end-to-end.*

### 2.1 Captive Portal Detection (CPD) Behavior

**Problem:** When a device connects to WiFi, the OS probes specific URLs to detect captive portals. If this detection fails, the user never sees the splash page.

**Questions to answer:**
- What exact URLs do iOS, Android, Windows, and macOS probe for CPD? Does openNDS intercept all of them?
- How does the iOS Captive Portal Assistant (CNA) mini-browser behave with HTTP vs. HTTPS redirects? Does it support cookies?
- Research #3 flagged: Does `allow_preemptive_authentication` in openNDS reliably work on all device types?
- What happens when a student uses a non-browser app first (e.g., opens Instagram before Safari)? Does CPD still trigger?

**Known risks:**
- iOS CNA is a restricted WebKit instance — it may not persist cookies the same way Safari does. This directly threatens our browser-token architecture.
- Some Android OEMs suppress CPD notifications entirely.

**Deliverable:** Device compatibility matrix (iOS versions, Android versions, Windows, macOS). Cookie persistence test results per platform.

---

### 2.2 Session Pause/Resume via BinAuth

**Problem:** Students must be able to pause their internet session, preserving unused time as credits.

**Questions to answer:**
- What exact arguments does openNDS pass to the BinAuth script during a `deauth` event? Verify: `session_start`, `session_end`, `bytes_incoming`, `bytes_outgoing`.
- Research #3 flagged: What is the execution latency of BinAuth? If a student rapidly toggles pause/resume, do we get race conditions in the PostgreSQL ledger?
- Should we implement a message queue (Redis queue) between BinAuth and the Laravel/Node.js backend to buffer rapid events?
- How does openNDS handle a device that disconnects without an explicit `deauth` (e.g., student walks out of range)? Is BinAuth still triggered?

**Known risks:**
- BinAuth is a shell script executed by the openNDS daemon. If it blocks or crashes, it may freeze the entire captive portal.
- Time calculation drift: if the server clock and openNDS clock diverge, refund amounts will be incorrect.

**Deliverable:** BinAuth script template. Race condition mitigation strategy. Timeout handling for ungraceful disconnects.

---

### 2.3 Mid-Session Top-Up & ndsctl Timeout Behavior

**Problem:** `ndsctl auth <MAC> <timeout>` overwrites the previous timeout — it does not add to it. The backend must independently track cumulative time.

**Questions to answer:**
- Does `ndsctl auth` accept timeouts in seconds or minutes? (Research #1 says minutes at line 254, but the openNDS docs may differ by version.)
- If a student inserts a coin during an ACTIVE session, what's the exact sequence? Query DB → calculate remaining → add new time → reissue `ndsctl auth` with new absolute timeout?
- What happens if `ndsctl auth` is called on a MAC that's already authenticated? Does it seamlessly extend, or does it briefly drop the connection?
- Can we batch multiple rapid coin insertions (e.g., 5 coins in 3 seconds) into a single `ndsctl auth` call using a debounce window?

**Known risks:**
- If the backend crashes between debiting credits and executing `ndsctl auth`, the student loses money without getting internet. Need atomic transaction design.

**Deliverable:** Sequence diagram for mid-session top-up. Debounce strategy. Atomic transaction design for credit-to-auth flow.

---

### 2.4 SQM / CAKE Bandwidth Management

**Problem:** 1,000 users sharing a 100Mbps line will experience catastrophic bufferbloat without queue management. MQTT coin payment events could time out.

**Questions to answer:**
- Does `tc` (traffic control) with CAKE work correctly on VLAN subinterfaces (e.g., `eth1.10`), or must we create individual IFB (Intermediate Functional Block) interfaces per VLAN? (Research #1 flagged this as unverified.)
- How does CAKE interact with Docker's NAT? The `nat` keyword in CAKE is supposed to inspect inner IPs, but does this work when Docker has already masqueraded the source?
- What `bandwidth` values should we set? Research #1 recommends 95% of rated speed — but how do we detect the actual ISP speed dynamically?
- Should CAKE run on VM1 (the routing VM) or on the Proxmox host itself?

**Known risks:**
- CAKE on the wrong interface will shape Proxmox inter-VM traffic instead of student traffic.
- IFB interface creation may not survive reboots without explicit systemd service.

**Deliverable:** Complete `tc` command set. IFB setup script. Bufferbloat test protocol (using `flent` or similar).

---

### 2.5 Split-Horizon DNS & SSL Certificates

**Problem:** The portal domain (e.g., `portal.studenthub.ph`) must resolve to a local IP inside the campus and a public IP outside.

**Questions to answer:**
- How to configure dnsmasq (inside OpenWrt VM1) to intercept DNS queries for `*.studenthub.ph` and resolve them to VLAN 30 addresses?
- How does Traefik (in Coolify/VM2) obtain valid Let's Encrypt wildcard certificates via DNS-01 challenge using the Cloudflare API — all while behind a NAT with no public ports open?
- Can the openNDS splash page be served over HTTPS with a valid cert, or must it remain HTTP due to CPD browser limitations?
- If we use HTTP for the splash page but HTTPS for the Laravel API, how do we handle mixed-content browser warnings?

**Deliverable:** dnsmasq config for split-horizon. Traefik DNS-01 + Cloudflare setup guide. Certificate chain diagram.

---

## 🟠 Epic 3: Hardware & Physical Vending Unit

*Dependency: None (can be researched in parallel with Epic 2).*
*Objective: Finalize the complete hardware BOM and firmware design for the physical vending unit.*

### 3.1 Coin Acceptor Wiring & ESP32 Firmware

**Problem:** The ESP32 must reliably detect coin pulses and publish MQTT events with HMAC signatures.

**Questions to answer:**
- What coin acceptor models are available in the Philippine market? (CH-926, DG-600F are common.) What are their pulse timing characteristics?
- What logic level shifter circuit is needed (12V pulse → 3.3V ESP32 GPIO)?
- How to implement hardware interrupt debouncing in ESP32 firmware to avoid double-counting?
- What is the exact MQTT payload structure? Research #1 specifies: `{device_id, coin_value, msg_id, timestamp, hmac}`.
- How to securely store the HMAC shared secret on the ESP32 (flash encryption? NVS partition?)?

**Deliverable:** Wiring schematic. ESP32 firmware skeleton (Arduino/PlatformIO). MQTT payload spec.

---

### 3.2 Bill Acceptor Integration

**Problem:** Real PisoWifi deployments accept ₱20, ₱50, ₱100 bills — not just coins.

**Questions to answer:**
- What bill acceptor models are available in the PH market? (ICT, Innovative Technology, Allan brand validators.)
- Do they use pulse output (like coin acceptors) or serial/UART protocol? What's the voltage?
- Can one ESP32 handle both a coin acceptor AND a bill acceptor simultaneously, or do we need separate GPIO interrupt lines?
- How do bill acceptors handle jammed/counterfeit bills? What signal does the ESP32 receive on rejection?
- What is the physical enclosure requirement? Bill acceptors are significantly larger than coin slots.

**Deliverable:** Bill acceptor model recommendation. Wiring schematic alongside coin acceptor. Firmware interrupt handler for dual-input.

---

### 3.3 Power Relay & Operating Schedule

**Problem:** The vending unit should power down during off-hours to save electricity and reduce wear.

**Questions to answer:**
- What relay modules work with the ESP32? (5V mechanical relay, solid-state relay, MOSFET-based switching.)
- Should the ESP32 itself be always-on (to receive MQTT schedule commands from the server), with only the peripherals (coin acceptor, LCD, LEDs) switched via relay?
- How does the Laravel backend communicate the on/off schedule? MQTT retained message? Cron job publishing to a `schedule` topic?
- What happens if the ESP32 loses WiFi connectivity during a power transition? Does it default to ON or OFF?

**Deliverable:** Relay wiring schematic. Schedule management MQTT topic design. Failsafe behavior spec.

---

### 3.4 Hardware BOM Validation

**Problem:** All components must be purchasable in the Philippines within the ₱20,000 SSC budget.

**Questions to answer:**
- Verify current Shopee/Lazada pricing for: Beelink S12 Pro N100, Dell Optiplex 3060 Micro, TP-Link Omada SG2008P, TP-Link EAP610, ESP32 DevKit, CH-926 coin acceptor, relay modules, UPS.
- Verify the Intel NIC requirement — can the N100 Mini PC's built-in Realtek NIC handle 500+ NAT sessions, or is a USB ASIX AX88179A adapter strictly required?
- What UPS provides adequate runtime (10+ minutes) for graceful shutdown during brownouts?

**Deliverable:** Updated BOM table with real PH market links and prices. Total cost vs. budget gap analysis.

---

## 🔵 Epic 4: Security & Payment Integrity

*Dependency: Epics 1-2 (need working captive portal to test against).*
*Objective: Harden every attack surface — from MQTT spoofing to ndsctl injection to webhook replay.*

### 4.1 MQTT Security & Anti-Replay

**Questions to answer:**
- How to configure Mosquitto ACLs with `%c` pattern so each ESP32 can only publish to its own topic?
- What is the exact HMAC-SHA256 validation flow in Node.js? How does the backend verify the signature and reject forged payloads?
- How does Redis-based message deduplication work for replay attack prevention? What TTL should the `msg_id` keys have?
- Should we use TLS for MQTT (port 8883) even on a local network, or is HMAC sufficient?

**Deliverable:** Mosquitto ACL config. Node.js HMAC validation code. Redis deduplication logic.

---

### 4.2 ndsctl Command Injection Prevention

**Questions to answer:**
- What is the exact regex for validating MAC addresses before passing to `ndsctl`?
- Confirm: Node.js `child_process.execFile` (not `exec`) prevents shell injection. What about Python `subprocess.run(shell=False)`?
- If the MAC validation regex is bypassed, what is the worst-case damage? Can `ndsctl` be sandboxed (AppArmor profile, seccomp filter)?

**Deliverable:** Input validation module. Security test cases (fuzzing MAC input).

---

### 4.3 Xendit Webhook Idempotency (Phase 2 prep)

**Questions to answer:**
- How does Xendit's `X-CALLBACK-TOKEN` header verification work?
- What is the exact `external_id` → `source_reference` deduplication flow in PostgreSQL?
- How to handle the race condition where two identical webhooks arrive simultaneously?

**Deliverable:** Webhook handler pseudocode. Idempotency key design. Database constraint strategy.

---

## 🟣 Epic 5: Database, Scaling & Observability

*Dependency: Epic 2 (need session mechanics defined to design the schema).*
*Objective: Finalize the PostgreSQL schema, connection pooling, and monitoring stack.*

### 5.1 PostgreSQL Schema Finalization

**Questions to answer:**
- Validate the schema from Research #1: `users`, `devices`, `sessions`, `transactions` tables. Are there missing columns or constraints?
- Should `audit_log` be a separate append-only table or a trigger-based audit on the `transactions` table?
- How to model the "tagged sub-balances" (e.g., `purpose=ipon` credits) from Research #3?
- What indexes are needed for the most common queries (active sessions by MAC, transaction history by user)?

**Deliverable:** Final `.sql` migration file. Index strategy. ER diagram.

---

### 5.2 PgBouncer & Redis Configuration

**Questions to answer:**
- What PgBouncer pool mode (session, transaction, statement) is appropriate for Laravel's Eloquent ORM?
- How to configure Redis AOF persistence to survive power loss without excessive I/O on the NVMe?
- What Redis data structures are needed? (Session cache, rate limiting counters, MQTT dedup keys, API token store.)

**Deliverable:** PgBouncer config. Redis config with AOF. Data structure catalog.

---

### 5.3 Conntrack Tuning & Kernel Parameters

**Questions to answer:**
- Validate the sysctl values from Research #1 (conntrack_max=524288, tcp_timeout_established=3600, etc.).
- How to apply these settings reliably on boot when `nf_conntrack` is loaded dynamically by Docker? Research #1 mentions a udev rule — what's the exact implementation?
- At what user count does the N100's single gigabit NIC become the bottleneck vs. conntrack?

**Deliverable:** `/etc/sysctl.d/` config file. udev rule. Monitoring alert thresholds.

---

### 5.4 Backup & Disaster Recovery

**Questions to answer:**
- What `vzdump` schedule and mode (snapshot vs. suspend) is appropriate for each VM/LXC?
- How long does a full restore of the Gateway VM (VM1) take on NVMe storage?
- Should we use Proxmox Backup Server (PBS) on a Raspberry Pi, or is a USB HDD sufficient for Phase 1?

**Deliverable:** Backup schedule. Recovery runbook with tested RTO (Recovery Time Objective).

---

## 🟤 Epic 6: Software Architecture & Commercial Parity

*Dependency: Epics 1-4 (need full stack operational to benchmark against).*
*Objective: Ensure StudentHub matches or exceeds existing PisoWifi products in UX and functionality.*

### 6.1 MAC Randomization — Field Evidence

**Questions to answer:**
- How do JuanFi, AdoPiSoft, WiFi5soft, and PisoFi handle MAC randomization today? Search their GitHub issues, Facebook groups, and community forums.
- Do any of them force WPA2-PSK to stabilize MACs? What are the UX tradeoffs?
- Has anyone in the PisoWifi community implemented browser-token identity? Or is StudentHub the first?
- What percentage of student devices (iPhone vs. Android vs. laptop) will we encounter? This affects which CPD behaviors matter most.

**Deliverable:** Field evidence report with citations. Validated browser-token architecture confidence level.

---

### 6.2 Feature Parity Benchmarking

**Questions to answer:**
- Catalog every feature of WiFi5soft, AdoPiSoft, PisoFi, and Tplex: session flows, voucher systems, top-up methods, admin dashboards, hardware compatibility, reporting.
- Which features are table-stakes for Phase 1 vs. nice-to-have for Phase 2?
- What UI/UX patterns do students already expect from PisoWifi splash pages?

**Deliverable:** Feature comparison matrix. Phase 1 minimum feature checklist. UI wireframe inspiration catalog.

---

### 6.3 App Access Tier Management

**Questions to answer:**
- How to implement the 3-tier model (Free / Credit-Gated / Monetization-Authorized) without manual `iptables`?
- Can Traefik middleware (via Coolify labels) check a Laravel API endpoint before forwarding requests to a container?
- Alternative: Should all apps sit behind a single Laravel reverse-proxy endpoint that checks access tier before proxying?
- How does the admin dashboard UI for changing an app's tier trigger the routing update?

**Deliverable:** Tier enforcement architecture diagram. Middleware vs. reverse-proxy decision. Admin UI flow.

---

### 6.4 Captive Portal Frontend Design

**Questions to answer:**
- What framework for the splash page? Svelte 5 (as mentioned in Research #3) or plain HTML/JS for maximum CPD compatibility?
- How to display: current balance, session timer, pause/resume button, "Link to Student ID" prompt, top-up options?
- How to handle the "incognito mode warning" UX so students understand the risk of losing their token?
- What localization is needed? (Filipino/English toggle.)

**Deliverable:** UI component inventory. Wireframes. CPD-compatible tech stack decision.

---

## ⚪ Track 7: Business & Compliance (Deferred)

*Researched parallel to the pitch deck, after the technical architecture is validated.*

| Topic | Key Question | When Needed |
|---|---|---|
| ISP Line Policy | Shared campus line vs. dedicated SSC-contracted line? | Before pitch |
| CHED CMO 20 | How to frame the 25% admin share as a benefit? | Pitch deck |
| Campus Monetary Policy | What paperwork for student org monetary collection? | Before app authorization flow design |
| NTC Compliance | VASP classification, Type Approval for APs | Before deployment |
| Domain Registration | `.ph` vs `.com.ph` — cost, process, timeline? | Before SSL setup |

---

## 📋 Research Tracking Table

| # | Topic | Epic | Status | Report File |
|---|---|---|---|---|
| 1.1 | Proxmox on Windows PC | 1 | ✅ Done | Researching Proxmox and Networking Stack.md |
| 1.2 | OPNsense vs OpenWrt x86 | 1 | ✅ Done | Researching Proxmox and Networking Stack.md |
| 1.3 | openNDS Compatibility & FAS | 1 | ✅ Done | Researching Proxmox and Networking Stack.md |
| 1.4 | Coolify + Docker + Firewall | 1 | ✅ Done | Researching Proxmox and Networking Stack.md |
| 1.5 | VLAN Architecture | 1 | ✅ Done | Researching Proxmox and Networking Stack.md |
| 2.1 | CPD Behavior | 2 | ✅ Done | Captive WiFi Vending Network Deep Dive.md |
| 2.2 | Session Pause/Resume (BinAuth) | 2 | ✅ Done | Captive WiFi Vending Network Deep Dive.md |
| 2.3 | Mid-Session Top-Up | 2 | ✅ Done | Captive WiFi Vending Network Deep Dive.md |
| 2.4 | SQM / CAKE Bandwidth | 2 | ✅ Done | Captive WiFi Vending Network Deep Dive.md |
| 2.5 | Split-Horizon DNS & SSL | 2 | ✅ Done | Captive WiFi Vending Network Deep Dive.md |
| 3.1 | Coin Acceptor & ESP32 | 3 | ✅ Done | Vending Hardware & BOM Report.md |
| 3.2 | Bill Acceptor | 3 | ✅ Done | Vending Hardware & BOM Report.md |
| 3.3 | Power Relay & Schedule | 3 | ✅ Done | Vending Hardware & BOM Report.md |
| 3.4 | Hardware BOM Validation | 3 | ✅ Done | Vending Hardware & BOM Report.md |
| 4.1 | MQTT Security & Anti-Replay | 4 | ✅ Done | StudentHub Vending System Security Architecture.md |
| 4.2 | ndsctl Injection Prevention | 4 | ✅ Done | StudentHub Vending System Security Architecture.md |
| 4.3 | Xendit Webhook Idempotency | 4 | ✅ Done | StudentHub Vending System Security Architecture.md |
| 5.1 | PostgreSQL Schema | 5 | ✅ Done | StudentHub Database Scaling & Observability.md |
| 5.2 | PgBouncer & Redis Config | 5 | ✅ Done | StudentHub Database Scaling & Observability.md |
| 5.3 | Conntrack & Kernel Tuning | 5 | ✅ Done | StudentHub Database Scaling & Observability.md |
| 5.4 | Backup & Disaster Recovery | 5 | ✅ Done | StudentHub Database Scaling & Observability.md |
| 6.1 | MAC Randomization Field Evidence | 6 | ✅ Done | Epic 6 Software Architecture & Commercial Parity.md |
| 6.2 | Feature Parity Benchmarking | 6 | ✅ Done | Epic 6 Software Architecture & Commercial Parity.md |
| 6.3 | App Access Tier Management | 6 | ✅ Done | Epic 6 Software Architecture & Commercial Parity.md |
| 6.4 | Captive Portal Frontend | 6 | ✅ Done | Epic 6 Software Architecture & Commercial Parity.md |

---

## 🚀 Execution Strategy

1. **Start with Epic 1.1 + 1.2** — Get Proxmox running locally and pick the routing OS.
2. **Epic 1.3 + 1.4 + 1.5** — Get openNDS, Docker, and VLANs working together in the lab.
3. **Epic 2 (all)** — Validate the full session lifecycle end-to-end on real devices.
4. **Epic 3 (parallel)** — Hardware research can happen alongside Epic 2 since it's independent.
5. **Epic 4 + 5** — Harden security and finalize the database after the session flow is proven.
6. **Epic 6** — Polish and benchmark against commercial products.
7. **Track 7** — Business items researched when preparing the pitch deck.

Each completed research topic updates the tracking table above and produces a numbered report in `/researches/`.
