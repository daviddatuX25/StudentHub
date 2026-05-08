# Epic 6 Validation — Software Architecture & Commercial Parity

**Validated against:** [Epic 6 Software Architecture & Commercial Parity.md](./Epic%206%20Software%20Architecture%20%26%20Commercial%20Parity.md)
**Roadmap source:** [5 StudentHub_Technical_Research_Roadmap.md](../5%20StudentHub_Technical_Research_Roadmap.md)
**Validation date:** 2026-05-08

---

## Validation Summary

| # | Sub-Topic | Verdict | Coverage |
|---|-----------|---------|----------|
| 6.1 | MAC Randomization — Field Evidence | ✅ COVERED | 4/4 questions |
| 6.2 | Feature Parity Benchmarking | ✅ COVERED | 3/3 questions |
| 6.3 | App Access Tier Management | ✅ COVERED | 4/4 questions |
| 6.4 | Captive Portal Frontend Design | ✅ COVERED | 4/4 questions |

**Overall: ✅ EPIC 6 COMPLETE**

---

## 6.1 — MAC Randomization: Field Evidence

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | How do JuanFi, AdoPiSoft, WiFi5soft, and PisoFi handle MAC randomization today? Search their GitHub issues, Facebook groups, and community forums. | §"How Existing Platforms Handle MAC Randomization" | **Fully documented with citations.** All 4 platforms analyzed + bonus coverage of iWiFi Portal and LPB. JuanFi uses "Kick Old Session" MikroTik script (`isRandomMacSyncFix`). AdoPiSoft uses cookie-based MAC Synchronizer + passcode recovery + customer account linking. WiFi5soft uses MikroTik-side "Fix Random Mac" configuration. PisoFi uses cookie-based session persistence decoupled from MAC. GitHub wiki links, README citations, and community sources provided. |
| Q2 | Do any of them force WPA2-PSK to stabilize MACs? What are the UX tradeoffs? | §"WPA2-PSK for MAC Stabilization — Not Used by Any Platform" | **Fully documented.** No platform forces WPA2-PSK. Apple's MAC behavior per security type documented (iOS 18+: fixed on WPA2, rotating every 2 weeks on open). Full UX tradeoff comparison table (6 factors × 2 modes). Explicitly addresses password friction for low-literacy users and shared-PSK security limitations. MikroTik forum evidence cited. |
| Q3 | Has anyone in the PisoWifi community implemented browser-token identity? Or is StudentHub the first? | §"Is StudentHub the First Cookie-First Identity Architecture?" | **Fully documented with comparison matrix.** StudentHub is NOT the first to use cookies — AdoPiSoft and PisoFi both use cookie-based sync. BUT StudentHub IS the first **clean cookie-first** architecture where HTTP-only cookies are the canonical identity (not supplementary). 5-column comparison matrix (AdoPiSoft, PisoFi, MikroTik cookie, StudentHub). Academic citation (Freudiger et al., arXiv:1907.02142) validates cookie-based identity in hospitality Wi-Fi. Confidence level explicitly stated: **HIGH**. |
| Q4 | What percentage of student devices (iPhone vs. Android vs. laptop) will we encounter? This affects which CPD behaviors matter most. | §"Real-World Device Mix Among Filipino Students" + §"MAC Randomization Behavior by Platform" | **Fully documented with market data.** Philippines mobile OS share: Android ~88.68%, iOS ~11.27%. Top vendors: Oppo 10.84%, Samsung 9.96%, Realme 9.11%, Vivo 8.83%, Apple 11.27%. MAC behavior documented per platform (Android 12+ non-persistent on open, iOS 18+ rotating every 2 weeks). Key finding: Android 12+ is the primary MAC rotation driver at ~89% market share. StatCounter April 2026 data cited. |

### Decision Captured

> **No WPA2-PSK** — UX cost outweighs MAC stabilization benefit. **Cookie-first identity** validated at HIGH confidence. AdoPiSoft/PisoFi validate cookies as viable; StudentHub differentiates by making them canonical. **Android 12+** is the primary MAC randomization concern (~89% of Filipino mobile market). **iOS CNA cookie-destruction** is a known limitation — mitigated by MAC recognition + Student ID linking as recovery mechanisms.

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| Field evidence report with citations | ✅ 4 platforms analyzed (JuanFi, AdoPiSoft, WiFi5soft, PisoFi) + 2 bonus (iWiFi Portal, LPB). GitHub, product pages, forums, and academic paper cited |
| Validated browser-token architecture confidence level | ✅ HIGH — with explicit iOS CNA caveat and recovery strategy |

---

## 6.2 — Feature Parity Benchmarking

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | Catalog every feature of WiFi5soft, AdoPiSoft, PisoFi, and Tplex: session flows, voucher systems, top-up methods, admin dashboards, hardware compatibility, reporting. | §"Product Feature Catalog" + §"Feature Comparison Matrix" | **Fully documented.** 5 products cataloged across 9 categories each (Session Flows, Voucher System, Coin/Bill, Top-Up, Admin Dashboard, Hardware, Reporting, Multi-Site, Pricing). Full comparison matrix: 27 features × 6 products (StudentHub + 5 competitors). LPB Piso WiFi identified as the feature leader (cloud-synced sessions, native GCash/Maya). Tplex identified as a reseller/brand running LPB or WiFi5soft, not a distinct product. JuanFi (open source, MIT) documented as baseline. |
| Q2 | Which features are table-stakes for Phase 1 vs. nice-to-have for Phase 2? | §"Phase 1 Table-Stakes vs. Phase 2 Nice-to-Have" | **Fully documented.** 10 Phase 1 table-stakes features enumerated with justification (coin-op flow, captive portal, pause/resume, rates, admin dashboard, vouchers, multi-denomination coins, bandwidth limiter, MAC mitigation, anti-abuse). 15 Phase 2 features ranked by priority (HIGH/MEDIUM/LOW) with competitive presence noted. GCash integration ranked #1 Phase 2 priority. |
| Q3 | What UI/UX patterns do students already expect from PisoWifi splash pages? | §"UI/UX Patterns Filipino Students Expect" + §"Biggest Pain Points from Community" | **Fully documented.** 10 UI elements cataloged with descriptions and source products (timer display, pause button, balance, signal indicator, insert coin, promo cards, carousel ads, voucher entry, green color scheme, mobile-first 44×44px targets). 8 operator pain points and 7 end-user pain points documented with affected products. |

### Decision Captured

> **LPB is the aspirational benchmark** — only platform with native GCash/Maya and cloud-synced sessions. **JuanFi is the open-source baseline.** **PisoFi has richest portal UX** but critical security vulnerabilities (RCE, hardcoded creds). **Tplex is not a distinct product** (reseller brand). **10 table-stakes features** must ship in Phase 1. **GCash integration** is #1 Phase 2 priority. **Security is StudentHub's strongest differentiator** — PisoFi ships known RCEs on outdated kernels.

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| Feature comparison matrix | ✅ 27-feature × 6-product matrix with competitive positioning |
| Phase 1 minimum feature checklist | ✅ 10 table-stakes features with justification |
| UI wireframe inspiration catalog | ✅ 10 UI element patterns documented from competitor analysis |

---

## 6.3 — App Access Tier Management

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | How to implement the 3-tier model (Free / Credit-Gated / Monetization-Authorized) without manual `iptables`? | §"3-Tier Intranet Model Without Manual iptables" | **Fully documented with code.** Traefik `forwardAuth` middleware per tier. Three tiers mapped: Free (no middleware), Credit-Gated (forwardAuth → `/api/auth/credit-check`), Monetization-Authorized (forwardAuth → `/api/auth/monetization-check`). Complete Docker label configurations and Laravel controller code provided. |
| Q2 | Can Traefik middleware (via Coolify labels) check a Laravel API endpoint before forwarding requests to a container? | §"Docker Label Configuration per Tier" + §"Traefik forwardAuth vs. Laravel Reverse-Proxy" | **Fully documented.** Yes — Traefik `forwardAuth` sends a sub-request to Laravel; 2XX proceeds, non-2XX blocks. `authRequestHeaders` passes cookies; `authResponseHeaders` propagates `X-User-Id`, `X-Session-Id`, `X-Remaining-Balance`. Traefik documentation cited. |
| Q3 | Alternative: Should all apps sit behind a single Laravel reverse-proxy endpoint? | §"Traefik forwardAuth vs. Laravel Reverse-Proxy — Decision" | **Fully documented with 7-dimension comparison.** Laravel reverse-proxy **strongly rejected**. Key disqualifiers: (1) bandwidth bottleneck — every byte passes through PHP-FPM, (2) streaming broken — Guzzle must buffer entire response, (3) failure mode — Laravel down kills ALL apps including free ones, (4) breaks Coolify's Docker label model. forwardAuth separates data plane (Traefik, Go) from control plane (Laravel, auth decisions). |
| Q4 | How does the admin dashboard UI for changing an app's tier trigger the routing update? | §"Admin Dashboard: Real-Time Tier Change Propagation" | **Fully documented with end-to-end flow.** Hybrid approach: Traefik File Provider (`watch: true`) + Database-driven auth + Redis Pub/Sub cache invalidation. 7-step flow documented: admin clicks → DB update → Redis pub/sub → cache invalidate → TraefikConfigWriter regenerates YAML (atomic rename) → Traefik inotify detects change → hot-reload <2s. Total propagation: <5 seconds, zero downtime, zero container restarts. Complete PHP code for `TraefikConfigWriter` with atomic file write. Architecture diagram included. |

### Decision Captured

> **Traefik forwardAuth** over Laravel reverse-proxy (strongly). **Data plane** (traffic proxying) stays in Traefik (Go); **control plane** (auth decisions) stays in Laravel. **File Provider + watch** for Traefik dynamic config. **Redis Pub/Sub** for cross-instance cache invalidation. **Atomic file write** (temp file → rename) for config changes. **Tier change propagation: <5 seconds** end-to-end.

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| Tier enforcement architecture diagram | ✅ ASCII architecture diagram with full data flow |
| Middleware vs. reverse-proxy decision | ✅ 7-dimension comparison table; forwardAuth strongly recommended |
| Admin UI flow | ✅ 7-step end-to-end propagation flow with code |

---

## 6.4 — Captive Portal Frontend Design

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | What framework for the splash page? Svelte 5 (as mentioned in Research #3) or plain HTML/JS for maximum CPD compatibility? | §"Framework Evaluation: CPD Browser Compatibility" + §"RECOMMENDATION: Dual-Mode Architecture" | **Fully documented with compatibility matrix.** 6-platform × 9-capability matrix (iOS CNA, Android 12+, Android legacy, macOS CNA, Windows, ChromeOS). iOS CNA critical limitations documented: localStorage crashes CNA, ES Modules not supported, cookies destroyed on close. **Decision: Dual-mode architecture.** Core splash = Plain HTML/CSS (CNA-compatible). Enhanced dashboard = Svelte 5 SPA (post-auth, full browsers only). Server-side User-Agent detection routes users. Rationale: Svelte 5 requires Proxy + ResizeObserver, incompatible with CNA. |
| Q2 | How to display: current balance, session timer, pause/resume button, "Link to Student ID" prompt, top-up options? | §"Splash Page Layout Design" + §"UI Component Inventory" + §"Portal States Wireframe Descriptions" | **Fully documented.** ASCII wireframe of core splash page layout. 6-component inventory with Core HTML vs. Enhanced Svelte implementations. 9 portal states documented (Initial, Active, Paused, Low Balance, Expired, Coin Inserted, Linking Student ID, Error/Offline, Incognito Warning) with display and user action per state. |
| Q3 | How to handle the "incognito mode warning" UX so students understand the risk of losing their token? | §"Incognito Mode Warning UX" | **Fully documented with 3-layer strategy.** Layer 1: Always-visible warning banner (non-blocking). Layer 2: Student ID linking as recovery mechanism (balance moves to PostgreSQL server-side). Layer 3: Graceful re-connection flow (MAC recognition → auto-associate new token → prompt Student ID linking). 5-state cookie dependency communication strategy table. Academic + StackOverflow sources cited. |
| Q4 | What localization is needed? (Filipino/English toggle.) | §"Localization Requirements" | **Fully documented with census data.** Philippines 2020 census language demographics (7 languages with native speaker counts). 3-tier localization strategy: Tier 1 (must-have): Filipino/English toggle. Tier 2 (should-have): Cebuano/Bisaya (22.5% of population). Tier 3 (consider): Ilocano (for ISPSC Tagudin specifically), Hiligaynon. Server-side i18n implementation (not client-side, due to CNA JS restrictions). `/locales/` file structure provided. Language selection stored server-side. **First PisoWifi system to offer Filipino/Cebuano localization.** |

### Decision Captured

> **Dual-mode architecture**: Plain HTML/CSS core splash (CNA-compatible) + Svelte 5 enhanced dashboard (post-auth only). **Server-side User-Agent detection** routes between modes. **Server-side i18n** (no client-side due to CNA JS restrictions). **3-tier localization**: Filipino/English (must), Cebuano (should), Ilocano (consider for ISPSC). **3-layer incognito warning**: persistent banner → Student ID linking → graceful MAC-based re-connection. **PWA features deferred** to post-auth enhanced dashboard only.

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| UI component inventory | ✅ 6 components with Core HTML and Enhanced Svelte implementations |
| Wireframes | ✅ ASCII wireframe of core splash page + 9 portal state descriptions |
| CPD-compatible tech stack decision | ✅ Dual-mode architecture with explicit rationale and compatibility matrix |

---

## Bonus Coverage (Beyond Roadmap Scope)

| Extra Coverage | Report Section | Value |
|---|---|---|
| LPB Piso WiFi analysis | §"Product Feature Catalog" | 6th competitor product not in original roadmap; identified as feature leader |
| iWiFi Portal | §6.1 | Additional platform discovered with MAC sync history |
| PisoFi security vulnerabilities | §"Known Security Issues" | RCE, hardcoded credentials, outdated OS — competitive differentiator |
| iOS CNA technical deep-dive | §6.4 | localStorage crash, ES Module incompatibility, cookie destruction behavior |
| Android 12+ Custom Tabs | §6.4 | DHCP Option 114 + JSON response for full Chrome captive portal |
| Three-tier degradation architecture | §"Offline and Degraded State Handling" | 5 failure scenarios with detection and recovery |
| PWA considerations | §"PWA Considerations" | Service Worker, Cache API, IndexedDB, Background Sync scoping |
| Operator & end-user pain points | §6.2 | 8 operator + 7 user pain points from community |
| Strategic insights | §6.2 | 7 competitive positioning insights |
| Appendix: 40+ source citations | §"Appendix: Source Citations" | GitHub repos, official docs, forums, product sites, research papers |

---

## Consolidated Decision Register (Epic 6)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| MAC identity architecture | Cookie-first (HTTP-only token → device_id) | AdoPiSoft/PisoFi validate cookies as viable; StudentHub makes them canonical |
| WPA2-PSK for MAC stabilization | No | UX cost (password entry) outweighs benefit; no competitor does this |
| iOS CNA recovery mechanism | MAC recognition + Student ID linking | CNA destroys cookies on close; MAC + Student ID are recovery paths |
| Feature target for Phase 1 | 10 table-stakes features | Matches or exceeds all competitors on core functionality |
| Phase 2 top priority | GCash/Maya native e-payment | Only LPB has native; rest use KLCiS (₱150/month) |
| Tier enforcement mechanism | Traefik forwardAuth middleware | Separates data plane (Go) from control plane (PHP); no bandwidth bottleneck |
| Tier config propagation | File Provider + Redis Pub/Sub | <5 seconds, zero downtime, zero container restarts |
| Splash page framework | Plain HTML/CSS (CNA-compatible core) | iOS CNA crashes on localStorage, blocks ES Modules; only plain HTML is universal |
| Enhanced dashboard framework | Svelte 5 SPA (post-auth) | Smallest compiled bundle; best DX; full browser features |
| Localization strategy | Server-side i18n (Filipino/English + Cebuano) | CNA blocks client-side JS; first PisoWifi with localization |
| Incognito warning | 3-layer: banner → Student ID link → MAC re-connect | Addresses the default iOS/macOS cookie-destruction behavior |

---

## Risk Register (Epic 6)

| Risk | Severity | Mitigation |
|------|----------|------------|
| iOS CNA destroys cookies on every close | 🔴 HIGH | MAC-based re-association + Student ID linking; banner warning on every visit |
| Android 12+ non-persistent MAC on open networks | 🟡 MEDIUM | Cookie-first architecture is the architectural fix; MAC is not used for identity |
| Svelte 5 enhanced dashboard fails on legacy browsers | 🟢 LOW | Plain HTML core is always available as fallback; `<noscript>` safety net |
| Traefik forwardAuth latency on credit-check | 🟢 LOW | Sub-request is ~1KB; Redis-backed cache with 30s TTL on tier lookups |
| Traefik File Provider YAML corruption | 🟢 LOW | Atomic write (temp file → rename); Traefik ignores invalid config files |
| LPB achieves feature parity on security | 🟡 MEDIUM | StudentHub's open architecture (Proxmox + PostgreSQL + Coolify) is a structural advantage; LPB is SBC-locked |
| Student ID adoption rate too low | 🟡 MEDIUM | Aggressive prompting; balance-recovery incentive; consider mandatory after ₱10 threshold |

---

## Items Deferred to Later Phases

| Item | Deferred To | Rationale |
|------|-------------|-----------|
| GCash/Maya native integration | Phase 2 | Requires Xendit or direct API; not needed for coin-op Phase 1 |
| Cloud-synced sessions (multi-campus) | Phase 2 | Single-campus Phase 1 doesn't need cross-site session persistence |
| Bill acceptor support | Phase 2 | Research complete (Epic 3); hardware integration deferred to post-launch |
| Cebuano/Ilocano localization | Phase 2+ | Filipino/English sufficient for ISPSC Tagudin deployment |
| PWA with Background Sync | Phase 2 | Service Worker only viable post-auth; complexity not justified for Phase 1 |
| Carousel banner ads for operators | Phase 2 | Revenue feature; not needed for initial campus deployment |
| Chat system (user↔admin) | Phase 3+ | Only PisoFi has this; low priority |
