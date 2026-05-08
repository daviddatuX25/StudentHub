# Epic 6 Research Report: Software Architecture & Commercial Parity

> StudentHub — Phase 1.5 Deep Follow-Up Research  
> Date: 2026-05-07  
> Status: Research Complete  

---

## Table of Contents

1. [6.1 — MAC Randomization: Field Evidence from Philippine PisoWifi Community](#61--mac-randomization-field-evidence-from-philippine-pisowifi-community)
2. [6.2 — Feature Parity Benchmarking Against Commercial PisoWifi Products](#62--feature-parity-benchmarking-against-commercial-pisowifi-products)
3. [6.3 — App Access Tier Management](#63--app-access-tier-management-free--credit-gated--monetization-authorized)
4. [6.4 — Captive Portal Frontend Design](#64--captive-portal-frontend-design)

---

## 6.1 — MAC Randomization: Field Evidence from Philippine PisoWifi Community

### How Existing Platforms Handle MAC Randomization

#### JuanFi — "Kick Old Session" Script

JuanFi implements a **"Random MAC Synchronizer"** via a MikroTik on-login script. Controlled by `isRandomMacSyncFix` (default: `0` / disabled) in the hotspot user profile.

**Mechanism:** When a device reconnects with a new randomized MAC but the same voucher/username, the script:
1. Captures the MAC address of the current login (`cmac`)
2. Iterates through all active hotspot sessions matching the same username
3. Removes any active session whose MAC differs from the current one

```
:if ($isRandomMacSyncFix=1) do={
  :local cmac $"mac-address";
  :foreach AU in=[/ip hotspot active find user="$user"] do={
    :local amac [/ip hotspot active get $AU mac-address];
    :if ($cmac!=$amac) do={ /ip hotspot active remove [/ip hotspot active find mac-address="$amac"]; }
  }
}
```

**Limitation:** This is a "kick the old session" approach — it does NOT preserve session continuity. Remaining time from the old MAC-bound session is lost unless managed through the voucher system. The JuanFi wiki explicitly states: *"There's no really a fix for random mac address currently available for Mikrotik, and its more on mikrotik side to develop a way how to do the synchronization."*

- Source: [JuanFi GitHub Wiki — Random MAC Synchronization](https://github.com/ivanalayan15/JuanFi/wiki/Random-Mac-Synchronization)
- Source: [JuanFi README (master branch)](https://github.com/ivanalayan15/JuanFi/blob/master/README.md)

#### AdoPiSoft — Cookie-Based MAC Synchronizer (Closest to StudentHub)

AdoPiSoft implements the most sophisticated MAC randomization handling in two layers:

**1. MAC Synchronizer (cookie-based):**
> *"MAC Synchronizer (random MAC fix) — MAC synchronizer depends on browser cookies. To make this work, the user must have cookie support in their browser. If cookie is not supported in their browser, device identification falls back to MAC address."*

**2. Passcode-based session sync:**
> *"Passcode can be use to sync previous session records when client's mac address has changed. Auto-prompt passcode to clone devices without blocking them to access the captive portal."*

**3. Link sessions to customer account:**
> *"Fixes the issue on phones with auto-changing mac address."*

**Key difference from StudentHub:** AdoPiSoft still uses MAC as the fallback when cookies are unavailable, and the system is still architecturally **MAC-first with cookies as a sync mechanism**. StudentHub inverts this — cookies/HTTP-only tokens are the primary identity, with `device_id` in PostgreSQL as the canonical session anchor.

- Source: [AdoPiSoft Releases README](https://github.com/AdoPiSoft/Releases/blob/master/README.md)

#### WiFi5-Soft — MikroTik-Side "Fix Random Mac"

WiFi5-Soft addresses MAC randomization through MikroTik-side configuration, marketed as **"Fix Random Mac"** in tutorials. From the KLCiS-WiFi5-Soft README:

> *"WiFi5-Soft is celebrated as one of the most popular WiFi vending software for 2023... It has successfully attracted a large number of clients who have migrated from older systems due to its resolution of RANDOM MAC problems."*

The fix appears to be MikroTik firewall/routing configuration rather than an application-layer solution.

- Source: [KLCiS-WiFi5-Soft GitHub](https://github.com/darkhoundz/KLCiS-WiFi5-Soft)
- Source: [WiFi5-Soft VLAN + Fix Random Mac tutorial (YouTube)](https://www.youtube.com/watch?v=KwnfepWGjkM)

#### PisoFi — Cookie-Based Session Persistence

PisoFi implements the most user-facing approach:

> *"Regardless of MAC and IP randomization, every client should be able to transfer from one AP to another without the hassle of losing credit or time."*
> *"Login only once to any browser and your session will be remember to any browser, even your ip or mac changes"*
> *"Remember client sessions when switching APs (no need to login account)"*

PisoFi's approach appears to be **cookie-based session persistence** that decouples session identity from MAC address. Architecture details are proprietary.

- Source: [PisoFi Releases](https://pisofiph.com/blog/pisofi-releases)
- Source: [PisoFi Features](https://pisofiph.com/blog/pisofi-features)

#### iWiFi Portal (Additional Platform Found)

> *"Reimplemented account based timer synchronizer for randomized mac problems. This was first introduced last 2021 under 5.0.0 version which we discarded before."*

- Source: [iWiFi Portal changelog v5](https://www.iwifi-portal.com/changelog-v5)

### WPA2-PSK for MAC Stabilization — Not Used by Any Platform

**No PisoWifi platform forces WPA2-PSK to stabilize MACs.** The reason: the UX cost outweighs the benefit.

#### Apple's MAC Randomization by Network Security Type

| Network Security | iOS Default (18+) | Behavior |
|---|---|---|
| WPA2 or stronger | **Fixed** | Private address does not rotate |
| Weak or no security (open) | **Rotating** | Private address rotates every 2 weeks |

On an open PisoWifi network, iPhone users get a new MAC every 2 weeks by default. On WPA2-PSK, the private address stays fixed until network is forgotten or factory reset.

- Source: [Apple Support — About private Wi-Fi addresses](https://support.apple.com/en-us/102509)

#### UX Tradeoffs of WPA2-PSK for PisoWifi

| Factor | Open Network | WPA2-PSK |
|---|---|---|
| Initial connection | Connect + auto-redirect to portal | Enter password, then portal redirect |
| iOS MAC behavior (18+) | Rotating MAC (every 2 weeks) | Fixed private MAC |
| Android MAC behavior | Persistent per-SSID | Persistent per-SSID |
| Password friction | None | Extra step, problematic for low-literacy users |
| Group password leaks | N/A | Shared password posted on wall; anyone can share |
| Security benefit | None (traffic visible on air) | Per-session encryption (but shared PSK = any user can decrypt others) |
| Captive portal compatibility | Seamless | Works but adds a step |

From MikroTik forum discussion on MAC randomization, user **harunca** notes: *"http cookies are a good solution for verification"* on Android/Windows/Linux, but **"iOS denies this"** (referring to iOS captive portal browsers not sharing cookies with Safari).

- Source: [MikroTik Forum — Randomised Private MAC](https://forum.mikrotik.com/t/randomised-private-mac-address-causing-issues-with-hotspot-signin/158394)
- Source: [Security StackExchange — Free hotspot open WiFi vs WPA2](https://security.stackexchange.com/questions/68748/free-hotspot-open-wifi-vs-wpa2-wifi-with-known-password)

**Conclusion:** None of the four platforms forces WPA2-PSK. The UX cost (password entry for P1-per-session users) outweighs the MAC stabilization benefit.

### Is StudentHub the First Cookie-First Identity Architecture?

**No — but StudentHub is the first CLEAN cookie-first architecture.**

| Feature | AdoPiSoft | PisoFi | MikroTik `cookie` method | StudentHub |
|---|---|---|---|---|
| Primary identity | MAC (with cookie sync) | Unclear (proprietary) | MAC or cookie | **HTTP-only cookie → device_id in PostgreSQL** |
| Cookie role | Supplementary sync | Session persistence | Auto-re-auth | **Canonical identity** |
| MAC role | Primary identifier | Superseded by cookie | One of multiple methods | **Not used for identity** |
| Database-backed session | No (MikroTik internal) | Likely | No (MikroTik internal) | **Yes (PostgreSQL)** |
| Cross-AP session continuity | Via passcode | Yes | Via mac-cookie | **Via shared cookie + DB** |

From academic evidence (Freudiger et al.): *"Hotspots can use these cookies to uniquely identify and authenticate user devices even when the device MAC address is dynamically changed."* This confirms cookie-based identity is a known pattern in hospitality Wi-Fi, but NOT documented as a primary identity mechanism in PisoWifi.

- Source: [Freudiger et al. — Captive Portal Privacy (arXiv:1907.02142)](https://arxiv.org/pdf/1907.02142)

**Validated Confidence Level for StudentHub's browser-token architecture:** **HIGH**. AdoPiSoft and PisoFi both validate the cookie-based approach as a partial solution. StudentHub's full cookie-first architecture is architecturally sound, but must account for the iOS CNA cookie-destruction problem (cookies set in the CNA mini-browser are destroyed on close). The MAC-address recognition + Student ID linking serve as recovery mechanisms.

### Real-World Device Mix Among Filipino Students

| Platform | Market Share (Philippines) |
|---|---|
| **Android** | **~88.68%** (mobile) |
| **iOS** | **~11.27%** (mobile) |
| Windows | ~37% (all platforms combined) |
| macOS | ~2% (all platforms combined) |

**Top mobile vendors:** Oppo (10.84%), Samsung (9.96%), Realme (9.11%), Vivo (8.83%), Apple (11.27%). The 25.81% "Unknown" vendor share likely includes Tecno, Infinix, Xiaomi.

- Source: [StatCounter OS Market Share — Mobile Philippines (April 2026)](https://gs.statcounter.com/os-market-share/mobile/philippines)
- Source: [StatCounter Vendor Market Share — Mobile Philippines (April 2026)](https://gs.statcounter.com/vendor-market-share/mobile/philippines)
- Source: [StatCounter OS Market Share — All Philippines (Feb 2026)](https://gs.statcounter.com/os-market-share/all/philippines)

#### MAC Randomization Behavior by Platform

| Platform | MAC Behavior on Open Networks |
|---|---|
| **Android 12+** | **Non-persistent**: re-randomizes after 24h inactivity on open networks without captive portal detection |
| **Android 10-11** | Persistent per-SSID until factory reset |
| **iOS 18+** | Rotating: new private MAC every 2 weeks on open networks |
| **iOS 14-17** | One private MAC per SSID, reused on reconnection |
| **Windows 10/11** | "Random hardware address" off by default; often broken by drivers |
| **macOS** | Same as iOS for the same version |

**Key finding:** Android 12+'s non-persistent MAC randomization on open networks is the most aggressive MAC rotation behavior. Since ~89% of Filipino mobile users are on Android, this is the primary driver of MAC-based session breakage.

---

## 6.2 — Feature Parity Benchmarking Against Commercial PisoWifi Products

### Product Feature Catalog

#### WiFi5soft (Jonas WiFi5)

| Category | Details |
|---|---|
| Session Flows | Connect → captive portal → insert coins → credit-based time. Centralized multi-vendo. |
| Voucher System | KLCiS e-payment triggers auto voucher code generation with SMS. Codeless from coinslot. |
| Coin/Bill | Universal coin slot (1/5/10 peso). TOP TP70 bill acceptor (4-way, pulse, DC 12V, 96% acceptance). |
| Top-Up | Coin, GCash/PayMaya/GrabPay/ShopeePay via KLCiS (PHP 150/month fee). |
| Admin Dashboard | Web-based at 10.0.0.1. Sales reports, rates config, customizable HTML portal. |
| Hardware | Orange Pi One (primary SBC). No MikroTik dependency. |
| Reporting | Daily/weekly/monthly sales inventory. Wallet balance tracking. |
| Multi-Site | Centralized vendo architecture — one main unit managing multiple wireless sub-vendos. |
| Pricing | License: ~PHP 2,421. Complete set: ~PHP 12,999. |

- Source: [KLCiS-WiFi5-Soft GitHub](https://github.com/darkhoundz/KLCiS-WiFi5-Soft)
- Source: [Flarego/AdoPiSoft shop listing](https://shop.adopisoft.com/products/adopisoft-piso-wifi-vending-machine-high-quality-guaranteed)

#### AdoPiSoft

| Category | Details |
|---|---|
| Session Flows | MAC-based auth (no password). Insert coin → timer starts. Pause/continue. Free trial option. Anti-abuse with retry limits. |
| Voucher System | Print vouchers for weekly/monthly access. Subscription rates. |
| Coin/Bill | Multiple wired AND wireless coin-acceptors simultaneously. TOP TP70 bill acceptor. 1/5/10/20 peso coins. |
| Top-Up | Coin, KLCiS e-payment (GCash, PayMaya, GrabPay, ShopeePay), voucher codes, eLoading. |
| Admin Dashboard | Web-based at 10.0.0.1/admin. Remote management via Android app. Multi-admin support. Customizable webportal. Content filtering. |
| Hardware | ARM boards (Lite) or ARM+x64 (Business). Charging station plugin (GPIO). |
| Reporting | Built-in accounting. Daily/weekly/monthly sales monitoring. |
| Multi-Site | Remote management via AdoPiSoft Manager. No centralized multi-site panel — per-machine access. |
| Pricing | **Lite:** $16.99 (lifetime, 50 users). **Business:** $10/year or $65.99 lifetime. Distributor packs available. |

- Source: [adopisoft.com](https://www.adopisoft.com/)
- Source: [AdoPiSoft WiFi Rates Guide](https://www.adopisoft.com/en/guide/wifi-rates)
- Source: [KLCiS-AdoPisoft-E-Payment](https://github.com/darkhoundz/KLCiS-AdoPisoft-E-Payment)

#### PisoFi

| Category | Details |
|---|---|
| Session Flows | Auto-go-online, auto-pause on disconnect, auto-resume on reconnect. Free trial promos. |
| Voucher System | **WiPass Tickets**: custom vouchers with time/price/rate/expiration. Secured or unsecured. Print, CSV/XLSX/PDF/HTML export. Convert remaining time to WiPass. |
| Coin/Bill | Universal coin slot. Bill acceptor. Pulse rate multiplier. |
| Top-Up | Coin/bill, wallet credits, eload via Coins.ph, **live transfer of time between users on different devices**. |
| Admin Dashboard | Full client management (extend/deduct time, speed limit, disconnect, notifications, custom commands). Chat system (user-to-admin). Multi-admin with permissions. |
| Hardware | Raspberry Pi 4B (50+ users). Orange Pi variants. Desktop app for pisonet. |
| Reporting | Wallet/eload transactions. Sales monitoring. Downloadable WiPass. |
| Multi-Site | Sub-vendo support (up to 10 on Lite). VLAN support. No centralized cloud dashboard. |
| Pricing | **Individual:** PHP 3,150. **Starter:** PHP 12,550. Distributor: PHP 900-7,500. |

**Known Security Issues:** RCE via payload injection. Unauthenticated RCE. Hardcoded credentials. Based on Armbian 5.83 (Debian 9, kernel 4.19.38 — severely outdated).

- Source: [pisofiph.com](https://pisofiph.com/)
- Source: [PisoFi Features](https://pisofiph.com/blog/pisofi-features)
- Source: [PisoFi Vulnerability repo](https://github.com/jkram143/PisoFi-Vulnerability-and-Exploits)

#### JuanFi (Open Source)

| Category | Details |
|---|---|
| Session Flows | Connect to MikroTik hotspot → captive portal → insert coin → ESP creates hotspot user. Pause expiration. Random MAC synchronizer. |
| Voucher System | Codeless from coinslot. LCD display. JuanFi Generator creates up to 5,000 vouchers. |
| Coin/Bill | Universal coin slot via NodeMCU ESP8266/ESP32. Pulse-based. **No native bill acceptor.** |
| Top-Up | Coin insertion. KLCiS e-payment add-on (PHP 150/month). |
| Admin Dashboard | Web-based at ESP module IP. Setup wizard, MikroTik config, promo rates, sales dashboard. Android app. |
| Hardware | **MikroTik only** (hAP lite, hAP ac2, hAP ac3, HEX, RB951, CCR). NodeMCU ESP8266/ESP32. |
| Reporting | Daily/monthly income in MikroTik scripts. Optional Telegram notifications. |
| Multi-Site | Multi-vendo (multiple ESP to one MikroTik). JuanFi Extended Portal. AZK-Manager (PHP/SQLite). |
| Pricing | **Free / Open Source** (MIT license). KLCiS add-on: PHP 150/month. |

- Source: [github.com/ivanalayan15/JuanFi](https://github.com/ivanalayan15/JuanFi)
- Source: [Kintoyyy/JuanFiGenerator](https://github.com/Kintoyyy/JuanFiGenerator)
- Source: [Kintoyyy/AZK-Manager](https://github.com/Kintoyyy/AZK-Manager)

#### LPB Piso WiFi (Feature Leader)

| Category | Details |
|---|---|
| Session Flows | Cloud-synced session. Pause/resume from ANY LPB machine nationwide. Buy Time or Buy Data. PPPoE for monthly subscriptions with SMS reminders. |
| Voucher System | Custom time/data vouchers for resellers. |
| Coin/Bill | Built-in coin slot. PisoNet computer rental. Phone rental coin-operated. |
| Top-Up | Coin, **native GCash and Maya direct payment** (built-in, no third-party), eload/cash-in, wallet system. |
| Admin Dashboard | **LPB Remote Monitoring** (built-in, no NGROK). Customizable portal theme. Multi-subvendo with auto VLAN. PPPoE management. 2-step email verification. |
| Hardware | Raspberry Pi 3/4/5, Orange Pi, Newifi 3, MXQ Android Box, Ruijie EW1200G PRO, Linksys EA8300, TP-Link TL-WR841N. |
| Reporting | Real-time wallet balance, credit transfers, license tracking. Detailed transaction logs with export. |
| Multi-Site | Centralized cloud system. Machine transfer between distributor accounts. 21 distributors nationwide. |
| Pricing | **Lite:** PHP 400/year. **Premium:** PHP 700/year. **Lifetime V2:** PHP 1,500. Eload: PHP 500. |

- Source: [lpbpisowifi.com](https://lpbpisowifi.com/)
- Source: [LPB Licenses](https://lpbpisowifi.com/dashboard/licensesshop)

**Note on Tplex:** Extensive searching found no distinct software product called "Tplex." It appears in e-commerce listings as a reseller/brand name for pre-built PisoWifi machines running LPB or WiFi5soft software.

### Feature Comparison Matrix: StudentHub vs. All Competitors

| Feature | StudentHub | WiFi5soft | AdoPiSoft | PisoFi | JuanFi | LPB |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Coin-op session flow | Planned | Yes | Yes | Yes | Yes | Yes |
| Pause/Resume | Planned | Yes | Yes | Yes | Yes | Yes |
| Captive portal splash | Planned (openNDS) | Yes | Yes | Yes | Yes | Yes |
| Configurable rates | Planned | Yes | Yes | Yes | Yes | Yes |
| Voucher codes | Planned | Yes (KLCiS) | Yes | WiPass | Generator | Yes |
| GCash/Maya native | Planned | No (KLCiS) | No (KLCiS) | No | No (KLCiS) | **Yes** |
| Bill acceptor | Planned | Yes | Yes | Yes | No | Yes |
| Admin dashboard | Planned (Laravel) | Basic | Full | Full | Basic | Full (cloud) |
| Multi-site management | Planned (cloud) | Centralized vendo | Per-machine remote | Per-machine | Per-machine | **Cloud** |
| Content filtering | Planned | No | Yes | No | No | No |
| Chat (user↔admin) | Not planned | No | No | Yes | No | No |
| Eloading | Not planned | No | Yes | Yes | No | Yes |
| Charging station | Not planned | No | Plugin | Yes | No | Yes |
| Security posture | **Modern** (no hardcoded secrets, updated OS) | Unknown | Good | **Critical RCE** | Good (MIT) | Good |
| MAC randomization fix | **Cookie-first (architectural)** | MikroTik fix | Cookie sync | Cookie persistence | Kick-old-session | Unknown |
| Browser-token identity | **Yes (primary)** | No | No (supplementary) | Partial | No | No |
| Student intranet | **Yes (3-tier)** | No | No | No | No | No |
| Campus-specific | **Yes** | No | No | No | No | No |
| Open source | Partial | No | No | No | **Yes (MIT)** | No |
| Proxmox/VM architecture | **Yes** | No (SBC) | No (SBC) | No (SBC) | No (MikroTik) | No (SBC) |
| PostgreSQL | **Yes** | No | No | No | No | No |
| ESP32 vending HW | **Yes** | No | No | No | Yes (ESP8266) | No |

### Phase 1 Table-Stakes vs. Phase 2 Nice-to-Have

#### Phase 1 — Absolute Table-Stakes (Must Ship)

| # | Feature | Justification |
|---|---|---|
| 1 | Coin-operated session flow | Defining feature of the category. All competitors have this. |
| 2 | Captive portal / splash page | Users expect to connect and be redirected. |
| 3 | Pause/Resume time | Users consider it a right, not a feature. All competitors support this. |
| 4 | Configurable time rates (PHP 1 = X minutes) | Core monetization mechanism. |
| 5 | Admin dashboard with sales reporting | Minimum operator expectation. |
| 6 | Voucher code generation | All competitors support some form of this. |
| 7 | Universal coin slot support (1/5/10 peso) | Philippine market requires all denominations. |
| 8 | Bandwidth limiter per user | Prevents abuse. AdoPiSoft, PisoFi, LPB all include this. |
| 9 | MAC randomization mitigation | #1 community pain point. StudentHub's cookie-first approach is the architectural fix. |
| 10 | Anti-abuse system (fake insert detection) | Essential for unattended machines. |

#### Phase 2 — Nice-to-Have (Post-Launch)

| # | Feature | Priority | Present In |
|---|---|---|---|
| 1 | **GCash/Maya native e-payment** | HIGH | LPB only (native); others need KLCiS |
| 2 | **Cloud-synced sessions** | HIGH | LPB only |
| 3 | Bill acceptor support | MEDIUM | AdoPiSoft, WiFi5soft |
| 4 | Multi-vendo / sub-vendo | MEDIUM | All products |
| 5 | Content filtering | MEDIUM | AdoPiSoft |
| 6 | WiPass / time transfer between devices | MEDIUM | PisoFi only |
| 7 | PPPoE server (monthly subs) | MEDIUM | LPB |
| 8 | Anti-tethering / TTL manipulation | MEDIUM | iWiFi Portal |
| 9 | Eloading integration | LOW | AdoPiSoft, LPB, PisoFi |
| 10 | Charging station | LOW | AdoPiSoft (plugin), PisoFi, LPB |
| 11 | Desktop/PisoNet mode | LOW | PisoFi, LPB |
| 12 | Chat system (user↔admin) | LOW | PisoFi |
| 13 | Telegram notifications | LOW | JuanFi |
| 14 | Phone rental mode | LOW | LPB |
| 15 | VPN blocking | LOW | iWiFi Portal |

### UI/UX Patterns Filipino Students Expect

| UI Element | Description | Source Products |
|---|---|---|
| **Timer display** | Prominent countdown (HH:MM:SS). Must be visible at all times. | PisoFi, LPB, AdoPiSoft, JuanFi |
| **Pause button** | Large, clearly labeled "PAUSE". PisoFi shows pause count and configurable max pause time. | All products |
| **Remaining balance** | Peso equivalent of remaining time. | PisoFi, LPB |
| **WiFi signal indicator** | Connection indicator on portal. | PisoFi |
| **Insert Coin button** | Large button triggering coin slot wait mode. | All products |
| **Promo/rate cards** | Button list showing rate tiers. | All products |
| **Carousel/banner ads** | PisoFi supports carousel banner display. Operators use for ad revenue. | PisoFi |
| **WiPass/Voucher entry** | Text input for voucher codes. | PisoFi, JuanFi |
| **Green color scheme** | Peso values displayed in green. | PisoFi, KLCiS templates |
| **Mobile-first** | Large touch targets (44x44px minimum). Simple one-screen flow. | All products |

### Biggest Pain Points from Community

#### Operator Pain Points

| # | Pain Point | Products Affected |
|---|---|---|
| 1 | **Random MAC address problems** | All MikroTik-based (JuanFi, older systems) |
| 2 | **Coins go through but no time added** | All (wiring/calibration issue) |
| 3 | **Ghost credits / coin reading inaccuracy** | PisoFi (Raspberry Pi) — fixed in v4.6.0 |
| 4 | **Power interruption losing sessions** | All products |
| 5 | **Overheating / random reboots** | All hardware-based |
| 6 | **Security vulnerabilities (RCE, hardcoded credentials)** | PisoFi (critical) |
| 7 | **No native e-payment** | AdoPiSoft, JuanFi, WiFi5soft (need KLCiS) |
| 8 | **No centralized multi-site management** | AdoPiSoft, PisoFi, JuanFi |

#### End-User Pain Points

| # | Pain Point | Description |
|---|---|---|
| 1 | Time runs out too quickly | Device sleep, unstable signals, timer bugs |
| 2 | Portal page doesn't load | Browser cache/DNS issues |
| 3 | Slow speeds with many users | Bandwidth divided among concurrent users |
| 4 | Coins accepted but no internet | Server error or broken coinslot-router connection |
| 5 | Lost time after power outage | No session persistence across reboots |
| 6 | Cannot transfer remaining time to another device | Only PisoFi supports live transfer |
| 7 | No cashless payment option | Most machines are coin-only |

- Sources: [wifi.tips troubleshooting](https://wifi.tips/piso-wifi-vendo/), [weeklyavoid.com common problems](https://weeklyavoid.com/common-problems-when-using-piso-wifi-and-how-to-fix-them/), [PisoFi v4.6.0 changelog](https://www.facebook.com/1WifiBiz/posts/640964849881541/)

### Strategic Insights for StudentHub

1. **LPB is the feature leader** — cloud-synced sessions, native GCash/Maya, centralized management, widest hardware support, PHP 400-700/year pricing. Target feature parity with LPB as aspirational benchmark.
2. **JuanFi is the open-source baseline** — free, MikroTik-integrated. StudentHub differentiates by eliminating MikroTik complexity.
3. **PisoFi has the richest portal UX** — WiPass, live transfer, carousel banners, chat. But critical security vulnerabilities.
4. **AdoPiSoft is the commercial standard** — most professionally managed, distributor network, official apps.
5. **WiFi5soft's RANDOM MAC fix was a market-moving feature** — StudentHub's cookie-first architecture is the proper fix.
6. **GCash integration is the #1 Phase 2 priority** — students increasingly cashless. Only LPB has native e-payment.
7. **Security is an underserved market gap** — PisoFi ships RCE + hardcoded credentials on outdated kernel. StudentHub differentiates with modern security.

---

## 6.3 — App Access Tier Management (Free / Credit-Gated / Monetization-Authorized)

### 3-Tier Intranet Model Without Manual iptables

**Architecture: Traefik routers + forwardAuth middleware per tier.** Every app container registers via Coolify Docker labels, and Traefik enforces tier access at the proxy layer before traffic reaches the container.

| Tier | Traefik Mechanism | What Happens |
|---|---|---|
| **Free** | No middleware applied | Any device on VLAN 30 can reach it |
| **Credit-Gated** | `forwardAuth` → `/api/auth/credit-check` | Traefik sends sub-request to Laravel; 2XX = proceed, non-2XX = return auth error |
| **Monetization-Authorized** | `forwardAuth` → `/api/auth/monetization-check` | Same pattern but checks purchase/subscription entitlement |

#### Docker Label Configuration per Tier

```yaml
# FREE TIER — no middleware
services:
  school-website:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.school-website.rule=Host(`school.intranet`)"
      - "traefik.http.routers.school-website.entrypoints=web"
      # NO middleware = free access

  # CREDIT-GATED TIER
  wikipedia:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.wikipedia.rule=Host(`wiki.intranet`)"
      - "traefik.http.routers.wikipedia.entrypoints=web"
      - "traefik.http.routers.wikipedia.middlewares=credit-gate"
      - "traefik.http.middlewares.credit-gate.forwardauth.address=http://laravel-backend:80/api/auth/credit-check"
      - "traefik.http.middlewares.credit-gate.forwardauth.authResponseHeaders=X-User-Id,X-Session-Id,X-Remaining-Balance"
      - "traefik.http.middlewares.credit-gate.forwardauth.authRequestHeaders=Cookie"

  # MONETIZATION-AUTHORIZED TIER
  premium-gaming:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.premium-gaming.rule=Host(`games.intranet`)"
      - "traefik.http.routers.premium-gaming.entrypoints=web"
      - "traefik.http.routers.premium-gaming.middlewares=monetization-gate"
      - "traefik.http.middlewares.monetization-gate.forwardauth.address=http://laravel-backend:80/api/auth/monetization-check"
      - "traefik.http.middlewares.monetization-gate.forwardauth.authResponseHeaders=X-User-Id,X-Subscription-Tier"
      - "traefik.http.middlewares.monetization-gate.forwardauth.authRequestHeaders=Cookie"
```

- Source: [Traefik forwardAuth docs](https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/forwardauth)

#### Laravel Auth Endpoints

```php
// routes/api.php
Route::get('/auth/credit-check', [TierAuthController::class, 'creditCheck']);
Route::get('/auth/monetization-check', [TierAuthController::class, 'monetizationCheck']);

// TierAuthController
public function creditCheck(Request $request): JsonResponse
{
    $deviceId = $request->cookie('device_token');

    $session = Session::where('device_id', $deviceId)
        ->where('expires_at', '>', now())
        ->where('remaining_balance', '>', 0)
        ->first();

    if (!$session) {
        return response()->json(['error' => 'No active session with balance'], 402);
    }

    return response()->json(['status' => 'authorized'])
        ->header('X-User-Id', $session->user_id)
        ->header('X-Session-Id', $session->id)
        ->header('X-Remaining-Balance', $session->remaining_balance);
}

public function monetizationCheck(Request $request): JsonResponse
{
    $deviceId = $request->cookie('device_token');
    $targetApp = $request->header('X-Forwarded-Host');

    $entitlement = Entitlement::where('device_id', $deviceId)
        ->where('app_slug', $this->slugFromHost($targetApp))
        ->where('expires_at', '>', now())
        ->first();

    if (!$entitlement) {
        return response()->json(['error' => 'No subscription'], 403);
    }

    return response()->json(['status' => 'authorized'])
        ->header('X-User-Id', $entitlement->user_id)
        ->header('X-Subscription-Tier', $entitlement->tier);
}
```

### Traefik forwardAuth vs. Laravel Reverse-Proxy — Decision

| Dimension | Traefik forwardAuth (Recommended) | Laravel Reverse Proxy |
|---|---|---|
| **Latency** | +1 sub-request (~5-15ms auth check). Original request goes direct: Traefik→App. | +1 full hop for EVERY request: Client→Traefik→Laravel→App→Laravel→Traefik→Client |
| **Streaming** | No impact. Traefik streams directly to app after auth. | **Broken**. Laravel must buffer entire response (Guzzle constraint). Large files/video degrade. |
| **Complexity** | Distributed config (Docker labels + Laravel). Two systems. | Single codebase in Laravel. Easier initially. |
| **Scalability** | Auth endpoint lightweight (~1KB). Easily cached via Redis. | **Every byte** passes through Laravel. PHP-FPM bottleneck at campus scale. |
| **Failure mode** | Laravel auth down → credit/premium apps return 502. **Free apps unaffected**. | Laravel down → **ALL apps go down** including free ones. Single point of failure. |
| **Coolify integration** | Labels are native to Coolify's Docker model. | Requires custom compose routing all traffic to Laravel. Breaks Coolify model. |
| **Debugging** | Traefik API + Laravel logs. Two places. | Single Laravel log. But proxy bugs (headers stripped, timeouts) harder to diagnose. |

**Verdict: Traefik forwardAuth is strongly recommended.** Laravel reverse proxy creates a bandwidth bottleneck that is disqualifying at campus scale. Traefik handles the data plane (heavy traffic proxying) natively in Go; Laravel should only handle the control plane (auth decisions).

### Admin Dashboard: Real-Time Tier Change Propagation

**Recommended: Hybrid approach — Traefik File Provider + Database-Driven Auth + Redis Pub/Sub**

#### 1. Traefik File Provider with `watch: true` (Router Wiring)

Traefik watches a directory for file changes. When a YAML file changes, Traefik hot-reloads dynamic configuration without container restarts.

```yaml
# Traefik static config
providers:
  file:
    directory: "/etc/traefik/dynamic"
    watch: true  # Auto-reload on file change
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
```

```yaml
# /etc/traefik/dynamic/app-tiers.yml — generated by Laravel
http:
  middlewares:
    credit-gate:
      forwardAuth:
        address: "http://laravel-backend:80/api/auth/credit-check"
        authRequestHeaders:
          - Cookie
        authResponseHeaders:
          - X-User-Id
          - X-Session-Id
          - X-Remaining-Balance

  routers:
    wiki-router:
      rule: "Host(`wiki.intranet`)"
      service: wiki-service@docker
      middlewares:
        - credit-gate
      entryPoints:
        - web
```

- Source: [Traefik Dynamic Configuration docs](https://doc.traefik.io/traefik/reference/routing-configuration/dynamic-configuration-methods/)

#### 2. Database-Driven forwardAuth Endpoint (Actual Policy)

The Laravel auth endpoint checks the DATABASE for the current tier assignment on every request. This means the endpoint is always the source of truth, and tier changes in the database take effect on the very next request.

```php
// Single auth endpoint that checks tier from DB
Route::get('/auth/access-check', function (Request $request) {
    $targetHost = $request->header('X-Forwarded-Host');
    $deviceId = $request->cookie('device_token');

    $app = Cache::remember("app:tier:{$targetHost}", 30, function () use ($targetHost) {
        return App::where('host', $targetHost)->first();
    });

    if ($app->tier === 'free') {
        return response()->json(['status' => 'ok'], 200);
    }
    // ... credit/premium checks
});
```

#### 3. Redis Pub/Sub for Cache Invalidation

When an admin changes a tier, Laravel publishes to Redis. All Laravel instances subscribe and invalidate their cache.

```php
class AppTierController extends Controller
{
    public function update(Request $request, App $app)
    {
        $oldTier = $app->tier;
        $app->update(['tier' => $request->tier]);

        // Invalidate cache via Redis pub/sub
        Redis::publish('tier:changed:' . $app->slug, json_encode([
            'app_slug' => $app->slug,
            'old_tier' => $oldTier,
            'new_tier' => $request->tier,
        ]));

        // If tier crosses a boundary (free <-> gated), update Traefik config
        if ($this->affectsMiddleware($oldTier, $request->tier)) {
            $this->traefikConfigWriter->regenerateAndWrite();
        }

        return response()->json(['updated' => true]);
    }
}
```

#### Traefik Config Writer (Atomic File Write)

```php
class TraefikConfigWriter
{
    public function regenerateAndWrite(): void
    {
        $apps = App::all();
        $config = $this->buildConfig($apps);

        // Atomic write: temp file then rename
        $tempPath = '/etc/traefik/dynamic/app-tiers.yml.tmp';
        $finalPath = '/etc/traefik/dynamic/app-tiers.yml';

        File::put($tempPath, Yaml::dump($config, 10, 2));
        rename($tempPath, $finalPath); // Atomic on same filesystem

        // Traefik file provider watch detects change within ~2s
    }
}
```

#### Tier Change Flow (End-to-End)

1. Admin clicks "Change Wikipedia to Free" in dashboard
2. Laravel updates `apps` table: `tier = 'free'`
3. Laravel publishes `tier:changed:wikipedia` to Redis
4. All Laravel worker processes invalidate their `app:tier:wiki.intranet` cache
5. Laravel's `TraefikConfigWriter` regenerates `/etc/traefik/dynamic/app-tiers.yml`, removing `credit-gate` middleware from `wiki-router`
6. Traefik detects file change (inotify, <2s) and reloads routing
7. Subsequent requests to `wiki.intranet` bypass auth entirely
8. **Total propagation: < 5 seconds. Zero downtime. Zero container restarts.**

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        ADMIN DASHBOARD                           │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  App Tier Manager                                     │       │
│  │  [Free] [Credit-Gated] [Monetization]   [Save]       │       │
│  └──────────────┬───────────────────────────────────────┘       │
│                 │                                                  │
│     ┌───────────┼───────────┐                                     │
│     ▼           ▼           ▼                                     │
│  PostgreSQL    Redis       TraefikConfig                          │
│  (tier=free)  (pub/sub)   (write YAML)                           │
└─────┬─────────────┬─────────────┬─────────────────────────────────┘
      │             │             │
      │             │             ▼
      │             │    ┌─────────────────────┐
      │             │    │  /etc/traefik/dynamic│
      │             │    │  /app-tiers.yml      │
      │             │    └──────────┬──────────┘
      │             │               │ inotify watch
      │             │               ▼
      │             │    ┌─────────────────────┐
      │             │    │      TRAEFIK        │
      │             │    │  (hot reload <2s)  │
      │             │    └──┬──────┬──────┬────┘
      │             │       │      │      │
      │    cache    │    ┌──┘  ┌──┘  ┌──┘
      │   invalidate│    │     │     │
      ▼             ▼    ▼     ▼     ▼
┌──────────┐  ┌──────┐ ┌────┐ ┌────┐ ┌────────┐
│ Laravel  │  │Laravel│ │Free│ │Gated│ │Premium │
│ Auth API │  │Workers│ │App │ │App  │ │App     │
│(DB check)│  │(cache)│ │    │ │     │ │        │
└──────────┘  └──────┘ └────┘ └─────┘ └────────┘
                  ▲
                  │ forwardAuth sub-request
                  │ (only for credit-gated + monetization)
                  │
          ┌───────┴───────┐
          │  CLIENT DEVICE │
          └───────────────┘
```

---

## 6.4 — Captive Portal Frontend Design

### Framework Evaluation: CPD Browser Compatibility

#### CPD Browser Compatibility Matrix

| Platform | Display | Engine | JS | localStorage | Cookies | ES Modules | fetch/XHR | External Files | Self-Close |
|---|---|---|---|---|---|---|---|---|---|
| **iOS** | CNA mini-browser | Restricted WebKit | Limited; AJAX doesn't trigger CPD re-check | **NO — crashes CNA** | Session-only; destroyed on close | **NO** | fetch works; AJAX doesn't re-trigger CPD | Blocked by CPD policy | After auth; "Cancel" disassociates |
| **Android 12+** | Chrome Custom Tab | Full Chrome | **Full** | YES (shared) | YES (shared) | YES | YES | YES | Minimizable |
| **Android legacy** | WebView | Chromium WebView | Most JS | Isolated | Isolated | Partial | YES | Limited | Closes on auth |
| **macOS** | CNA mini-browser | Safari WebKit | **No** `alert()`/`confirm()` | **NO** | Session-only | **NO** | Limited | Blocked | Fixed 900x572px |
| **Windows** | Default browser | Chrome/Edge/Firefox | **Full** | YES | YES (persistent) | YES | YES | YES | N/A |
| **ChromeOS** | Chrome tab | Chrome | Full | YES | YES | YES | YES | YES | N/A |

- Source: [WBA Captive Behavior Reference](https://captivebehavior.wballiance.com/)
- Source: [openNDS customize docs](https://opennds.readthedocs.io/en/stable/customize.html)
- Source: [SO#30353380 — localStorage crashes iOS CNA](https://stackoverflow.com/questions/30353380)
- Source: [Apple Developer Forums — CNA limitations](https://developer.apple.com/forums/thread/75498)

#### iOS CNA Critical Technical Limitations

- **localStorage/sessionStorage**: Accessing `localStorage` **crashes the CNA**. AngularJS apps fail because Angular's default localStorage module causes the entire page to fail to render.
- **ES Modules**: Not supported. `<script type="module">` does not work.
- **Cookies**: Set during CNA session are **destroyed when CNA closes**. No persistent cookies survive.
- **window.alert()/confirm()**: Non-functional in macOS CNA; unreliable on iOS CNA.
- **Focus switching**: Switching to another app dismisses CNA. Pressing "Cancel" disassociates from SSID.
- **CNA User-Agent detection**: Pre-iOS 10.3 included "CaptiveNetworkSupport"; post-10.3 uses standard Safari UA but omits "Safari". Detect by absence of "Safari" + presence of WebKit.
- **iOS 14+ improvement**: DHCP/RA Captive Portal options (RFC 8908) allow portal to provide session status as JSON.

#### Android 12+ Custom Tabs

Android 12+ supports **Custom Tabs** for captive portal login — significant upgrade:
- Full primary browser engine (Chrome)
- One-tap autofill for credentials/payments
- Background persistence
- VPN/Private DNS compatibility
- Requires DHCP Option 114 + `"x-android-use-custom-tabs": 361335020` in JSON response
- Source: [source.android.com — Custom Tabs Captive Portal](https://source.android.com/docs/core/connect/android-custom-tabs-captive-portal)

#### Framework Evaluation Summary

| Criteria | Svelte 5 | React | Vue 3 | Plain HTML/JS |
|---|---|---|---|---|
| **Compiled output** | Vanilla JS, no runtime | Requires React runtime (~42KB) | Requires Vue runtime (~33KB) | Zero overhead |
| **Bundle size** | ~2-5KB (compiler strips framework) | ~45-50KB minimum | ~35-40KB minimum | As written |
| **iOS CNA compat** | Requires `Proxy` + `ResizeObserver` — **incompatible** | Runtime likely blocked | Same | **Works** if JS works; failsafe works naturally |
| **Progressive enhancement** | Hard; requires JS to render | Hard; requires JS | Hard; requires JS | **Native** — HTML works without JS |
| **openNDS ThemeSpec** | Cannot use (generates server-side) | Same | Same | Compatible |
| **Dev experience** | Best for component-based UI | Rich ecosystem | Good | Simple but verbose |

### RECOMMENDATION: Dual-Mode Architecture

**Do NOT use Svelte 5, React, or Vue as the primary rendering layer for the captive portal splash page.**

**Approach: Plain HTML/CSS core + optional Svelte 5 enhancement layer**

1. **Core splash page** (MUST work everywhere, including iOS CNA): Plain HTML + inline CSS. Zero JavaScript dependency. Served as initial page that renders in ALL CPD environments.

2. **Enhanced dashboard** (full browsers after auth): Svelte 5 compiled SPA served from FAS Node.js server. Handles real-time timer, pause/resume, balance display, coin animation, app launcher grid. Only loads in full browsers.

3. **Detection**: Server checks User-Agent. CNA browser → plain HTML. Full browser → Svelte-enhanced version. `<noscript>` fallback as safety net.

**Rationale**: Svelte 5 requires `Proxy` and `ResizeObserver` which are incompatible with CNA. iOS CNA may block all JS entirely. Plain HTML is the only format guaranteed to render across all CPD implementations. Once authenticated in a full browser, Svelte 5 provides the best dev experience and smallest bundle.

### Splash Page Layout Design

#### Core Splash Page (Plain HTML, CNA-compatible)

```
+------------------------------------------+
|  [StudentHub Logo]                       |
|  "Welcome to StudentHub WiFi"            |
+------------------------------------------+
|                                          |
|    PHP 5.00                    [coin icon]|
|    Current Balance                       |
|                                          |
|  +------------------------------------+ |
|  |  00:29:45                          | |
|  |  Session Timer                     | |
|  +------------------------------------+ |
|                                          |
|  [  Pause  ]    [  Resume  ]             |
|                                          |
|  +------------------------------------+ |
|  | Link to Student ID               | |
|  | (Save your balance! Tap here)     | |
|  +------------------------------------+ |
|                                          |
|  Top-Up: [1 Peso] [5 Peso] [10 Peso]    |
|          [GCash]                          |
|                                          |
|  Coin inserted! +PHP 5.00  (animation)  |
|                                          |
|  +------------------------------------+ |
|  |  Campus Apps                       | |
|  |  [CRS] [LMS] [Lib] [Mail] [Org]   | |
|  |  [Map] [Evt] [SIS] [New] [Dir]    | |
|  +------------------------------------+ |
|                                          |
+------------------------------------------+
|  Warning: Clearing cookies or using      |
|  incognito mode will lose your session.  |
|  Link your Student ID to keep your       |
|  balance safe.                            |
+------------------------------------------+
```

#### UI Component Inventory

| Element | Core HTML | Enhanced (Svelte) |
|---|---|---|
| **Current balance** | Static text, updated on page reload | Reactive `$state()` with animated counter |
| **Session timer** | Server-rendered, meta-refresh countdown | `setInterval` countdown with HH:MM:SS, pause/resume |
| **Pause/Resume** | HTML form POST, two buttons | Single toggle with animated state change |
| **Student ID link** | Anchor to linking page | In-page modal with verification |
| **Coin insert animation** | CSS-only animation / static text | Svelte transition with coin-drop SVG |
| **Top-up options** | HTML form buttons (POST) | Styled interactive buttons, GCash deep-link/QR |
| **App launcher grid** | Static HTML anchor grid | Animated grid with lazy-loaded favicons, search/filter |

#### Portal States Wireframe Descriptions

| State | Display | User Action |
|---|---|---|
| **Initial (no session)** | Welcome message, "Insert Coin" button, Student ID link, rate cards | Insert coin or enter voucher |
| **Active session** | Balance, timer (countdown), pause/resume, app launcher | Use services, top-up, pause |
| **Paused** | Balance (frozen), "PAUSED" badge, resume button | Resume or top-up |
| **Low balance warning** | Balance in amber/yellow, "Insert more coins" prompt | Top-up |
| **Expired** | "Session ended" message, "Insert coin to continue" CTA | Start new session |
| **Coin inserted** | "+PHP X" animation, updated balance, refreshed timer | Continue browsing |
| **Linking Student ID** | Student ID input field, verification status | Enter ID, verify |
| **Error/Offline** | "System temporarily unavailable" message, auto-retry | Wait for recovery |
| **Incognito warning** | Persistent amber banner: "Clearing cookies loses your session" | Dismiss or link Student ID |

### Incognito Mode Warning UX

#### The Problem

Browser-token identity uses HTTP-only cookies. In CPD contexts:
- iOS/macOS CNA **destroys all cookies on close**
- Android captive portal WebView cookies are **not shared** with main Chrome
- Incognito/private mode **clears all cookies on close**

This is not an edge case — it is the **default behavior** for iOS/macOS users.

- Source: [SO#53800858 — cookies disappear after captive portal auth](https://stackoverflow.com/questions/53800858)
- Source: [SF#1060010 — persistent storage in captive portals](https://serverfault.com/questions/1060010)

#### Recommended UX: Persistent Warning + Student ID Recovery

**Layer 1: Always-visible warning banner** (non-blocking, below the fold)
```
+----------------------------------------------------+
| ! Your session is tied to this browser.            |
|   Clearing cookies will disconnect you and lose   |
|   unlinked balance. [Link Student ID] to protect. |
+----------------------------------------------------+
```

**Layer 2: Student ID linking as recovery mechanism**
- Once linked, balance stored server-side (PostgreSQL), not in cookies
- If user loses cookie, re-enter Student ID to recover
- Mirrors PisoFi's "convert remaining time to WiPass" concept

**Layer 3: Graceful re-connection flow**
1. openNDS intercepts and redirects to FAS
2. FAS checks device MAC against `devices` table
3. MAC recognized → auto-associate new browser token, show "Welcome back! [Link Student ID for balance access]"
4. MAC unrecognized → standard welcome page with linking prompt

#### Cookie Dependency Communication Strategy

| State | What User Sees | Action |
|---|---|---|
| First visit, no Student ID | Warning banner + "Link Student ID" prompt | Link ID to protect balance |
| First visit, has Student ID | No warning (balance is server-side) | Proceed |
| Returning, cookie valid | No warning | Seamless reconnection |
| Returning, cookie lost, MAC recognized | "Welcome back" + link prompt | Re-link if needed |
| Returning, cookie lost, MAC not recognized | Full warning + "Insert coin to start" | Fresh start; warn about incognito |

### Localization Requirements

#### Language Demographics (Philippines Census 2020)

| Language | Native Speakers | % of Population |
|---|---|---|
| Tagalog/Filipino | 43.1M | 39.9% |
| Cebuano/Bisaya | 25.6M | 22.5% |
| Ilocano | 7.6M | 8.0% |
| Hiligaynon/Ilonggo | 7.9M | 7.3% |
| Bikol | 4.2M | 3.9% |
| Waray | 2.9M | 2.6% |
| Kapampangan | 2.6M | 2.4% |

- Source: [Wikipedia — Languages of the Philippines](https://en.wikipedia.org/wiki/Languages_of_the_Philippines)

#### Recommended Localization Strategy

**Tier 1 (Must-have): Filipino/English toggle**
- Filipino (Tagalog-based) covers 39.9% native + virtually all educated Filipinos
- English covers all higher education students; preferred for technical UI
- Default: detect `Accept-Language` header; fall back to English
- Toggle in footer (matching AdoPiSoft pattern)

**Tier 2 (Should-have for Visayas/Mindanao campuses): Cebuano/Bisaya**
- 22.5% of population, dominant in Visayas and Mindanao

**Tier 3 (Consider for specific deployments): Ilocano, Hiligaynon**
- Ilocano for Ilocos Region campuses (8%) — directly relevant to ISPSC Tagudin
- Hiligaynon for Western Visayas (7.3%)

**Implementation:** Server-side i18n (not client-side, due to CNA JS restrictions):

```
/locales/
  en.json    # English (default)
  fil.json   # Filipino
  ceb.json   # Cebuano
  ilo.json   # Ilocano (for ISPSC deployment)
```

Language selection stored server-side (linked to device MAC or Student ID), not in cookies/localStorage.

**PisoWifi precedent:** Existing systems (PisoFi, AdoPiSoft, LPB) do NOT implement localization beyond English. StudentHub would be the first PisoWifi-class system to offer Filipino/Cebuano localization — a differentiator for campus deployments.

### Offline and Degraded State Handling

#### Failure Scenarios

| Scenario | User Impact | Detection | Recovery |
|---|---|---|---|
| **Server unreachable** | Splash page cannot load | HTTP timeout to FAS | openNDS ThemeSpec static fallback from router (no FAS dependency) |
| **Redis down** | Cannot validate sessions | FAS health check returns 503 | Queue coin events locally; "System temporarily unavailable" message; retry with backoff |
| **PostgreSQL down** | Cannot look up balance | DB query timeout | Read-only: show cached last-known balance; prevent new transactions |
| **Session expired mid-browse** | Internet revoked; CPD redirect | openNDS deauth | Normal behavior; user sees splash page, re-auths with existing balance |
| **MQTT broker down** | Coin inserts not processed | MQTT connection failure | ESP32 queues events locally; "Coin detected — updating balance..." spinner |
| **Captive portal loop (iOS)** | CNA re-triggers after auth | Same MAC re-appears at FAS within seconds | Return Apple "Success" page: `<body>Success</body>` with white text |

#### Three-Tier Degradation Architecture

```
Full browser + all services up       →  Svelte 5 dashboard (full interactivity)
Full browser + Redis down            →  Svelte 5 dashboard, read-only, banner: "Pause/resume temporarily unavailable"
Full browser + server down           →  Cached dashboard shell + "Reconnecting..." overlay + auto-retry
CNA/CPMB + all services up          →  Plain HTML splash page (core flow only)
CNA/CPMB + server down              →  openNDS ThemeSpec fallback (static page from router)
```

#### PWA Considerations (Post-Auth Only)

Service Workers and PWA features are **only relevant for the post-authentication enhanced dashboard**, NOT for the captive portal itself:

- **Service Worker**: Cannot register in CNA. Register after full browser access. Cache dashboard shell for instant revisit.
- **Cache API**: Static assets (CSS, JS, images) of enhanced dashboard. Not available in CNA.
- **IndexedDB**: Queue coin insertions and session data for offline sync. Full browsers only.
- **Background Sync API**: Queue writes for replay when connectivity returns. Chromium-only; Safari/Firefox don't implement.
- **Offline fallback**: Branded `/offline.html` — "Your session will resume when connectivity returns."

- Source: [rishikc.com — PWA Background Sync](https://rishikc.com/articles/advanced-pwa-features-offline-push-background-sync/)

---

## Appendix: Source Citations

### GitHub Repositories
- [JuanFi — github.com/ivanalayan15/JuanFi](https://github.com/ivanalayan15/JuanFi)
- [KLCiS-WiFi5-Soft — github.com/darkhoundz/KLCiS-WiFi5-Soft](https://github.com/darkhoundz/KLCiS-WiFi5-Soft)
- [AdoPiSoft Releases — github.com/AdoPiSoft/Releases](https://github.com/AdoPiSoft/Releases)
- [KLCiS-AdoPisoft-E-Payment — github.com/darkhoundz/KLCiS-AdoPisoft-E-Payment](https://github.com/darkhoundz/KLCiS-AdoPisoft-E-Payment)
- [AdoPiSoft Charging Station Plugin — github.com/AdoPiSoft-Plugins/charging-station](https://github.com/AdoPiSoft-Plugins/charging-station)
- [PisoFi Vulnerabilities — github.com/jkram143/PisoFi-Vulnerability-and-Exploits](https://github.com/jkram143/PisoFi-Vulnerability-and-Exploits)
- [JuanFi Generator — github.com/Kintoyyy/JuanFiGenerator](https://github.com/Kintoyyy/JuanFiGenerator)
- [AZK-Manager — github.com/Kintoyyy/AZK-Manager](https://github.com/Kintoyyy/AZK-Manager)
- [JuanFi Extended Portal — github.com/ivanalayan15/juanfi-extended-portal](https://github.com/ivanalayan15/juanfi-extended-portal)

### Official Documentation
- [Apple — About private Wi-Fi addresses](https://support.apple.com/en-us/102509)
- [Traefik forwardAuth middleware](https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/forwardauth)
- [Traefik Dynamic Configuration](https://doc.traefik.io/traefik/reference/routing-configuration/dynamic-configuration-methods/)
- [Traefik Docker Provider](https://doc.traefik.io/traefik/v3.4/reference/install-configuration/providers/docker/)
- [openNDS Customize](https://opennds.readthedocs.io/en/stable/customize.html)
- [Android Custom Tabs Captive Portal](https://source.android.com/docs/core/connect/android-custom-tabs-captive-portal)
- [MikroTik RouterOS HotSpot cookie method](https://help.mikrotik.com/docs/pages/viewpage.action?pageId=56459266)

### Community & Forums
- [MikroTik Forum — Randomised Private MAC](https://forum.mikrotik.com/t/randomised-private-mac-address-causing-issues-with-hotspot-signin/158394)
- [WBA Captive Behavior Reference](https://captivebehavior.wballiance.com/)
- [SO#30353380 — localStorage crashes iOS CNA](https://stackoverflow.com/questions/30353380)
- [SO#53800858 — cookies disappear after captive portal auth](https://stackoverflow.com/questions/53800858)
- [SF#1060010 — persistent storage in captive portals](https://serverfault.com/questions/1060010)
- [Security SE — Free hotspot open vs WPA2](https://security.stackexchange.com/questions/68748/free-hotspot-open-wifi-vs-wpa2-wifi-with-known-password)

### Product Sites & Market Data
- [AdoPiSoft — adopisoft.com](https://www.adopisoft.com/)
- [PisoFi — pisofiph.com](https://pisofiph.com/)
- [LPB Piso WiFi — lpbpisowifi.com](https://lpbpisowifi.com/)
- [iWiFi Portal — iwifi-portal.com](https://www.iwifi-portal.com/)
- [StatCounter Philippines — Mobile OS](https://gs.statcounter.com/os-market-share/mobile/philippines)
- [StatCounter Philippines — Vendor](https://gs.statcounter.com/vendor-market-share/mobile/philippines)
- [StatCounter Philippines — All OS](https://gs.statcounter.com/os-market-share/all/philippines)
- [PisoFi Shopify](https://pisowifi.myshopify.com/products/software-license-piso-wifi-vending-machine)
- [LPB Licenses](https://lpbpisowifi.com/dashboard/licensesshop)

### Research Papers
- [Freudiger et al. — Captive Portal Privacy (arXiv:1907.02142)](https://arxiv.org/pdf/1907.02142)

### Troubleshooting Guides
- [wifi.tips — Piso WiFi troubleshooting](https://wifi.tips/piso-wifi-vendo/)
- [weeklyavoid.com — Common PisoWifi problems](https://weeklyavoid.com/common-problems-when-using-piso-wifi-and-how-to-fix-them/)