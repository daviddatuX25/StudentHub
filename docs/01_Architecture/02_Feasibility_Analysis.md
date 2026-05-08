# **Research Report: Technical Architecture and Feasibility Analysis of StudentHub**

## **Executive Summary**

The StudentHub platform is a proposed local-first, dual-layer ecosystem deployed within a Philippine educational institution. It functions primarily as a coin-operated WiFi vending machine (Income-Generating Project) and secondarily as an offline-capable student intranet. Transitioning the architecture away from constrained, embedded consumer routers (like the legacy WR840N) to a fully centralized "All-in-One" Linux x86 server drastically shifts the performance paradigm. By consolidating the routing, firewall, captive portal, and application layers onto a single robust machine (such as an N100 or surplus enterprise Mini PC), the system removes gateway bottlenecks, drastically improves session handling, and provides massive operational headroom for Dockerized "sidequest" intranet applications. This report outlines the optimal pathways for building this consolidated infrastructure, detailing the technical hardware/software requirements, and the non-technical regulatory and financial frameworks necessary for a successful pitch to the student body government.

## ---

**Part 1: Technical (Infrastructure, Hardware, Software)**

### **1.1 Infrastructure Architecture: The All-in-One Paradigm**

Opting to place the router and the application server on the same physical Linux machine is a highly performant and scalable approach, provided the networking interfaces are managed correctly.

In this paradigm, the Linux server acts as the primary gateway. It requires at least two Network Interface Cards (NICs): eth0 (connected to the external ISP for the WAN feed) and eth1 (the LAN interface providing DHCP to the student network).

There are two primary ways to architect this on an x86 Mini PC:

1. **Bare-Metal Linux (Ubuntu/Debian) with Native Routing:** The OS runs a standard Linux kernel handling routing via iptables or nftables. Services like dnsmasq are installed to handle DHCP and DNS for the local network. The captive portal daemon (openNDS) runs natively on the host, while the backend applications (Node.js/Laravel, MQTT) run in Docker containers. This is the most resource-efficient method.  
2. **The Hypervisor Approach (Proxmox):** The machine runs Proxmox VE. A dedicated firewall OS like OPNsense (FreeBSD-based, highly robust for enterprise network security) or OpenWrt x86 is virtualized to handle the routing. A separate Ubuntu Server VM is spun up to host Docker and the backend. This offers incredible network visibility and segmentation but requires slightly more RAM and configuration overhead.

**Docker Networking & Firewall Constraints:**

When running Docker on a host that also acts as a router, iptables conflicts are a major risk. Docker automatically manipulates iptables to implement its bridge networks and port publishing, routing container traffic in the nat table before standard firewall rules apply.

To implement the "Walled Garden" (allowing access to the local Docker intranet while blocking external internet), you must utilize the DOCKER-USER iptables chain. Docker evaluates the DOCKER-USER chain before its own internal routing rules. By inserting rules here, the server can explicitly allow traffic destined for the local Docker subnet (e.g., 172.18.0.0/16) while rejecting all other outbound packets until the captive portal authorizes the specific MAC address.

### **1.2 Hardware Ecosystem**

By adopting the Linux-first approach, the hardware requirements shift from relying on OpenWrt-compatible consumer routers to acquiring x86 computing power and "dumb" access points.

**The Central Server/Router (x86 Mini PCs)**

The Philippine surplus market offers highly capable enterprise micro-computers that vastly outperform a Raspberry Pi at a similar price point.

* **Intel N100 Mini PCs (e.g., Beelink S12 Pro):** Available on Shopee/Lazada for roughly ₱5,650 to ₱7,189. These feature 16GB DDR4 RAM, a 500GB NVMe SSD, and draw only 6W to 15W.  
* **Surplus Enterprise Micro PCs:** Models like the HP EliteDesk 800 G3/G4 Mini or Dell Optiplex 7050 Micro (Core i5 6th/7th/8th Gen) are widely available used for ₱5,000 to ₱10,000. These machines are built for 24/7 operation.  
* *Requirement:* Since these usually have only one Ethernet port, a reliable USB 3.0 to Gigabit Ethernet adapter (using a Realtek RTL8153 or ASIX AX88179 chipset) is required to act as the second NIC (eth1 for LAN).

**Wireless Access Points (APs)**

Because the Linux server handles the routing, you no longer need complex routing hardware. The server's LAN port connects to an unmanaged Gigabit PoE switch, which then powers dedicated, enterprise-grade Access Points (APs) distributed across the campus.

* *Recommendation:* Ubiquiti UniFi U6 Lite or TP-Link Omada EAP610. These devices are designed strictly to convert ethernet to wireless signals and can handle 100+ concurrent users per AP without the CPU bottlenecking associated with consumer routers. (Note: Avoid using Linux hostapd with USB WiFi dongles for a campus deployment; it cannot handle high client density).

**Microcontroller Bridge (ESP32)**

The ESP32 remains the bridge for the physical coin acceptor. It wires to the acceptor's signal line (via a 12V to 3.3V logic level shifter) and publishes hardware interrupts to the local MQTT broker.

### **1.3 Software Stack**

**Captive Portal: openNDS on Linux** While CoovaChilli can be compiled and run on Ubuntu, it is notoriously complex and prone to performance degradation. openNDS remains the superior choice.1 It compiles easily on standard Linux distributions and runs as a lightweight daemon intercepting traffic on the LAN interface (eth1). openNDS handles the initial splash page redirection, capturing the device's MAC address and pausing internet transit until authorized.

**Authentication Execution: ndsctl vs FreeRADIUS** Running FreeRADIUS alongside a Linux captive portal introduces unnecessary complexity. The most performant method is direct execution. When the Node.js/Laravel backend receives the MQTT event confirming a 5 PHP coin insertion, the backend executes the openNDS command-line utility directly on the host system: ndsctl auth \<MAC\_ADDRESS\> \<SESSION\_TIMEOUT\>.2 This immediately opens the firewall for the client device.

**Backend Development: Node.js vs Laravel**

Given the baseline of 8GB to 16GB of RAM on the recommended x86 Mini PCs, the Docker memory footprint differences between Node.js and Laravel (PHP-FPM) become irrelevant.

* **Node.js / Express:** Inherently faster for handling persistent MQTT subscriptions and real-time event loops due to its asynchronous architecture.  
* **Laravel 12:** Provides vastly superior built-in tools for the business logic required in Phase 2 (Eloquent ORM for financial ledgers, robust RBAC for student admin roles, and easier integration with Xendit webhooks).  
* *Recommendation:* A hybrid Docker approach. Run a lightweight Node.js container strictly for the MQTT subscriber and ndsctl execution (The Real-Time Engine), and use Laravel 12 for the user dashboard, billing, and administrative portal (The Business Engine).

## ---

**Part 2: Non-Technical (Legal, Pricing Strategy, and Pitch Intelligence)**

Pitching this to a Philippine State University or College (SUC) requires framing StudentHub not just as a vending machine, but as compliant, revenue-generating campus infrastructure.

### **2.1 Institutional & Legal Framework**

**NTC Regulatory Compliance** Operating a WiFi vending platform technically classifies the student organization as a Value-Added Service Provider (VASP) under National Telecommunications Commission (NTC) regulations, as the system resells bandwidth from an authorized ISP.4 While individual campus deployments often fly under the radar, full compliance protects the student body. The pitch must note that the underlying ISP connection must be legally declared for shared/commercial use. Furthermore, if using high-power access points, NTC Type Approval for the broadcasting equipment is necessary.5

**CHED CMO 20, s. 2011 (IGP Fund Management)** Commission on Higher Education (CHED) Memorandum Order No. 20, series of 2011, dictates the financial management of Income-Generating Projects (IGPs) in SUCs.6 The policy strictly mandates that an administrative cost contribution of exactly 25% of the IGP's net revenue must be automatically remitted for the direct use of the university Administration.6 Structuring the proposal to explicitly acknowledge and offer this 25% administrative share is the most critical non-technical step to securing institutional approval. The remaining 75% is retained by the student organization to fund Phase 2 development and general operations.

### **2.2 Pricing Strategy and Financial Model**

The standard market rate for Piso WiFi in Philippine communities is ₱1 per 10 to 15 minutes, or ₱5 for 1 hour. Given the student demographic, aggressive volume pricing (e.g., ₱5 for 1.5 hours) can drive higher adoption rates while remaining highly profitable due to the low operational expenditure.

**Conservative ROI Projection (Monthly Base)**

* **Capital Expenditure (CAPEX):** ₱15,000 (Surplus i5 Mini PC \+ 2 Ubiquiti/Omada APs \+ Switch \+ ESP32 Coin box).  
* **Operational Expenditure (OPEX):** ₱2,000 (Dedicated ISP line) \+ ₱300 (Electricity for 30W constant draw) \= ₱2,300/month.  
* **Revenue Assumption:** 150 unique students per day spending an average of ₱5 (moderate usage).  
* **Gross Monthly Revenue:** ₱22,500 (based on a 30-day operational month).  
* **Net Operational Revenue:** ₱22,500 \- ₱2,300 \= ₱20,200.  
* **Institutional Share (25% to CHED/Admin):** ₱5,050.  
* **Net Student Org Income:** ₱15,150 per month.

Under this model, the StudentHub project achieves a 100% Return on Investment (ROI) within the first 30 to 45 days of operation, creating a perpetual funding source for the student council thereafter.

### **2.3 The "Intranet Sidequest" Pitch Angle**

To differentiate from standard commercial vendors (like JuanFi setups), the pitch must heavily emphasize Layer 2: The Student Intranet. Because the system runs on a powerful x86 Linux server, hosting local instances of Moodle, a digital PDF library, or a secure e-voting system requires zero external internet bandwidth. Students access these services for free through the openNDS Walled Garden. This positions the project as an educational tool that happens to pay for itself, making it highly attractive to academic deans and IT departments.

## ---

**Recommended Next Steps**

To successfully build out this all-in-one Linux architecture, the developer should execute the following sequence:

1. **Procure the Server Engine:** Acquire a used x86 Mini PC (N100, Dell Optiplex, or HP EliteDesk) and a USB 3.0 Gigabit Ethernet adapter to establish the eth0 (WAN) and eth1 (LAN) interfaces.  
2. **Establish the Linux Gateway:** Install Ubuntu Server. Configure eth0 for internet access, and eth1 with a static IP (e.g., 192.168.50.1). Install dnsmasq to serve DHCP to the eth1 subnet, and configure iptables to enable IP forwarding and NAT masquerading to allow standard routing.  
3. **Compile openNDS Natively:** Install the dependencies and compile openNDS directly onto the Ubuntu host. Configure it to listen on eth1 and verify that connecting a laptop to the eth1 port triggers the default captive portal splash page.  
4. **Docker & Iptables Integration:** Install Docker. Create the docker-compose.yml for Mosquitto, Node.js, and Laravel. Crucially, write the DOCKER-USER iptables rules to ensure that the Docker bridge networks do not inadvertently bypass the openNDS captive portal logic.  
5. **Develop the Execution API:** Write the Node.js or Laravel endpoint that listens to the MQTT coin pulse, updates the database ledger, and executes the native ndsctl auth \<MAC\> command using system subprocess execution to grant access.

#### **Works cited**

1. \[OpenWrt Wiki\] OpenNDS Captive Portal, accessed May 6, 2026, [https://openwrt.org/docs/guide-user/services/captive-portal/opennds](https://openwrt.org/docs/guide-user/services/captive-portal/opennds)  
2. Using ndsctl — openNDS v10.3.0, accessed May 6, 2026, [https://opennds.readthedocs.io/en/stable/ndsctl.html](https://opennds.readthedocs.io/en/stable/ndsctl.html)  
3. ndsctl \- Max Fang's Notes, accessed May 6, 2026, [https://notes.maxfa.ng/Dev/Networking/OpenNDS/Config/ndsctl](https://notes.maxfa.ng/Dev/Networking/OpenNDS/Config/ndsctl)  
4. NTC Permit Requirements for Piso WiFi Vending Machines in the Philippines, accessed May 6, 2026, [https://www.respicio.ph/commentaries/ntc-permit-requirements-for-piso-wifi-vending-machines-in-the-philippines](https://www.respicio.ph/commentaries/ntc-permit-requirements-for-piso-wifi-vending-machines-in-the-philippines)  
5. NTC Permit Requirements for Piso WiFi Businesses in the Philippines, accessed May 6, 2026, [https://www.respicio.ph/commentaries/ntc-permit-requirements-for-piso-wifi-businesses-in-the-philippines](https://www.respicio.ph/commentaries/ntc-permit-requirements-for-piso-wifi-businesses-in-the-philippines)  
6. Republic of the Philippines OFFICE OF THE PRESIDENT COMMISSION ON HIGHER EDUCATION, accessed May 6, 2026, [https://cms-cdn.e.gov.ph/CHED/pdf/2011-CMO-NO20.pdf](https://cms-cdn.e.gov.ph/CHED/pdf/2011-CMO-NO20.pdf)  
7. Income-generating projects in higher education: Performance and management practices of a Philippine state university \- Science-Gate, accessed May 6, 2026, [https://www.science-gate.com/IJAAS/2025/V12I11/1021833ijaas202511021.html](https://www.science-gate.com/IJAAS/2025/V12I11/1021833ijaas202511021.html)