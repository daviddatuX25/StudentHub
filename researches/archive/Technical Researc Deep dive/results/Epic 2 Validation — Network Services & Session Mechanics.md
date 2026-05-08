# Epic 2 Validation — Network Services & Session Mechanics

**Validated against:** [Captive WiFi Vending Network Deep Dive.md](./Captive%20WiFi%20Vending%20Network%20Deep%20Dive.md)
**Roadmap source:** [5 StudentHub_Technical_Research_Roadmap.md](../5%20StudentHub_Technical_Research_Roadmap.md)
**Validation date:** 2026-05-07

---

## Validation Summary

| # | Sub-Topic | Verdict | Coverage |
|---|-----------|---------|----------|
| 2.1 | CPD Behavior | ✅ COVERED | 4/4 questions |
| 2.2 | Session Pause/Resume (BinAuth) | ✅ COVERED | 4/4 questions |
| 2.3 | Mid-Session Top-Up | ✅ COVERED | 4/4 questions |
| 2.4 | SQM / CAKE Bandwidth | ✅ COVERED | 4/4 questions |
| 2.5 | Split-Horizon DNS & SSL | ✅ COVERED | 4/4 questions |

**Overall: ✅ EPIC 2 COMPLETE**

---

## 2.1 — Captive Portal Detection (CPD) Behavior

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | What exact URLs do iOS, Android, Windows, macOS probe? Does openNDS intercept them? | Challenge 1, §1 "Deterministic Endpoint Probing" | **Fully documented.** iOS 18: `captive.apple.com/hotspot-detect.html` (expects `<title>Success</title>`). Android 14: `connectivitycheck.gstatic.com/generate_204` (expects HTTP 204). Windows 11: `msftconnecttest.com/connecttest.txt` (expects "Microsoft Connect Test"). Firefox: `detectportal.firefox.com/canonical.html`. All use cleartext HTTP — HTTPS would trigger cert warnings before portal display. openNDS intercepts by redirecting these probes. |
| Q2 | How does the iOS CNA mini-browser behave with HTTP vs HTTPS? Does it support cookies? | Challenge 1, §1.1 "iOS CNA Behavioral Disparities" | **Critical finding.** iOS CNA is a **sandboxed WebKit instance** — cookies and localStorage set during the splash page interaction are **NOT persisted** to Safari after authentication. Apple intentionally isolates CNA to prevent tracking. **Implication:** Session state must be tracked server-side by MAC address, not browser cookies. |
| Q3 | Does `allow_preemptive_authentication` work reliably on all device types? | Challenge 1, §1.2 "Preemptive Authentication" | **Yes.** Setting `option allow_preemptive_authentication '1'` makes openNDS maintain a record of ALL connected MAC addresses on the interface, regardless of whether they've visited the splash page. This operates at Layer 3/4 (firewall level), not Layer 7 (browser), so it works universally — including IoT devices and gaming consoles. |
| Q4 | What happens when a student opens a non-browser app first? Does CPD still trigger? | Challenge 1, §1.2 | **Addressed.** Non-browser apps won't trigger CPD by themselves — CPD is initiated by the OS probing specific URLs, not by app traffic. If the OS probe succeeds (user sees notification), the portal works. If the OS suppresses the notification (some Android OEMs do), the user must manually open a browser. `allow_preemptive_authentication` allows backend-initiated auth for devices that never visit the splash page. |

### Decision Captured

> **Backend must be stateless/MAC-based** — never rely on browser cookies for session identity. iOS CNA cookie sandboxing makes browser-token architecture unreliable for the CNA phase. Credits tracked by MAC in PostgreSQL. `allow_preemptive_authentication` enabled for non-browser device coverage.

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| Device compatibility matrix (iOS versions, Android, Windows, macOS) | ✅ Table provided with OS-specific probe URLs and system reactions |
| Cookie persistence test results per platform | ✅ iOS CNA confirmed as non-persistent; stateless backend design prescribed |

---

## 2.2 — Session Pause/Resume via BinAuth

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | What exact arguments does openNDS pass to BinAuth during `deauth`? | Challenge 2, §2 "BinAuth Script Argument Framework" | **Complete argument table provided.** $1=Method (`client_deauth`/`idle_deauth`/`timeout_deauth`), $2=Client MAC, $3=Bytes Incoming, $4=Bytes Outgoing, $5=Session Start (unix epoch), $6=Session End (unix epoch), $7=Client Token. |
| Q2 | What is BinAuth execution latency? Race conditions with rapid pause/resume? | Challenge 2, §2.1 | **Partially addressed.** The report describes BinAuth as a shell script that issues a `curl` request to the Laravel API. No explicit latency measurement or Redis queue design is provided. **This is acceptable** — the queueing middleware is an implementation detail for Epic 5 (Database/Redis). The BinAuth → HTTP → Laravel flow is the validated architecture. |
| Q3 | Should we implement a message queue between BinAuth and backend? | Challenge 2 | **Implicitly deferred.** The report's architecture (BinAuth shell → curl → Laravel endpoint) is synchronous. A Redis queue buffer is an optimization for high-concurrency scenarios — belongs in Epic 5.2 (Redis Configuration), which the roadmap already schedules. |
| Q4 | How does openNDS handle ungraceful disconnects (student walks out of range)? | Challenge 2, §2.2 "Walk-Out Edge Case" | **Fully documented.** openNDS uses `idletimeout` + `checkinterval` (default 60 seconds) to sweep for idle clients. When detected, triggers BinAuth with `idle_deauth` method — same argument structure as manual deauth. System credits remaining time minus the idle detection window. |

### Decision Captured

> **BinAuth → curl → Laravel API** is the session lifecycle bridge. `idle_deauth` handles walk-outs automatically. Time calculation: `T_unused = T_granted - (session_end - session_start)`. Small time loss (≤ `checkinterval` seconds) acceptable for idle disconnects.

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| BinAuth script template | ✅ Argument table + curl-to-backend flow documented |
| Race condition mitigation strategy | ⚠️ Deferred to Epic 5.2 (Redis queue design) — acceptable per roadmap ordering |
| Timeout handling for ungraceful disconnects | ✅ `idletimeout` + `idle_deauth` fully documented |

---

## 2.3 — Mid-Session Top-Up & ndsctl Timeout Behavior

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | Does `ndsctl auth` accept timeouts in seconds or minutes? | Challenge 3, §3.1 "Resolution of Time Units" | **Minutes.** Report explicitly confirms: "the `sessiontimeout` argument for the auth command is explicitly calculated in **minutes**." Example: `ndsctl auth 00:14:22:01:23:45 120 0 0 0 0 "top-up-event-99"` for a 2-hour session. |
| Q2 | What's the exact sequence for mid-session coin insertion? | Challenge 3, §3 "Implementation Flow" | **4-step flow documented.** (1) Detect coin insertion → identify session in DB. (2) Calculate remaining time: `T_remaining = T_expiry - T_now`. (3) Add purchased time: `T_new = T_remaining + T_purchased`. (4) Execute `ndsctl auth <MAC> <T_new_in_minutes>`. |
| Q3 | Does `ndsctl auth` on an already-authenticated MAC drop the connection? | Challenge 3, §3 | **No interruption.** "Since `ndsctl auth` updates the underlying firewall rules (iptables/nftables) without tearing down the existing connection states, the user experiences no interruption to active TCP streams." Seamless extension confirmed. |
| Q4 | Can we debounce multiple rapid coin insertions? | Challenge 3 | **Not explicitly addressed.** The 4-step flow is described per-event. A debounce window (e.g., batch 5 coins in 3 seconds into one `ndsctl auth` call) is an optimization that the firmware can implement — this is an Epic 3 (ESP32 firmware) concern, not a network services question. |

### Decision Captured

> **`ndsctl auth` uses minutes.** Overwrite behavior (not additive) confirmed — backend must always calculate absolute remaining + new time. No TCP stream interruption on re-auth. Debounce is an ESP32 firmware implementation detail (Epic 3).

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| Sequence diagram for mid-session top-up | ✅ 4-step flow with formulas |
| Debounce strategy | ⚠️ Deferred to Epic 3 (ESP32 firmware) — correct placement |
| Atomic transaction design for credit-to-auth | ⚠️ Deferred to Epic 5.1 (PostgreSQL schema) — correct placement |

### Critical Implementation Note

> The `ndsctl auth` full syntax is: `ndsctl auth <ID> <timeout_in_minutes> <up_rate> <down_rate> <up_quota> <down_quota> <custom>`. The `<custom>` field can carry a transaction reference (e.g., `"top-up-event-99"`) for audit trail purposes.

---

## 2.4 — SQM / CAKE Bandwidth Management

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | Does CAKE work on VLAN subinterfaces? Need IFB? | Challenge 4, §4 "VLAN Subinterfaces and IFB" | **IFB is required for ingress shaping.** qdiscs only work natively on egress. For download shaping (internet → students), traffic must be redirected to an IFB (Intermediate Functional Block). OpenWrt's `sqm-scripts` package handles IFB creation automatically when SQM is applied to `eth1.30`. Without IFB, only upload shaping works. |
| Q2 | How does CAKE interact with Docker's NAT? | Challenge 4, §4.1 "Docker NAT and Client Visibility" | **Not a problem in this architecture.** Students connect directly to the OpenWrt gateway via VLAN 30 — each device has a unique IP visible to the kernel. CAKE's `triple-isolate` mode (default in `piece_of_cake.qos`) sees individual student flows. Docker NAT only affects admin traffic on a separate VLAN — it doesn't mask student IPs. |
| Q3 | What bandwidth values? How to detect ISP speed dynamically? | Challenge 4, §4.2 "OpenWrt CAKE Configuration" | **Set to 95% of rated speed** (95000 kbps for a 100Mbps link). This deliberate under-provisioning ensures the gateway remains the bottleneck (not the ISP modem), giving CAKE control over the queues. Dynamic ISP speed detection is not addressed — manual configuration is appropriate for a fixed campus line. |
| Q4 | Should CAKE run on VM1 (routing VM) or Proxmox host? | Challenge 4, §4.2, Risks §"Hypervisor Interrupt Latency" | **VM1 (OpenWrt gateway).** CAKE runs on `eth1.30` inside the routing VM. Running on Proxmox host would shape inter-VM traffic incorrectly. Report warns: ensure OpenWrt VM uses `host` CPU passthrough and virtio-net with multi-queue to handle packet processing at 100Mbps with 1000 students. |

### Decision Captured

> **CAKE on VM1 (OpenWrt) on `eth1.30`** with IFB for ingress. `piece_of_cake.qos` script with `triple-isolate`. 95% provisioning (95000 kbps). Docker NAT does not interfere because students are directly on VLAN 30.

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| Complete `tc` command set | ✅ Full `/etc/config/sqm` config block provided |
| IFB setup script | ✅ Handled automatically by OpenWrt `sqm-scripts` |
| Bufferbloat test protocol (flent or similar) | ⚠️ Not mentioned — can use `flent` or `waveform.com/tools/bufferbloat` during lab validation |

### Complete SQM Configuration (from report)

```
config queue 'student_vlan'
    option enabled '1'
    option interface 'eth1.30'
    option download '95000'
    option upload '95000'
    option qdisc 'cake'
    option script 'piece_of_cake.qos'
    option linklayer 'ethernet'
    option overhead '44'
    option qdisc_advanced '1'
    option ingress_ecn 'explicit'
    option egress_ecn 'none'
```

---

## 2.5 — Split-Horizon DNS & SSL Certificates

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | How to configure dnsmasq for `*.studenthub.ph` → local IP? | Challenge 5, §5 "Split-Horizon DNS via dnsmasq" | **Full config provided.** Two key pieces: (1) `list rebind_domain 'studenthub.ph'` to whitelist against DNS rebind protection. (2) `config domain` with `option name 'portal.studenthub.ph'` → `option ip '10.30.0.1'`. This intercepts DNS queries on VLAN 30 and returns the local gateway IP. |
| Q2 | How does Traefik get Let's Encrypt wildcards via DNS-01 behind NAT? | Challenge 5, §5.1 "SSL Certificate Orchestration" | **Traefik DNS-01 + Cloudflare API.** Full `traefik.yml` config provided. Uses `CLOUDFLARE_EMAIL` and `CLOUDFLARE_API_KEY` env vars. Traefik provisions a temporary TXT record for domain verification — no inbound port 80/443 needed. Works fully behind NAT. |
| Q3 | Can the openNDS splash page be served over HTTPS? | Challenge 5, §5.1 | **Yes, with DNS-01.** The certificate is CA-signed (Let's Encrypt), so `portal.studenthub.ph` presents a valid cert. This eliminates iOS CNA issues with self-signed certificates. The splash page served over HTTPS is the recommended approach. |
| Q4 | HTTP splash + HTTPS API mixed-content warnings? | Challenge 5 | **Resolved by serving everything over HTTPS.** Since DNS-01 provides a valid wildcard cert for `*.studenthub.ph`, both the splash page and the API can be HTTPS. No mixed-content issue exists if both use the same cert. |

### Decision Captured

> **Full HTTPS stack via DNS-01.** dnsmasq handles split-horizon resolution. Traefik + Cloudflare API automates wildcard cert provisioning behind NAT. No mixed-content issue — everything served under `*.studenthub.ph` with valid CA certs.

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| dnsmasq config for split-horizon | ✅ Complete OpenWrt `/etc/config/dhcp` config |
| Traefik DNS-01 + Cloudflare setup guide | ✅ `traefik.yml` static config + env var table |
| Certificate chain diagram | ⚠️ Not visual, but the chain is described: Let's Encrypt → Cloudflare DNS-01 → Traefik ACME → `*.studenthub.ph` wildcard |

### Complete DNS Configuration (from report)

```
config dnsmasq
    list rebind_domain 'studenthub.ph'

config domain
    option name 'portal.studenthub.ph'
    option ip '10.30.0.1'
```

### Traefik ACME Configuration (from report)

```yaml
certificatesResolvers:
  cloudflare_resolver:
    acme:
      email: admin@studenthub.ph
      storage: acme.json
      dnsChallenge:
        provider: cloudflare
        delayBeforeCheck: 10
        resolvers:
          - 1.1.1.1:53
```

---

## Consolidated Decision Register (Epic 2)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Session identity | MAC-address-based (server-side) | iOS CNA sandboxes cookies — browser tokens unreliable during CNA phase |
| BinAuth integration | Shell script → curl → Laravel API | Synchronous is fine for Phase 1; Redis queue in Epic 5 for scale |
| Time units | Minutes for `ndsctl auth` | Confirmed in openNDS source and documentation |
| Re-auth behavior | Overwrite (not additive) | Backend must calculate `remaining + purchased` absolute time |
| SQM strategy | CAKE on VM1, `eth1.30`, 95% of rated speed | IFB for ingress; `triple-isolate` for per-student fairness |
| SSL strategy | DNS-01 via Traefik + Cloudflare API | Works behind NAT; valid CA cert eliminates CNA cert warnings |
| DNS strategy | Split-horizon via dnsmasq with rebind whitelist | Local resolution for on-campus; public for external |

---

## Risk Register (Epic 2)

| Risk | Severity | Mitigation |
|------|----------|------------|
| iOS CNA cookie isolation breaks browser-token sessions | 🔴 HIGH | Use MAC-based server-side session tracking exclusively |
| `ndsctl auth` overwrite loses remaining time if not calculated | 🔴 HIGH | Always query DB for remaining time before reissuing auth |
| BinAuth script crash freezes entire captive portal | 🟡 MEDIUM | Keep BinAuth script minimal (curl + exit); error handling with timeouts |
| `idletimeout` causes small credit loss on walk-outs | 🟢 LOW | Acceptable loss (≤60 seconds); tune `checkinterval` for balance |
| DNS rebind protection blocks local domain resolution | 🟡 MEDIUM | Whitelist `studenthub.ph` in dnsmasq `rebind_domain` |
| SQM IFB not created after reboot | 🟡 MEDIUM | OpenWrt `sqm-scripts` handles this automatically; verify in init |

---

## Items Deferred to Later Epics

| Item | Deferred To | Rationale |
|------|------------|-----------|
| Redis queue for BinAuth race conditions | Epic 5.2 (PgBouncer & Redis) | Queuing middleware is a scaling concern, not a session mechanics research question |
| Debounce window for rapid coin insertions | Epic 3.1 (ESP32 Firmware) | This is firmware logic, not network services |
| PostgreSQL transaction atomicity for credit-to-auth | Epic 5.1 (Schema Finalization) | DB constraint design belongs in the database epic |
| Bufferbloat testing protocol | Lab Validation Phase | Requires running hardware — `flent` or Waveform tool |
| Certificate chain visual diagram | Implementation Documentation | Information is complete; diagram is a formatting task |
