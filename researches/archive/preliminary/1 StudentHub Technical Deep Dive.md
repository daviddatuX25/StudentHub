# **Technical Architecture and Implementation Report: StudentHub Phase 1.5**

## **Problem Area 1: MAC Randomization Solution Architecture**

The advent of aggressive MAC address randomization across major mobile operating systems fundamentally disrupts the traditional captive portal paradigm. Historically, captive portals, including preceding architectures like the JuanFi system, relied on the Media Access Control (MAC) address as a persistent hardware identifier to bind a device to a session or voucher. To ensure session continuity and accurate billing for a coin-operated internet service provider model at a polytechnic college, the architecture must abandon device-centric identity in favor of session-centric identity using cryptographic tokens, ultimately bridging to user-centric identity via account linking.

### **MAC Randomization Behavior Across Mobile Platforms**

Current mobile operating systems implement sophisticated MAC randomization strategies designed to prevent passive network tracking and location profiling.1 Understanding the specific frequency and triggers for these rotations is critical for designing a resilient session management architecture.

Apple devices running iOS 14 through iOS 17, along with Android devices running versions 10 and 11, default to a persistent per-SSID randomization strategy.1 Under this model, the operating system generates a unique, randomized MAC address based on the network profile parameters, such as the SSID and security type, and utilizes this same randomized MAC address consistently upon reconnection to that specific network.1 The address remains static across reboots and disconnects. However, if a user explicitly executes a "Forget This Network" command, the underlying network profile is purged, and the device will generate an entirely new randomized MAC address upon the next connection attempt.3

The environment has become significantly more hostile to captive portals with the release of iOS 18, iPadOS 18, and macOS 15 Sequoia, which introduced the "Rotate Wi-Fi Address" feature.4 For networks classified as open or utilizing weak security—which inherently includes all traditional captive portals lacking WPA2/WPA3 enterprise encryption—the default behavior automatically rotates the MAC address approximately every fourteen days.5 Furthermore, the operating system may rotate the address if the device has not connected to the network for a period exceeding six weeks, or within twenty-four hours of the user forgetting the network.4

Android 12 and subsequent versions introduced a non-persistent randomization model. While persistent per-SSID randomization remains the default, non-persistent randomization can be triggered via developer options or network suggestion APIs. When active, the Wi-Fi module re-randomizes the MAC address at the start of every connection if the DHCP lease has expired and four hours have passed since the last disconnection, or if the current randomized MAC was generated more than twenty-four hours prior.1 In all cases of randomization, the locally administered bit is set to 1, and the unicast bit is set to 0, leaving 46 bits of randomized address space.1

### **The Browser Token Architecture**

To survive arbitrary MAC rotation without severing the student's paid session, the system must decouple the financial balance from the MAC address. The openNDS Forwarding Authentication Service (FAS) provides the necessary interception layer to issue and validate persistent browser tokens.8 The token, rather than the hardware address, becomes the authoritative source of session identity.

When a device connects and attempts to access the internet, openNDS intercepts the HTTP traffic and redirects the client to the backend portal via the FAS protocol. The backend API generates a cryptographically secure UUIDv4 session token and sets it as an HTTP cookie. Because the Phase 1 captive portal operates without HTTPS on a local domain, the cookie cannot utilize the Secure flag. Instead, it must be configured with the HttpOnly=true flag to prevent Cross-Site Scripting (XSS) extraction, the SameSite=Lax flag to permit top-level navigation from captive portal assistant browsers, and a Max-Age matching the maximum allowable session lifespan plus a grace period (e.g., 30 days). The token is subsequently tied to a primary key in the PostgreSQL database.

The exact request and response flow for re-authentication relies on the interplay between the browser cookie and the openNDS FAS payload. When a student's device rotates its MAC address and reconnects, openNDS observes an entirely new, unauthenticated MAC address. Consequently, openNDS intercepts the traffic and executes the FAS redirect. The backend API is hit, and the browser automatically appends the previously stored cookie token to the request. The backend reads the token, queries the database, and identifies the active session and its remaining time balance. Simultaneously, the backend decodes the FAS payload provided by openNDS, extracting the newly rotated clientmac variable.9 The backend then executes the ndsctl auth subprocess, passing the new MAC address and the remaining timeout value.10 The portal displays a localized "Welcome Back" interface, and the student resumes their session without inserting additional coins.

This token-based architecture introduces specific edge cases. If a student initiates a session using private or incognito browsing mode, the token is destroyed the moment the captive portal browser is closed. The financial balance becomes permanently orphaned because the backend has no mechanism to link the subsequent connection to the lost token. This is an unavoidable limitation of device-agnostic identity, necessitating explicit warnings in the portal user interface advising against the use of private browsing. Furthermore, regarding multi-device usage in Phase 1, a token is strictly bound to the browser that requested it. If a student connects a laptop alongside their smartphone, the laptop will receive a distinct token and require separate coin insertions.

While MAC randomization introduces the theoretical risk of a MAC collision—where two discrete devices generate the exact same randomized MAC address—the mathematical probability across a 46-bit randomized space (![][image1], or approximately 70.3 trillion unique addresses) is astronomically low.1 In a localized deployment of 1,000 concurrent users, the risk of a collision resulting in session hijacking is zero.

### **Recommended Architecture Evaluation**

An alternative approach to the browser token is a strict captive portal login wall. In this model, openNDS intercepts the traffic, and the backend mandates that a student input a Student ID and PIN before accessing the internet. Identity is entirely account-based. This permanently neutralizes MAC randomization, incognito mode data loss, and enables seamless multi-device balance sharing. openNDS natively supports this via custom HTML forms submitted to the FAS backend.8 However, this approach introduces immense friction for a micro-transaction environment. A student inserting a five-peso coin for thirty minutes of immediate access faces significant user experience degradation if forced to authenticate with a ten-digit student number on a mobile keyboard.

The optimal Phase 1 solution is a cookie-first, account-upgradeable hybrid model. Upon initial connection and coin insertion, the system relies entirely on the persistent cookie token to grant frictionless, immediate access. The token ensures MAC rotations are handled silently. For Phase 2, which introduces GCash top-ups and multi-device capabilities, the portal will introduce a "Link to Student ID" interface. By logging in, the anonymous token is permanently bound to the student's database record. Once linked, the student can log in on secondary devices, allowing the backend to sever the active session on the primary device and transfer the remaining balance to the secondary device's current MAC address.

## **Problem Area 2: iptables \+ Docker \+ openNDS Coexistence**

Deploying openNDS natively alongside Dockerized application services on a single Linux host introduces severe Netfilter race conditions. Both subsystems assume authoritative control over packet routing, leading to silent failures where captive portal enforcement is bypassed or Docker containers become completely inaccessible.

### **The Netfilter Conflict**

When the Docker daemon initializes, it aggressively manipulates the Linux iptables to isolate container networks and map published ports.12 Docker creates several custom chains within the nat and filter tables, specifically injecting rules into the FORWARD chain to route traffic to its internal DOCKER, DOCKER-ISOLATION-STAGE-1, and DOCKER-ISOLATION-STAGE-2 chains.12 Concurrently, openNDS inserts its own rules into the PREROUTING and FORWARD chains, creating ndsOUT, ndsIN, and ndsNET to intercept unauthenticated traffic and redirect it to the captive portal daemon.

The conflict arises during daemon lifecycle events. If the Docker daemon restarts, it flushes and rebuilds its iptables rules, frequently overwriting or altering the precedence of the openNDS FORWARD rules. This results in scenarios where unauthenticated clients can utilize Docker's masquerading to reach external networks without paying, or conversely, clients lose the ability to access the locally hosted captive portal payload. Furthermore, Docker's manipulation of the nat table means packets are often diverted before reaching standard firewall rules, rendering tools like the Uncomplicated Firewall (UFW) entirely ineffective.12

### **The DOCKER-USER Chain Implementation**

To resolve this conflict, Docker provides the DOCKER-USER chain within the filter table explicitly for administrator-defined routing policies.12 Docker guarantees that traffic evaluated by the FORWARD chain will be processed by the DOCKER-USER chain prior to reaching Docker's internal routing logic, and critically, Docker will never flush the DOCKER-USER chain during daemon restarts.12 Therefore, all captive portal enforcement and walled garden whitelisting must be securely anchored here.

The following iptables rules mandate the required traffic flow. In this architecture, eth0 represents the external WAN interface, eth1.10 represents the student WiFi VLAN, and 172.18.0.0/16 represents the Docker bridge subnet hosting the backend API and portal.

| Rule Order | Command | Purpose |
| :---- | :---- | :---- |
| 1 | iptables \-I DOCKER-USER 1 \-m conntrack \--ctstate RELATED,ESTABLISHED \-j RETURN | Permits ongoing, already established connections to bypass further evaluation, reducing CPU load. |
| 2 | iptables \-I DOCKER-USER 2 \-i eth1.10 \-p tcp \-m multiport \--dports 80,443 \-j RETURN | Establishes the Walled Garden. Allows all devices on the student VLAN to access the Docker-hosted captive portal API on standard web ports. |
| 3 | iptables \-I DOCKER-USER 3 \-i eth1.10 \-p tcp \--dport 1883 \-j RETURN | Permits unauthenticated ESP32 microcontrollers to communicate with the Docker-hosted Mosquitto MQTT broker. |
| 4 | iptables \-I DOCKER-USER 4 \-i eth1.10 \-o eth0 \-m mark\! \--mark 0x10000 \-j REJECT \--reject-with icmp-port-unreachable | Blocks unauthenticated devices from reaching the external internet. openNDS applies a specific Netfilter mark to authenticated packets. Traffic lacking this mark is actively rejected. |
| 5 | iptables \-I DOCKER-USER 5 \-j RETURN | Returns control to Docker's internal routing logic for all other legitimate traffic. |

Simultaneously, within the native openNDS configuration (/etc/opennds/opennds.conf), the Docker bridge subnet must be explicitly whitelisted. While older captive portal implementations like JuanFi utilized MikroTik's walled-garden IP address lists, openNDS manages this via the Preauthenticated Users firewall rule set. This prevents the openNDS daemon from intercepting traffic destined for the backend APIs before the HTTP redirect can execute. The configuration must include FirewallRule allow tcp port 80 to 172.18.0.0/16 and the equivalent for port 443\.

### **Persistence and System Compatibility**

Ubuntu 22.04 LTS defaults to the nftables backend via the iptables-nft translation wrapper. Docker handles this translation natively, but openNDS has historically relied on legacy iptables syntax. The system must operate under a unified approach: the host must utilize the default iptables-nft translation layer. Downgrading the host to iptables-legacy is strongly discouraged, as it spawns dual, conflicting firewall namespaces within the kernel memory space, leading to unpredictable packet drops.

Because iptables rules are volatile, they do not survive system reboots. To ensure the DOCKER-USER rules persist, the iptables-persistent package must be utilized. To guarantee that the rules are securely applied even after Docker daemon upgrades, a custom systemd service must be deployed. This service, configured with After=docker.service and Requires=docker.service, will execute an iptables-restore operation strictly targeting the DOCKER-USER chain immediately after Docker completes its network initialization.

### **Testing Methodology and Failure Modes**

Validating this coexistence requires rigorous testing to simulate known production failure modes. Administrators must connect an unauthenticated device to the student network and attempt an external ping (curl \-I http://1.1.1.1). This must return an openNDS HTTP 302 redirect or time out, confirming the external block. Subsequently, the device must query the portal's local IP address, which must return an HTTP 200 OK, confirming the Walled Garden is intact. Finally, the administrator must execute systemctl restart docker on the host and repeat the external ping. If the device achieves internet connectivity, the DOCKER-USER persistence mechanism has failed. The most common production failure mode involves Docker upgrades silently wiping custom nat rules; anchoring policies in DOCKER-USER effectively immunizes the system against this risk.

## **Problem Area 3: ndsctl Execution Security**

The backend system relies on executing the ndsctl auth \<MAC\> \<TIMEOUT\> subprocess to inform the openNDS daemon that a client has paid and should be granted network routing access.10 This subprocess execution represents the most critical attack surface within the StudentHub architecture. If exploitable, an adversary could grant themselves unlimited free internet, bypassing the coin mechanisms entirely.

### **Attack Surface and Input Validation**

The realistic attack vectors include command injection via manipulated MAC addresses and replay attacks on the MQTT broker. If the backend API passes unsanitized user input directly to a system shell, an attacker could terminate the ndsctl command and append malicious Linux commands (e.g., providing a MAC address formatted as 00:00:00:00:00:00; rm \-rf /).

To neutralize this, the MAC address must be strictly validated against a hardcoded regular expression before interacting with the system execution layer. In Node.js, the validation logic must enforce the structure of six groups of hexadecimal pairs separated by colons. Furthermore, subprocess execution must never invoke a system shell. In Node.js, developers must avoid the child\_process.exec function, utilizing execFile instead, which invokes the binary directly and passes arguments as an array, eliminating shell expansion vulnerabilities. Similarly, if utilizing Python's FastAPI, the subprocess.run method must be invoked with the shell=False parameter, passing the command and arguments as a strict list. If openNDS receives a malformed MAC address via a safely executed subprocess, the daemon simply logs an error and exits safely without altering routing tables.

### **MQTT Authorization and HMAC Signatures**

The ESP32 microcontrollers publish coin insertion events to the Mosquitto MQTT broker. A critical security gap in earlier open-source implementations, such as the JuanFi codebase, was the lack of authentication on coin endpoints, allowing any script to publish fake top-up events. To secure StudentHub, the ESP32 must never publish raw, unsigned data.

First, Mosquitto must be configured with Access Control Lists (ACLs). The ESP32 devices must authenticate using discrete username and password credentials. The ACL configuration utilizes the %c pattern substitution variable to restrict topic access dynamically based on the client ID.14 By configuring the ACL with pattern write studenthub/coinslot/%c/pulse, Mosquitto guarantees that an ESP32 can only publish coin events to its specific topic hierarchy, preventing cross-device topic spoofing.14

Second, the MQTT payloads must be cryptographically verified using HMAC-SHA256 signatures.15 The ESP32 firmware calculates a hash of the payload using a shared secret pre-programmed during flashing. The payload must include the device ID, the coin value, an incrementing message ID, and a timestamp.

When the backend receives the message, it recalculates the HMAC using the identical shared secret. If the signatures mismatch, the payload is forged and immediately discarded. To mitigate replay attacks—where a malicious user captures valid Wi-Fi packets and resends the exact same MQTT payload to generate free time—the backend utilizes a Redis caching layer. The backend stores the unique message ID in Redis with an expiration timer. If a subsequent message arrives bearing an identical message ID, the deduplication logic identifies it as a replay attack and rejects the event. This Token Bucket logic is vastly superior to sliding window counters, as coin slots naturally generate rapid bursts of data (e.g., inserting five individual coins in rapid succession) that legitimate a bursty rate profile.

### **Immutable Audit Schema**

For Income Generating Project (IGP) accounting, establishing tamper-evident visibility into revenue generation is mandatory. Every ndsctl action must be recorded in an immutable ledger.

The PostgreSQL schema must enforce this ledger as an append-only table structure. The audit\_log table captures the primary key, a timestamp, the precise action performed (e.g., AUTH\_GRANTED), the target MAC address, the granted duration in seconds, the source type (COIN, GCASH, or ADMIN), the specific hardware or API reference ID, and the financial revenue amount. This ensures that the student government can cross-reference the physical coins collected from the ESP32 vending machines against the exact seconds of internet access dispensed by the Linux host.

## **Problem Area 4: Backend Stack Recommendation**

Given the architectural constraint of an all-in-one Linux x86 server and a design target of 1,000 concurrent users, the selection of the backend stack dictates CPU scheduling behavior, Docker memory footprint, and long-term maintainability.

### **Framework Evaluation**

The engineering team evaluated FastAPI (Python), Node.js (Express), and Laravel (PHP).

FastAPI provides unparalleled execution speed for standard API workloads via the Uvicorn ASGI server. It leverages Python's native Pydantic validation, which securely handles MAC address and JSON schema sanitation. Furthermore, its auto-generated OpenAPI documentation accelerates integration for Phase 2 billing features.17 Crucially, a FastAPI Uvicorn worker exhibits extreme memory efficiency, typically consuming up to 40% less RAM than an equivalent Express instance under identical loads, and features rapid cold start times.19 However, Python's asyncio-mqtt ecosystem, while functional, lacks the enterprise maturity of JavaScript's MQTT implementations. Furthermore, subprocess management in asynchronous Python requires meticulous implementation utilizing asyncio.create\_subprocess\_exec to prevent blocking the single-threaded event loop.

Node.js remains the industry standard for IoT and real-time MQTT pipelines.17 The mqtt.js library is robust, heavily tested, and manages complex network reconnect logic flawlessly. The event-driven architecture handles high-concurrency I/O bound tasks, such as database writes and subprocess executions, exceptionally well, routinely managing 40% to 60% more simultaneous connections than Python equivalents in raw concurrency tests.17 The primary weakness is a higher baseline memory footprint and a reliance on external libraries like Zod to achieve the strict runtime type-checking native to Pydantic.

Laravel 12 (PHP) provides best-in-class ORM capabilities via Eloquent, rapid business logic scaffolding, and seamless integration with payment providers like Xendit. However, PHP-FPM operates on a blocking, synchronous model that spawns discrete processes per request. It is fundamentally incapable of acting as a persistent, asynchronous MQTT subscriber without deploying complex, long-running artisan daemon commands that are highly susceptible to memory leaks over time.

### **Docker Memory Footprint Comparison (1,000 Users)**

Telemetry derived from bare-metal deployments under a 1,000-user load reveals distinct resource profiles 19:

| Container Role | Idle RAM | 1,000 Sessions Load RAM | Architectural Notes |
| :---- | :---- | :---- | :---- |
| **Node.js (Real-time)** | \~60 MB | 300 \- 450 MB | Excels at persistent MQTT loops and ndsctl bridging. |
| **FastAPI (Real-time)** | \~45 MB | 200 \- 300 MB | Highly efficient footprint; requires careful async subprocess handling. |
| **Laravel/PHP-FPM** | \~80 MB | 400 \- 600 MB | High overhead due to discrete worker pooling for admin/billing. |
| **PostgreSQL 16** | \~120 MB | 800 \- 1,200 MB | Footprint dictated primarily by shared\_buffers configuration. |
| **Redis** | \~10 MB | 50 \- 100 MB | Minimal footprint for high-speed idempotency locks. |
| **Mosquitto** | \~5 MB | 20 \- 40 MB | Highly optimized C-based execution. |
| **openNDS (Native)** | \~10 MB | 30 \- 50 MB | Negligible overhead; bottlenecks exist in kernel conntrack, not the daemon. |

### **Final Recommendation: The Hybrid Architecture**

While the specified Intel N100 Mini PC equipped with 16GB of RAM ensures memory is not a hard constraint, architectural separation of concerns is critical for Phase 2 stability. A monolithic implementation in a single language forces unacceptable compromises.

The recommended architecture is a hybrid stack: **Node.js (Real-time Engine) paired with Laravel 12 (Business Engine)**.

In this configuration, Node.js acts purely as a highly specialized microservice. It manages the persistent MQTT subscriber loop, interfaces with Redis to deduplicate ESP32 payloads, and executes the ndsctl system commands. It is selected over FastAPI due to the superior maturity and resilience of the Node.js MQTT ecosystem for IoT applications.

Conversely, Laravel handles the REST API, serves the Svelte 5 frontend, powers the administrator dashboard, manages complex PostgreSQL relations, and processes Xendit webhooks. This hybrid approach enables the deployment to leverage Laravel's massive ecosystem for Phase 2 billing requirements while isolating the volatile, high-speed coin-pulse processing into a lightweight, non-blocking JavaScript environment.

## **Problem Area 5: Hardware Specification for Real Concurrency**

Supporting 1,000 concurrent, active students requires hardware calibrated for high-frequency packet processing rather than raw computational throughput. The true bottleneck in a localized ISP deployment is the Linux kernel's software interrupt (SoftIRQ) processing and connection tracking table lookups, not application-level logic.

### **Compute and NIC Requirements**

For CPU requirements, the Intel N100 (featuring 4 E-Cores capable of boosting to 3.4GHz) is highly capable of routing 1,000 Network Address Translation (NAT) connections. Similarly, surplus hardware such as the Intel i5-8500T offers robust multi-core performance suitable for this scale.

The critical hardware dependency lies in the Network Interface Controllers (NICs). Standard Realtek controllers (such as the RTL8153 or RTL8168), commonly found on entry-level Mini PCs, offload interrupt handling directly to the CPU. Under the high packet interrupt pressure generated by 1,000 active devices, Realtek drivers frequently crash or silently drop packets. Hardware utilizing **Intel i226-V or i210** controllers is strictly required.20 These Intel chips feature multiple hardware queues that efficiently distribute interrupt processing across CPU cores, ensuring driver stability (utilizing the igc or igb drivers in Linux). If a dual-NIC configuration necessitates a USB 3.0 Ethernet adapter for the LAN side, administrators must utilize adapters built on the ASIX AX88179A chipset, avoiding Realtek variants.

### **Sysctl Conntrack Tuning**

The Linux Netfilter connection tracking (conntrack) system monitors the state of all active connections to facilitate NAT routing. By default, Ubuntu restricts the nf\_conntrack\_max value to 65,536 entries.21 A deployment of 1,000 users, where modern browsers and background applications routinely open dozens of simultaneous connections, will exhaust this limit within minutes. When the table fills, the kernel drops all new packets, resulting in catastrophic connection failures logged as nf\_conntrack: table full, dropping packet.20

To accommodate the load, the sysctl parameters must be aggressively tuned:

| Sysctl Parameter | Recommended Value | Rationale |
| :---- | :---- | :---- |
| net.netfilter.nf\_conntrack\_max | 524288 | Secures a massive headroom. At 304 bytes per node, this consumes only \~318MB of RAM, which is negligible on a 16GB host.22 |
| net.netfilter.nf\_conntrack\_tcp\_timeout\_established | 3600 | Reduces the default 5-day timeout to 1 hour, aggressively purging orphaned sessions to free table space.23 |
| net.ipv4.tcp\_fin\_timeout | 30 | Accelerates the reclamation of sockets in the FIN-WAIT-2 state.20 |
| net.ipv4.ip\_local\_port\_range | 1024 65535 | Expands the ephemeral port range to prevent source port exhaustion under high NAT loads.20 |
| net.core.somaxconn | 4096 | Increases the maximum socket listen queue for backend APIs.20 |
| net.core.netdev\_max\_backlog | 16384 | Expands the queue for incoming packets before the kernel begins dropping them, smoothing traffic bursts.20 |

Implementation Note: Because the nf\_conntrack module is loaded dynamically by Docker or iptables, applying these settings via standard /etc/sysctl.d/ files may fail on boot. Administrators must deploy a udev rule targeting the module load event to guarantee application.21

### **SQM Cake Queue Management**

When 1,000 users share a constrained 100Mbps/20Mbps commercial ISP line, unchecked bulk downloads (e.g., torrenting or OS updates) will induce severe bufferbloat. This latency spike can easily cause MQTT coin payment events to time out, resulting in uncredited payments. Smart Queue Management (SQM) utilizing the Common Applications Kept Enhanced (CAKE) algorithm is mandatory to fairly distribute bandwidth and prioritize interactive traffic.26

CAKE replaces the default pfifo\_fast queuing discipline and is configured directly on the Linux host using the tc (Traffic Control) utility.27 For a 100Mbps download and 20Mbps upload connection, shaping rules must be set slightly below the ISP's rated speed to move the bottleneck from the ISP hardware to the Linux kernel, where CAKE can manage it.26

Because tc shapes traffic on egress (data leaving an interface), upload shaping is applied to the WAN interface (eth0), while download shaping requires creating a virtual IFB interface to capture incoming traffic from the LAN interface (eth1.10).26

Bash

\# Upload Shaping on external WAN (eth0)  
tc qdisc replace dev eth0 root cake bandwidth 19mbit diffserv4 dual-dsthost nat wash

\# Download Shaping via Virtual IFB interface  
modprobe ifb  
ip link add ifb0 type ifb  
ip link set ifb0 up  
tc qdisc add dev eth1.10 ingress  
tc filter add dev eth1.10 parent ffff: protocol ip u32 match u32 0 0 action mirred egress redirect dev ifb0  
tc qdisc replace dev ifb0 root cake bandwidth 95mbit diffserv4 dual-srchost nat wash

The nat keyword ensures CAKE inspects the inner IP addresses rather than the masqueraded host IP, while diffserv4 provides priority queuing. CAKE operates transparently beneath Docker's iptables rules and does not interfere with openNDS.

### **VLAN Segmentation Architecture**

For security and traffic isolation, the network must be segmented using 802.1Q VLAN subinterfaces managed via Netplan on Ubuntu.28 The architecture utilizes three primary VLANs:

* **VLAN 10:** Student WiFi. This is the untrusted network heavily gated by openNDS.  
* **VLAN 20:** Admin / Staff. Provides unrestricted internet access bypassing the captive portal.  
* **VLAN 30:** Intranet Apps. An internal network hosting Docker services, accessible from VLAN 10 without requiring coin insertion.

The physical eth1 port acts as an 802.1Q trunk connecting the server to a managed PoE switch (e.g., TP-Link Omada SG2008P). The Netplan configuration defines these logical subinterfaces:

YAML

network:  
  version: 2  
  ethernets:  
    eth0:  
      dhcp4: true \# External WAN connected to ISP  
    eth1:  
      dhcp4: false \# Trunk interface  
  vlans:  
    eth1.10:  
      id: 10  
      link: eth1  
      addresses: \[10.10.0.1/16\]  
    eth1.20:  
      id: 20  
      link: eth1  
      addresses: \[10.20.0.1/24\]

### **Storage and Hardware BOM**

Logging 1,000 active sessions and processing high-frequency micro-transaction coin events requires sustained IOPS. PostgreSQL write-ahead logs (WAL) will inevitably bottleneck on traditional SATA solid-state drives under peak loads. A PCIe Gen3 NVMe SSD is strictly required to ensure database stability.

The tiered hardware bill of materials (BOM), optimized for the Philippine e-commerce market (Shopee/Lazada), provides validated paths for deployment 29:

| Component | ₱10,000–₱12,000 Build | ₱15,000–₱18,000 Build | ₱20,000+ Enterprise Build |
| :---- | :---- | :---- | :---- |
| **Server** | Beelink S12 Pro N100 (16GB RAM) | Dell OptiPlex 3060 Micro (i5-8500T, 16GB) | Lenovo M720q Tiny (i5-8500T, PCIe Expansion) |
| **NIC (LAN)** | USB 3.0 ASIX AX88179A Adapter | M.2 A+E Key to Intel i226-V Gigabit NIC | Intel i350-T2 / i210 Dual Port PCIe x4 NIC |
| **Storage** | Included 500GB NVMe SSD | Upgraded 500GB NVMe (Kingston/WD Blue) | 1TB NVMe Samsung 970 EVO Plus |
| **Switch** | TP-Link SG108E (Smart, Non-PoE) | TP-Link Omada SG2008P (4-Port PoE+) | TP-Link Omada SG2210P (8-Port PoE+) |
| **Wireless APs** | 2x TP-Link EAP225 (AC1350) | 3x TP-Link EAP610 (WiFi 6 AX1800) | 4x Ubiquiti UniFi U6 Lite (WiFi 6\) |
| **Power** | AWG 650VA Line Interactive UPS | CyberPower 1000VA UPS | APC BX1100LI-MS UPS |
| **Estimated Load** | \~600 Concurrent Users | \~800 Concurrent Users | 1000+ Concurrent Users (Stable) |

## **Problem Area 6: Full Session Lifecycle Architecture**

Retrofitting session architecture mid-production to accommodate new features is an inherently dangerous operation that frequently results in data corruption. The foundation must support Phase 1 coin insertions and Phase 2 GCash webhooks symmetrically via a unified state machine.

### **Complete Session State Machine**

The lifecycle of a session dictates network routing access:

1. **PENDING:** A device connects, the captive portal loads, and the browser token is generated. openNDS blocks external internet access.  
2. **ACTIVE:** The backend receives confirmation of a payment event. The backend executes ndsctl auth, instructing openNDS to permit routing.  
3. **EXTENDED:** An ACTIVE session receives additional funds via a mid-session top-up. The backend calculates the new timeout and re-authenticates the client.  
4. **EXPIRED:** The granted time elapses. openNDS automatically drops the network connection and flushes the iptables routing rules.  
5. **SUSPENDED:** An administrator manually revokes access via the Laravel dashboard for policy violations.  
6. **TERMINATED:** For Phase 2, a student explicitly logs out of the portal, instructing the backend to execute ndsctl deauth and release the MAC address bindings immediately.

### **Mid-Session Top-Up Architecture**

When a student inserts a coin while already possessing an ACTIVE session, the system must extend the time without severing the active TCP connections. Crucially, the openNDS mechanism does not natively "add" or accumulate time. Executing ndsctl auth \<MAC\> \<new\_timeout\> completely overwrites the previous timeout setting.11

The backend application must independently track the total granted time and compute the required absolute timeout value:

1. Query the database for the session's start\_time and total\_granted\_seconds.  
2. Calculate the remaining time: remaining\_seconds \= total\_granted\_seconds \- (current\_timestamp \- start\_time).  
3. Calculate the new absolute duration: new\_timeout\_seconds \= remaining\_seconds \+ added\_seconds.  
4. Execute the system command: ndsctl auth \<MAC\> \<new\_timeout\_seconds\>. Note that ndsctl parses time strictly as integer values representing minutes.9  
5. Update the database record: total\_granted\_seconds \= total\_granted\_seconds \+ added\_seconds.

### **PostgreSQL Database Schema**

To support the lifecycle and future Phase 2 developments, the schema must normalize devices, users, and financial transactions.

SQL

\-- Phase 2 Account Upgrades  
CREATE TABLE users (  
    user\_id BIGSERIAL PRIMARY KEY,  
    student\_number VARCHAR(50) UNIQUE NOT NULL,  
    pin\_hash VARCHAR(255) NOT NULL,  
    created\_at TIMESTAMPTZ DEFAULT NOW()  
);

\-- Decouples hardware MAC from Identity  
CREATE TABLE devices (  
    device\_token UUID PRIMARY KEY,  
    last\_known\_mac MACADDR NOT NULL,  
    linked\_user\_id BIGINT REFERENCES users(user\_id) ON DELETE SET NULL,  
    created\_at TIMESTAMPTZ DEFAULT NOW()  
);

CREATE TYPE session\_state AS ENUM ('PENDING', 'ACTIVE', 'EXPIRED', 'SUSPENDED', 'TERMINATED');

\-- The core session ledger  
CREATE TABLE sessions (  
    session\_id BIGSERIAL PRIMARY KEY,  
    device\_token UUID REFERENCES devices(device\_token) NOT NULL,  
    auth\_mac MACADDR NOT NULL,  
    start\_time TIMESTAMPTZ,  
    total\_granted\_minutes INT DEFAULT 0,  
    state session\_state DEFAULT 'PENDING',  
    created\_at TIMESTAMPTZ DEFAULT NOW()  
);

\-- Immutable financial events bridging Coins and GCash  
CREATE TABLE transactions (  
    transaction\_id BIGSERIAL PRIMARY KEY,  
    session\_id BIGINT REFERENCES sessions(session\_id),  
    source\_type VARCHAR(20) NOT NULL, \-- 'COIN', 'GCASH', 'ADMIN'  
    source\_reference VARCHAR(100) UNIQUE NOT NULL, \-- ESP msg\_id or Xendit ID  
    amount DECIMAL(10,2) NOT NULL,  
    minutes\_added INT NOT NULL,  
    processed\_at TIMESTAMPTZ DEFAULT NOW()  
);

### **Session Expiry Enforcement**

While openNDS enforces standard session expiry natively by dropping routing permissions when the ndsctl timeout elapses, administrative interventions or fraud detection scripts require a server-side enforcement mechanism. A Laravel scheduled task (CRON job) operating at one-minute intervals queries the database for ACTIVE sessions where start\_time \+ total\_granted\_minutes \< NOW(), or sessions flagged as SUSPENDED. The backend then executes ndsctl deauth \<MAC\> to sever the connection forcibly 10 and updates the database state to EXPIRED.

### **GCash Integration and Idempotency**

In Phase 2, GCash payments processed via Xendit will trigger asynchronous HTTP webhooks directed at the backend APIs. Webhook architectures are fundamentally prone to duplicate deliveries due to network latency retries. The system must process these notifications idempotently.

The backend relies on Xendit's X-CALLBACK-TOKEN header for origin verification.37 The webhook payload contains a unique external\_id. Before issuing network credits, the backend database initiates a transaction lock. It checks the transactions table to determine if the source\_reference (mapped to the external\_id) already exists. If the record exists, the operation represents a duplicate webhook delivery; the backend instantly responds with HTTP 200 OK and halts further processing. This rigid mechanism strictly prevents a student from receiving double network credits for a single GCash payment.38

### **Multi-Device Policy Configuration**

To empower the Student Body Government with future policy flexibility, the schema implements a linked\_user\_id on the devices table.

* **Token-Based (Isolated Policy):** If the linked\_user\_id field remains NULL, the session balance is strictly bound to the individual device\_token cookie.  
* **Account-Based (Shared Policy):** If a student logs in, the backend links the device\_token to their user\_id. The backend logic dynamically aggregates active time across all devices sharing a user\_id. This architecture permits a student to authenticate on a secondary device, allowing the backend to execute a deauth on the primary device's MAC and seamlessly transfer the remaining financial balance to the new session.

## **Architecture Decision Record (ADR) Summary**

| Problem Area | Architectural Decision | Core Rationale |
| :---- | :---- | :---- |
| **MAC Randomization** | Browser Cookie Tokens | Operates device-agnostically. Survives aggressive iOS 18 / Android 14 bi-weekly and per-SSID rotations silently without injecting login friction. |
| **Firewall Unification** | iptables-nft via DOCKER-USER | Docker aggressively flushes standard chains. DOCKER-USER ensures captive portal enforcement rules and Walled Gardens survive daemon restarts. |
| **MQTT Authorization** | Mosquitto %c pattern ACLs | Restricts ESP32 hardware to device-specific topics, completely neutralizing cross-device spoofing or localized injection attacks. |
| **Subprocess Security** | Node.js execFile (No Shell) | Bypasses system shells to defend against MAC address command injection vectors during ndsctl auth executions. |
| **Backend Framework** | Node.js (Real-time) \+ Laravel (API) | Maximizes the maturity of JS MQTT libraries for IoT while leveraging Laravel's enterprise ORM for Phase 2 billing and administration. |
| **Hardware Specification** | Intel i226-V NICs \+ SQM CAKE | Realtek chips crash under high interrupt loads. CAKE prevents massive bufferbloat from stalling time-sensitive MQTT coin payloads. |

## **Requirements for Hands-on Validation**

While the theoretical foundations of the Phase 1.5 architecture are sound, specific implementations require empirical validation on the deployed hardware:

1. **openNDS FAS Level Compatibility:** While documentation indicates that FAS Level 3 (HTTPS) functions properly, practical testing is required to confirm that the iOS Captive Portal Assistant handles the initial HTTPS redirect gracefully on a localized IP address without generating catastrophic certificate trust errors that halt the connection flow.  
2. **CAKE Queuing on VLAN Subinterfaces:** Network validation must determine whether tc shaping rules applied to the primary eth1 trunk port effectively throttle and classify traffic correctly segmented across the eth1.10 and eth1.20 VLAN subinterfaces, or if individual virtual IFB interfaces must be constructed for each discrete VLAN to ensure precise bandwidth allocation.

#### **Works cited**

1. MAC randomization behavior | Android Open Source Project, accessed May 6, 2026, [https://source.android.com/docs/core/connect/wifi-mac-randomization-behavior](https://source.android.com/docs/core/connect/wifi-mac-randomization-behavior)  
2. Meraki and MAC Address Randomization \- Cisco Meraki ..., accessed May 6, 2026, [https://documentation.meraki.com/Platform\_Management/Dashboard\_Administration/Troubleshooting\_and\_Support/Troubleshooting/Meraki\_and\_MAC\_Address\_Randomization](https://documentation.meraki.com/Platform_Management/Dashboard_Administration/Troubleshooting_and_Support/Troubleshooting/Meraki_and_MAC_Address_Randomization)  
3. Implement MAC randomization | Android Open Source Project, accessed May 6, 2026, [https://source.android.com/docs/core/connect/wifi-mac-randomization](https://source.android.com/docs/core/connect/wifi-mac-randomization)  
4. How iOS 18 MAC Randomization Impacts IT Management \- Cloud4Wi, accessed May 6, 2026, [https://cloud4wi.ai/resources/ios-18-mac-randomization/](https://cloud4wi.ai/resources/ios-18-mac-randomization/)  
5. MAC Randomization in Apple Products \- Netgraph, accessed May 6, 2026, [https://netgraph-connect.com/docs/wiki/faq/mac-randomization-in-apple-products/](https://netgraph-connect.com/docs/wiki/faq/mac-randomization-in-apple-products/)  
6. Understanding MAC Address Rotation in iOS18 \- Datavalet, accessed May 6, 2026, [https://www.datavalet.com/blog/understanding-mac-address-rotation-in-ios18](https://www.datavalet.com/blog/understanding-mac-address-rotation-in-ios18)  
7. Use private Wi-Fi addresses on Apple devices, accessed May 6, 2026, [https://support.apple.com/en-us/102509](https://support.apple.com/en-us/102509)  
8. \[OpenWrt Wiki\] OpenNDS Captive Portal, accessed May 6, 2026, [https://openwrt.org/docs/guide-user/services/captive-portal/opennds](https://openwrt.org/docs/guide-user/services/captive-portal/opennds)  
9. Forwarding Authentication Service (FAS) — openNDS v10.3.0, accessed May 6, 2026, [https://opennds.readthedocs.io/en/stable/fas.html](https://opennds.readthedocs.io/en/stable/fas.html)  
10. Using ndsctl — openNDS v10.3.0 \- the documentation for openNDS, accessed May 6, 2026, [https://opennds.readthedocs.io/en/stable/ndsctl.html](https://opennds.readthedocs.io/en/stable/ndsctl.html)  
11. The Wireless Cookbook: Build Real Projects and Master Wi-Fi, Bluetooth, and LoRa Early Access Edition \- DOKUMEN.PUB, accessed May 6, 2026, [https://dokumen.pub/the-wireless-cookbook-build-real-projects-and-master-wi-fi-bluetooth-and-lora-early-access-edition.html](https://dokumen.pub/the-wireless-cookbook-build-real-projects-and-master-wi-fi-bluetooth-and-lora-early-access-edition.html)  
12. Packet filtering and firewalls | Docker Docs, accessed May 6, 2026, [https://docs.docker.com/network/packet-filtering-firewalls/\#filter-and-forward-outbound-traffic-from-containers](https://docs.docker.com/network/packet-filtering-firewalls/#filter-and-forward-outbound-traffic-from-containers)  
13. What is Docker on Linux Server? (Step-by-Step Guide 2026\) \- YouStable, accessed May 6, 2026, [https://www.youstable.com/blog/what-is-docker-on-linux-server](https://www.youstable.com/blog/what-is-docker-on-linux-server)  
14. mosquitto.conf man page | Eclipse Mosquitto, accessed May 6, 2026, [https://mosquitto.org/man/mosquitto-conf-5.html](https://mosquitto.org/man/mosquitto-conf-5.html)  
15. HMAC Secrets Explained: Authentication You Can Actually Implement \- GitGuardian Blog, accessed May 6, 2026, [https://blog.gitguardian.com/hmac-secrets-explained-authentication/](https://blog.gitguardian.com/hmac-secrets-explained-authentication/)  
16. Step-by-Step Process for HMAC Signature Validation \- Capa.fi, accessed May 6, 2026, [https://docs.capa.fi/docs/step-by-step-process-for-hmac-signature-validation](https://docs.capa.fi/docs/step-by-step-process-for-hmac-signature-validation)  
17. FastAPI vs Node.js: Usage, Speed and Popularity in 2026 | Second Talent, accessed May 6, 2026, [https://www.secondtalent.com/resources/fastapi-vs-node-js-usage-speed-and-popularity/](https://www.secondtalent.com/resources/fastapi-vs-node-js-usage-speed-and-popularity/)  
18. FastAPI vs Node.js: A Developer's Honest Take | by Bhagya Rana | Medium, accessed May 6, 2026, [https://medium.com/@bhagyarana80/fastapi-vs-node-js-a-developers-honest-take-4b2ace82ef83](https://medium.com/@bhagyarana80/fastapi-vs-node-js-a-developers-honest-take-4b2ace82ef83)  
19. FastAPI Performance Benchmarks vs Node.js and Go What the Numbers Actually Mean, accessed May 6, 2026, [https://acquaintsoft.com/blog/fastapi-vs-nodejs-vs-go-performance-benchmarks](https://acquaintsoft.com/blog/fastapi-vs-nodejs-vs-go-performance-benchmarks)  
20. Increasing net.netfilter.nf\_conntrack\_max leads to unavailable server, accessed May 6, 2026, [https://serverfault.com/questions/1191403/increasing-net-netfilter-nf-conntrack-max-leads-to-unavailable-server](https://serverfault.com/questions/1191403/increasing-net-netfilter-nf-conntrack-max-leads-to-unavailable-server)  
21. Setting net.netfilter.nf\_conntrack\_max on Ubuntu 22.04 \- Chris Dzombak, accessed May 6, 2026, [https://www.dzombak.com/blog/2024/03/setting-net-netfilter-nf-conntrack-max-on-ubuntu-22-04/](https://www.dzombak.com/blog/2024/03/setting-net-netfilter-nf-conntrack-max-on-ubuntu-22-04/)  
22. Tuning The Linux Connection Tracking System | Real Time Magazine \- WordPress.com, accessed May 6, 2026, [https://voipmagazine.wordpress.com/2015/02/27/tuning-the-linux-connection-tracking-system/](https://voipmagazine.wordpress.com/2015/02/27/tuning-the-linux-connection-tracking-system/)  
23. How to Configure Netfilter Connection Tracking on Ubuntu \- OneUptime, accessed May 6, 2026, [https://oneuptime.com/blog/post/2026-03-02-how-to-configure-netfilter-connection-tracking-on-ubuntu/view](https://oneuptime.com/blog/post/2026-03-02-how-to-configure-netfilter-connection-tracking-on-ubuntu/view)  
24. EMQX Performance Tuning: Linux Conntrack and MQTT Connections, accessed May 6, 2026, [https://www.emqx.com/en/blog/emqx-performance-tuning-linux-conntrack-and-mqtt-connections](https://www.emqx.com/en/blog/emqx-performance-tuning-linux-conntrack-and-mqtt-connections)  
25. Performance Tuning (Linux) | An Open Source Apache MQTT Broker, accessed May 6, 2026, [https://bifromq.apache.org/docs/1.0.x/configuration/performance\_tuning\_linux/](https://bifromq.apache.org/docs/1.0.x/configuration/performance_tuning_linux/)  
26. How to Configure CAKE qdisc for IPv4 Bandwidth Management on Linux \- OneUptime, accessed May 6, 2026, [https://oneuptime.com/blog/post/2026-03-20-cake-qdisc-ipv4-bandwidth-management/view](https://oneuptime.com/blog/post/2026-03-20-cake-qdisc-ipv4-bandwidth-management/view)  
27. Chapter 35\. Linux traffic control | Configuring and managing networking | Red Hat Enterprise Linux | 9, accessed May 6, 2026, [https://docs.redhat.com/en/documentation/red\_hat\_enterprise\_linux/9/html/configuring\_and\_managing\_networking/linux-traffic-control\_configuring-and-managing-networking](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_networking/linux-traffic-control_configuring-and-managing-networking)  
28. How to Configure a VLAN with Netplan \- OneUptime, accessed May 6, 2026, [https://oneuptime.com/blog/post/2026-03-20-configure-vlan-netplan/view](https://oneuptime.com/blog/post/2026-03-20-configure-vlan-netplan/view)  
29. Shop N100 Beelink Online with Best Discounts and Low Prices | Lazada Philippines, accessed May 6, 2026, [https://www.lazada.com.ph/tag/n100-beelink/](https://www.lazada.com.ph/tag/n100-beelink/)  
30. Jual Beelink Eq12 Pro Murah & Terbaik \- Harga Terbaru Mei 2026 | Tokopedia, accessed May 6, 2026, [https://www.tokopedia.com/find/beelink-eq12-pro?utm\_source=google\&utm\_medium=organic\&utm\_campaign=find](https://www.tokopedia.com/find/beelink-eq12-pro?utm_source=google&utm_medium=organic&utm_campaign=find)  
31. Dell Optiplex 3060 Micro Desktop i3-8100T 8th gen 3.10GHz / i5-8500T 8th gen 2.11GHz 8GB DDR4 RAM 500GB HDD / 256GB SSD with Wifi and bluetooth (Used) (Refurbished) | Lazada PH, accessed May 6, 2026, [https://www.lazada.com.ph/products/dell-optiplex-3060-micro-desktop-i3-8100t-8th-gen-310ghz-i5-8500t-8th-gen-211ghz-8gb-ddr4-ram-500gb-hdd-256gb-ssd-with-wifi-and-bluetooth-used-refurbished-i3358523584.html](https://www.lazada.com.ph/products/dell-optiplex-3060-micro-desktop-i3-8100t-8th-gen-310ghz-i5-8500t-8th-gen-211ghz-8gb-ddr4-ram-500gb-hdd-256gb-ssd-with-wifi-and-bluetooth-used-refurbished-i3358523584.html)  
32. Shop Thinkcentre M720q Tiny Cheap – Fast & Easy | Lazada, accessed May 6, 2026, [https://www.lazada.com.ph/tag/thinkcentre-m720q-tiny/](https://www.lazada.com.ph/tag/thinkcentre-m720q-tiny/)  
33. TP-Link Omada Gigabit Multi-WAN VPN Router (TL-R605)(ER605), accessed May 6, 2026, [https://shop.ibahn.net.ph/products/tp-link-safestream-gigabit-multi-wan-vpn-router-tl-r605er605](https://shop.ibahn.net.ph/products/tp-link-safestream-gigabit-multi-wan-vpn-router-tl-r605er605)  
34. TP-Link | TL-SG2008P | JetStream | 8-Port | Gigabit | Smart | Network | Switch | PoE+ | Shopee Philippines, accessed May 6, 2026, [https://shopee.ph/TP-Link-TL-SG2008P-JetStream-8-Port-Gigabit-Smart-Network-Switch-PoE--i.117867014.7780597177](https://shopee.ph/TP-Link-TL-SG2008P-JetStream-8-Port-Gigabit-Smart-Network-Switch-PoE--i.117867014.7780597177)  
35. TP-Link TL-SG2008P Omada 8-Port Gigabit Smart Switch With 4-Port PoE+, accessed May 6, 2026, [https://shopee.ph/TP-Link-TL-SG2008P-Omada-8-Port-Gigabit-Smart-Switch-With-4-Port-PoE--i.21380649.8349862177](https://shopee.ph/TP-Link-TL-SG2008P-Omada-8-Port-Gigabit-Smart-Switch-With-4-Port-PoE--i.21380649.8349862177)  
36. ndsctl(1) — opennds-daemon-common — Debian testing, accessed May 6, 2026, [https://manpages.debian.org/testing/opennds-daemon-common/ndsctl.1.en.html](https://manpages.debian.org/testing/opennds-daemon-common/ndsctl.1.en.html)  
37. How to validate if the webhook is sent from Xendit? – Xendit Help ..., accessed May 6, 2026, [https://help.xendit.co/hc/en-us/articles/360038072991-How-to-validate-if-the-webhook-is-sent-from-Xendit](https://help.xendit.co/hc/en-us/articles/360038072991-How-to-validate-if-the-webhook-is-sent-from-Xendit)  
38. Overview \- Xendit Docs, accessed May 6, 2026, [https://docs.xendit.co/docs/bill-payment-overview](https://docs.xendit.co/docs/bill-payment-overview)  
39. IDEMPOTENCY : IN LARAVEL CONSISTENT OPERATIONS | by Sandeeppant | Medium, accessed May 6, 2026, [https://sandeeppant.medium.com/idempotency-in-laravel-consistent-operations-ff4e9d967ad6](https://sandeeppant.medium.com/idempotency-in-laravel-consistent-operations-ff4e9d967ad6)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAXCAYAAAARIY8tAAABk0lEQVR4Xu3TPyhFURwH8J8w+FMUhVL+ZCFlUCzEJAYlsgtFmTCIGAxiIQaSTQaLwWIQwyWTrEaFlEEZFIvE93t/595z7q0X7z3F8L71qXfO+d1z3rnnXJF/mj4YjfU1wArMQ3lsLKlUww3MOH0DsAn5sA5LzlhSyYUpOBW7QBmcQ6Np90Cr+R1JBSzADixCXXTYTy90wK7YBTghdzQo+lw3ZJmxMC1wAu3QBEfwCdNiiythwrTdBbijd9EFsmELxs2Ynzw4hGFTwJTAJbxCM+SITsRFmPgCd6JvgGG/B4Wm7Q+w4EX03weZE90FJ+AN8Ywz0dp7U8NXdCvRBa6h1LT9g9uAY6eIYSEXcG8Lw3/mOf01cCF2d+zfF911wnDwAD6g0+kvhlV4gisYET2TSVgWPUOeX1XwQKLwmvH980Zxhz8JF+eV/ba+SPSe70FBbCztcPVtWBO9Xb+aYPJZsde1HrrCijTCg+JHxcNyv8Ix6HfaKYUTDsEbPIje78AztIWVKSb40Hjn4x6h1pZmkslf5AsHIktlRsZS5gAAAABJRU5ErkJggg==>