# Capstone 3 Proposal — FlexiQueue (School Edition)

This directory contains the proposal resources, engineering specifications, and title defense preparation guides for **FlexiQueue (A Multi-Surface Queue Management and Service Routing Platform)**.

## Project Thesis
**FlexiQueue** investigates a highly configurable, local-first queue management and service routing platform. It orchestrates multiple physical and web-based service surfaces—including self-service touch kiosks, WebSocket-driven display boards, staff calling terminals, and mobile public triage web pages—on low-cost single-board computers (like Raspberry Pi / Orange Pi). 

Designed to operate seamlessly during WAN outages in institutional settings, it leverages a strict state pattern and a dynamic flow engine to manage complex multi-window customer journeys (e.g., student routes spanning Advising, Registrar, Cashier, and Library) while maintaining an immutable, append-only transaction log for administrative auditability (COA compliance).

## Directory Structure
*   [README.md](file:///d:/Projects/StudentHub/researches/capstone/capstone3/README.md) — The repository index and proposal roadmap.
*   [FlexiQueue Capstone Research Grounding.md](file:///d:/Projects/StudentHub/researches/capstone/capstone3/FlexiQueue%20Capstone%20Research%20Grounding.md) — Academic lit-review, database normalizations, queueing theory model (M/M/c), audit logs, and hardware deployment strategy.
*   [flexiqueue_defense_guide.md](file:///d:/Projects/StudentHub/researches/capstone/capstone3/flexiqueue_defense_guide.md) — Slide pacing, system architecture diagrams (Mermaid), key arguments, and Q&A strategies.
*   [flexiqueue_pitch.md](file:///d:/Projects/StudentHub/researches/capstone/capstone3/flexiqueue_pitch.md) — Spoken presentation script built around the 8-Section presentation framework.
*   [flexiqueue_slides.html](file:///d:/Projects/StudentHub/researches/capstone/capstone3/flexiqueue_slides.html) — Interactive presentation deck featuring an emerald glassmorphism layout, neural network canvas animation, and a real-time multi-surface queue simulator with localized voice calling.
*   [Archived/](file:///d:/Projects/StudentHub/researches/capstone/capstone3/Archived/) — Original paper-based student clearance tracker (SwiftClear) proposal assets for record keeping.

## System Target Metrics
*   **Token-to-Screen Propagation**: $<500\text{ms}$ from a staff click to display board refresh using WebSockets (Laravel Reverb/Pusher).
*   **Local Failover Resilience**: $100\%$ queueing uptime in the local LAN environment during active wide-area network (WAN) outages.
*   **Kiosk Transaction Time**: $<15\text{s}$ average walk-up token generation time on the self-service kiosk.
*   **Text-to-Speech (TTS) Dispatch Delay**: $<2\text{s}$ from session call to localized voice announcement execution on display screens.
*   **Audit Trail Reliability**: $100\%$ immutable transaction writes via append-only logs for all session state transitions.
