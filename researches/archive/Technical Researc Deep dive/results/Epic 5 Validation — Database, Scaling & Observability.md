# Epic 5 Validation — Database, Scaling & Observability

**Validated against:** [StudentHub Database Scaling & Observability.md](./StudentHub%20Database%20Scaling%20%26%20Observability.md)
**Roadmap source:** [5 StudentHub_Technical_Research_Roadmap.md](../5%20StudentHub_Technical_Research_Roadmap.md)
**Validation date:** 2026-05-07

---

## Validation Summary

| # | Sub-Topic | Verdict | Coverage |
|---|-----------|---------|----------|
| 5.1 | PostgreSQL Schema Finalization | ✅ COVERED | 4/4 questions |
| 5.2 | PgBouncer & Redis Configuration | ✅ COVERED | 3/3 questions |
| 5.3 | Conntrack & Kernel Tuning | ✅ COVERED | 3/3 questions |
| 5.4 | Backup & Disaster Recovery | ✅ COVERED | 3/3 questions |

**Overall: ✅ EPIC 5 COMPLETE**

---

## 5.1 — PostgreSQL Schema Finalization

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | Validate the schema from Research #1: `users`, `devices`, `sessions`, `transactions` tables. Are there missing columns or constraints? | §"Schema Validation Against Research #1" | **Fully documented.** All four tables validated and expanded. Key additions vs. Research #1: `MACADDR` native type for `devices.mac_address`, `CHECK` constraint on `users.balance >= 0`, `total_paused_ms` column on `sessions` for pause billing, `balance_before`/`balance_after` audit trail on `transactions`. Status enum enforced via `CHECK` constraint. UUID primary keys chosen over SERIAL. |
| Q2 | Should `audit_log` be a separate append-only table or a trigger-based audit on the `transactions` table? | §"Decision: Separate table vs. trigger-based audit" | **Fully documented with rationale.** Separate append-only `audit_log` table chosen. 4 reasons provided: decoupled performance, flexible retention, cross-entity tracking, explicit over implicit. Trigger-based auditing acknowledged as valid for compliance-heavy environments but rejected for this use case due to hidden I/O costs and schema migration fragility. |
| Q3 | How to model the "tagged sub-balances" (e.g., `purpose=ipon` credits) from Research #3? | §"Tagged Sub-Balances (from Research #3)" | **Fully documented.** Dedicated `sub_balances` table with `UNIQUE(user_id, purpose)` constraint. Four purpose types defined: `wifi`, `ipon`, `printing`, `general`. Main `users.balance` remains as sum of all sub-balances. `CHECK(amount >= 0)` prevents negative sub-balances. |
| Q4 | What indexes are needed for the most common queries (active sessions by MAC, transaction history by user)? | §"Index Strategy Summary" | **Fully documented.** 7 indexes specified with types. Key insight: **partial indexes** on `sessions` WHERE `status = 'ACTIVE'` — dramatically reduces index size since 99% of sessions are historical. Composite index on `audit_log(entity_type, entity_id)` for cross-entity queries. UNIQUE index on `source_reference` serves double duty as idempotency guard. |

### Decision Captured

> **UUID** primary keys for all tables. **NUMERIC(12,2)** for monetary values (never FLOAT). **Separate append-only `audit_log`** over trigger-based auditing. **`sub_balances`** table with `UNIQUE(user_id, purpose)` for tagged balances. **Partial indexes** on active sessions for query performance. **`MACADDR`** native PostgreSQL type for MAC addresses.

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| Final `.sql` migration file | ✅ Complete CREATE TABLE + CREATE INDEX statements for all 6 tables |
| Index strategy | ✅ 7 indexes documented with types, partial index rationale explained |
| ER diagram | ✅ Mermaid entity-relationship diagram with cardinality |

---

## 5.2 — PgBouncer & Redis Configuration

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | What PgBouncer pool mode (session, transaction, statement) is appropriate for Laravel's Eloquent ORM? | §"PgBouncer Pool Mode Decision" | **Fully documented with comparison table.** Transaction mode selected. 3 modes compared on behavior, Laravel compatibility, and verdict. Key caveats: disable persistent connections, set `server_prepared_statements = 0`, avoid `LISTEN/NOTIFY` through PgBouncer. Complete `pgbouncer.ini` provided with sizing rationale (20 pooled connections handle 200+ concurrent requests). |
| Q2 | How to configure Redis AOF persistence to survive power loss without excessive I/O on the NVMe? | §"AOF Persistence Strategy" | **Fully documented.** `appendfsync everysec` chosen — max 1-second data loss; reasonable NVMe wear. `always` rejected (excessive wear), `no` rejected (unacceptable for anti-replay keys). `auto-aof-rewrite` enabled for compaction. RDB snapshots disabled (`save ""`) since AOF is sufficient. `maxmemory 512mb` with `allkeys-lru` eviction. |
| Q3 | What Redis data structures are needed? (Session cache, rate limiting counters, MQTT dedup keys, API token store.) | §"Redis Data Structure Catalog" | **Fully documented.** 8 key patterns specified with type, TTL, and purpose. Covers: active session cache (Hash), browser token lookup (String), MQTT dedup (String, 24h TTL from Epic 4), coin debounce (String, 5s), API rate limiting (String, 60s), ndsctl distributed lock (String, 10s), vending schedule (Hash, persistent), bandwidth stats (Hash, 1h). |

### Decision Captured

> **Transaction pool mode** for PgBouncer (with Laravel caveats: no persistent connections, no LISTEN/NOTIFY). **AOF `everysec`** for Redis persistence (1-second RPO). **`allkeys-lru`** eviction at 512MB cap. **8 key patterns** cataloged covering sessions, dedup, rate limiting, locks, and scheduling.

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| PgBouncer config | ✅ Complete `pgbouncer.ini` with pool sizing, timeouts, and TLS |
| Redis config with AOF | ✅ Complete `redis.conf` with AOF, memory limits, and eviction policy |
| Data structure catalog | ✅ 8 key patterns with types, TTLs, and purpose descriptions |

---

## 5.3 — Conntrack Tuning & Kernel Parameters

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | Validate the sysctl values from Research #1 (conntrack_max=524288, tcp_timeout_established=3600, etc.). | §"Validated Sysctl Configuration" + §"Conntrack Sizing Rationale" | **Fully documented.** Complete `/etc/sysctl.d/99-studenthub.conf` provided. conntrack_max=524,288 validated with scaling table: 10× headroom at 1,000 clients, ~160 MB RAM cost. Bucket ratio 4:1 for O(1) lookup. TCP timeouts (established=3600, time_wait=30) validated. Additional network performance and security sysctls included. |
| Q2 | How to apply these settings reliably on boot when `nf_conntrack` is loaded dynamically by Docker? What's the exact udev rule? | §"udev Rule for Docker-Loaded nf_conntrack" | **Fully documented with two approaches.** Primary: udev rule at `/etc/udev/rules.d/99-conntrack.rules` that triggers `sysctl --system` when `nf_conntrack` module loads. Alternative: systemd `ExecStartPre` override that `modprobe`s the module and applies sysctl before Docker starts. Both approaches explained with tradeoffs (udev is more defensive; systemd is more predictable). |
| Q3 | At what user count does the N100's single gigabit NIC become the bottleneck vs. conntrack? | §"N100 NIC Bottleneck Analysis" | **Fully documented with comparison table.** Built-in Realtek RTL8111 handles ~940 Mbps NAT throughput and ~300,000 sessions. USB ASIX AX88179A limited to 300-400 Mbps due to USB 3.0 overhead. **Conclusion: NIC is NOT the bottleneck** — CPU (NAT + SQM/CAKE) becomes the constraint at 1,000 clients. USB adapter adds WAN/LAN separation but isn't required for capacity. |

### Decision Captured

> **conntrack_max=524,288** (10× headroom at 1,000 clients, ~160 MB RAM). **udev rule** for reliable sysctl application after Docker loads nf_conntrack. **Built-in Realtek NIC is sufficient** — CPU is the bottleneck at scale, not the NIC. **Monitoring thresholds** set at 60% warning / 85% critical for conntrack utilization.

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| `/etc/sysctl.d/` config file | ✅ Complete `99-studenthub.conf` with conntrack, network perf, and security settings |
| udev rule | ✅ `/etc/udev/rules.d/99-conntrack.rules` with systemd alternative |
| Monitoring alert thresholds | ✅ 5 metrics with warning/critical levels and actions |

---

## 5.4 — Backup & Disaster Recovery

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | What `vzdump` schedule and mode (snapshot vs. suspend) is appropriate for each VM/LXC? | §"vzdump Schedule & Mode" | **Fully documented.** 4 VMs/LXCs specified with mode, schedule, and retention. VM1/VM2: snapshot mode at 03:00 (7-day retention). PostgreSQL LXC: stop mode at 02:00 (14-day retention — longest for critical financial data). Redis LXC: snapshot at 03:30 (3-day retention — AOF provides separate recovery). Complete `vzdump.cron` configuration provided. |
| Q2 | How long does a full restore of the Gateway VM (VM1) take on NVMe storage? | §"Restore Time Estimates (NVMe Storage)" | **Fully documented with comparison table.** VM1 restore: ~30 seconds (NVMe) / ~2 minutes (USB HDD). Full stack restore: ~3 minutes (NVMe) / ~15 minutes (USB HDD). Three recovery runbooks provided: single VM failure (RTO ~2 min), PostgreSQL corruption (RTO ~3 min), full NVMe death (RTO ~30 min including Proxmox install). |
| Q3 | Should we use Proxmox Backup Server (PBS) on a Raspberry Pi, or is a USB HDD sufficient for Phase 1? | §"Storage Strategy: USB HDD vs. PBS" | **Fully documented with cost comparison.** USB HDD (₱2,500–3,500) recommended for Phase 1 — simple, no extra hardware. PBS on Pi (₱5,000+) deferred to Phase 2 when managing multiple campus deployments. Weekly off-site copy via rsync to second USB drive recommended. **WAL archiving** recommended for PostgreSQL to reduce RPO from 24 hours to minutes. |

### Decision Captured

> **vzdump snapshot** for VMs (zero-downtime), **vzdump stop** for PostgreSQL LXC (consistency). **USB HDD** for Phase 1 backups with weekly off-site rsync. **PBS deferred** to Phase 2 multi-campus deployment. **WAL archiving** enabled for PostgreSQL to achieve minute-level RPO for transaction ledger. Full stack RTO: **~3 minutes** on NVMe.

### Deliverable Check

| Expected Deliverable | Status |
|---------------------|--------|
| Backup schedule | ✅ vzdump.cron with staggered times, modes, and retention per VM/LXC |
| Recovery runbook with tested RTO | ✅ 3 scenarios documented: single VM, DB corruption, full system failure |

---

## Bonus Coverage (Beyond Roadmap Scope)

| Extra Coverage | Report Section | Value |
|---|---|---|
| ER diagram | §"ER Diagram (Mermaid)" | Visual entity relationships for all 6 tables |
| PgBouncer sizing rationale | §"Sizing rationale" | N100 connection budget analysis |
| NVMe I/O management | §"AOF Persistence Strategy" | `no-appendfsync-on-rewrite` tip for I/O spike mitigation |
| WAL archiving config | §"Tested RTO Summary" | PostgreSQL WAL setup to reduce RPO from 24h to minutes |
| Conntrack memory calculation | §"Conntrack Sizing Rationale" | 320 bytes/entry × 524,288 = ~160 MB RAM cost |

---

## Consolidated Decision Register (Epic 5)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary key type | UUID (gen_random_uuid) | Prevents enumeration; cross-service friendly |
| Monetary column type | NUMERIC(12,2) | Exact decimal; CHECK >= 0 at DB level |
| MAC address column type | MACADDR (native) | Built-in operators; validates format |
| Session index strategy | Partial indexes (WHERE status = 'ACTIVE') | 99% of queries target active sessions; shrinks index by 100× |
| Audit strategy | Separate append-only table | Decoupled; flexible retention; cross-entity |
| Sub-balance model | `sub_balances` table, UNIQUE(user_id, purpose) | Clean tagged balances; purpose-level CHECK constraints |
| PgBouncer pool mode | Transaction | Best connection reuse; Laravel-compatible (with caveats) |
| PgBouncer pool size | 20 (max 50 DB connections) | N100 comfortably handles 50 PG connections |
| Redis persistence | AOF `everysec` | 1-second max loss; reasonable NVMe wear |
| Redis eviction | allkeys-lru at 512 MB | Graceful degradation; LRU fits session cache pattern |
| conntrack_max | 524,288 | 10× headroom at 1,000 clients |
| conntrack module init | udev rule on module load | Handles Docker's dynamic nf_conntrack loading |
| NIC strategy | Built-in Realtek (single NIC) | Sufficient for 1,000 clients; CPU is real bottleneck |
| Backup storage (Phase 1) | USB HDD + weekly off-site rsync | ₱3K budget; simple; PBS deferred to Phase 2 |
| Backup mode (PostgreSQL) | vzdump stop + WAL archiving | Filesystem consistency + minute-level RPO |
| Backup mode (VMs) | vzdump snapshot | Zero-downtime; NVMe handles I/O |

---

## Risk Register (Epic 5)

| Risk | Severity | Mitigation |
|------|----------|------------|
| PgBouncer transaction mode breaks Laravel LISTEN/NOTIFY | 🟡 MEDIUM | Use dedicated direct PG connection for BinAuth event listener |
| Redis `allkeys-lru` evicts active session cache | 🟡 MEDIUM | Monitor eviction rate; increase maxmemory if needed; critical keys use explicit TTLs |
| conntrack sysctl not applied on first Docker start | 🟢 LOW | udev rule fires on module load; systemd override as backup |
| USB HDD backup drive failure | 🟡 MEDIUM | Weekly off-site copy to second drive; daily automated verify (`vzdump --verify`) |
| PostgreSQL WAL archive disk fills up | 🟡 MEDIUM | Monitor archive directory; implement `archive_cleanup_command`; alert at 80% |
| N100 CPU saturated under full load | 🟡 MEDIUM | SQM/CAKE is CPU-intensive; benchmark at 500 clients; consider hardware upgrade path |

---

## Items Deferred to Later Phases

| Item | Deferred To | Rationale |
|------|------------|-----------|
| Proxmox Backup Server (PBS) | Phase 2 (multi-campus) | Overkill for single-site Phase 1 |
| Read replicas for PostgreSQL | Phase 2 (scaling) | Single LXC handles Phase 1 load |
| Redis Cluster/Sentinel | Phase 2 (HA) | Single Redis instance sufficient for Phase 1 |
| Automated failover (Keepalived/CARP) | Phase 2 (HA) | Manual recovery acceptable for Phase 1 (3-min RTO) |
| Time-series DB (Prometheus/VictoriaMetrics) | Implementation Phase | Monitoring stack design depends on final deployment topology |
