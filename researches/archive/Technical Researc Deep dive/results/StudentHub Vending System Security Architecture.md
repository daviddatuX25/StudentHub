# **Security and Payment Integrity Architecture for the StudentHub Campus WiFi Vending System**

The deployment of a distributed IoT-based payment and access control system within a campus environment necessitates a robust, multi-layered security architecture. The StudentHub system, which integrates ESP32-based hardware for physical currency collection with a virtualized Proxmox backend and an OpenWrt gateway, presents a complex attack surface. Security must be addressed not merely as an add-on but as a foundational element of the communication protocols, command execution environment, and financial transaction handling. This report analyzes the security and payment integrity of the StudentHub architecture, focusing on MQTT security, the prevention of command injection on the gateway, and the idempotent processing of digital payment webhooks.

## **4.1 MQTT Communication Security and Anti-Replay Architectures**

The MQTT (Message Queuing Telemetry Transport) protocol serves as the primary messaging backbone for the StudentHub architecture, facilitating high-frequency communication between the ESP32 vending units and the centralized Node.js backend hosted on Proxmox. In a campus environment, where the local area network (LAN) may be shared with thousands of students, the risk of unauthorized access, message spoofing, and replay attacks is substantial. The design must ensure that only authorized devices can publish payment events and that those events cannot be duplicated or intercepted by malicious actors.

### **Configuration of Mosquitto Access Control Lists via Client Identity**

The primary defense against unauthorized topic access is the implementation of a robust Access Control List (ACL). In the StudentHub system, it is critical that each ESP32 device is restricted to its own designated topic hierarchy. This prevents a compromised or malicious device from publishing fraudulent payment events on behalf of another unit. The Mosquitto broker supports pattern-based ACLs that utilize substitution variables to enforce this isolation.1

The %c variable in Mosquitto configuration matches the Client ID provided by the device during the CONNECT phase.1 For a system using the topic structure sh/v1/payment/raw/HUB-01, where HUB-01 corresponds to the Client ID, the ACL must be configured to ensure that only a client with the identity HUB-01 can write to that specific topic. Using the mosquitto\_acl\_file plugin or the internal acl\_file option allows for granular control over these permissions.2

The configuration of the aclfile must follow a specific sequence to ensure that global patterns do not inadvertently grant broader access than intended. For the StudentHub deployment, the following aclfile provides the necessary isolation:

# **Global patterns for all authenticated users**

# **This allows each device to write to its specific topic based on its Client ID**

pattern write sh/v1/payment/raw/%c

pattern write sh/v1/status/%c

# **Restricted backend service account**

user backend\_user

topic read sh/v1/payment/raw/\#

topic read sh/v1/status/\#

# **Admin management account**

user admin\_user

topic readwrite \#

In this configuration, when an ESP32 with Client ID HUB-01 connects, the broker substitutes %c with HUB-01, effectively creating a rule that allows writing only to sh/v1/payment/raw/HUB-01.3 If the device attempts to publish to sh/v1/payment/raw/HUB-02, the broker will deny the PUBLISH packet and log an ACL violation.1 It is critical to ensure that allow\_anonymous is set to false in the main mosquitto.conf to force authentication for all clients.6 Furthermore, the per\_listener\_settings parameter should be carefully considered if multiple network interfaces are in use.1

### **HMAC-SHA256 Cryptographic Validation for Payload Integrity**

While ACLs prevent a device from publishing to the wrong topic, they do not guarantee that the payload itself has not been tampered with or that the publisher is a legitimate StudentHub device. To achieve message-level authentication and integrity, the system must implement Hash-based Message Authentication Code (HMAC) using the SHA-256 algorithm. HMAC provides a way to verify both the data integrity and the authenticity of a message by using a shared secret key.7

The HMAC process involves the sender generating a cryptographic hash of the message payload combined with a secret key. The receiver re-computes the hash upon arrival and compares it to the signature provided. If the signatures match, the receiver is assured the message was sent by a party possessing the secret key and was not modified in transit.7

#### **Implementation on ESP32 (C++/Arduino)**

On the ESP32 side, the mbedtls library is utilized for cryptographic operations. This library is standard in the ESP32 Arduino core and provides hardware-accelerated SHA-256 functions.9 The following implementation shows the signing of a JSON payload:

C++

\#**include** "mbedtls/md.h"

// Example signing function for ESP32  
String signPayload(String payload, String secretKey) {  
    byte hmacResult;  
    mbedtls\_md\_context\_t ctx;  
    mbedtls\_md\_type\_t md\_type \= MBEDTLS\_MD\_SHA256;

    const size\_t payloadLength \= payload.length();  
    const size\_t keyLength \= secretKey.length();

    mbedtls\_md\_init(\&ctx);  
    mbedtls\_md\_setup(\&ctx, mbedtls\_md\_info\_from\_type(md\_type), 1); // 1 indicates HMAC  
    mbedtls\_md\_hmac\_starts(\&ctx, (const unsigned char \*) secretKey.c\_str(), keyLength);  
    mbedtls\_md\_hmac\_update(\&ctx, (const unsigned char \*) payload.c\_str(), payloadLength);  
    mbedtls\_md\_hmac\_finish(\&ctx, hmacResult);  
    mbedtls\_md\_free(\&ctx);

    String hash \= "";  
    for (int i \= 0; i \< 32; i++) {  
        char str;  
        sprintf(str, "%02x", (int)hmacResult\[i\]);  
        hash \+= str;  
    }  
    return hash;  
}

This function initializes the mbedtls context, sets up the HMAC with the SHA-256 algorithm, and processes the payload to produce a 32-byte hash.7 The resulting hash is then appended to the MQTT message as a signature field.

#### **Verification on Node.js Backend**

The Node.js backend receives the payload and the signature. Using the native crypto module, it performs a comparison. It is vital to use a constant-time comparison function to prevent timing attacks, which could potentially leak information about the secret key.13

JavaScript

const crypto \= require('crypto');

function verifyMqttSignature(payload, receivedSignature, secretKey) {  
    const computedSignature \= crypto  
       .createHmac('sha256', secretKey)  
       .update(typeof payload \=== 'string'? payload : JSON.stringify(payload))  
       .digest('hex');

    // Use timingSafeEqual to mitigate side-channel timing attacks  
    const signatureBuffer \= Buffer.from(receivedSignature, 'hex');  
    const computedBuffer \= Buffer.from(computedSignature, 'hex');

    if (signatureBuffer.length\!== computedBuffer.length) {  
        return false;  
    }

    return crypto.timingSafeEqual(signatureBuffer, computedBuffer);  
}

By ensuring that the payload string is reconstructed exactly as it was sent by the ESP32 (including whitespace and key order), the backend can reliably verify the authenticity of every payment event.

### **Redis-based Anti-Replay and Message Deduplication**

A replay attack involves an attacker capturing a valid payment message and re-sending it to the broker later to gain unearned internet access. Even with a valid HMAC signature, the message would appear legitimate unless the backend tracks message freshness and uniqueness. The StudentHub system employs a Redis-based deduplication mechanism using a unique msg\_id generated by the ESP32 for every transmission.

The backend must implement a check-and-set logic that is atomic. When a message arrives, the backend checks if the msg\_id exists in Redis. If it does not, the message is processed and the msg\_id is stored with a Time-to-Live (TTL).

| Deduplication Component | Specification |
| :---- | :---- |
| Key Pattern | mqtt:dedup:{client\_id}:{msg\_id} |
| Storage Engine | Redis (In-memory for performance) |
| TTL (Expiry) | 24 Hours (Prevents key-space bloat while stopping replays) |
| Atomicity | Handled via SET key value NX EX seconds |

In Node.js, this is executed using the SET command with the NX (Only set if not exist) and EX (Expire) flags. This approach effectively handles race conditions where two identical messages might arrive in quick succession due to network retries or malicious injection.

JavaScript

async function isMessageNew(clientId, msgId) {  
    const key \= \`mqtt:dedup:${clientId}:${msgId}\`;  
    // NX flag ensures the key is only set if it does not already exist  
    const result \= await redis.set(key, Date.now(), 'NX', 'EX', 86400);  
    return result \=== 'OK';  
}

If the isMessageNew function returns false, the backend must immediately drop the message and log a potential replay attack attempt.

### **Local Network Threat Model and the Necessity of TLS**

A fundamental architectural question for the StudentHub project is whether to utilize TLS (Transport Layer Security) for MQTT traffic (Port 8883\) or if HMAC is sufficient given the Proxmox-hosted backend and the ESP32s reside on the same campus LAN.

On a campus network, several threat vectors are prominent:

1. **ARP Spoofing and Man-in-the-Middle (MITM):** Malicious users can intercept traffic between the ESP32 and the gateway by poisoning the ARP cache of the local switches or the gateway itself.  
2. **Passive Sniffing:** Unencrypted MQTT traffic (Port 1883\) allows any user on the same subnet to read the contents of the payment messages, including sensitive metadata like MAC addresses and payment amounts.  
3. **Credential Harvesting:** While ACLs and HMAC protect the data, the MQTT CONNECT packet itself transmits the username and password in plain text on unencrypted connections.

While HMAC provides message integrity and authenticity, it does not provide confidentiality (encryption). An attacker cannot forge a message, but they can see exactly what is being sent. Furthermore, without TLS, the initial authentication credentials of the ESP32 units are vulnerable to capture.

| Security Feature | HMAC-SHA256 Only | TLS (Port 8883\) | Combined (Recommended) |
| :---- | :---- | :---- | :---- |
| Message Integrity | High | High (via MAC) | Highest |
| Authenticity | High | High (via Certs) | Highest |
| Confidentiality | None | High | High |
| Protection against MITM | Partial | Full | Full |
| Credential Security | Low | High | High |

Given that the ESP32 supports hardware-accelerated TLS and the Proxmox environment can handle the overhead of a secure broker, the StudentHub system should prioritize TLS on Port 8883\. This provides a secure tunnel for all MQTT traffic, ensuring that both credentials and payment data are protected from the diverse and untrusted environment of a campus LAN.

## **4.2 Gateway Security and NDSCTL Command Integrity**

The interface between the application backend and the network gateway is a critical security boundary. The StudentHub system uses ndsctl, the control utility for OpenNDS (formerly NoDogSplash), to authenticate clients on the OpenWrt gateway.14 Executing system-level commands from a Node.js or Laravel environment requires rigorous validation to prevent command injection, a vulnerability where an attacker manipulates input to execute unauthorized code on the host operating system.

### **MAC Address Validation Standards and Regular Expressions**

The ndsctl auth command requires a MAC address as an argument.14 Since this MAC address is often derived from client-side requests or MQTT payloads, it must be validated against a strict format. A MAC address consists of 48 bits, typically represented as six groups of two hexadecimal digits separated by colons or hyphens.15

To prevent injection, the regex must be anchored and restricted only to valid characters. The recommended regex for the StudentHub system is:

^(\[0-9A-Fa-f\]{2}\[:-\]){5}(\[0-9A-Fa-f\]{2})$

This regex performs the following checks:

* ^ and $ ensure the entire string is matched, preventing attackers from appending commands after a valid MAC address.16  
* \[0-9A-Fa-f\]{2} ensures each segment consists exactly of two hexadecimal characters.15  
* \[:-\] allows for either a colon or a hyphen as a separator, which is common in diverse network hardware.17

Validation should occur at the earliest possible stage in the backend processing pipeline before any interaction with the operating system shell.

### **Prevention of Shell Injection via Child Process Selection**

The method used to invoke ndsctl on the OpenWrt gateway determines the system's susceptibility to shell injection. In Node.js, the child\_process.exec function spawns a shell and executes the command string within that shell environment. This is highly dangerous as shell metacharacters like ;, &, |, and $() are interpreted by the shell, allowing an attacker to execute arbitrary commands if validation fails.

The safer alternative is child\_process.execFile, which bypasses the shell entirely. Instead of passing a single string to a shell, execFile takes the path to the executable and an array of arguments. These arguments are passed directly to the operating system's execve system call, meaning the shell never sees them and metacharacters are treated as literal text.5

The following table compares the execution methods in Node.js and Python, highlighting the security implications for the StudentHub backend.

| Language | Unsafe Execution (Shell Enabled) | Safe Execution (Shell Disabled) |
| :---- | :---- | :---- |
| Node.js | exec("ndsctl auth " \+ mac) | execFile("/usr/bin/ndsctl", \["auth", mac\]) |
| Python | subprocess.run("ndsctl auth " \+ mac, shell=True) | subprocess.run(\["ndsctl", "auth", mac\], shell=False) |

By using execFile, the system ensures that even if a malicious string like 00:11:22:33:44:55; rm \-rf / were to pass validation, the ndsctl binary would simply receive the entire string as a single argument and fail with a "Format Error," rather than the system executing the rm command.

### **Risk Assessment of Validation Failures and NDSCTL Abuse**

The ndsctl utility provides extensive control over the OpenNDS daemon. If an attacker achieves command injection, the consequences range from service disruption to full gateway compromise.

The ndsctl utility supports several commands that could be weaponized:

* ndsctl status: Discloses internal network information and connected client lists.14  
* ndsctl stop: Disables the captive portal, potentially causing a "fail-open" scenario where the entire campus has free internet, or a "fail-closed" scenario where all access is blocked.14  
* ndsctl deauth \<MAC\>: Allows an attacker to target and disconnect specific students, leading to a localized Denial of Service.14  
* ndsctl debuglevel \<n\>: Can be used to set the logging verbosity to level 3 (debug), which may fill the gateway's storage with excessive log data, eventually crashing the system.14

To mitigate these risks, the gateway should be hardened using Linux security modules. **AppArmor** profiles can be created for the ndsctl binary and the opennds daemon to restrict their access to the filesystem and network. For example, a profile can ensure that ndsctl can only communicate with the specific Unix socket used by the daemon and cannot execute other binaries like wget or sh.21

### **Validation Module Engineering and Fuzzing Strategy**

A dedicated validation module should be implemented to act as a gatekeeper for all gateway-bound commands. This module should include "fuzzing" test cases that simulate common injection payloads to ensure the regex and execution logic are resilient.

JavaScript

// Validation Module (validator.js)  
const macRegex \= /^(\[0-9A-Fa-f\]{2}\[:-\]){5}(\[0-9A-Fa-f\]{2})$/;

function validateMac(mac) {  
    if (typeof mac\!== 'string') return false;  
    return macRegex.test(mac.trim());  
}

// Security Test Cases  
const testPayloads \=;

testPayloads.forEach(payload \=\> {  
    console.log(\`Payload: \[${payload}\] \-\> Valid: ${validateMac(payload)}\`);  
});

This module ensures that only syntactically perfect MAC addresses are ever passed to the operating system, creating a layered defense-in-depth approach.

## **4.3 Xendit Webhook Idempotency and Phase 2 Integration**

The second phase of the StudentHub project involves the integration of digital payments via the Xendit payment gateway. Unlike the MQTT-based coin payments which occur on a controlled network, Xendit webhooks are delivered over the public internet. This requires a different set of security protocols, specifically focusing on webhook authentication and the prevention of "double-crediting" through idempotency.

### **Authentication via X-CALLBACK-TOKEN**

Xendit secures its webhooks by including a verification token in the header of every request. This token, identified by the X-CALLBACK-TOKEN header, is a static secret configured by the developer in the Xendit dashboard.22 The StudentHub backend must verify this token against its stored secret for every incoming POST request.23

The validation flow in a Node.js or Laravel environment is straightforward:

1. Receive the POST request from Xendit.  
2. Extract the X-CALLBACK-TOKEN from the headers.  
3. Compare it to the local environment variable XENDIT\_SECRET\_TOKEN.  
4. If they do not match, return a 401 Unauthorized response immediately and do not process the payload.

JavaScript

// Node.js Express example for Xendit token validation  
app.post('/webhooks/xendit', (req, res) \=\> {  
    const token \= req.headers\['x-callback-token'\];  
    if (token\!== process.env.XENDIT\_SECRET\_TOKEN) {  
        return res.status(401).send('Unauthorized');  
    }  
    // Proceed with idempotency check and payment processing  
});

In Laravel, this is best handled via a dedicated middleware that wraps the webhook routes.24

### **Design of the External ID and Source Reference Deduplication**

In the StudentHub workflow, when a student initiates a digital payment, the backend generates a unique external\_id. This ID is passed to Xendit during the creation of a payment request (e.g., an invoice or a virtual account). When the payment is completed, Xendit sends a webhook containing this same external\_id.23

To prevent double-crediting, the external\_id must be used as a unique identifier in the PostgreSQL database. The deduplication flow should be integrated into a single database transaction.

1. **Start Transaction:** Ensure atomicity.  
2. **Check Status:** Query the payments table for the external\_id. If the status is already 'COMPLETED', skip processing.  
3. **Update/Insert:** Use a unique constraint on the external\_id column to prevent duplicate records at the storage level.  
4. **Credit User:** Update the student's balance or internet timeout.  
5. **Commit Transaction:** Finalize the changes.

The use of a UNIQUE constraint in PostgreSQL provides a final, non-bypassable layer of protection against race conditions.

### **Resolution of Webhook Race Conditions**

A race condition occurs if two identical webhook POST requests for the same external\_id arrive within milliseconds of each other. This can happen if Xendit's retry logic is triggered prematurely or due to network anomalies.26 If both requests are processed by different backend threads simultaneously, they might both see the payment as "unprocessed" and credit the student twice.

The following table compares strategies for preventing these race conditions in the StudentHub backend.

| Strategy | Mechanism | Performance | Reliability |
| :---- | :---- | :---- | :---- |
| **PostgreSQL Unique Constraint** | Database index prevents duplicate external\_id insertion. | High | Absolute |
| **Redis Distributed Lock** | SET external\_id locked NX EX 10 before processing. | Highest | High |
| **PostgreSQL Advisory Locks** | SELECT pg\_advisory\_xact\_lock(id) within a transaction. | Medium | Absolute |
| **Application-level Checking** | if (\!already\_exists) { process() } | High | Low (Susceptible to race) |

For the StudentHub architecture, the **PostgreSQL Unique Constraint** is the most appropriate primary defense. It is inherently atomic and does not require additional infrastructure beyond the existing database. For even higher concurrency, a **Redis Distributed Lock** can be used to ensure that only one worker thread can attempt to process a specific external\_id at a time.

### **HTTP Response Signaling and Retry Policies**

The HTTP status code returned by the StudentHub backend informs Xendit whether the delivery was successful. Xendit treats any response in the 2xx range (e.g., 200 OK, 201 Created) as a success and will stop retrying.26

It is essential to follow these status code conventions:

* **Success (First time):** Return 200 OK.  
* **Duplicate Request:** If the system detects a webhook for an external\_id that has already been processed, it should still return 200 OK. This tells Xendit that the message was received and acknowledged, preventing unnecessary retries that could clog the system.26  
* **Validation Error:** Return 400 Bad Request or 422 Unprocessable Entity if the payload is malformed.  
* **Internal Error:** Return 500 Internal Server Error if the database or gateway is down. This will trigger Xendit's exponential backoff retry schedule, which attempts re-delivery up to six times over 24 hours.27

By adhering to these response standards, the StudentHub system ensures that it remains synchronized with the payment provider while maintaining internal consistency.

## **Infrastructure Security and Multi-Tenant Isolation**

The StudentHub system is hosted on a single Proxmox node, which hosts several Virtual Machines (VMs) and Containers (LXCs). This virtualization layer provides an opportunity for network segmentation that enhances the overall security posture.

### **Proxmox Network Topology and VLAN Segmentation**

The system architecture should utilize Proxmox's bridge networking to create separate VLANs for different functional domains.

1. **VLAN 10 (Management):** Host Proxmox management interface and SSH access. Restricted to administrator IPs.  
2. **VLAN 20 (Backend/Database):** Contains the Node.js/Laravel VM and the PostgreSQL/Redis Docker containers. No direct access from the campus WiFi.  
3. **VLAN 30 (IoT/MQTT):** Dedicated network for ESP32 devices to communicate with the Mosquitto broker.  
4. **VLAN 40 (Public WiFi):** The untrusted network where students connect. This is the network managed by the OpenWrt gateway and OpenNDS.

| Network Segment | Access to Internet | Access to Backend | Access to MQTT |
| :---- | :---- | :---- | :---- |
| **VLAN 20 (Backend)** | Yes (Updates/Webhooks) | Internal Only | Yes (Subscriber) |
| **VLAN 30 (IoT)** | No | Limited (via MQTT) | Yes (Publisher) |
| **VLAN 40 (WiFi)** | Restricted (until auth) | Web Port 80/443 Only | No |

By isolating the ESP32 units and the backend services into separate VLANs, an attacker who gains access to the campus WiFi cannot directly scan or attack the database or the management interfaces of the Proxmox host.

### **Conclusion and Architectural Recommendations**

The StudentHub security and payment integrity architecture is designed to address the unique challenges of an automated vending system in a public campus environment. The combination of MQTT ACLs, HMAC-SHA256 signatures, and Redis-based anti-replay mechanisms ensures that physical coin payments are processed securely and without the risk of duplication.

On the network gateway, the transition from shell-based execution to the more secure execFile pattern, backed by rigorous regex-based MAC validation, effectively mitigates the risk of command injection. The inclusion of AppArmor sandboxing provides a critical safety net for the privileged ndsctl utility.

For Phase 2, the integration of Xendit webhooks leverages established idempotency patterns to ensure financial consistency. By utilizing PostgreSQL's unique constraints and adhering to standardized HTTP response signaling, the system provides a resilient platform for digital transactions.

This multi-layered approach—covering network segmentation, cryptographic authentication, and secure process management—establishes a reliable foundation for the StudentHub campus WiFi vending system, protecting both the service provider's revenue and the students' access integrity.

#### **Works cited**

1. mosquitto.conf man page, accessed May 7, 2026, [https://mosquitto.org/man/mosquitto-conf-5.html](https://mosquitto.org/man/mosquitto-conf-5.html)  
2. ACL file Plugin \- Eclipse Mosquitto, accessed May 7, 2026, [https://mosquitto.org/documentation/plugins/acl-file/](https://mosquitto.org/documentation/plugins/acl-file/)  
3. Acl file configuration in Mosquitto \- mqtt \- Stack Overflow, accessed May 7, 2026, [https://stackoverflow.com/questions/59944345/acl-file-configuration-in-mosquitto](https://stackoverflow.com/questions/59944345/acl-file-configuration-in-mosquitto)  
4. mosquitto/mosquitto.conf at master · eclipse-mosquitto/mosquitto \- GitHub, accessed May 7, 2026, [https://github.com/eclipse-mosquitto/mosquitto/blob/master/mosquitto.conf](https://github.com/eclipse-mosquitto/mosquitto/blob/master/mosquitto.conf)  
5. ACL denies PUBLISH but accepts Will on the same topic · Issue \#3552 \- GitHub, accessed May 7, 2026, [https://github.com/eclipse-mosquitto/mosquitto/issues/3552](https://github.com/eclipse-mosquitto/mosquitto/issues/3552)  
6. mosquitto.conf(5) \- Arch manual pages, accessed May 7, 2026, [https://man.archlinux.org/man/mosquitto.conf.5.en](https://man.archlinux.org/man/mosquitto.conf.5.en)  
7. ESP32 Arduino: Applying the HMAC SHA-256 mechanism \- DFRobot, accessed May 7, 2026, [https://www.dfrobot.com/blog-921.html](https://www.dfrobot.com/blog-921.html)  
8. What is SHA-256 and how to use it on ESP32, accessed May 7, 2026, [https://www.luisllamas.es/en/esp32-sha256/](https://www.luisllamas.es/en/esp32-sha256/)  
9. ESP32 HMAC SHA-256 \- Wokwi ESP32, STM32, Arduino Simulator, accessed May 7, 2026, [https://wokwi.com/projects/407045345171632129](https://wokwi.com/projects/407045345171632129)  
10. ESP32 Arduino Tutorial mbed TLS: using the SHA-256 algorithm \- DFRobot, accessed May 7, 2026, [https://www.dfrobot.com/blog-1002.html](https://www.dfrobot.com/blog-1002.html)  
11. How to Encode a HMAC SHA256 has with base64 on a ESP32 · Issue \#6546 \- GitHub, accessed May 7, 2026, [https://github.com/espressif/arduino-esp32/issues/6546](https://github.com/espressif/arduino-esp32/issues/6546)  
12. ESP32: HMAC with SHA256 (other md's will do, too) via inline c | B4X Programming Forum, accessed May 7, 2026, [https://www.b4x.com/android/forum/threads/esp32-hmac-with-sha256-other-mds-will-do-too-via-inline-c.138094/](https://www.b4x.com/android/forum/threads/esp32-hmac-with-sha256-other-mds-will-do-too-via-inline-c.138094/)  
13. Verify webhook signatures using HMAC | Qlik Developer Portal, accessed May 7, 2026, [https://qlik.dev/apis/event/verify-webhook-signatures-hmac/](https://qlik.dev/apis/event/verify-webhook-signatures-hmac/)  
14. Using ndsctl — openNDS v10.3.0 \- the documentation for openNDS, accessed May 7, 2026, [https://opennds.readthedocs.io/en/stable/ndsctl.html](https://opennds.readthedocs.io/en/stable/ndsctl.html)  
15. How to Use Regex to Match a MAC Address, accessed May 7, 2026, [https://regexforge.com/blog/how-to-use-regex-to-match-a-mac-address](https://regexforge.com/blog/how-to-use-regex-to-match-a-mac-address)  
16. Mac address regex \- UI Bakery, accessed May 7, 2026, [https://uibakery.io/regex-library/mac-address](https://uibakery.io/regex-library/mac-address)  
17. How to validate MAC address using Regular Expression \- GeeksforGeeks, accessed May 7, 2026, [https://www.geeksforgeeks.org/dsa/how-to-validate-mac-address-using-regular-expression/](https://www.geeksforgeeks.org/dsa/how-to-validate-mac-address-using-regular-expression/)  
18. MAC Address Regex JavaScript Validator, Test Patterns Online \- Qodex.ai, accessed May 7, 2026, [https://qodex.ai/all-tools/mac-address-regex-javascript-validator](https://qodex.ai/all-tools/mac-address-regex-javascript-validator)  
19. MAC Address regex validation for comma separated, colon or dash delimited values, accessed May 7, 2026, [https://stackoverflow.com/questions/54784941/mac-address-regex-validation-for-comma-separated-colon-or-dash-delimited-values](https://stackoverflow.com/questions/54784941/mac-address-regex-validation-for-comma-separated-colon-or-dash-delimited-values)  
20. ndsctl(1) — opennds-daemon-common — Debian testing, accessed May 7, 2026, [https://manpages.debian.org/testing/opennds-daemon-common/ndsctl.1.en.html](https://manpages.debian.org/testing/opennds-daemon-common/ndsctl.1.en.html)  
21. \[Release-1.21\] \- When running default (open) security profile, seccomp and apparmor changes are blocked · Issue \#2444 · rancher/rke2 \- GitHub, accessed May 7, 2026, [https://github.com/rancher/rke2/issues/2444](https://github.com/rancher/rke2/issues/2444)  
22. How to validate if the webhook is sent from Xendit?, accessed May 7, 2026, [https://help.xendit.co/hc/en-us/articles/360038072991-How-to-validate-if-the-webhook-is-sent-from-Xendit](https://help.xendit.co/hc/en-us/articles/360038072991-How-to-validate-if-the-webhook-is-sent-from-Xendit)  
23. Callbacks \- In-Person Payment Terminal \- Xendit Documentation, accessed May 7, 2026, [https://terminal-docs.xendit.co/api-reference/terminal-api/callbacks](https://terminal-docs.xendit.co/api-reference/terminal-api/callbacks)  
24. asagiri-moe/xendit-wrapper \- Packagist.org, accessed May 7, 2026, [https://packagist.org/packages/asagiri-moe/xendit-wrapper](https://packagist.org/packages/asagiri-moe/xendit-wrapper)  
25. Refresh Token in Node.js and Laravel: Complete Production Implementation Guide 2026, accessed May 7, 2026, [https://khaizinam.io.vn/en/refresh-token-nodejs-va-laravel-huong-dan-implement-chuan-production-2026](https://khaizinam.io.vn/en/refresh-token-nodejs-va-laravel-huong-dan-implement-chuan-production-2026)  
26. Handling webhooks \- Xendit Docs, accessed May 7, 2026, [https://docs.xendit.co/docs/handling-webhooks](https://docs.xendit.co/docs/handling-webhooks)  
27. Webhook behavior \- Xendit Docs, accessed May 7, 2026, [https://docs.xendit.co/apidocs/webhook-behavior](https://docs.xendit.co/apidocs/webhook-behavior)  
28. Why am I getting error from my webhook? \- Xendit Help Center, accessed May 7, 2026, [https://help.xendit.co/hc/en-us/articles/28158730181273-Why-am-I-getting-error-from-my-webhook](https://help.xendit.co/hc/en-us/articles/28158730181273-Why-am-I-getting-error-from-my-webhook)