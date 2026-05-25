# Capstone 3 Proposal — SwiftClear

This directory contains the proposal resources, engineering specifications, and title defense preparation guides for **SwiftClear (A Web-Based Student Clearance Tracking System with Automated Departmental Sign-Offs)**.

## Project Thesis
SwiftClear investigates a centralized, role-based workflow automation engine that replaces physical paper-based semester and graduation clearance forms with an audited relational state matrix, real-time WebSocket progress tracking, and low-latency transactional deficiency resolving.

## Contents
*   `README.md` — The repository index and proposal roadmap.
*   `SwiftClear Capstone Research Grounding.md` — Academic lit-review, database normalizations, Data Privacy Act compliance, cryptographic trails, and performance scaling.
*   `swiftclear_defense_guide.md` — Slide pacing, system architecture (Mermaid), key arguments (override validation, race condition prevention, privacy), and Q&A strategies.
*   `swiftclear_pitch.md` — Spoken presentation script built around the 8-Section presentation framework.
*   `swiftclear_slides.html` — Interactive presentation deck featuring a custom midnight glassmorphism layout, animated canvas network, and a real-time clearance workflow simulator.

## System Target Metrics
*   **Approval State Propagation Delay**: $<500\text{ms}$ from administrative click to student portal UI updates via WebSockets.
*   **SMS Deficiency Dispatch Latency**: $<5\text{s}$ from a department logging a deficiency to the student receiving an alert.
*   **State Integrity (Global Lock)**: $100\%$ mathematical reliability. A student's global status remains locked if:
    $$\sum \text{Pending\_Departments} > 0$$
*   **Database Concurrent Transaction Handling**: $>500$ transactions per second (TPS) during high-density end-of-semester clearance windows.
*   **Usability Score**: $>80$ on the System Usability Scale (SUS) during institutional trials.
