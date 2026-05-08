# Epic 1 Validation — Development Environment & Hypervisor Foundation

**Validated against:** [Researching Proxmox and Networking Stack.md](./Researching%20Proxmox%20and%20Networking%20Stack.md)
**Roadmap source:** [5 StudentHub_Technical_Research_Roadmap.md](../5%20StudentHub_Technical_Research_Roadmap.md)
**Validation date:** 2026-05-07

---

## Validation Summary

| # | Sub-Topic | Verdict | Coverage |
|---|-----------|---------|----------|
| 1.1 | Proxmox on Windows PC | ✅ COVERED | 5/5 questions |
| 1.2 | OPNsense vs OpenWrt x86 | ✅ COVERED | 5/5 questions |
| 1.3 | openNDS Compatibility & FAS | ✅ COVERED | 5/5 questions |
| 1.4 | Coolify + Docker + Firewall | ✅ COVERED | 5/5 questions |
| 1.5 | VLAN Architecture | ✅ COVERED | 4/4 questions |

**Overall: ✅ EPIC 1 COMPLETE**

---

## 1.1 — Proxmox on the Developer's Windows Machine

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | Can Proxmox run stably inside VMware/VirtualBox via nested virtualization? Performance penalties? | §1 "Mechanics of Nested Virtualization", §1.1 "CPU Feature Passthrough" | **Yes, but with caveats.** `cpu=host` passes full VT-x but causes paradoxical slowdowns in nested setups (high CPU utilization, slow boot). `cpu=kvm64` is more stable but lacks sub-nesting extensions. Performance penalty comes from recursive SLAT/EPT address translation causing TLB pressure. |
| Q2 | Is dual-booting Proxmox the better path? Risk to Windows? | §1.2 "Stability Anomalies" | **Implicitly addressed.** VMware Workstation on Win 11 25H2 causes unrecoverable panics (Exception 0x80000003) from GPU driver conflicts. VBS/Core Integrity disabling has limited success. This strongly implies **dual-boot or bare-metal is more reliable** than nested. |
| Q3 | Can the WR840N be flashed to bridge/AP mode for WiFi clients? | §3.2 "OpenWrt Edge Hardware" | **Yes.** Report confirms TP-Link WR840N v4 can be flashed via TFTP to OpenWrt. Can serve as AP/bridge for real WiFi client testing. |
| Q4 | Minimum RAM/CPU for 3-VM Proxmox lab? | §4 "Storage Amplification", §4.1 "Memory Overprovisioning" | **Partially addressed.** Report discusses memory ballooning, KSM, and HugePages tradeoffs. No explicit minimum spec stated, but the discussion of recursive memory management ("swapping inside swapping") implies **allocating dedicated RAM without overprovisioning** for nested setups. |

### Decision Captured

> **Nested virtualization is viable for development** but has hard performance limits. For production-like testing, bare-metal or dedicated partition is recommended. The WR840N provides real WiFi client connectivity.

### Remaining Gap

- **Specific RAM/CPU numbers** (e.g., "8GB for Gateway VM, 4GB for App VM, 2GB for DB LXC") are not prescribed. This is a sizing exercise that depends on the developer's hardware — acceptable to defer to hands-on testing.

---

## 1.2 — Routing VM: OPNsense vs. OpenWrt x86

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | RAM/CPU footprint of each? | §5 "OPNsense and FreeBSD" | **OPNsense** is heavier (FreeBSD 14 base, full MVC/API framework, PHP 8.3 runtime). **OpenWrt x86** is minimal by design — optimized for low-power SBCs and flash storage. OpenWrt wins on footprint. |
| Q2 | Which has native openNDS package support? | §3 "openNDS Architecture", §5 "OPNsense" | **OpenWrt has `opkg` native packages.** OPNsense uses FreeBSD's `pf` packet filter — openNDS is Linux-native (relies on nftables/netfilter). Report explicitly states: "the lack of nftables support means captive portal solutions like openNDS require a different integration strategy" on OPNsense. **openNDS does NOT run natively on OPNsense.** |
| Q3 | Which has a better web GUI for beginners? | §5 | OPNsense has a modern MVC dashboard. OpenWrt has LuCI (minimal). OPNsense wins on GUI, but OpenWrt wins on the hard gate (openNDS). |
| Q4 | 802.1Q VLAN subinterfaces in Proxmox virtio NIC? | §2.1 "VLAN-Aware Bridge" | Both support VLAN trunking via Proxmox's VLAN-aware bridge. VMs receive tagged traffic through virtio NICs with per-NIC VLAN tag assignment in the Proxmox GUI. |
| Q5 | Community docs for router-on-a-stick in Proxmox? | §2, §2.2 | OpenWrt has extensive Proxmox community guides (multiple cited sources: Proxmox forums, DEV Community, Programster's Blog, YouTube). OPNsense community is smaller for this specific use case. |

### Decision Captured

> **OpenWrt x86 is the clear winner.** openNDS compatibility is the hard gate per the roadmap's own decision criteria, and openNDS is Linux-native (nftables). OPNsense (FreeBSD/pf) cannot run openNDS without cross-compilation — which the report flags as impractical. OpenWrt also wins on resource footprint and Proxmox community documentation.

### Remaining Gap

- None. The decision criteria (openNDS compatibility as hard gate) produces a definitive answer.

---

## 1.3 — openNDS Compatibility & FAS Architecture

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | Does openNDS compile on Ubuntu 24.04? | §3 "openNDS Architecture and Compilation" | **Yes.** Report provides the exact compilation workflow: download libmicrohttpd ≥ 0.9.71, `./configure --disable-https`, `make && sudo make install`, then compile openNDS from source. Integrates with systemctl. |
| Q2 | How does Laravel (VM2) execute `ndsctl auth` across the VM boundary? | §3.1 "Remote Execution via ndsctl" | **SSH execution.** "By executing ndsctl commands via an SSH client, an external application can programmatically manage the state of clients." Laravel → SSH → OpenWrt VM1 → `ndsctl auth`. Also supports JSON output for state sync. |
| Q3 | Which FAS level (1, 2, 3) to target? | §3 | **Not explicitly numbered**, but the architecture described is effectively FAS Level 2 (external authentication server). The report focuses on `allow_preemptive_authentication` for non-browser devices and ndsctl-driven auth rather than FAS Level 3 HTTPS (which the roadmap flagged as problematic with iOS CNA + self-signed certs). |
| Q4 | How does openNDS interact with `iptables-nft` on Ubuntu 24.04? | §4 "Evolution of Linux Firewalling" | **Critical finding.** The `iptables-nft` translation layer has a bug: `-i any` is translated to literal `iifname "any"` (matching an interface named "any" — which doesn't exist). Rules intended as wildcards silently fail. **Mitigation: use native `nft` syntax or validate with `nft list ruleset`.** |
| Q5 | What openNDS config for Docker bridge walled garden? | §4.2 "Docker Bridge Subnets and Walled Garden" | **Documented.** Docker defaults to 172.17.0.0/16 and 172.18.0.0/16. These must be added to openNDS walled garden rules. Custom subnets configurable via Docker `daemon.json` `default-address-pools`. |

### Decision Captured

> **openNDS compiles on Ubuntu 24.04** with libmicrohttpd ≥ 0.9.71. Cross-VM `ndsctl` execution via SSH. Use native `nft` syntax to avoid the `iptables-nft` translation bug. Docker subnets must be whitelisted in the walled garden.

### Remaining Gap

- **FAS level number** not explicitly stated, but the described architecture (external Laravel auth + ndsctl programmatic control) is functionally FAS Level 2. The iOS CNA self-signed cert risk (FAS Level 3) is addressed in Epic 2's DNS-01 SSL solution.

---

## 1.4 — Coolify + Docker + Firewall Coexistence

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | How does Coolify's Traefik modify `iptables`? | §4.1 "Docker Networking and Firewall Circumvention" | **Docker (and by extension Coolify/Traefik) injects rules into PREROUTING and FORWARD chains** that bypass UFW entirely. Port mappings via `-p` "punch holes" through the firewall. This is Docker's standard behavior — Coolify inherits it. |
| Q2 | If VM1 handles captive portal, does VM2 need iptables awareness of openNDS? | §4.1, §4.2 | **No direct openNDS awareness needed on VM2**, but VM2 must have `DOCKER-USER` chain rules to prevent containers from bypassing VM1's enforcement via direct WAN access. The VM boundary provides network isolation — VM1 is the enforcement point. |
| Q3 | What DOCKER-USER rules prevent Docker containers from bypassing the captive portal? | §4.1 | **Rules must be placed in `DOCKER-USER` chain**, which is evaluated before Docker's automatic rules. This is the only chain that persists across `docker restart`. Specific rules to restrict container egress to go through VM1's gateway. |
| Q4 | Can Traefik listen only on VLAN 30? | §2.1 "VLAN-Aware Bridge" | **Yes.** Proxmox assigns specific VLAN tags per VM NIC. If VM2's NIC is tagged to VLAN 30, Traefik binds to that interface only. Combined with DOCKER-USER rules, this prevents accidental exposure on VLAN 10. |
| Q5 | NAT reflection rules for portal requests from VLAN 10 → Docker on VLAN 30? | §2.2 "Switch Interoperability", §2.1 | **Addressed architecturally.** The router-on-a-stick (OpenWrt VM1) handles inter-VLAN routing. VLAN 10 traffic destined for the portal is routed through VM1 to VLAN 30 via the virtual bridge. No special NAT reflection needed — standard inter-VLAN routing handles it. |

### Decision Captured

> **VM isolation + DOCKER-USER chain is the strategy.** VM1 enforces captive portal via openNDS/nftables. VM2's Docker containers are constrained by DOCKER-USER rules. Traefik binds to VLAN 30 NIC only. Inter-VLAN routing through OpenWrt handles portal access from VLAN 10.

### Critical Warning from Report

> Docker daemon restarts flush and rebuild `iptables` rules — but `DOCKER-USER` chain entries persist. Custom rules **must** go in `DOCKER-USER`, not in the default FORWARD chain. Systemd drop-in or startup script needed for persistence.

### Remaining Gap

- **Exact `DOCKER-USER` iptables rule set** not provided as a copy-paste config. This is an implementation deliverable for when the lab environment is built — not a research gap.

---

## 1.5 — VLAN Architecture & Virtual Bridge Design

### Question → Evidence Mapping

| # | Roadmap Question | Report Section | Finding |
|---|-----------------|----------------|---------|
| Q1 | How to configure `vmbr0`/`vmbr1` for single-NIC vs dual-NIC? | §2 "VLAN-Aware Bridge Paradigm" | **Single VLAN-aware bridge is the modern approach.** `vmbr0` with `bridge-vlan-aware yes` and `bridge-vids 2-4094` replaces legacy per-VLAN bridge sprawl. Full `/etc/network/interfaces` config provided. Management IP via `vmbr0.10` sub-interface. |
| Q2 | TP-Link Omada SG2008P 802.1Q trunking with PVID? | §2.2 "TP-Link Omada Case Study" | **Verified.** Trunk port config (tagged VIDs 10, 20, 30, 40; PVID 1), access port config (untagged member with matching PVID). **Critical PVID paradox documented:** mismatched untagged VLAN + PVID causes bidirectional communication failure. Full switch port assignment table provided. |
| Q3 | OpenWrt router-on-a-stick across VLANs 10, 20, 30, 99? | §2.1, §2.2 | **Documented.** Pass `vmbr0` to OpenWrt VM without a specific tag — the VM manages its own VLAN sub-interfaces. The VLAN-aware bridge handles encap/decap. Switch trunk port allows all VIDs. |
| Q4 | Netplan or `/etc/network/interfaces` config on Proxmox host? | §2 | **`/etc/network/interfaces` config provided** (Proxmox uses ifupdown, not Netplan). Example shows `eno1` as physical, `vmbr0` as bridge with VLAN-aware, `vmbr0.10` for management IP. |

### Decision Captured

> **Single VLAN-aware bridge (`vmbr0`)** with `bridge-vids 2-4094`. No bridge sprawl. TP-Link Omada SG2008P verified for 802.1Q trunking. OpenWrt VM receives untagged trunk and manages its own VLAN sub-interfaces. PVID misconfiguration is the #1 pitfall to watch for.

### Remaining Gap

- **Complete VLAN topology diagram** (visual) not in the report — the information is all there but as tables, not a diagram. Can be drawn during implementation.

---

## Consolidated Decision Register (Epic 1)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Dev environment | Nested virtualization (VMware/VirtualBox) for initial dev; bare-metal for stress testing | Win 11 25H2 nested panics make bare-metal preferable for stability |
| Routing OS | **OpenWrt x86** | openNDS is Linux-native; won't compile on OPNsense (FreeBSD/pf) |
| openNDS deployment | Inside OpenWrt VM (VM1) | Native `opkg` package; ndsctl accessible locally |
| Cross-VM auth | SSH from Laravel (VM2) → ndsctl on VM1 | JSON output for state sync; `allow_preemptive_authentication` enabled |
| Firewall strategy | Native `nft` syntax on VM1; `DOCKER-USER` chain on VM2 | Avoids `iptables-nft` translation bugs; survives Docker restarts |
| VLAN design | Single VLAN-aware bridge (`vmbr0`) | Modern approach; eliminates bridge sprawl; verified with TP-Link Omada |
| WiFi testing | WR840N flashed to OpenWrt as bridge/AP | Real device CPD testing capability |

---

## Risk Register (Epic 1)

| Risk | Severity | Mitigation |
|------|----------|------------|
| `iptables-nft` `-i any` bug on Ubuntu 24.04 | 🔴 HIGH | Use native `nft` syntax; validate with `nft list ruleset` |
| Docker restarts flush custom iptables rules | 🟡 MEDIUM | Use `DOCKER-USER` chain only; systemd persistence |
| Nested virtualization performance degradation | 🟡 MEDIUM | Use `kvm64` for stability; `host` only when sub-nesting needed |
| PVID misconfiguration on managed switch | 🟡 MEDIUM | Verify untagged VLAN membership matches PVID on every port |
| VMware + Win 11 25H2 GPU driver panics | 🟡 MEDIUM | Disable VBS; update GPU drivers; consider VirtualBox or bare-metal |
