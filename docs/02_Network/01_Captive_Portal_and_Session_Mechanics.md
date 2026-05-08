# **Technical Architecture and Implementation Analysis for Campus-Scale WiFi Vending Systems**

The deployment of a campus-wide WiFi vending infrastructure involves the intricate synchronization of hypervisor-level resource management, granular Layer 3 traffic control, and highly specific application-layer session states. Utilizing a Proxmox VE hypervisor to consolidate the network gateway and the application backend provides a resilient foundation, yet the efficacy of such a system relies heavily on the nuanced interaction between the openNDS captive portal daemon and the connectivity check behaviors of modern client operating systems. This report provides an exhaustive technical analysis of the mechanisms governing session persistence, bandwidth management, and service discovery within this architecture.

## **Challenge 1: Captive Portal Detection (CPD) and Client Behavioral Analysis**

Captive Portal Detection (CPD) is a proactive investigative process initiated by the client operating system rather than a reactive push from the network infrastructure. When a device associates with a wireless access point and obtains an IP address via DHCP, the OS immediately attempts to reach a set of vendor-controlled endpoints to verify "true" internet connectivity. The outcome of these probes dictates whether the OS informs the user of a functional connection or triggers a restricted browser environment, often referred to as the Captive Network Assistant (CNA).

### **Deterministic Endpoint Probing for Modern Operating Systems**

Modern operating systems have evolved to use specific, lightweight URLs that return a predictable HTTP status or body content. If the response is redirected or modified, the OS identifies the presence of a captive portal.

| Operating System | Connectivity Probe URL | Expected Valid Response | System Reaction to Interception |
| :---- | :---- | :---- | :---- |
| iOS 18 | http://captive.apple.com/hotspot-detect.html | \<title\>Success\</title\> | Launches CNA Sandbox 1 |
| Android 14 | http://connectivitycheck.gstatic.com/generate\_204 | HTTP 204 (No Content) | Displays "Sign in to network" 2 |
| Windows 11 | http://www.msftconnecttest.com/connecttest.txt | "Microsoft Connect Test" | Action Center Prompt 2 |
| Firefox Browser | http://detectportal.firefox.com/canonical.html | HTML Success Page | Opens portal in a new tab 2 |

The evolution of these probes is significant. For instance, Android 14 continues the reliance on cleartext HTTP probes primarily because intercepting an HTTPS request would trigger a TLS certificate warning, potentially alarming the user before the portal is even presented.1 Consequently, the network architect must ensure that these specific domains are not blocked by pre-authentication access control lists (ACLs) but rather intercepted and redirected to the splash page domain.

### **Behavioral Disparities in the iOS Captive Network Assistant (CNA)**

The iOS CNA is a highly restricted WebKit instance designed to isolate the pre-authentication environment from the user's primary browsing data.5 A critical observation for systems architects is the disparity between the CNA and the full Safari browser regarding cookie persistence and local storage. Apple implemented strict sandboxing to prevent malicious captive portals from harvesting authentication cookies or tracking users across sessions.6

When a student interacts with the Laravel splash page inside the iOS CNA, any session cookies or local storage items set during the "coin insertion" phase will likely not be available when the device transitions to the full Safari browser post-authentication. This necessitates a stateless or MAC-address-tied session management strategy on the backend. The student's progress must be tracked in the Ubuntu/Laravel database associated with their device hardware address, as the browser-side session will be cleared once the CNA window closes after successful authentication.5

### **Preemptive Authentication and Non-GUI Device Management**

In a campus environment, not all devices possess a browser capable of triggering the CPD process. IoT devices, gaming consoles, or background application updates may attempt to access the internet without ever initiating a web request. The allow\_preemptive\_authentication directive in the openNDS configuration is the primary tool for managing these scenarios.7

By default, openNDS only tracks and permits authentication for clients currently in the "preauthenticated" state—meaning they have already attempted a web request and been redirected.9 If a device does not support CPD, it remains invisible to the standard ndsctl auth command. Setting option allow\_preemptive\_authentication '1' instructs the openNDS daemon to maintain a record of all connected MAC addresses on the interface, allowing the backend to authorize them even if they haven't visited the splash page.7 This is particularly reliable across device types because it operates at the firewall level (Layer 3/4) rather than relying on application-layer (Layer 7\) browser interactions.

## **Challenge 2: Session Lifecycle Management and Persistent BinAuth Logic**

The requirement for students to "pause" and "resume" their sessions introduces the need for a stateful transition between the active authenticated state and a dormant, credit-preserving state. openNDS facilitates this through the BinAuth interface, a local script execution framework that triggers at every significant change in a client's status.

### **The BinAuth Script Argument Framework**

When openNDS executes the configured BinAuth script (typically located at /usr/lib/opennds/binauth\_log.sh or a custom path), it passes a series of arguments that represent the current state of the client.11 For deauthentication events, which occur when a student clicks "pause" or when their session naturally expires, the arguments are standardized to provide the backend with everything needed to calculate time consumption.

The arguments passed during a client\_deauth, idle\_deauth, or timeout\_deauth event are:

| Argument Index | Parameter | Description |
| :---- | :---- | :---- |
| $1 | Method | The trigger event (e.g., client\_deauth, idle\_deauth) 11 |
| $2 | Client MAC | Unique identifier for the hardware 11 |
| $3 | Bytes Incoming | Total traffic uploaded by the client during the session 11 |
| $4 | Bytes Outgoing | Total traffic downloaded by the client during the session 11 |
| $5 | Session Start | Unix epoch timestamp of authentication 11 |
| $6 | Session End | Unix epoch timestamp of deauthentication 11 |
| $7 | Client Token | Unique session token provided by openNDS 11 |

### **Calculation of Unused Time and Credit Preservation**

To reliably save a student's remaining time, the backend must implement a calculation logic within the BinAuth script that communicates with the Laravel API. The calculation for unused time is a function of the total time originally granted and the duration of the session just ended.

The calculation can be expressed as:

![][image1]  
When the BinAuth script receives a deauthentication method, it should parse $2 (MAC) and the timestamps to determine the consumed duration. It then issues a curl request to the Ubuntu VM backend, updating the student's credit balance. This ensures that even if the student does not explicitly logout, the system captures the exact end time of their internet usage.11

### **Managing the "Walk-Out" Edge Case**

A common challenge in large campuses is the "walk-out" scenario, where a student moves out of range or disables their WiFi without an explicit disconnect signal. openNDS handles this via the idletimeout mechanism.14 The daemon periodically sweeps the client list (governed by the checkinterval setting, often defaulting to 60 seconds) to detect clients that have stopped generating traffic.7

If a client is deemed idle, openNDS triggers the BinAuth script with the idle\_deauth method.11 Critically, this still provides the $5 and $6 timestamps, allowing the system to credit the student for the remaining time after the idle period is accounted for. The idle\_deauth is functionally identical to a manual pause for the purposes of balance preservation, though it may result in a small loss of time (the duration of the idle timeout period itself) for the student.12

## **Challenge 3: Transactional Integrity in Session Extensions**

The mid-session top-up is a complex transactional event because the ndsctl auth command in openNDS is destructive rather than additive; issuing a new auth command for an already authenticated MAC address overwrites the existing expiration time with the new value provided.10

### **Implementation Flow for Seamless Time Extension**

To provide a seamless experience where a student inserts a coin and sees their time increase without a connection drop, the orchestration must happen at the application layer.

1. **Event Capture**: The hardware/backend detects a successful coin insertion and identifies the student's current session in the Laravel database.  
2. **Current State Retrieval**: The backend calculates the *remaining* time for the active session: ![][image2].  
3. **Additive Calculation**: The backend sums the remaining time and the newly purchased time: ![][image3].  
4. **Command Execution**: The backend executes the command on the OpenWrt gateway: ndsctl auth \<MAC\> \<T\_new\_total\_in\_minutes\>.

Since ndsctl auth updates the underlying firewall rules (iptables/nftables) without tearing down the existing connection states, the user experiences no interruption to active TCP streams.9

### **Resolution of Time Units in ndsctl**

A critical implementation detail often misunderstood in legacy documentation is the unit of time used by ndsctl. In current versions of the openNDS daemon, the sessiontimeout argument for the auth command is explicitly calculated in **minutes**.16

Bash

\# Correct syntax for ndsctl auth in recent versions:  
\# ndsctl auth \<ID\> \<timeout\_in\_minutes\> \<up\_rate\> \<down\_rate\> \<up\_quota\> \<down\_quota\> \<custom\>  
\# Example: 2 hours (120 minutes) session for a specific MAC:  
ndsctl auth 00:14:22:01:23:45 120 0 0 0 0 "top-up-event-99"

The global checkinterval in the opennds.conf file determines how frequently the daemon checks if these minute-based timeouts have been reached, ensuring that the resolution of session termination is accurate to within the check interval (defaulting to 15 or 60 seconds depending on the build).7

## **Challenge 4: Congestion Control and Fairness via SQM/CAKE**

Scaling a 100Mbps backhaul to accommodate 1,000 students necessitates a sophisticated approach to bufferbloat management. Standard First-In-First-Out (FIFO) queuing fails under these conditions, as a single high-bandwidth stream (like a video download) can fill the router's buffers, causing latency spikes for all other users. The CAKE (Common Applications Kept Equal) queuing discipline is the recommended solution due to its integrated flow-fairness and host-fairness capabilities.

### **VLAN Subinterfaces and the Necessity of IFB**

In the Linux networking stack, queuing disciplines (qdiscs) are natively effective on egress traffic (packets leaving an interface). To shape ingress traffic (packets coming from the internet to the students), the traffic must be redirected to an Intermediate Functional Block (IFB).18 This is because the gateway cannot control the rate at which the ISP sends data; it can only control the rate at which it drops or delays packets to signal the sender (via TCP congestion control) to slow down.

In OpenWrt, the sqm-scripts package handles this complexity automatically. When SQM is applied to a VLAN subinterface such as eth1.30, the script creates a corresponding ifb interface and uses tc (traffic control) to redirect incoming traffic through the CAKE qdisc on that virtual interface.18 While it is technically possible to apply tc directly to a VLAN subinterface, doing so without an IFB limits shaping to the upload direction only, which is insufficient for managing the downstream 100Mbps bottleneck.

### **Interaction with Docker NAT and Client Visibility**

The visibility of individual client IPs is a primary concern when using CAKE for fairness. If the students were behind a secondary NAT (such as a Docker-managed NAT), CAKE would only see the IP of the NAT gateway (the Docker host), effectively treating all 1,000 students as a single user.18

However, in the proposed architecture, the students are connected to the OpenWrt gateway via VLAN 30\. The OpenWrt gateway acts as the primary DHCP server and gateway for these devices. Consequently, each student's device has a unique IP and MAC address visible to the OpenWrt kernel. CAKE's triple-isolate mode (the default in piece\_of\_cake.qos) will successfully identify these individual flows and ensure that the 100Mbps is distributed fairly among the active student IPs, regardless of the NAT occurring on the App VM for administrative traffic.

### **OpenWrt CAKE Configuration Specification**

For an optimal deployment on eth1.30 with a 100Mbps symmetrical backhaul, the following configuration in /etc/config/sqm is required:

Bash

config queue 'student\_vlan'  
    option enabled '1'  
    option interface 'eth1.30'  
    option download '95000' \# Slightly under-provisioned to ensure gateway control  
    option upload '95000'  
    option qdisc 'cake'  
    option script 'piece\_of\_cake.qos'  
    option linklayer 'ethernet'  
    option overhead '44'     \# Accounting for VLAN tags and PPoE if applicable  
    option qdisc\_advanced '1'  
    option ingress\_ecn 'explicit'  
    option egress\_ecn 'none'

This configuration ensures that the gateway remains the bottleneck, allowing CAKE to manage the queues effectively and prevent bufferbloat.

## **Challenge 5: Service Discovery and Domain Validation**

To ensure a seamless user experience, the splash page must be accessible via a user-friendly domain name. This introduces two challenges: local resolution (Split-Horizon DNS) and valid SSL certificate acquisition for a private network.

### **Split-Horizon DNS via dnsmasq**

The goal of split-horizon DNS is to have portal.studenthub.ph resolve to the local gateway IP (e.g., 10.30.0.1) for students on campus, while potentially resolving to a public address for external users. In OpenWrt, dnsmasq provides this capability through the address and rebind\_domain directives.

A critical hurdle in OpenWrt is the "DNS Rebind Protection," which discards upstream DNS responses that resolve to private (RFC1918) IP addresses. To resolve the portal domain to a local IP, the domain must be whitelisted.19

**OpenWrt /etc/config/dhcp Configuration:**

Bash

config dnsmasq  
    list rebind\_domain 'studenthub.ph'

config domain  
    option name 'portal.studenthub.ph'  
    option ip '10.30.0.1'

This configuration ensures that any DNS query for the portal originating from VLAN 30 will be intercepted by dnsmasq and answered with the local gateway IP, bypassing the need for public internet access to find the portal.

### **SSL Certificate Orchestration via Traefik and DNS-01**

Modern browsers, particularly the iOS CNA, require HTTPS for a secure user experience, yet standard Let's Encrypt HTTP-01 challenges fail when the server is not reachable on port 80/443 from the public internet. The DNS-01 challenge solves this by proving ownership via the DNS provider's API (e.g., Cloudflare).20

Traefik, running in the Ubuntu Docker environment, can automate this process. It uses the Cloudflare API to provision a temporary TXT record, allowing Let's Encrypt to verify domain ownership and issue a wildcard certificate.

**Traefik Static Configuration (traefik.yml):**

YAML

certificatesResolvers:  
  cloudflare\_resolver:  
    acme:  
      email: \[email protected\]  
      storage: acme.json  
      dnsChallenge:  
        provider: cloudflare  
        delayBeforeCheck: 10 \# Useful if Cloudflare propagation is slow  
        resolvers:  
          \- 1.1.1.1:53

**Required Environment Variables for the Traefik Container:**

| Variable | Source | Value Type |
| :---- | :---- | :---- |
| CLOUDFLARE\_EMAIL | Cloudflare Account | Email Address 20 |
| CLOUDFLARE\_API\_KEY | Cloudflare Profile | Global API Key 20 |

By using this method, the portal.studenthub.ph domain will present a valid, CA-signed certificate to student devices, eliminating SSL warnings and ensuring the CNA transitions smoothly to the authenticated state.

## **Architectural Risks and Implementation "Gotchas"**

The complexity of a campus-scale WiFi vending platform introduces several systemic risks that require preemptive mitigation.

### **MAC Randomization (Private WiFi Addresses)**

The shift toward MAC randomization in iOS and Android poses a threat to session tracking. If a student's device rotates its MAC address after a "pause" event, the system will not recognize the device when it reconnects.

* **Behavioral Note**: MAC randomization is typically persistent per SSID. As long as the SSID name (SSID\_Campus\_WiFi) remains unchanged, the "private" MAC generated by the phone for that network usually remains the same.1  
* **Mitigation**: The splash page should include clear instructions for students to disable "Private WiFi Address" for the campus network if they experience session loss. For more advanced tracking, the system should link credits to a student's username rather than just the MAC address.

### **openNDS Socket and Proxmox Volatile Storage**

openNDS utilizes a Unix domain socket (defaulting to /tmp/ndsctl.sock) for communication between the ndsctl utility and the daemon.8 In a Proxmox environment, if the OpenWrt VM experiences a hard reboot or the /tmp directory (which is often a tmpfs/RAM disk) is cleared, the socket must be recreated. Furthermore, openNDS logs and client databases are often stored in volatile memory to protect the flash storage of physical routers.8 In a VM environment, it is recommended to redirect logs to a persistent virtual disk to ensure that session data survives a Proxmox host reboot.

Bash

\# Example redirection in /etc/config/opennds  
option log\_mountpoint '/mnt/persistent\_data/ndslog'

### **Hypervisor Interrupt Latency**

Running a high-traffic gateway in a VM can introduce interrupt latency, which affects SQM precision. On Proxmox, ensure that the OpenWrt VM is utilizing "Host" CPU pass-through and that the network interfaces are using the virtio-net driver with multi-queue support enabled. This ensures that the CAKE qdisc can process the 100Mbps of small packets (typical of 1,000 active students) without CPU bottlenecks.

## **Conclusions and Implementation Recommendations**

The success of a coin-operated WiFi vending platform is defined by the reliability of its session mechanics and the perceived quality of its bandwidth. By leveraging the BinAuth framework of openNDS, the system can provide a sophisticated pause/resume feature that protects student credits during walk-outs or manual disconnects. The integration of CAKE SQM ensures that the 100Mbps backhaul remains usable for all 1,000 potential users, while DNS-01 SSL challenges provide the security posture required by modern mobile operating systems.

Key technical takeaways for the deployment include:

1. **Strict Unit Management**: Always pass timeouts to ndsctl auth in **minutes** to align with the current daemon logic.  
2. **Stateless Frontend**: Design the Laravel backend to be independent of browser cookies, relying instead on MAC-address associations retrieved via BinAuth or ndsctl json.  
3. **Active Congestion Control**: Implement SQM on the VLAN subinterface using an IFB to ensure ingress shaping is functional.  
4. **DNS-01 Over HTTP-01**: Abandon port-based SSL challenges in favor of DNS-based API challenges to support the internal-only resolution of the splash page.

This architectural approach results in a production-grade network that is both resilient to the eccentricities of mobile device behavior and fair in its distribution of limited campus resources.

#### **Works cited**

1. WISPr and Captive Portal Auto-Login: What Still Works in 2026 | Technical Guides | Purple, accessed May 7, 2026, [https://www.purple.ai/en-us/guides/wispr-captive-portal-auto-login-2026](https://www.purple.ai/en-us/guides/wispr-captive-portal-auto-login-2026)  
2. Captive portal \- Wikipedia, accessed May 7, 2026, [https://en.wikipedia.org/wiki/Captive\_portal](https://en.wikipedia.org/wiki/Captive_portal)  
3. Captive portal API support \- Android Developers, accessed May 7, 2026, [https://developer.android.com/about/versions/11/features/captive-portal](https://developer.android.com/about/versions/11/features/captive-portal)  
4. Captive Portal Detection and User Experience in Windows \- Microsoft Learn, accessed May 7, 2026, [https://learn.microsoft.com/en-us/windows-hardware/drivers/mobilebroadband/captive-portals](https://learn.microsoft.com/en-us/windows-hardware/drivers/mobilebroadband/captive-portals)  
5. iOS: Open a Welcome Page in Safari, not CNA (post-authentication) \- Stack Overflow, accessed May 7, 2026, [https://stackoverflow.com/questions/29744245/ios-open-a-welcome-page-in-safari-not-cna-post-authentication](https://stackoverflow.com/questions/29744245/ios-open-a-welcome-page-in-safari-not-cna-post-authentication)  
6. Persistent storage in captive portals or mobile internet while wifi connection without internet, accessed May 7, 2026, [https://serverfault.com/questions/1060010/persistent-storage-in-captive-portals-or-mobile-internet-while-wifi-connection-w](https://serverfault.com/questions/1060010/persistent-storage-in-captive-portals-or-mobile-internet-while-wifi-connection-w)  
7. Configuration Options — openNDS v9.2.0, accessed May 7, 2026, [https://opennds.readthedocs.io/en/v9.2.0/config.html](https://opennds.readthedocs.io/en/v9.2.0/config.html)  
8. Configuration Options — openNDS v9.9.0, accessed May 7, 2026, [https://opennds.readthedocs.io/en/v9.9.0/config.html](https://opennds.readthedocs.io/en/v9.9.0/config.html)  
9. Using ndsctl — openNDS v10.3.0, accessed May 7, 2026, [https://opennds.readthedocs.io/en/stable/ndsctl.html](https://opennds.readthedocs.io/en/stable/ndsctl.html)  
10. ndsctl \- Max Fang's Notes, accessed May 7, 2026, [https://notes.maxfa.ng/Dev/Networking/OpenNDS/Config/ndsctl](https://notes.maxfa.ng/Dev/Networking/OpenNDS/Config/ndsctl)  
11. BinAuth Option — openNDS v10.3.0, accessed May 7, 2026, [https://opennds.readthedocs.io/en/stable/binauth.html](https://opennds.readthedocs.io/en/stable/binauth.html)  
12. BinAuth Option — openNDS v9.0.0, accessed May 7, 2026, [https://opennds.readthedocs.io/en/v9.0.0/binauth.html](https://opennds.readthedocs.io/en/v9.0.0/binauth.html)  
13. openNDS and Forwarding Accounting Service? · Issue \#7 \- GitHub, accessed May 7, 2026, [https://github.com/openNDS/openNDS/issues/7](https://github.com/openNDS/openNDS/issues/7)  
14. preauthidletimeout authidletimeout sessiontimeout · Issue \#155 \- GitHub, accessed May 7, 2026, [https://github.com/openNDS/openNDS/issues/155](https://github.com/openNDS/openNDS/issues/155)  
15. ndsctl(1) — opennds-daemon-common — Debian testing, accessed May 7, 2026, [https://manpages.debian.org/testing/opennds-daemon-common/ndsctl.1.en.html](https://manpages.debian.org/testing/opennds-daemon-common/ndsctl.1.en.html)  
16. openNDS/src/ndsctl.c at master \- GitHub, accessed May 7, 2026, [https://github.com/openNDS/openNDS/blob/master/src/ndsctl.c](https://github.com/openNDS/openNDS/blob/master/src/ndsctl.c)  
17. Configuration Options — openNDS v10.3.0, accessed May 7, 2026, [https://opennds.readthedocs.io/en/stable/config.html](https://opennds.readthedocs.io/en/stable/config.html)  
18. \[OpenWrt Wiki\] SQM (Smart Queue Management), accessed May 7, 2026, [https://openwrt.org/docs/guide-user/network/traffic-shaping/sqm](https://openwrt.org/docs/guide-user/network/traffic-shaping/sqm)  
19. dnsmasq \- forwarding local dns queries \- Stack Overflow, accessed May 7, 2026, [https://stackoverflow.com/questions/70841431/dnsmasq-forwarding-local-dns-queries](https://stackoverflow.com/questions/70841431/dnsmasq-forwarding-local-dns-queries)  
20. Traefik & ACME Certificates Resolver \- Traefik, accessed May 7, 2026, [https://doc.traefik.io/traefik/https/acme/](https://doc.traefik.io/traefik/https/acme/)

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,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>

[image3]: <data:image/png;base64,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>