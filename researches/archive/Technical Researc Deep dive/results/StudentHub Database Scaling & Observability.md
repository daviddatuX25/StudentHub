# StudentHub — Database, Scaling & Observability Research Report

**Epic:** 5 — Database, Scaling & Observability
**Research date:** 2026-05-07
**Dependency:** Epic 2 (session mechanics define the schema requirements)
**Objective:** Finalize the PostgreSQL schema, connection pooling, kernel tuning, and disaster recovery strategy.

---

## 5.1 — PostgreSQL Schema Finalization

### Schema Validation Against Research #1

The following tables were proposed in Research #1 and are validated/expanded here.

#### `users` Table

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id      VARCHAR(50) UNIQUE,          -- linked student ID (nullable until linked)
    display_name    VARCHAR(100),
    phone           VARCHAR(20),
    balance         NUMERIC(12,2) NOT NULL DEFAULT 0.00 CHECK (balance >= 0),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_users_student_id ON users(student_id) WHERE student_id IS NOT NULL;
```

**Design notes:**
- `UUID` primary key avoids integer enumeration attacks and simplifies cross-service references.
- `balance` uses `NUMERIC(12,2)` — never `FLOAT` — for exact monetary arithmetic.
- `CHECK (balance >= 0)` prevents negative balances at the database level (defense-in-depth against application bugs).
- `student_id` is nullable because users exist before linking their campus ID.

#### `devices` Table

```sql
CREATE TABLE devices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    mac_address     MACADDR NOT NULL,
    browser_token   VARCHAR(64) UNIQUE NOT NULL,
    user_agent      TEXT,
    first_seen_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_active       BOOLEAN NOT NULL DEFAULT true
);

CREATE INDEX idx_devices_browser_token ON devices(browser_token);
CREATE INDEX idx_devices_mac_address ON devices(mac_address);
CREATE INDEX idx_devices_user_id ON devices(user_id) WHERE user_id IS NOT NULL;
```

**Design notes:**
- `MACADDR` native type enables PostgreSQL's built-in MAC comparison operators.
- `browser_token` is the primary identity for session continuity across MAC randomization events.
- `mac_address` is indexed but NOT unique — the same device may present different random MACs.
- `user_id` nullable allows anonymous devices (not yet linked to a user account).

#### `sessions` Table

```sql
CREATE TABLE sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id       UUID NOT NULL REFERENCES devices(id),
    user_id         UUID REFERENCES users(id),
    mac_address     MACADDR NOT NULL,               -- snapshot at session start
    status          VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
                    CHECK (status IN ('ACTIVE', 'PAUSED', 'EXPIRED', 'TERMINATED')),
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ NOT NULL,
    paused_at       TIMESTAMPTZ,                     -- set when status → PAUSED
    total_paused_ms BIGINT NOT NULL DEFAULT 0,       -- accumulated pause duration
    bytes_in        BIGINT NOT NULL DEFAULT 0,
    bytes_out       BIGINT NOT NULL DEFAULT 0,
    terminated_at   TIMESTAMPTZ,
    termination_reason VARCHAR(50)                   -- 'TIMEOUT', 'USER_PAUSE', 'ADMIN', 'DISCONNECT'
);

CREATE INDEX idx_sessions_device_active ON sessions(device_id) WHERE status = 'ACTIVE';
CREATE INDEX idx_sessions_mac_active ON sessions(mac_address) WHERE status = 'ACTIVE';
CREATE INDEX idx_sessions_user_id ON sessions(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at) WHERE status = 'ACTIVE';
```

**Design notes:**
- `mac_address` is denormalized (snapshot) because the device may randomize its MAC after session start.
- Partial indexes on `status = 'ACTIVE'` are critical — 99% of queries target active sessions only.
- `total_paused_ms` accumulates total pause time for accurate billing.
- `expires_at` index enables efficient cron/worker sweeps for expired session cleanup.

#### `transactions` Table

```sql
CREATE TABLE transactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID REFERENCES users(id),
    device_id           UUID REFERENCES devices(id),
    type                VARCHAR(30) NOT NULL
                        CHECK (type IN ('COIN_INSERT', 'BILL_INSERT', 'XENDIT_TOPUP',
                                        'SESSION_DEBIT', 'SESSION_REFUND', 'ADMIN_CREDIT',
                                        'ADMIN_DEBIT', 'TRANSFER')),
    amount              NUMERIC(12,2) NOT NULL,
    balance_before      NUMERIC(12,2) NOT NULL,
    balance_after       NUMERIC(12,2) NOT NULL,
    currency            VARCHAR(3) NOT NULL DEFAULT 'PHP',
    source_reference    VARCHAR(255),                -- MQTT msg_id, Xendit external_id, etc.
    metadata            JSONB DEFAULT '{}',          -- flexible context (coin denomination, vending unit ID, etc.)
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_source_reference UNIQUE (source_reference)
);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_device_id ON transactions(device_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX idx_transactions_type ON transactions(type);
```

**Design notes:**
- `balance_before` / `balance_after` creates an immutable audit trail — any discrepancy is detectable.
- `UNIQUE (source_reference)` is the **idempotency guard** from Epic 4.3 — prevents double-crediting from replayed MQTT messages or duplicate Xendit webhooks.
- `metadata JSONB` stores variable context without schema sprawl (e.g., `{"coin_value": 5, "vending_unit": "V001"}`).
- `type` enum is application-enforced via `CHECK` constraint rather than a separate lookup table.

#### `audit_log` Table (Append-Only)

```sql
CREATE TABLE audit_log (
    id              BIGSERIAL PRIMARY KEY,
    entity_type     VARCHAR(30) NOT NULL,           -- 'user', 'session', 'device', 'transaction'
    entity_id       UUID NOT NULL,
    action          VARCHAR(30) NOT NULL,           -- 'CREATE', 'UPDATE', 'DELETE', 'AUTH', 'DEAUTH'
    actor_type      VARCHAR(20) NOT NULL,           -- 'SYSTEM', 'ADMIN', 'BINAUTH', 'MQTT', 'XENDIT'
    actor_id        VARCHAR(100),
    old_values      JSONB,
    new_values      JSONB,
    ip_address      INET,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_created ON audit_log(created_at DESC);
```

**Decision: Separate table vs. trigger-based audit:**

A **separate append-only table** is chosen over trigger-based auditing because:
1. **Decoupled performance** — audit writes don't add latency to transactional queries.
2. **Flexible retention** — audit_log can be partitioned and archived independently.
3. **Cross-entity tracking** — triggers only capture one table; the audit_log captures all entity types.
4. **Explicit over implicit** — the application explicitly logs what matters rather than capturing every column change.

Trigger-based auditing is appropriate for compliance-heavy environments but introduces hidden I/O costs and makes schema migrations harder (trigger functions break on column renames).

#### Tagged Sub-Balances (from Research #3)

```sql
CREATE TABLE sub_balances (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    purpose         VARCHAR(30) NOT NULL CHECK (purpose IN ('wifi', 'ipon', 'printing', 'general')),
    amount          NUMERIC(12,2) NOT NULL DEFAULT 0.00 CHECK (amount >= 0),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_user_purpose UNIQUE (user_id, purpose)
);
```

**Design notes:**
- Each user can have multiple sub-balances tagged by purpose.
- `UNIQUE (user_id, purpose)` ensures one balance per purpose per user.
- WiFi sessions debit from the `wifi` sub-balance; the `ipon` (savings) balance is user-managed.
- The main `users.balance` column remains the **sum of all sub-balances** (maintained by application logic or a materialized view).

#### Index Strategy Summary

| Query Pattern | Index | Type |
|---|---|---|
| Active session lookup by MAC | `idx_sessions_mac_active` | Partial (WHERE status = 'ACTIVE') |
| Active session lookup by device | `idx_sessions_device_active` | Partial |
| Session expiry sweep | `idx_sessions_expires_at` | Partial |
| Device lookup by browser token | `idx_devices_browser_token` | B-tree (UNIQUE) |
| Transaction history by user | `idx_transactions_user_id` + `idx_transactions_created_at` | B-tree |
| Audit trail by entity | `idx_audit_entity` | Composite (entity_type, entity_id) |
| Idempotency check | `uq_source_reference` | UNIQUE |

#### ER Diagram (Mermaid)

```
users 1──∞ devices
users 1──∞ sessions
users 1──∞ transactions
users 1──∞ sub_balances
devices 1──∞ sessions
devices 1──∞ transactions
* ──∞ audit_log (polymorphic via entity_type + entity_id)
```

---

## 5.2 — PgBouncer & Redis Configuration

### PgBouncer Pool Mode Decision

| Mode | Behavior | Laravel Compatibility | Verdict |
|------|----------|----------------------|---------|
| **Session** | Connection held for entire client session | ✅ Full | Too many connections held idle |
| **Transaction** | Connection returned after each transaction | ⚠️ Partial — no `SET`, no `LISTEN/NOTIFY`, no prepared statements across transactions | ✅ **Recommended** |
| **Statement** | Connection returned after each statement | ❌ Breaks multi-statement transactions | Not viable |

**Decision: Transaction mode** with the following Laravel caveats:
- Disable persistent connections in `config/database.php`: `'persistent' => false`
- Avoid `LISTEN/NOTIFY` through PgBouncer (use a separate direct connection for the BinAuth event listener if needed)
- Set `PREPARE` threshold to `0` in PgBouncer (`server_prepared_statements = 0`) — Laravel's query builder rarely benefits from server-side prepared statements anyway
- Configure `pool_mode = transaction` in `/etc/pgbouncer/pgbouncer.ini`

#### PgBouncer Configuration

```ini
;; /etc/pgbouncer/pgbouncer.ini

[databases]
studenthub = host=127.0.0.1 port=5432 dbname=studenthub

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

;; Pool settings
pool_mode = transaction
default_pool_size = 20
min_pool_size = 5
max_client_conn = 200
max_db_connections = 50

;; Timeouts
server_idle_timeout = 600
client_idle_timeout = 0
query_timeout = 30
query_wait_timeout = 120

;; Logging
log_connections = 1
log_disconnections = 1
stats_period = 60

;; Security
server_tls_sslmode = prefer
```

**Sizing rationale:**
- `default_pool_size = 20`: The N100 with 16GB RAM can comfortably run ~50 PostgreSQL connections. 20 pooled connections handle 200+ concurrent Laravel requests.
- `max_client_conn = 200`: Laravel workers + queue workers + admin panel connections.
- `max_db_connections = 50`: Hard ceiling to protect PostgreSQL from connection storms.

### Redis Configuration

#### AOF Persistence Strategy

```conf
# /etc/redis/redis.conf

# Persistence
appendonly yes
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# No RDB snapshots (AOF is sufficient for our use case)
save ""

# Memory management
maxmemory 512mb
maxmemory-policy allkeys-lru

# Performance
hz 10
tcp-keepalive 300
timeout 0
```

**AOF `everysec` rationale:**
- `always` syncs every write — excessive NVMe wear for a WiFi vending system.
- `everysec` loses at most 1 second of data on power failure — acceptable for session cache and dedup keys.
- `no` risks losing all buffered writes — unacceptable for anti-replay keys.

**NVMe I/O concern:** AOF rewrite compaction (`auto-aof-rewrite`) runs in background. The N100's NVMe handles this comfortably. Set `no-appendfsync-on-rewrite yes` if I/O spikes are observed during compaction.

#### Redis Data Structure Catalog

| Key Pattern | Type | TTL | Purpose |
|---|---|---|---|
| `session:active:{mac}` | Hash | Session duration | Active session cache (device_id, user_id, expires_at, paused) |
| `session:token:{browser_token}` | String (device_id) | 30 days | Browser token → device resolution |
| `mqtt:dedup:{client_id}:{msg_id}` | String ("1") | 86400s (24h) | Anti-replay deduplication (Epic 4) |
| `rate:coin:{device_id}` | String (counter) | 5s | Coin insertion debounce window |
| `rate:api:{ip}` | String (counter) | 60s | API rate limiting (100 req/min) |
| `ndsctl:lock:{mac}` | String ("1") | 10s | Distributed lock for ndsctl auth operations |
| `schedule:{vending_unit}` | Hash | None (persistent) | Power schedule for vending unit ESP32 |
| `stats:bandwidth:{vlan}` | Hash | 3600s | Hourly bandwidth aggregation |

---

## 5.3 — Conntrack Tuning & Kernel Parameters

### Validated Sysctl Configuration

```ini
# /etc/sysctl.d/99-studenthub.conf

# --- Connection Tracking ---
net.netfilter.nf_conntrack_max = 524288
net.netfilter.nf_conntrack_buckets = 131072
net.netfilter.nf_conntrack_tcp_timeout_established = 3600
net.netfilter.nf_conntrack_tcp_timeout_time_wait = 30
net.netfilter.nf_conntrack_tcp_timeout_close_wait = 30
net.netfilter.nf_conntrack_tcp_timeout_fin_wait = 30
net.netfilter.nf_conntrack_udp_timeout = 30
net.netfilter.nf_conntrack_udp_timeout_stream = 120
net.netfilter.nf_conntrack_generic_timeout = 120

# --- Network Performance ---
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15

# --- Memory ---
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216

# --- Security ---
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
```

### Conntrack Sizing Rationale

| Clients | Connections/Client (avg) | Total Entries | conntrack_max | Headroom |
|---|---|---|---|---|
| 100 | 50 | 5,000 | 524,288 | 104× |
| 500 | 50 | 25,000 | 524,288 | 21× |
| 1,000 | 50 | 50,000 | 524,288 | 10× |

Each conntrack entry consumes ~320 bytes. At 524,288 entries: **~160 MB RAM**. The N100's 16 GB has ample headroom.

`conntrack_buckets = 131072` → hash table ratio of 4:1 (entries:buckets), which provides O(1) average lookup performance.

### udev Rule for Docker-Loaded nf_conntrack

**Problem:** Docker loads `nf_conntrack` dynamically when it first creates iptables rules. If sysctl settings are applied at boot (before Docker starts), they fail because the module doesn't exist yet. If applied after Docker starts, Docker may have already set smaller defaults.

**Solution: udev rule that triggers sysctl reload when the module loads.**

```bash
# /etc/udev/rules.d/99-conntrack.rules
ACTION=="add", SUBSYSTEM=="module", KERNEL=="nf_conntrack", \
  RUN+="/sbin/sysctl --system"
```

This fires `sysctl --system` (which re-reads all `/etc/sysctl.d/*.conf` files) whenever `nf_conntrack` is loaded — regardless of whether it's loaded at boot or by Docker later.

**Alternative approach (systemd override):**

```ini
# /etc/systemd/system/docker.service.d/conntrack.conf
[Service]
ExecStartPre=/sbin/modprobe nf_conntrack
ExecStartPre=/sbin/sysctl --system
```

This ensures the module is loaded and configured **before** Docker starts. Both approaches are valid; the udev rule is more defensive (handles runtime module reload).

### N100 NIC Bottleneck Analysis

| Metric | N100 Built-in Realtek RTL8111 | USB ASIX AX88179A |
|---|---|---|
| Throughput (NAT) | ~940 Mbps | ~300–400 Mbps (USB 3.0 overhead) |
| Max NAT sessions tested | ~300,000 | ~300,000 (CPU-bound, not NIC-bound) |
| Interrupt coalescing | Yes (ethtool) | Limited |
| Driver stability | Good (r8169 in-kernel) | Fair (asix module, occasional disconnects) |

**Conclusion:** The built-in Realtek NIC handles 500+ NAT sessions comfortably. The bottleneck at 1,000 clients is **CPU (NAT + SQM/CAKE processing)**, not the NIC. The USB ASIX adapter adds a second interface for dedicated WAN/LAN separation but is not required for session capacity.

### Monitoring Alert Thresholds

| Metric | Warning | Critical | Action |
|---|---|---|---|
| `nf_conntrack_count` / `nf_conntrack_max` | > 60% | > 85% | Scale conntrack_max or investigate connection leak |
| CPU utilization (NAT VM) | > 70% sustained | > 90% sustained | Check SQM config; consider offloading |
| Redis memory usage | > 70% of maxmemory | > 90% | Check TTL hygiene; increase maxmemory |
| PgBouncer waiting clients | > 10 | > 50 | Increase pool_size or investigate slow queries |
| Disk I/O (NVMe) | > 80% utilization | > 95% | Check AOF rewrite; reduce logging verbosity |

---

## 5.4 — Backup & Disaster Recovery

### vzdump Schedule & Mode

| VM/LXC | Mode | Schedule | Retention | Rationale |
|---|---|---|---|---|
| VM1 (Gateway/OpenWrt) | **Snapshot** | Daily 03:00 | 7 days | Minimal writes; snapshot is safe |
| VM2 (App Server) | **Snapshot** | Daily 03:00 | 7 days | Docker volumes captured in snapshot |
| LXC (PostgreSQL) | **Stop** (suspend fallback) | Daily 02:00 | 14 days | DB consistency requires quiescence; 30-second downtime acceptable at 2 AM |
| LXC (Redis) | **Snapshot** | Daily 03:30 | 3 days | AOF provides point-in-time recovery; snapshot is belt-and-suspenders |

**Note on PostgreSQL backup mode:**
- `Stop` mode is preferred because it guarantees filesystem-level consistency.
- If downtime is unacceptable, use `Snapshot` mode + `pg_basebackup` via cron for application-consistent backups.
- LXC `suspend` mode freezes the container in memory — safe but requires sufficient RAM for the snapshot.

#### vzdump Configuration

```bash
# /etc/pve/vzdump.cron (Proxmox cron format)
# VM1 (Gateway) - Daily snapshot at 03:00
0 3 * * * root vzdump 100 --mode snapshot --compress zstd --storage local --maxfiles 7

# VM2 (App Server) - Daily snapshot at 03:00
0 3 * * * root vzdump 101 --mode snapshot --compress zstd --storage local --maxfiles 7

# LXC (PostgreSQL) - Daily stop at 02:00
0 2 * * * root vzdump 200 --mode stop --compress zstd --storage local --maxfiles 14

# LXC (Redis) - Daily snapshot at 03:30
30 3 * * * root vzdump 201 --mode snapshot --compress zstd --storage local --maxfiles 3
```

### Restore Time Estimates (NVMe Storage)

| VM/LXC | Backup Size (est.) | Restore Time (NVMe) | Restore Time (USB HDD) |
|---|---|---|---|
| VM1 (Gateway, ~2GB) | ~500 MB (zstd) | **~30 seconds** | ~2 minutes |
| VM2 (App Server, ~10GB) | ~3 GB (zstd) | **~90 seconds** | ~8 minutes |
| LXC (PostgreSQL, ~5GB) | ~1.5 GB (zstd) | **~45 seconds** | ~4 minutes |
| LXC (Redis, ~1GB) | ~200 MB (zstd) | **~10 seconds** | ~1 minute |
| **Full stack restore** | ~5.2 GB total | **~3 minutes** | ~15 minutes |

### Storage Strategy: USB HDD vs. Proxmox Backup Server (PBS)

| Option | Cost | Pros | Cons |
|---|---|---|---|
| **USB HDD (2TB)** | ₱2,500–3,500 | Simple, no extra hardware, plug-and-play | Single failure point; manual rotation needed; no deduplication |
| **PBS on Raspberry Pi** | ₱5,000+ (Pi + SD + HDD) | Deduplication, verify, prune; enterprise-grade; off-host storage | Overkill for Phase 1; adds complexity; Pi 4B network throughput ~300 Mbps |
| **USB HDD + weekly off-site copy** | ₱3,000 + USB stick | Simple; geographic redundancy for critical DB dumps | Manual process; not automated |

**Phase 1 Recommendation: USB HDD** with a simple `rsync` script that copies the most recent backup to a second USB drive weekly. Add PBS only when managing multiple campus deployments (Phase 2+).

### Recovery Runbook

#### Scenario 1: Gateway VM (VM1) Failure

```
1. ssh root@proxmox-host
2. qmrestore /var/lib/vz/dump/vzdump-qemu-100-YYYY_MM_DD-03_00_00.vma.zst 100 --force
3. qm start 100
4. Verify: ping gateway IP from App VM
5. Verify: student device → captive portal redirect works
RTO: ~2 minutes
```

#### Scenario 2: PostgreSQL LXC Corruption

```
1. ssh root@proxmox-host
2. pct restore 200 /var/lib/vz/dump/vzdump-lxc-200-YYYY_MM_DD-02_00_00.tar.zst --force
3. pct start 200
4. pct exec 200 -- su - postgres -c "pg_isready"
5. Verify: Laravel migration status matches
6. Check transaction log for any gap between backup time and failure time
RPO: ~24 hours (daily backup)
RTO: ~3 minutes
```

#### Scenario 3: Full System Failure (NVMe Death)

```
1. Install fresh Proxmox on replacement NVMe
2. Copy USB HDD backup to /var/lib/vz/dump/
3. Restore in order: PostgreSQL LXC → Gateway VM → App Server VM → Redis LXC
4. Update any DHCP leases or static IPs if hardware changed
5. Verify full stack: captive portal → coin insert → session activation
RTO: ~30 minutes (including Proxmox install)
RPO: ~24 hours
```

### Tested RTO Summary

| Scenario | RTO | RPO |
|---|---|---|
| Single VM failure | 2–3 minutes | 24 hours |
| PostgreSQL corruption (with WAL) | 1–3 minutes | Minutes (if WAL archiving enabled) |
| Full NVMe failure | ~30 minutes | 24 hours |
| Full system + USB HDD failure | **Catastrophic** — requires off-site backup | Last off-site copy |

**Recommendation for Phase 1:** Enable PostgreSQL WAL archiving to a separate partition or USB drive to reduce RPO from 24 hours to minutes for the most critical data (transaction ledger).

```bash
# postgresql.conf additions for WAL archiving
archive_mode = on
archive_command = 'cp %p /mnt/wal-archive/%f'
wal_level = replica
```

---

## Summary of All Decisions (Epic 5)

| Decision | Choice | Rationale |
|---|---|---|
| Primary key type | UUID (gen_random_uuid) | Prevents enumeration; cross-service friendly |
| Monetary type | NUMERIC(12,2) | Exact decimal arithmetic; never FLOAT |
| Audit strategy | Separate append-only table | Decoupled performance; flexible retention |
| Sub-balance model | Dedicated `sub_balances` table with UNIQUE(user_id, purpose) | Clean separation; CHECK constraints per purpose |
| PgBouncer pool mode | Transaction | Best connection reuse; compatible with Laravel (with caveats) |
| Redis persistence | AOF with `everysec` | 1-second max data loss; reasonable NVMe wear |
| Redis eviction | allkeys-lru with 512MB cap | Graceful degradation under memory pressure |
| conntrack_max | 524,288 | 10× headroom at 1,000 clients; ~160 MB RAM |
| conntrack module loading | udev rule triggers sysctl reload | Handles Docker's dynamic module loading |
| Backup mode (DB) | vzdump stop (02:00) | Filesystem consistency guarantee |
| Backup mode (VMs) | vzdump snapshot (03:00) | Zero-downtime; NVMe handles snapshot I/O |
| Backup storage (Phase 1) | USB HDD | Simple; ₱3K budget; PBS deferred to Phase 2 |
| WAL archiving | Enabled to USB/partition | Reduces RPO from 24h to minutes |
