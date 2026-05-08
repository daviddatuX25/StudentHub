# StudentHub Technical Documentation

Welcome to the consolidated technical documentation for **StudentHub Phase 1.5**.

This repository contains the definitive architectural blueprint, infrastructure design, and implementation requirements for the StudentHub campus Wi-Fi vending platform. All documents herein are the result of rigorous technical research, practical lab validation, and competitive analysis against existing Philippine PisoWifi products.

## Context for Developers

If you are reading this, you are likely preparing to implement the system. **Do not treat these documents as mere suggestions.** They represent hard-won knowledge regarding captive portal mechanics, iOS limitations, MAC randomization behaviors, and `iptables` conflicts.

The architecture was deliberately designed to solve specific problems that plague commercial PisoWifi systems (e.g., ghost credits, session loss on MAC rotation, security vulnerabilities). Deviating from the core architecture—especially regarding the **cookie-first identity model** and the **Traefik forwardAuth tiered access model**—will reintroduce these critical flaws.

## Documentation Structure

The documentation is organized by domain rather than chronologically. A developer working on a specific subsystem only needs to read the relevant directory.

*   `01_Architecture/` - Proxmox virtualization, system overview, and networking foundation.
*   `02_Network/` - Captive portal integration (openNDS), CPD behavior, pause/resume mechanics, and bandwidth management.
*   `03_Hardware/` - ESP32 firmware design, coin/bill acceptor integration, and the validated Bill of Materials.
*   `04_Backend_Database/` - PostgreSQL schema, PgBouncer/Redis configuration, MQTT security, and anti-replay mechanisms.
*   `05_Frontend_Identity/` - The dual-mode captive portal frontend (HTML/Svelte), MAC randomization mitigation, and localization.
*   `06_Commercial/` - Feature parity benchmarking against competitors (LPB, PisoFi, AdoPiSoft) and tiered access strategy.
*   `07_Registers/` - Centralized `Decision_Register.md` and `Risk_Register.md` compiled from all research phases.

## Execution

The original chronological research epics and preliminary reports have been archived to `../researches/archive/`. This `docs/` folder is the living single source of truth for the project's technical spec.
