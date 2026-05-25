# StudentHub — Project Context

## What This Is

Campus WiFi vending system where a student drops a coin (or pays via GCash/Xendit), gets internet access through a captive portal, and their identity persists across device changes via browser tokens. Every peso is accounted for through an immutable transaction ledger.

## Core Value

A student drops a coin and reliably gets internet — that transaction must never fail. Payment is final and irrevocable; identity can recover; financial integrity is enforced by code.

## Current Focus

Phase 1: Database & Auth — the foundation that all other features depend on.

## How to Work Here

### GSD Workflow
This project uses the GSD (Get Shit Done) workflow:
- `.planning/PROJECT.md` — living project context
- `.planning/REQUIREMENTS.md` — checkable requirements
- `.planning/ROADMAP.md` — phase structure
- `.planning/STATE.md` — current project state
- Use `/gsd-discuss-phase N` to gather context before planning
- Use `/gsd-plan-phase N` to create an execution plan
- Use `/gsd-execute-phase N` to build the phase

### Tech Stack
- **Backend:** Laravel 12 (PHP 8.2+), PostgreSQL 16, Redis, PgBouncer
- **Bridge:** Node.js (Express 5), Mosquitto MQTT
- **Frontend:** Svelte progressive enhancement + vanilla HTML/CSS/JS (dual-mode for iOS CPD)
- **Hardware:** ESP32 + coin/bill acceptor (MQTT publisher)
- **Payments:** Xendit webhook (idempotent)
- **Dev Environment:** Laragon on Windows (G:\ drive)
- **Simulator:** 7-panel web UI + CLI scripts for local testing

### Key Constraints
- No real hardware required for development — simulator covers all flows
- iOS CPD requires static HTML fallback (no JS)
- BSP Circular 1166 closed-loop e-money (credits non-cashable, non-transferable)
- UI branding (color, typography) not yet defined — blocker for frontend phases

### Build Order
1. PostgreSQL schema + migrations
2. Laravel API (Wallet, Session, Identity, Voucher)
3. Node.js bridge (MQTT → HMAC → API)
4. Simulator (web UI + CLI scripts)
5. Frontend (Svelte progressive enhancement)
6. Admin panel
7. Platform API (developer keys, scoped access)
8. Xendit integration

## Important Files
- `docs/BUILD-CONTEXT.md` — single context anchor for all phases
- `docs/phases/01_Database_and_Auth.md` — Phase 1 spec draft
- `ROADMAP.md` — full project roadmap with all tracks
- `dev/simulator/` — local development simulator (to be built)

## Edge Cases to Remember
27 critical edge cases defined in BUILD-CONTEXT.md across:
- Session & Payment (12)
- Identity & Device (5)
- Voucher (4)
- Xendit Webhook (3)
- Infrastructure (3)

## Research
- `.planning/research/SUMMARY.md` — synthesized research from all docs
- `.planning/research/FEATURES.md` — feature landscape (table stakes vs differentiators)