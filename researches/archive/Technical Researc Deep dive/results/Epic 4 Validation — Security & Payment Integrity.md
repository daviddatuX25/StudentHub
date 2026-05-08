# Epic 4 Validation — Security & Payment Integrity

**Validated against:** [StudentHub Vending System Security Architecture.md](./StudentHub%20Vending%20System%20Security%20Architecture.md)
**Roadmap source:** [5 StudentHub_Technical_Research_Roadmap.md](../5%20StudentHub_Technical_Research_Roadmap.md)
**Validation date:** 2026-05-07

---

## Validation Summary

| # | Sub-Topic | Verdict | Coverage |
|---|-----------|---------|----------|
| 4.1 | MQTT Security & Anti-Replay | ✅ COVERED | 4/4 questions |
| 4.2 | ndsctl Injection Prevention | ✅ COVERED | 3/3 questions |
| 4.3 | Xendit Webhook Idempotency | ✅ COVERED | 3/3 questions |

**Overall: ✅ EPIC 4 COMPLETE**

---

## 4.1 — MQTT Security & Anti-Replay

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | How to configure Mosquitto ACLs with `%c` pattern so each ESP32 can only publish to its own topic? | §"Configuration of Mosquitto Access Control Lists via Client Identity" | **Fully documented.** Complete `aclfile` provided with `pattern write sh/v1/payment/raw/%c` and `pattern write sh/v1/status/%c`. `%c` substitutes the Client ID at CONNECT time. Backend user (`backend_user`) gets read-only access to `#` subtrees. Admin user gets full `readwrite #`. `allow_anonymous false` enforced. Per-listener settings noted. |
| Q2 | What is the exact HMAC-SHA256 validation flow in Node.js? How does the backend verify the signature and reject forged payloads? | §"HMAC-SHA256 Cryptographic Validation for Payload Integrity" | **Fully documented with code.** ESP32 side: `mbedtls` library with hardware-accelerated SHA-256. `mbedtls_md_hmac_starts/update/finish` sequence produces 32-byte hash appended as `signature` field. Node.js side: `crypto.createHmac('sha256', secretKey).update(payload).digest('hex')`. Uses `crypto.timingSafeEqual()` to prevent timing side-channel attacks. |
| Q3 | How does Redis-based message deduplication work for replay attack prevention? What TTL should the `msg_id` keys have? | §"Redis-based Anti-Replay and Message Deduplication" | **Fully documented with code.** Key pattern: `mqtt:dedup:{client_id}:{msg_id}`. Uses atomic `SET key value NX EX 86400` (24-hour TTL). Node.js `isMessageNew()` function returns `false` for replayed messages. If NX fails, backend drops message and logs a replay attempt. |
| Q4 | Should we use TLS for MQTT (port 8883) even on a local network, or is HMAC sufficient? | §"Local Network Threat Model and the Necessity of TLS" | **Fully documented with threat analysis.** Three campus LAN threats analyzed: ARP spoofing/MITM, passive sniffing, credential harvesting. Comparison table shows HMAC provides integrity but **no confidentiality**. CONNECT packet credentials are plaintext without TLS. **Recommendation: TLS on Port 8883** — ESP32 supports hardware-accelerated TLS; combined TLS + HMAC provides defense-in-depth. |

### Decision Captured

> **Mosquitto ACLs** with `%c` pattern for per-device topic isolation. **HMAC-SHA256** for payload integrity (mbedtls on ESP32, crypto module on Node.js) with timing-safe comparison. **Redis SET NX EX 86400** for anti-replay (24-hour TTL). **TLS on Port 8883** recommended for campus LAN confidentiality + credential protection.

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| Mosquitto ACL config | ✅ Complete `aclfile` with pattern rules, backend user, and admin user |
| Node.js HMAC validation code | ✅ `verifyMqttSignature()` function with `timingSafeEqual` |
| Redis deduplication logic | ✅ `isMessageNew()` function with atomic NX + EX pattern |

---

## 4.2 — ndsctl Command Injection Prevention

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | What is the exact regex for validating MAC addresses before passing to `ndsctl`? | §"MAC Address Validation Standards and Regular Expressions" | **Fully documented.** Regex: `^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$`. Anchored with `^` and `$` to prevent payload appending. Supports colon or hyphen separators. Enforces exactly 6 groups of 2 hex digits. |
| Q2 | Confirm: Node.js `child_process.execFile` (not `exec`) prevents shell injection. What about Python `subprocess.run(shell=False)`? | §"Prevention of Shell Injection via Child Process Selection" | **Fully documented with comparison table.** `exec()` spawns a shell → metacharacters (`;`, `&`, `|`, `$()`) are interpreted → injection possible. `execFile()` bypasses the shell → arguments passed directly to `execve` → metacharacters treated as literal text. Python equivalent: `subprocess.run([...], shell=False)`. Example: `00:11:22:33:44:55; rm -rf /` is passed as a single literal argument to ndsctl, which simply returns a format error. |
| Q3 | If MAC validation regex is bypassed, what is the worst-case damage? Can `ndsctl` be sandboxed? | §"Risk Assessment of Validation Failures and NDSCTL Abuse" + §"Validation Module Engineering and Fuzzing Strategy" | **Fully documented.** Worst-case scenarios: `ndsctl stop` → fail-open/fail-closed captive portal; `ndsctl deauth <MAC>` → targeted student DoS; `ndsctl debuglevel 3` → storage exhaustion crash. **AppArmor** sandboxing recommended — profile restricts ndsctl to Unix socket communication only, blocks execution of other binaries (`wget`, `sh`). Fuzzing test suite provided in `validator.js` with injection payloads. |

### Decision Captured

> **MAC regex** `^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$` applied at earliest pipeline stage. **`execFile`** (Node.js) / **`subprocess.run(shell=False)`** (Python) for all ndsctl invocations — no shell spawned. **AppArmor** profile sandboxes ndsctl binary to socket-only communication. **Fuzzing test suite** validates regex against common injection payloads.

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| Input validation module | ✅ `validator.js` with MAC regex and `validateMac()` function |
| Security test cases (fuzzing MAC input) | ✅ `testPayloads` array with injection attempts (semicolons, pipes, subshells) |

---

## 4.3 — Xendit Webhook Idempotency (Phase 2 Prep)

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | How does Xendit's `X-CALLBACK-TOKEN` header verification work? | §"Authentication via X-CALLBACK-TOKEN" | **Fully documented with code.** Xendit includes a static `X-CALLBACK-TOKEN` header on every webhook POST. Backend compares against `process.env.XENDIT_SECRET_TOKEN`. Mismatch → `401 Unauthorized` returned immediately. Node.js Express example provided. Laravel middleware approach noted. |
| Q2 | What is the exact `external_id` → `source_reference` deduplication flow in PostgreSQL? | §"Design of the External ID and Source Reference Deduplication" | **Fully documented.** Backend generates unique `external_id` when creating Xendit payment request. Webhook returns same `external_id`. 5-step flow: Start Transaction → Check Status (if `COMPLETED`, skip) → Update/Insert with UNIQUE constraint → Credit User → Commit Transaction. PostgreSQL UNIQUE constraint is the "non-bypassable" final defense. |
| Q3 | How to handle the race condition where two identical webhooks arrive simultaneously? | §"Resolution of Webhook Race Conditions" | **Fully documented with comparison table.** 4 strategies compared: PostgreSQL Unique Constraint (absolute reliability), Redis Distributed Lock (`SET NX EX 10`, highest performance), PostgreSQL Advisory Locks (`pg_advisory_xact_lock`, absolute reliability), Application-level checking (low reliability — race-susceptible). **Recommendation: PostgreSQL Unique Constraint as primary** + optional Redis Distributed Lock for high-concurrency scenarios. |

### Decision Captured

> **X-CALLBACK-TOKEN** validation as first middleware check. **PostgreSQL UNIQUE constraint** on `external_id` as primary race-condition defense. **Redis Distributed Lock** as optional high-concurrency layer. **200 OK** returned for both first-time and duplicate webhooks (prevents Xendit retries). **500** returned only for genuine server errors to trigger exponential backoff (6 retries over 24 hours).

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| Webhook handler pseudocode | ✅ Express route with token validation + idempotency check |
| Idempotency key design | ✅ `external_id` as UNIQUE constraint with transactional processing |
| Database constraint strategy | ✅ PostgreSQL UNIQUE + 5-step transactional flow documented |

---

## Bonus Coverage (Beyond Roadmap Scope)

The Security Architecture report included additional material not explicitly requested by the roadmap:

| Extra Coverage | Report Section | Value |
|---------------|----------------|-------|
| Infrastructure VLAN segmentation | §"Proxmox Network Topology and VLAN Segmentation" | 4-VLAN isolation model (Management, Backend, IoT, WiFi) with access matrix — reinforces Epic 1.5 decisions |
| HTTP response signaling for Xendit | §"HTTP Response Signaling and Retry Policies" | Detailed status code conventions (200 for success + duplicates, 400/422 for malformed, 500 for retryable errors) |
| ESP32 HMAC implementation (C++) | §"Implementation on ESP32 (C++/Arduino)" | Complete `signPayload()` function using mbedtls — fills the firmware gap noted in Epic 3 validation |

---

## Consolidated Decision Register (Epic 4)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| MQTT topic isolation | `%c` ACL pattern per Client ID | Prevents cross-device spoofing at broker level |
| Payload integrity | HMAC-SHA256 (mbedtls + crypto) | Hardware-accelerated on ESP32; timing-safe on backend |
| Anti-replay | Redis `SET NX EX 86400` | Atomic dedup with 24-hour window; drops replayed messages |
| Transport encryption | TLS on Port 8883 | Campus LAN is untrusted; protects credentials + data confidentiality |
| MAC validation | Anchored regex `^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$` | Prevents injection payload appending |
| Command execution | `execFile` / `subprocess.run(shell=False)` | No shell spawned; metacharacters treated as literals |
| ndsctl sandboxing | AppArmor profile | Restricts binary to socket-only communication |
| Webhook auth | `X-CALLBACK-TOKEN` header check | Static secret verification per Xendit spec |
| Payment idempotency | PostgreSQL UNIQUE on `external_id` | Absolute prevention of double-credit at DB level |
| Race condition defense | UNIQUE constraint + optional Redis lock | Defense-in-depth for concurrent webhook delivery |

---

## Risk Register (Epic 4)

| Risk | Severity | Mitigation |
|------|----------|------------|
| ESP32 HMAC secret extracted via flash dump | 🔴 HIGH | Use ESP32 flash encryption (NVS encrypted partition); rotate keys periodically |
| TLS certificate management on ESP32 fleet | 🟡 MEDIUM | Use CA bundle approach; provision certs at manufacturing/deployment time |
| Redis anti-replay key-space exhaustion | 🟢 LOW | 24-hour TTL auto-evicts; monitor Redis memory usage via Prometheus |
| AppArmor profile blocks legitimate ndsctl operations | 🟡 MEDIUM | Test profile thoroughly in dev lab; use `complain` mode before `enforce` |
| Xendit webhook endpoint exposed to public internet | 🟡 MEDIUM | IP whitelist (Xendit publishes source IPs) + rate limiting + token validation |
| Timing attack on HMAC comparison | 🟢 LOW | `crypto.timingSafeEqual()` already specified; constant-time comparison |

---

## Items Deferred to Later Epics

| Item | Deferred To | Rationale |
|------|------------|-----------|
| PostgreSQL UNIQUE constraint implementation | Epic 5.1 (Schema Finalization) | Constraint belongs in the migration file design |
| Redis data structure catalog (dedup keys) | Epic 5.2 (PgBouncer & Redis Config) | Redis configuration is a database-layer concern |
| Prometheus monitoring for Redis/MQTT metrics | Epic 5.3 (Conntrack & Kernel Tuning) | Observability is an ops concern |
| ESP32 flash encryption implementation | Implementation Phase | Requires physical hardware for testing |
| AppArmor profile creation and testing | Implementation Phase | Requires live OpenWrt gateway |
