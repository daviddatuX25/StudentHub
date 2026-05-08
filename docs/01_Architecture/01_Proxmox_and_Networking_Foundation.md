# **Comprehensive Analysis of Hypervisor Abstraction, Software-Defined Networking, and Captive Portal Integration in Enterprise Virtual Environments**

The architectural landscape of modern data centers is increasingly defined by layers of abstraction that seek to decouple software services from physical hardware constraints. This paradigm, while offering unprecedented flexibility, introduces significant complexities in instruction set passthrough, memory management, and packet steering. The following analysis examines the technical intricacies of nested virtualization, the evolution of Linux-based firewalling architectures, and the deployment of sophisticated gateway services within segmented network environments, specifically focusing on the Proxmox Virtual Environment (VE) ecosystem and its interaction with upstream hypervisors and downstream networking hardware.

## **The Mechanics of Nested Virtualization and Hardware Abstraction**

Nested virtualization represents a recursive abstraction layer where a hypervisor—the "guest hypervisor"—is executed within a virtual machine managed by a "host hypervisor." This configuration is essential for development, testing, and training environments, yet it introduces unique performance penalties and stability challenges. Within the Proxmox VE framework, the efficacy of nested virtualization is primarily dictated by the interaction between the physical CPU, the host hypervisor (such as VMware Workstation or VirtualBox), and the guest hypervisor’s configuration.1

### **CPU Feature Passthrough and Performance Disparities**

A central conflict in nested virtualization involves the selection of CPU types for the intermediary virtual machine. In Proxmox, administrators often oscillate between the "host" CPU type and the "kvm64" compatibility type. The "host" setting is theoretically superior as it passes through the complete instruction set of the physical processor, including essential virtualization extensions like Intel VT-x and AMD-V.1 However, empirical observations indicate a paradoxical performance degradation when running Windows-based guests within a nested Proxmox environment. Reports suggest that using the "host" CPU type in a nested setup can lead to "worryingly slow" boot times and excessive host CPU utilization, despite the guest having access to native instruction sets.1

Conversely, the "kvm64" type provides a standardized, albeit restricted, feature set. While it offers improved stability and faster boot times in some nested scenarios, it fails to provide the nested guest with the virtualization extensions required for tertiary layers.1 For instance, a Windows 10 guest running on a Proxmox VM configured with "kvm64" would be unable to support Windows Subsystem for Linux (WSL2), Hyper-V, or Windows Subsystem for Android (WSA), as these features depend on the exposure of VMX/SVM flags to the guest OS.1

| CPU Type | Extension Support | Performance Impact (Nested) | Use Case Suitability |
| :---- | :---- | :---- | :---- |
| host | Full VT-x/AMD-V/EPT/RVI | Variable; potentially high latency | Performance-critical nested hypervisors |
| kvm64 | Minimal standard KVM | Low overhead; high stability | Generic workloads; no sub-nesting |
| qemu64 | Basic legacy features | Consistent baseline | Maximum compatibility across aging nodes |
| custom | Microarchitecture-specific | Optimized for specific silicon | Heterogeneous clusters with specific ISA needs |

The performance overhead in the "host" configuration is largely attributed to the complexity of nested address translation. Second-Level Address Translation (SLAT) technologies, such as Extended Page Tables (EPT) for Intel and Rapid Virtualization Indexing (RVI) for AMD, are designed to offload the mapping of guest physical memory to host physical memory.3 In a nested scenario, this mapping must occur twice, leading to a "translation lookaside buffer" (TLB) pressure and increased memory access latency.4

### **Stability Anomalies in Modern Operating Systems**

Recent iterations of host operating systems and hypervisors have introduced specific instability patterns in nested environments. Users of VMware Workstation Pro running on Windows 11 25H2 hosts have documented unrecoverable errors when attempting to execute nested guests requiring internal hypervisors.5 These panics often manifest as Exception 0x80000003 (debug breakpoint) and are frequently correlated with conflicts in the host’s graphics driver stack, such as igdml64.dll (Intel GPU driver), which interferes with the virtual CPU's execution context.5

| Hypervisor | Host OS | Symptom | Reported Resolution Attempts |
| :---- | :---- | :---- | :---- |
| VMware Workstation Pro | Windows 11 25H2 | Crash/Panic (vcpu-3) | Disable VBS; Update GPU drivers; bcdedit tweaks |
| VirtualBox | Various | Poor performance | Increase allocated cores; Enable VT-x passthrough |
| Proxmox (Nested) | Any | High CPU load; Slow boot | Switch to kvm64; Disable nested=1 if not required |

These stability issues suggest that nested virtualization is not merely a software toggle but a deep integration with the host’s hardware-level security and driver state. Traditional mitigation strategies, such as disabling Virtualization-Based Security (VBS) or Core Integrity on the host, have shown limited success in resolving these modern panics, indicating a shift toward hardware-enforced isolation that is increasingly resistant to recursive abstraction.3

### **Virtualization-Based Security and Credential Guard**

There is a significant distinction between "nested virtualization" as a feature for running hypervisors and the hardware extensions required for modern Windows security features like Credential Guard and VBS. Contrary to common belief, VBS and Credential Guard do not necessarily require the enabling of the global nested parameter in the KVM module.3 Instead, they require the hypervisor to provide SLAT (EPT/NPT) and specific Hyper-V enlightenments (hv\_\* flags) to the guest.3

VBS operates by creating a Virtual Secure Mode (VSM) that leverages the hypervisor to isolate sensitive memory regions from the primary guest kernel. This is accomplished using the same hardware extensions that power nested virtualization, but it does not technically create a hypervisor-within-a-hypervisor unless the guest itself is hosting additional VMs.2 Proxmox administrators can thus maintain high security in Windows guests by passing through the host CPU type and configuring the machine: pc-q35 type without necessarily enabling the potentially performance-degrading nested=1 option in the host's KVM configuration.2

## **Advanced Network Configuration and VLAN Segmentation**

Effective isolation and traffic management in a Proxmox environment are predicated on a sophisticated understanding of 802.1Q VLAN tagging and the Linux bridge architecture. The transition from physical networking to software-defined networking (SDN) within the hypervisor allows for complex "router-on-a-stick" configurations using a single physical network interface.6

### **The VLAN-Aware Bridge Paradigm**

The traditional method of managing VLANs in Proxmox involved creating a separate Linux bridge (e.g., vmbr1, vmbr2) for every VLAN ID. This approach is increasingly considered legacy, as it leads to "bridge sprawl" and complex /etc/network/interfaces files.6 The modern alternative is the "VLAN-aware" bridge, which allows a single bridge (vmbr0) to handle multiple VLAN tags simultaneously, functioning much like a physical managed switch.7

In a VLAN-aware configuration, the bridge is enabled with the bridge-vlan-aware yes attribute. This allows virtual machine NICs to be assigned specific VLAN tags directly within the Proxmox GUI, while the bridge handles the encapsulation and decapsulation of packets as they egress and ingress the physical network interface.7

Bash

\# Example /etc/network/interfaces for VLAN-aware bridge  
auto eno1  
iface eno1 inet manual

auto vmbr0  
iface vmbr0 inet manual  
    bridge-ports eno1  
    bridge-stp off  
    bridge-fd 0  
    bridge-vlan-aware yes  
    bridge-vids 2-4094

This configuration permits the Proxmox host to participate in a trunked connection with an upstream switch. Furthermore, if the Proxmox management interface itself needs to be on a specific VLAN (for example, VLAN 10), a virtual interface must be defined specifically for that VLAN.7

| Interface Name | Logic | Function |
| :---- | :---- | :---- |
| eno1 | Physical | The hardware Ethernet port |
| vmbr0 | Logical Bridge | The virtual switch handling all traffic |
| vmbr0.10 | VLAN Interface | The management IP for the Proxmox node on VLAN 10 |
| eth0 (in VM) | Virtual NIC | Assigned tag 20; traffic isolated to VLAN 20 |

The implementation of a VLAN-aware bridge also enables the Proxmox node to act as a trunking host for virtualized routers like OPNsense or pfSense. By passing the vmbr0 bridge to the router VM without a specific tag, the router VM can manage its own virtual sub-interfaces for various VLANs, completing the "router-on-a-stick" topology within the software layer.7

### **Interoperability with Managed Switches: TP-Link Omada Case Study**

The efficacy of Proxmox’s virtual networking is dependent on the configuration of the physical switch. Using the TP-Link Omada SG2008P as a reference, the configuration of trunk and access ports is vital for maintaining network integrity across the physical-virtual boundary.11

1. **Trunk Port Configuration:** The port on the switch connected to the Proxmox host must be configured as a "trunk" port (or "General" in some TP-Link models). This involves allowing tagged traffic for all VIDs used within the Proxmox environment (e.g., VLAN 10, 20, 30\) while typically keeping the management VLAN (VLAN 1\) as the untagged PVID.12  
2. **Access Port Configuration:** Ports connected to end-user devices (like a desktop PC) that are not VLAN-aware must be configured as "untagged" members of their respective VLAN. Crucially, the PVID of these ports must be set to the corresponding VLAN ID. For instance, if a port is intended for VLAN 20, its PVID must be 20 to ensure that untagged ingress traffic is properly encapsulated.12  
3. **The PVID Paradox:** A common configuration error involves mismatching the untagged VLAN membership and the PVID. If a port is an untagged member of VLAN 20 but has a PVID of 1, the switch will egress traffic from VLAN 20 to the device, but any return traffic from the device will be placed on VLAN 1, leading to a complete breakdown in bidirectional communication.6

| Switch Port | Connected Device | VLAN Mode | PVID | Tagged VIDs | Untagged VIDs |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Port 1 | Proxmox Host | Trunk | 1 | 10, 20, 30, 40 | 1 |
| Port 2 | Gateway Router | Trunk | 1 | 10, 20, 30, 40 | 1 |
| Port 3 | Desktop PC | Access | 20 | N/A | 20 |
| Port 4 | IoT Device | Access | 30 | N/A | 30 |

This layered approach ensures that the "router-on-a-stick" can provide DHCP and inter-VLAN routing for the entire network while maintaining strict isolation at the hardware level.10

## **Captive Portal Integration and Edge Networking**

In public access or multi-tenant environments, the deployment of captive portals is a standard requirement for user authentication and policy enforcement. openNDS (Open Network Dashboard System) has become a prominent solution for this purpose, particularly within the OpenWrt and generic Linux ecosystems.2

### **openNDS Architecture and Compilation**

openNDS is designed as a lightweight user-space daemon that leverages the Linux kernel's netfilter subsystem (specifically nftables in modern versions) to intercept and redirect HTTP traffic from unauthenticated clients.15 The deployment of openNDS on a generic Linux distribution (such as Ubuntu 24.04 or a Proxmox-hosted Debian VM) requires the compilation of specific dependencies.

The primary dependency for openNDS is libmicrohttpd (MHD), a library for embedding HTTP server functionality. For openNDS versions 10.x and above, MHD version 0.9.71 or higher is required.15 The compilation process involves disabling HTTPS within MHD to maintain the lightweight nature required for high-throughput redirection.15

Bash

\# Core Compilation Workflow for openNDS dependencies  
wget https://ftp.gnu.org/gnu/libmicrohttpd/libmicrohttpd-0.9.71.tar.gz  
tar \-xf libmicrohttpd-0.9.71.tar.gz  
cd libmicrohttpd-0.9.71  
./configure \--disable-https  
make && sudo make install

Once the dependencies are established, openNDS itself is compiled from source. It integrates with the system’s init system (typically systemctl) to manage the daemon's lifecycle and ensures that the necessary redirection rules are injected into the kernel's packet filtering tables upon startup.15

### **Remote Execution and API Integration via ndsctl**

The ndsctl utility provides a command-line interface for interacting with the openNDS daemon. In a modern automated environment, this allows for the integration of the captive portal with external authentication backends, such as a Laravel-based management API.16 By executing ndsctl commands via an SSH client, an external application can programmatically manage the state of clients on the network.16

One of the most powerful features of ndsctl is its ability to output client data in JSON format, which can be easily parsed by remote scripts to synchronize the captive portal's state with a central database.16

| Function | ndsctl Command | Context / Requirement |
| :---- | :---- | :---- |
| Authenticate Client | auth \<IP|MAC\> | Pre-authentication must be enabled for proactive auth |
| Deauthenticate Client | deauth \<IP|MAC\> | Immediate removal from the authenticated list |
| Query Client Data | json \<MAC\> | Returns token, usage stats, and connection time |
| Global Status | status | Checks daemon health and active client count |
| Walled Garden Entry | allow \<IP\> | Temporary bypass for specific destination IPs |

For a Laravel application to effectively manage openNDS, the allow\_preemptive\_authentication option must be enabled in the openNDS configuration. Without this, the daemon will reject authentication attempts for clients that it has not yet redirected, which complicates scenarios where a user might be pre-authorized via a mobile app or a previous session.16

### **Deployment on Edge Hardware: The OpenWrt Ecosystem**

For edge deployments, openNDS is frequently paired with OpenWrt-compatible hardware. This includes flashing lightweight routers like the TP-Link WR840N v4. The flashing process for these devices often necessitates the use of a TFTP server to bypass the restrictions of the manufacturer’s original firmware.17

On OpenWrt, openNDS benefits from the opkg package management system and a highly optimized nftables implementation. This is particularly relevant for low-power SBCs (Single Board Computers) like the Orange Pi or Mango Pi, which may have limited CPU and RAM resources.15 The efficiency of openNDS in these environments is achieved by offloading as much packet processing as possible to the kernel’s fast-path filtering, while only bringing the initial "splash page" request into user space.15

## **The Evolution of Linux Firewalling: nftables and Ubuntu 24.04**

The release of Ubuntu 24.04 (Noble Numbat) marks a significant point in the transition from the legacy iptables framework to the modern nftables architecture. While nftables offers improved performance and a more consolidated syntax, the transition has introduced subtle bugs that can compromise network security if not properly understood.19

### **The iptables-nft Translation Layer and the "Any" Bug**

Ubuntu 24.04 uses nftables as its default backend, but it maintains compatibility with legacy scripts via the iptables-nft utility. This tool translates standard iptables commands into nft rules on the fly.19 However, a significant translation bug has been identified regarding the interpretation of the "any" interface flag (-i any).

In legacy iptables, the \-i any flag is a wildcard indicating that the rule applies to all interfaces. When this is processed by iptables-nft on Ubuntu 22.04 and 24.04, it is incorrectly translated into a literal nft match for an interface named "any" (iifname "any").21 Since an interface with this name rarely exists, rules intended to drop traffic on all interfaces (such as a default-deny policy) will fail to match, potentially leaving the system exposed.21

| Legacy Command | Intended Behavior | nft Translation Bug | Actual Result |
| :---- | :---- | :---- | :---- |
| iptables \-A INPUT \-i any \-j DROP | Drop all incoming packets | iifname "any"... drop | Rule never matches; traffic allowed |
| iptables \-A INPUT \-j DROP | Drop all (omitting \-i) | counter... drop | Rule matches correctly |
| nft add rule... iifname eth0 | Native nft command | N/A (Manual rule) | Correct and performant |

This issue highlights the necessity for systems engineers to migrate toward native nft syntax or to carefully validate translated rules using nft list ruleset to ensure that the kernel-level logic matches the administrative intent.19

### **Docker Networking and Firewall Circumvention**

A perennial challenge in Linux administration is the interaction between Docker and the host-level firewall, such as UFW (Uncomplicated Firewall). Docker manages its own iptables chains to facilitate Network Address Translation (NAT) and port forwarding for containers.22 When a port is mapped using the \-p flag in Docker, the daemon inserts rules into the PREROUTING and FORWARD chains that take precedence over standard UFW rules.22

This means that an administrator might configure UFW to block all traffic to a specific port, only to find that the port is still publicly accessible because Docker has "punched a hole" through the firewall.22 To mitigate this, rules intended to restrict access to Docker containers must be placed in the DOCKER-USER chain, which is evaluated before Docker’s automatic rules.22

### **Docker Bridge Subnets and Walled Garden Conflict**

When openNDS is used in conjunction with containerized services, the internal IP ranges used by Docker (defaulting to 172.17.0.0/16 and 172.18.0.0/16) can cause conflicts with the captive portal’s redirection logic.24 If a user is unauthenticated, openNDS will intercept traffic destined for the internet. However, if the user needs to access a containerized service (part of a "walled garden"), the firewall rules must specifically allow traffic to the Docker bridge subnets.27

The default docker\_gwbridge subnet (172.18.0.0/16) is frequently used for inter-container communication in Swarm environments. Modifying this subnet is possible via the daemon.json configuration, which is often necessary in enterprise environments to avoid overlapping with existing corporate IP space.24

JSON

{  
  "default-address-pools": \[  
    { "base": "172.20.0.0/16", "size": 16 }  
  \]  
}

Failure to properly account for these subnets in the openNDS walled garden rules can result in unauthenticated clients being unable to reach internal resources, even if they are intended to be accessible before login.27

## **Comparative Analysis of Hypervisor Performance and Storage Overhead**

The decision to virtualize high-performance workloads, such as database servers or primary network gateways, requires a rigorous assessment of the overhead introduced by the virtualization layer.

### **Storage Amplification and Write Latency**

One of the most significant performance penalties in a virtualized environment is storage I/O latency. Each layer of abstraction—ranging from the virtual machine's filesystem (e.g., NTFS or Ext4) to the virtual disk format (e.g., QCOW2 or RAW), and finally to the host's underlying storage (e.g., ZFS with CoW or a hardware RAID)—contributes to "write amplification".4

In a nested scenario, this amplification is compounded. A write operation from a sub-nested guest must pass through the guest hypervisor’s disk driver, the host hypervisor’s disk driver, and finally reach the physical controller.4 For performance-critical applications, the use of "VirtIO" drivers and the "host" CPU type is essential, but even these cannot fully eliminate the latency of nested filesystem synchronization.4

### **Memory Overprovisioning and Ballooning**

Memory management in Proxmox and VMware involves techniques like memory ballooning and Kernel Same-page Merging (KSM). While these allow for higher density (running more VMs than the physical RAM would typically allow), they introduce performance non-determinism.4 In a nested environment, the host hypervisor may attempt to balloon memory from the Proxmox VM, while the Proxmox VM is simultaneously attempting to manage the memory of its own guests. This recursive memory management can lead to "swapping inside swapping," which drastically reduces system responsiveness.4

| Feature | Mechanism | Benefit | Performance Penalty |
| :---- | :---- | :---- | :---- |
| Ballooning | Reclaims unused RAM from guest | High VM density | Latency during memory pressure |
| KSM | Merges identical memory pages | Reduced RAM footprint | CPU overhead for scanning |
| HugePages | Uses larger memory pages (2MB/1GB) | Reduced TLB misses | Inflexible allocation |
| VirtIO | Paravirtualized drivers | Faster I/O and Networking | Minimal (Requires guest drivers) |

## **OPNsense and FreeBSD: A Firewall Platform Comparison**

While much of the discussed networking logic applies to Linux-based systems, OPNsense provides a robust alternative based on FreeBSD. The OPNsense release cycle is tied to specific FreeBSD versions, which dictates the available hardware support and networking features.28

### **Kernel-Level Performance and Feature Set**

OPNsense utilizes the pf (packet filter) from OpenBSD, which is widely regarded for its security and performance on FreeBSD. Recent versions of OPNsense have migrated to FreeBSD 13 and 14, introducing support for modern technologies like Intel QuickAssist (QAT) for hardware-accelerated encryption and improved ZFS snapshot management.28

The transition to FreeBSD 14 in OPNsense 24.7 and 25.1 has brought significant improvements in networking throughput and support for modern hardware like 25Gbps and 100Gbps NICs.28 However, for users coming from a Linux background, the lack of nftables support means that captive portal solutions like openNDS require a different integration strategy, often involving the ipfw or pf rule engines native to FreeBSD.28

| OPNsense Version | FreeBSD Base | Major Innovations | PHP/Python Version |
| :---- | :---- | :---- | :---- |
| 25.7 | 14.3-RELEASE | Reusable frontend; strict web UI | PHP 8.3 |
| 24.7 | 14.1-RELEASE | New Dashboard; System Trust | Python 3.11 |
| 23.1 | 13.1-RELEASE | WireGuard kernel module | PHP 8.1 |
| 21.7 | 12.1 (Hardened) | Native ZFS installer | Legacy |

The choice between a Linux-based gateway (like OpenWrt or a custom Debian VM) and a FreeBSD-based gateway (like OPNsense) often comes down to the specific needs for driver support and the administrative familiarity with the respective packet-filtering syntax. OPNsense’s migration toward a modern MVC/API system makes it highly suitable for enterprise automation, mirroring the capabilities found in the ndsctl JSON interface used by openNDS.16

## **Conclusion and Future Outlook**

The research into nested virtualization, advanced networking, and captive portal integration reveals a landscape where the primary challenge is no longer just the provision of services, but the management of the interactions between competing layers of abstraction.

Nested virtualization remains a powerful tool, yet its performance paradoxes—where more "native" CPU settings can sometimes result in slower execution—require a nuanced approach to configuration. The findings suggest that for most enterprise sub-nesting needs, the performance hit of recursive address translation is unavoidable without specialized hardware offloading.

In the realm of networking, the shift toward VLAN-aware bridges in Proxmox and the adoption of nftables in Ubuntu 24.04 represent a significant modernization of the Linux networking stack. However, the discovery of critical translation bugs in the iptables-nft layer serves as a reminder of the risks inherent in such transitions. The circumvention of host firewalls by container engines like Docker further emphasizes the need for a "defense in depth" strategy, where rules are implemented at multiple layers of the stack.

Finally, the integration of captive portal services like openNDS highlights the increasing importance of API-driven network management. The ability to programmatically control user access via JSON-based CLI tools allows for a level of automation that was previously unattainable with legacy gateway solutions. As organizations continue to push toward the edge, the combination of lightweight hypervisors, software-defined networking, and automated gateway services will provide the foundation for the next generation of secure, scalable, and flexible infrastructure.

The synthesis of these disparate technical domains—hypervisors, kernel-level packet filters, and application-level gateways—constitutes the core of modern systems engineering. Success in this field requires not only the mastery of each individual component but a profound understanding of how they influence one another across the virtual-physical divide.

#### **Works cited**

1. cpu=host enables nested virutalization… but is way slower than cpu=kvm64… forum and wiki are contradictory, accessed May 7, 2026, [https://forum.proxmox.com/threads/cpu-host-enables-nested-virutalization%E2%80%A6-but-is-way-slower-than-cpu-kvm64%E2%80%A6-forum-and-wiki-are-contradictory.100110/](https://forum.proxmox.com/threads/cpu-host-enables-nested-virutalization%E2%80%A6-but-is-way-slower-than-cpu-kvm64%E2%80%A6-forum-and-wiki-are-contradictory.100110/)  
2. A beginner's guide to setting up nested virtualization on Proxmox \- XDA Developers, accessed May 7, 2026, [https://www.xda-developers.com/set-up-nested-virtualization-on-proxmox/](https://www.xda-developers.com/set-up-nested-virtualization-on-proxmox/)  
3. Am I wrong about Proxmox and nested virtualization \- Reddit, accessed May 7, 2026, [https://www.reddit.com/r/Proxmox/comments/1o7iono/am\_i\_wrong\_about\_proxmox\_and\_nested\_virtualization/](https://www.reddit.com/r/Proxmox/comments/1o7iono/am_i_wrong_about_proxmox_and_nested_virtualization/)  
4. Does Proxmox degrade Windows performance?, accessed May 7, 2026, [https://forum.proxmox.com/threads/does-proxmox-degrade-windows-performance.107575/](https://forum.proxmox.com/threads/does-proxmox-degrade-windows-performance.107575/)  
5. Nested Virtualization Issues on VMware Workstation Pro 25 \+ Windows 11 25H2, accessed May 7, 2026, [https://community.broadcom.com/vmware-cloud-foundation/discussion/nested-virtualization-issues-on-vmware-workstation-pro-25-windows-11-25h2](https://community.broadcom.com/vmware-cloud-foundation/discussion/nested-virtualization-issues-on-vmware-workstation-pro-25-windows-11-25h2)  
6. Proper or best practice way to set-up VLANs on single NIC? \- Proxmox Support Forum, accessed May 7, 2026, [https://forum.proxmox.com/threads/proper-or-best-practice-way-to-set-up-vlans-on-single-nic.173064/](https://forum.proxmox.com/threads/proper-or-best-practice-way-to-set-up-vlans-on-single-nic.173064/)  
7. Set a VLAN interface in your Proxmox node \- DEV Community, accessed May 7, 2026, [https://dev.to/onticdani/set-a-vlan-interface-in-your-proxmox-node-492n](https://dev.to/onticdani/set-a-vlan-interface-in-your-proxmox-node-492n)  
8. Proxmox network configuration (VLANs) \- Reddit, accessed May 7, 2026, [https://www.reddit.com/r/Proxmox/comments/1q1kvzx/proxmox\_network\_configuration\_vlans/](https://www.reddit.com/r/Proxmox/comments/1q1kvzx/proxmox_network_configuration_vlans/)  
9. Proxmox Example Network Config With VLANs \- Programster's Blog, accessed May 7, 2026, [https://blog.programster.org/proxmox-example-network-config-with-vlans](https://blog.programster.org/proxmox-example-network-config-with-vlans)  
10. One Interface, Multiple VLANs: Proxmox Router on a Stick Guide \- YouTube, accessed May 7, 2026, [https://www.youtube.com/watch?v=U-bdP345BBM](https://www.youtube.com/watch?v=U-bdP345BBM)  
11. How to configure 802.1Q VLAN on TP-Link Easy Smart/Unmanaged Pro Switches, accessed May 7, 2026, [https://www.tp-link.com/us/support/faq/788/](https://www.tp-link.com/us/support/faq/788/)  
12. How to Setup TP-Link AP's Multi-SSID (VLAN) to Work with TP-Link Switch, accessed May 7, 2026, [https://www.tp-link.com/uy/support/faq/418/](https://www.tp-link.com/uy/support/faq/418/)  
13. How to Setup TP-Link AP's Multi-SSID (VLAN) to Work with TP-Link Switch, accessed May 7, 2026, [https://support.omadanetworks.com/en/document/12887/?app=omada](https://support.omadanetworks.com/en/document/12887/?app=omada)  
14. How to Configure Management VLAN on TP-Link Smart and Managed Switches Using the New GUI, accessed May 7, 2026, [https://www.tp-link.com/latam/support/faq/3629/](https://www.tp-link.com/latam/support/faq/3629/)  
15. How to Compile openNDS, accessed May 7, 2026, [https://opennds.readthedocs.io/en/stable/compile.html](https://opennds.readthedocs.io/en/stable/compile.html)  
16. Using ndsctl — openNDS v10.3.0 \- the documentation for openNDS, accessed May 7, 2026, [https://opennds.readthedocs.io/en/stable/ndsctl.html](https://opennds.readthedocs.io/en/stable/ndsctl.html)  
17. \[OpenWrt Wiki\] TP-Link TL-WR840N(EU) v4, accessed May 7, 2026, [https://openwrt.org/toh/tp-link/tl-wr840n\_v4](https://openwrt.org/toh/tp-link/tl-wr840n_v4)  
18. OpenWRT and OPNsense \- NEWB comparison, accessed May 7, 2026, [https://forum.opnsense.org/index.php?topic=51778.0](https://forum.opnsense.org/index.php?topic=51778.0)  
19. Firewall \- Ubuntu security documentation, accessed May 7, 2026, [https://documentation.ubuntu.com/security/security-features/network/firewall/](https://documentation.ubuntu.com/security/security-features/network/firewall/)  
20. does \`ufw\` use \`nftables\` directly or indirectly via \`iptables-nft\`? \- Ask Ubuntu, accessed May 7, 2026, [https://askubuntu.com/questions/1562803/does-ufw-use-nftables-directly-or-indirectly-via-iptables-nft](https://askubuntu.com/questions/1562803/does-ufw-use-nftables-directly-or-indirectly-via-iptables-nft)  
21. Ubuntu 24.04 \- problems with iptables rules \- Server Fault, accessed May 7, 2026, [https://serverfault.com/questions/1166428/ubuntu-24-04-problems-with-iptables-rules](https://serverfault.com/questions/1166428/ubuntu-24-04-problems-with-iptables-rules)  
22. TIL: Docker overrides ufw and iptables rules by injecting it's own rules : r/selfhosted \- Reddit, accessed May 7, 2026, [https://www.reddit.com/r/selfhosted/comments/1atjsra/til\_docker\_overrides\_ufw\_and\_iptables\_rules\_by/](https://www.reddit.com/r/selfhosted/comments/1atjsra/til_docker_overrides_ufw_and_iptables_rules_by/)  
23. Communication within "Project" · coollabsio coolify · Discussion \#5059 \- GitHub, accessed May 7, 2026, [https://github.com/coollabsio/coolify/discussions/5059](https://github.com/coollabsio/coolify/discussions/5059)  
24. docker\_gwbridge \- Mirantis Kubernetes Engine, accessed May 7, 2026, [https://docs.mirantis.com/mke/3.8/install/plan-deployment/mcr-considerations/docker\_gwbridge.html](https://docs.mirantis.com/mke/3.8/install/plan-deployment/mcr-considerations/docker_gwbridge.html)  
25. Internet access on bridge networks, host is fine \- General \- Docker Community Forums, accessed May 7, 2026, [https://forums.docker.com/t/internet-access-on-bridge-networks-host-is-fine/148079](https://forums.docker.com/t/internet-access-on-bridge-networks-host-is-fine/148079)  
26. docker default subnet change while the ip range used by other applications, accessed May 7, 2026, [https://community.blackduck.com/s/article/docker-default-subnet-change-while-the-ip-range-used-by-other-applications](https://community.blackduck.com/s/article/docker-default-subnet-change-while-the-ip-range-used-by-other-applications)  
27. Hotspot Walled Garden Rules Not Working \- Wireless Networking \- MikroTik Forum, accessed May 7, 2026, [https://forum.mikrotik.com/t/hotspot-walled-garden-rules-not-working/50997](https://forum.mikrotik.com/t/hotspot-walled-garden-rules-not-working/50997)  
28. OPNsense Release Information \- Thomas-Krenn-Wiki-en, accessed May 7, 2026, [https://www.thomas-krenn.com/en/wiki/OPNsense\_Release\_Information](https://www.thomas-krenn.com/en/wiki/OPNsense_Release_Information)  
29. Opnsense Build From Source, accessed May 7, 2026, [https://forum.opnsense.org/index.php?topic=22445.0](https://forum.opnsense.org/index.php?topic=22445.0)