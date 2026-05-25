# **FlexiQueue: Title Defense Presentation Script**

**Time Limit**: ~5 Minutes  
**Focus**: Multi-surface orchestration, local-first LAN architecture, dynamic queue routing (FlowEngine), wait prediction ML regressions, and physical indoor mapping desk guides.

---

### **Slide 1: Title & Introduction (15 Seconds)**
*   **Slide Visuals**: Title: **FlexiQueue: A Highly Configurable, Multi-Surface Queue Management and Service Routing Platform** and an emerald glassmorphic layout.
*   **Verbal Script**:
    > *"Good morning, members of the panel. We propose **FlexiQueue**: a highly configurable, multi-surface queue management and service routing platform. Our research investigates how institutional service lines—such as university registrars, cashiers, and department desks—can coordinate physical kiosks, display boards, and mobile web pages to reduce wait times, manage student journeys, and ensure continuous operations during active network outages."*

---

### **Slide 2: The Scene (30 Seconds)**
*   **Slide Visuals**: Split layout contrasting long student lines outside registrar offices with a clean simulated command-line output showing automated token transitions.
*   **Verbal Script**:
    > *"Let's establish the scene. On any campus, queues or 'pila' are a daily reality. During enrollment or graduation weeks, thousands of students wait for hours outside the Registrar, Cashier, Advising desks, and Library. Currently, if a student reaches a window only to find out they have a cashier deficiency, they must leave the window, line up at the Cashier, and then queue all over again at the Registrar. This physical friction wastes time, causes hall congestion, and leads to massive inefficiencies."*

---

### **Slide 3: The Problem (30 Seconds)**
*   **Slide Visuals**: Three distinct cards detailing: (1) Disjointed Journeys, (2) Announcement Fatigue, and (3) High Infrastructure Costs.
*   **Verbal Script**:
    > *"Our system addresses three critical bottlenecks. First, disjointed journeys: there is no dynamic cross-department handoff, forcing students to restart queue lines. Second, vocal announcement fatigue: staff waste energy shouting names, and students miss calls in noisy corridors. Third, high infrastructure costs: commercial systems are prohibitively expensive and require proprietary hardware, while cloud-only solutions fail completely during campus internet outages, paralyzing operations."*

---

### **Slide 4: Proposed System & Architecture (45 Seconds)**
*   **Slide Visuals**: A visual architecture node map with glowing SVG connecting flow lines separating: (1) Entrance Self-Service Kiosk, (2) Local LAN Server, (3) Lobby Display TV, (4) Clerk Staff Stations, and (5) Student Mobile status page.
*   **Verbal Script**:
    > *"To solve these bottlenecks, we present the FlexiQueue deployment architecture. It is built entirely as a local-first system. At the entrance, an Orange Pi-driven self-service kiosk prints tickets. In the lobby, WebSocket-based display screens show and announce the called numbers. Windows staff call tokens from their desks, and students monitor queue status on their phones. All devices connect locally to the LAN server running a dynamic FlowEngine routing database."*

---

### **Slide 5: Live Demonstration (45 Seconds)**
*   **Slide Visuals**: Three-column active simulator showing Kiosk ticket printing, Display Board updates, and Staff Calling Panel with an append-only terminal log.
*   **Verbal Script**:
    > *"Here, we can simulate the multi-surface interaction. A student walks up to the kiosk and prints a ticket. When staff click 'Call Next' on their terminal, the WebSocket-driven display board updates and calls the token with localized text-to-speech. Most importantly, if a registrar clerk identifies a cashier deficiency, they can transfer the token directly to the Cashier queue using the system's FlowEngine, bypassing the need for a new number and linking the student's journey together."*

---

### **Slide 6: Component Coverage Mapping (45 Seconds)**
*   **Slide Visuals**: Five-row table detailing the 5 Capstone Pillars: (1) Web (Admin & Staff window panels), (2) Mobile (Responsive status pages), (3) ML (Random Forest wait time regressions), (4) IoT (Orange Pi ticket kiosk + printer), and (5) Mapping (Leaflet.js desk physical routes).
*   **Verbal Script**:
    > *"Our system covers all five pillars of our curriculum. The Web portal for administrative and clerk controls runs on Laravel 12 and Svelte 5. The Mobile interface provides students with responsive queue tracking. For machine learning, a Random Forest regression model runs on the local server to predict wait times using historical transaction data. The IoT component integrates Orange Pi SBCs with ESC/POS thermal printers. Finally, the Mapping component uses Leaflet.js to render indoor layouts that guide students during window-to-window transfers."*

---

### **Slide 7: Novelty Claim (30 Seconds)**
*   **Slide Visuals**: Comparison matrix showing FlexiQueue vs. Standard QMS.
*   **Verbal Script**:
    > *"FlexiQueue's novelty lies in its local-first architecture. While standard web ticket counters crash when the internet drops, FlexiQueue operates completely on the local LAN using an edge SQLite database on low-cost single-board computers (like Orange Pi). Transactions sync to the central cloud once connection returns. Furthermore, every queue event is written to an immutable transaction log, providing a tamper-proof audit trail for government compliance."*

---

### **Slide 8: System Scope & Boundaries (30 Seconds)**
*   **Slide Visuals**: In-scope and Out-of-scope columns showing system boundaries.
*   **Verbal Script**:
    > *"Our project scope includes the multi-surface views, FlowEngine routing rules, ML wait estimation, Leaflet routing maps, and append-only database logs. Out of scope are native mobile app packages and global WAN-wide queueing during active offline states. By keeping all interfaces browser-based and locking devices using signed cookies, we eliminate complex app installations and keep the hardware footprint lightweight."*

---

### **Slide 9: Development Roadmap (15 Seconds)**
*   **Slide Visuals**: 5-phase horizontal timeline from DB design to validation.
*   **Verbal Script**:
    > *"We have planned a 7-week development timeline. We begin with database normalization, FlowEngine rules, and wait-time regression modeling. We then build the Svelte 5 surface views and integrate Leaflet campus maps, followed by WebSocket broadcasts, TTS announcement queues, and final performance load testing."*

---

### **Slide 10: Verification Plan (15 Seconds)**
*   **Slide Visuals**: Automated and manual testing criteria cards.
*   **Verbal Script**:
    > *"We will verify system performance using automated latency benchmarks under simulated loads, and validate the kiosk transaction speed through manual user acceptance testing, targeting a System Usability Scale score of 80."*

---

### **Slide 11: Conclusion (15 Seconds)**
*   **Slide Visuals**: "Orchestrating Campus Services" tagline with key badges.
*   **Verbal Script**:
    > *"FlexiQueue transforms chaotic, disconnected queues into an organized, real-time, multi-screen experience. It is flexible, budget-friendly, and resilient. Thank you, and we are now open for your questions."*
