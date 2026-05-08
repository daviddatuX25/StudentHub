# **Engineering Analysis and Technical Specification for the StudentHub Vending Hardware Ecosystem**

The physical vending unit for the StudentHub WiFi ecosystem represents the critical bridge between the digital networking infrastructure, previously validated through Proxmox and OpenWrt, and the tangible user interface where currency transactions occur. In a campus environment, where high-frequency usage is coupled with potential environmental stressors and security risks, the hardware design must prioritize durability, precision in currency validation, and seamless integration with the backend session lifecycle manager. This report provides an exhaustive technical deep-dive into the physical vending unit, designated as Epic 3 of the StudentHub development cycle.

## **Electrical Engineering and Signal Interfacing for Currency Validation**

The efficacy of a self-service vending kiosk is fundamentally dependent on the reliability of its currency acceptors. The StudentHub system utilizes a dual-modality approach, integrating both multi-coin and multi-banknote validation systems to cater to the diverse payment habits of the Philippine student population.

### **Multi-Coin Validation Architecture: The CH-926 Integration**

The selection of the CH-926 (or its regional variant, the JY-926) is predicated on its CPU-controlled recognition system, which facilitates the identification of up to six different coin denominations simultaneously.1 This capability is essential in the Philippines, where the circulation of both the older BSP series and the newer New Generation Currency (NGC) coins presents a complex validation landscape. The CH-926 identifies coins by analyzing material composition, diameter, and thickness through a proprietary algorithm that remains stable despite fluctuations in temperature and humidity—an environmental reality in campus deployments.1

The mechanical operation of the CH-926 involves a 12V DC power supply, which must be capable of handling peak currents during solenoid activation. While the nominal working current is approximately 65mA, peak consumption often exceeds 100mA when the internal gate opens to accept a valid coin.3 For the StudentHub deployment, it is observed that a power supply capable of at least 1A is necessary to maintain stability across the entire validation circuit.3

Signal output from the CH-926 is primarily pulse-based. Upon successful recognition of a coin, the device generates a train of pulses on the "COIN" line. The physical characteristics of these pulses are adjustable via a three-way switch located on the rear of the device, allowing for "Fast" (20ms/pulse), "Medium" (50ms/pulse), or "Slow" (70-100ms/pulse) durations.2 Each individual pulse within a train is separated by a fixed 100ms pause.3 A critical engineering challenge identified in the research is the "quick insertion" problem: if a user inserts multiple coins in rapid succession, the pulse trains for different coins can merge into a single, continuous signal.3 To resolve this, the StudentHub firmware adopts a proportional pulse-to-value mapping, where ₱1 results in 1 pulse, ₱5 in 5 pulses, and ₱10 in 10 pulses, allowing the backend to calculate the total value regardless of insertion speed.3

### **Banknote Validation Engineering: The ICT L70 and Allan Series**

For higher-denomination transactions (₱20, ₱50, and ₱100), the StudentHub unit integrates the ICT L70 bill acceptor. The L70 is engineered for high-security environments, featuring an acceptance rate of 96% or greater and sophisticated anti-stringing mechanisms to prevent fraud.4 The device is constructed from durable plastic and supports four-way banknote insertion, which significantly improves the user experience by reducing rejection rates due to orientation errors.5

The ICT L70 is a multi-interface device, supporting Pulse, RS232, and MDB protocols.4 In the StudentHub architecture, the Pulse interface is prioritized for its simplicity and direct compatibility with the ESP32 interrupt-driven logic. Configuration of the L70 for the Philippine Peso requires the manipulation of internal DIP switches to set the pulse ratio. Standard deployment for the StudentHub project maps 1 pulse to a ₱10 value, effectively generating 2 pulses for a ₱20 bill and 5 pulses for ₱50.6

Power requirements for the L70 are more substantial than the coin selector, with a maximum consumption of 24W during the stacking process.4 This necessitates a robust 12V power rail. If the primary budget is constrained, the "Allan" brand bill acceptor serves as a viable alternative.8 While the Allan units are common in local arcade and kiosk markets, they lack the advanced optical validation and firmware updateability of the ICT L70, which is critical for future-proofing against new banknote releases by the Bangko Sentral ng Pilipinas.8

### **Signal Conditioning and Optoisolation Theory**

A primary risk in vending hardware is the potential for high-voltage transients and electromagnetic interference (EMI) to propagate from the currency acceptors' solenoids and motors back to the sensitive microcontroller logic. The CH-926 and ICT L70 both operate on a 12V rail, while the ESP32 logic is restricted to 3.3V. Direct connection of these systems is prohibited.

The StudentHub design utilizes PC817 optocouplers to provide galvanic isolation between the 12V vending circuit and the 3.3V microcontroller circuit.10 The PC817 uses an internal LED and phototransistor to transmit signals across an optical gap, ensuring that any electrical surge on the acceptor side does not reach the ESP32. On the input side, the 12V pulse from the acceptor is throttled by a current-limiting resistor (typically ![][image1]) before entering the optocoupler's anode. On the output side, the phototransistor collector is tied to the ESP32's 3.3V rail, while the emitter provides the logic signal to the GPIO pin, pulled low by a ![][image2] resistor to create an Active-High logic state.10

## **ESP32 Controller Architecture and Firmware Logic**

The ESP32-WROOM-32D serves as the primary controller for the vending unit, selected for its dual-core architecture, which allows for simultaneous currency validation and network communication without latency-induced pulse-counting errors.

### **Hardware-Software Interaction and Interrupt Handling**

To ensure no pulses are missed—a common failure in polling-based systems—the ESP32 firmware utilizes hardware interrupts (Interrupt Service Routines or ISRs). These ISRs are executed immediately upon a voltage change on the designated GPIO pins, bypassing the standard execution loop. Because variables modified within an ISR can be accessed by the main loop at any time, they must be declared as volatile to prevent the compiler from caching their values inappropriately.11

Access to multi-byte variables, such as the pulseCount, must be protected by atomic blocks in the main loop. This involves disabling interrupts briefly, copying the variable to a local buffer, and re-enabling interrupts.11 This prevents the processor from reading a partially updated value if an interrupt occurs midway through the read operation. Furthermore, the firmware avoids frequent writes to the ESP32's internal EEPROM to store the balance, as EEPROM has a finite write cycle life; instead, it utilizes a combination of RAM-based tracking and periodic MQTT-based cloud synchronization.11

### **ESP32 Firmware Skeleton (C++/PlatformIO)**

The following firmware skeleton provides the logical framework for the StudentHub vending unit. It incorporates the pulse train timing logic, MQTT event publishing, and basic OLED display feedback.

C++

\#**include** \<Arduino.h\>  
\#**include** \<WiFi.h\>  
\#**include** \<PubSubClient.h\>  
\#**include** \<Wire.h\>  
\#**include** \<Adafruit\_GFX.h\>  
\#**include** \<Adafruit\_SSD1306.h\>

// I/O Pin Definitions  
\#**define** PIN\_COIN\_INPUT 14  
\#**define** PIN\_BILL\_INPUT 27  
\#**define** PIN\_SYSTEM\_RELAY 12  
\#**define** OLED\_SDA 21  
\#**define** OLED\_SCL 22

// System Parameters  
const char\* WIFI\_SSID \= "StudentHub\_Mgmt";  
const char\* MQTT\_BROKER \= "192.168.10.5"; // Proxmox Backend IP  
const uint32\_t PULSE\_WINDOW \= 600; // ms to wait for pulse train completion

// Volatile State Variables  
volatile uint32\_t pulseCounter \= 0;  
volatile uint32\_t lastPulseReceived \= 0;  
bool isAwaitingProcessing \= false;

// Hardware Drivers  
Adafruit\_SSD1306 display(128, 64, \&Wire, \-1);  
WiFiClient espClient;  
PubSubClient mqtt(espClient);

// Interrupt Service Routine for Coin/Bill Detection  
void IRAM\_ATTR onCurrencyPulse() {  
    pulseCounter++;  
    lastPulseReceived \= millis();  
    isAwaitingProcessing \= true;  
}

void setupDisplay() {  
    if(\!display.begin(SSD1306\_SWITCHCAPVCC, 0x3C)) {  
        Serial.println("Display Error");  
        return;  
    }  
    display.clearDisplay();  
    display.setTextSize(1);  
    display.setTextColor(SSD1306\_WHITE);  
    display.setCursor(0,0);  
    display.println("StudentHub V1.0");  
    display.display();  
}

void connectNetwork() {  
    WiFi.begin(WIFI\_SSID, "campus\_secure\_pass");  
    while (WiFi.status()\!= WL\_CONNECTED) delay(500);  
    mqtt.setServer(MQTT\_BROKER, 1883);  
}

void publishPayment(uint32\_t pulses) {  
    // Logic: 1 Pulse \= 1 PHP for Coins; 1 Pulse \= 10 PHP for Bills  
    // Specific logic depends on pin-to-device mapping  
    char payload;  
    snprintf(payload, 128, "{\\"unit\_id\\":\\"HUB-01\\",\\"pulses\\":%d,\\"timestamp\\":%lu}", pulses, millis());  
    mqtt.publish("sh/v1/payment/raw", payload);  
}

void setup() {  
    Serial.begin(115200);  
    pinMode(PIN\_COIN\_INPUT, INPUT\_PULLDOWN);  
    pinMode(PIN\_BILL\_INPUT, INPUT\_PULLDOWN);  
    pinMode(PIN\_SYSTEM\_RELAY, OUTPUT);  
    digitalWrite(PIN\_SYSTEM\_RELAY, HIGH); // Default ON

    attachInterrupt(digitalPinToInterrupt(PIN\_COIN\_INPUT), onCurrencyPulse, RISING);  
    attachInterrupt(digitalPinToInterrupt(PIN\_BILL\_INPUT), onCurrencyPulse, RISING);  
      
    setupDisplay();  
    connectNetwork();  
}

void loop() {  
    if (\!mqtt.connected()) connectNetwork();  
    mqtt.loop();

    // Check if pulse train is complete  
    if (isAwaitingProcessing && (millis() \- lastPulseReceived \> PULSE\_WINDOW)) {  
        uint32\_t finalCount;  
          
        // Critical Section: Protect pulseCounter access  
        noInterrupts();  
        finalCount \= pulseCounter;  
        pulseCounter \= 0;  
        isAwaitingProcessing \= false;  
        interrupts();

        publishPayment(finalCount);  
          
        display.clearDisplay();  
        display.setCursor(0,10);  
        display.printf("Amount: P%d", finalCount);  
        display.display();  
    }  
}

## **System Integration and Operational Management**

The vending hardware does not operate in isolation. It is part of a larger ecosystem where power schedules and network performance directly influence the unit's profitability and reliability.

### **Power Relay and Operational Scheduling**

The StudentHub unit incorporates a 5V/10A relay module to control the 12V power delivery to the currency validation peripherals. This serves three primary functions:

* **Scheduled Downtime:** In accordance with campus regulations, the system can be programmed to disable currency acceptance during curfew hours (e.g., midnight to 5:00 AM). The backend sends an MQTT command to the ESP32, which toggles the relay, de-energizing the acceptors while keeping the core compute and networking active.  
* **Remote Reset:** If the backend detects a potential jam or communication error with the acceptors, it can remotely trigger a power cycle of the 12V rail to reset the mechanical hardware.  
* **Energy Conservation:** Disabling the high-power bill acceptor when not in use reduces the thermal load within the kiosk enclosure, extending the lifespan of the internal electronics.

### **MQTT Communication Specification**

The communication between the ESP32 and the Proxmox backend is standardized via a JSON-based MQTT protocol. This ensures that the Docker-based application backend can parse incoming payment data and correlate it with the openNDS captive portal session.

| Topic | Function | Data Structure (JSON) |
| :---- | :---- | :---- |
| sh/v1/payment/raw | Real-time payment pulse reporting | {"unit":"H1","p":5,"type":"coin"} |
| sh/v1/system/status | Periodic health and uptime reporting | {"uptime":3600,"temp":45.2,"rssi":-68} |
| sh/v1/control/relay | Inbound command to toggle power | {"cmd":"POWER\_OFF","duration":3600} |
| sh/v1/alert/error | Hardware failure notifications | {"error":"JAM\_BILL","code":404} |

## **Proxmox Backend Performance and Hardware Constraints**

The "brain" of the StudentHub system is a Beelink S12 Pro mini PC, powered by the Intel N100 processor.13 This unit runs a Proxmox hypervisor, hosting the OpenWrt gateway and the application stack. While the N100 is highly efficient for most home-lab and small-scale enterprise tasks, its deployment in a high-density campus WiFi environment requires specific optimizations.

### **Network Interface and Driver Stability**

A significant bottleneck for N100-based mini PCs is the reliance on Realtek RTL8111 or RTL8125 network interface cards (NICs). In Proxmox environments, these NICs often fail to initialize or provide substandard performance due to the default Linux kernel drivers (r8169).14 Reports indicate that under high session loads (approaching 500 concurrent users), the r8169 driver can cause system instability or severe packet loss.14

To achieve the necessary throughput for the StudentHub network, the system administrator must manually compile and install the r8125 DKMS driver on the Proxmox host. This ensures that the NIC can handle the interrupt-heavy traffic generated by the CAKE SQM algorithm and the Traefik reverse proxy.15 Furthermore, the N100 platform is limited to a single channel of DDR4/DDR5 RAM, maxing out at 16GB.16 This necessitates a lightweight approach to VM allocation; for example, utilizing LXC containers for the Docker host instead of full virtual machines to minimize memory overhead.17

### **Thermal and Environmental Considerations**

The N100's performance is also thermally sensitive. In the enclosed environment of a vending kiosk, heat accumulation can lead to CPU throttling, impacting the low-latency requirements of the CAKE SQM queue management. The kiosk enclosure must include active ventilation, triggered either by the ESP32 or the Proxmox host's internal sensors. Research indicates that while the N100 uses very little power (typically 6W-15W TDP), the cumulative heat from the mini PC, the 12V power supply, and the WiFi access point can exceed the passive cooling capacity of a sealed metal box.17

## **Hardware Bill of Materials (BOM) and Procurement Strategy**

The procurement of components for the StudentHub project is tailored to the Philippine market, leveraging major e-commerce platforms like Shopee and Lazada, which offer a balance of price and availability for technical parts.

### **Complete BOM Validation (May 2026 Estimates)**

| Component | Model/Specification | Qty | Unit Price (₱) | Subtotal (₱) | Source |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Compute Node | Beelink S12 Pro (Intel N100, 16GB RAM) | 1 | 13,840 | 13,840 | Shopee 13 |
| WiFi Access Point | TP-Link EAP610-Outdoor (WiFi 6\) | 1 | 7,755 | 7,755 | Shopee 19 |
| Network Switch | TP-Link TL-SG2008P (Managed PoE+) | 1 | 5,490 | 5,490 | Shopee 20 |
| Bill Acceptor | Allan Brand High-Speed Validator | 1 | 2,850 | 2,850 | Shopee 8 |
| Coin Acceptor | CH-926 Multi-Coin Selector | 1 | 1,500 | 1,500 | Sourcewell 1 |
| Main Controller | ESP32-WROOM-32D Development Board | 1 | 350 | 350 | Local Shop |
| System Display | SSD1306 OLED 0.96" I2C 128x64 | 1 | 170 | 170 | Shopee 21 |
| Power Supply | 12V 5A DC Switching Power Supply | 1 | 450 | 450 | Local Shop |
| Optoisolation | PC817 Optocoupler Modules (4-Channel) | 1 | 120 | 120 | Local Shop |
| Logic Relay | 5V 10A SPDT Relay Module | 1 | 80 | 80 | Local Shop |
| **Total Cost** |  |  |  | **32,605** |  |

### **Budget Gap Analysis and Cost Optimization**

The total unit cost of ₱32,605 represents a premium build intended for high-reliability service. For deployments with stricter budgetary limits, the following prioritized cost-cutting measures can be applied:

* **Compute Optimization (Save \~₱5,000):** Replace the Beelink N100 with a refurbished "Tiny-Mini-Micro" PC (e.g., HP EliteDesk 800 G2 Mini). These units often provide comparable performance for network gateway tasks at a significantly lower entry price in the second-hand market.  
* **Networking Optimization (Save \~₱3,500):** Transition from a managed PoE switch to a basic unmanaged PoE injector. While this removes the ability for Omada-based remote port management, it does not fundamentally compromise the captive portal's functionality if the VLANs are handled solely by the Proxmox host.  
* **WiFi Alternative (Save \~₱2,000):** For indoor campus environments, the EAP610-Outdoor can be replaced with an indoor-rated AX1800 access point, provided the environmental humidity is controlled.  
* **Display Downscaling (Save \~₱60):** A standard 16x2 Character LCD with I2C is cheaper than the OLED module and offers better legibility in high-glare environments common in tropical school settings.22

## **Structural and Mechanical Design Specifications**

The physical enclosure of the StudentHub unit must address both security and environmental protection. In the Philippine context, where humidity levels often exceed 80%, the choice of materials is critical.

### **Enclosure and Cooling Architecture**

The enclosure should be fabricated from 1.5mm thick powder-coated cold-rolled steel. This provides the necessary physical security to protect the currency bins from tampering while offering a heat-conductive surface to assist in thermal management. Internal components, particularly the Beelink N100 and the 12V power supply, should be mounted on standoffs to allow for airflow on all sides.

Dual 80mm cooling fans are recommended: one as an intake located at the bottom of the enclosure and one as an exhaust at the top. This creates a vertical chimney effect, which is particularly effective in preventing hot spots. The intake fan must be equipped with a replaceable dust filter to protect the sensitive optical sensors of the ICT L70 bill acceptor from campus dust and debris.4

### **Vending Slot and Bin Security**

The placement of the CH-926 and ICT L70 should be ergonomically optimized for standing height (approx. 100cm from the ground). The internal currency bin should be a separate, double-locked compartment within the main enclosure, ensuring that technicians performing electronic maintenance do not have access to the accumulated cash. This "tiered access" model is standard for high-security vending units.

## **Conclusion and Implementation Roadmap**

The StudentHub vending unit is a sophisticated integration of embedded systems, industrial currency validation, and virtualized networking. The move from theoretical network validation to physical hardware deployment necessitates a focus on signal integrity, electrical safety via optoisolation, and robust firmware that can handle the unique challenges of the Philippine currency landscape.

By utilizing the CH-926 and ICT L70, the system achieves a balance between cost and high-precision validation. The selection of the ESP32 as the hardware controller allows for a modern, MQTT-driven interface that integrates seamlessly with the Proxmox-hosted backend. While the N100 compute platform presents some networking challenges, these are surmountable through proper driver management and optimized containerization.

The final BOM of ₱32,605 provides a clear path toward a professional-grade deployment. Future iterations of the StudentHub project should focus on enhancing the enclosure's environmental resilience and exploring the integration of QR-based digital payments (e.g., GCash) as a supplement to the physical coin and bill infrastructure, thereby further increasing the accessibility of the campus WiFi service.

The implementation of Epic 3 completes the core development phase of the StudentHub project, setting the stage for a pilot deployment where the real-world performance of the pulse-counting logic and the N100's session management can be validated under actual student traffic loads. Through meticulous attention to electrical isolation, thermal management, and market-specific procurement, the StudentHub unit stands as a robust solution for decentralized campus connectivity.

#### **Works cited**

1. DG600F-Multi Coin Acceptor Trader \- Wholesaler / Distributor from Mumbai, accessed May 7, 2026, [https://www.sourcewelldevices.com/coin-acceptor.html](https://www.sourcewelldevices.com/coin-acceptor.html)  
2. Manual of CH-926 \- Arcade Express, accessed May 7, 2026, [https://www.arcadexpress.com/documentos/Manual%20CH926.pdf](https://www.arcadexpress.com/documentos/Manual%20CH926.pdf)  
3. CH923/CH925/CH926/CH928/ JY923/JY925/JY926/JY928 coin ..., accessed May 7, 2026, [https://blog.deconinck.info/post/2017/02/25/CH923/CH926/CH928-coin-acceptor-features-and-caveats](https://blog.deconinck.info/post/2017/02/25/CH923/CH926/CH928-coin-acceptor-features-and-caveats)  
4. ICT L70 MANUAL.pdf \- E & D Trading, Inc, accessed May 7, 2026, [https://endtrading.com/assets/images/Logos/ICT%20L70%20MANUAL.pdf](https://endtrading.com/assets/images/Logos/ICT%20L70%20MANUAL.pdf)  
5. ICT L70 Bill Acceptor Validator Instruction Manual, accessed May 7, 2026, [https://id.manuals.plus/ae/1005007347208925](https://id.manuals.plus/ae/1005007347208925)  
6. L70/P5 DIP SWITCHES SETTING, accessed May 7, 2026, [http://www.ictgroup.net.cn/files/l70-l70p5/L70-BOB5\_P5(Pulse\_ICT\_IGT).pdf](http://www.ictgroup.net.cn/files/l70-l70p5/L70-BOB5_P5\(Pulse_ICT_IGT\).pdf)  
7. MANUAL CABEZAL ICT L70-PEN4.P5 (Pulse+ICT+RS232 B2) | PDF \- Scribd, accessed May 7, 2026, [https://www.scribd.com/doc/259433162/MANUAL-CABEZAL-ICT-L70-PEN4-P5-Pulse-ICT-RS232-B2](https://www.scribd.com/doc/259433162/MANUAL-CABEZAL-ICT-L70-PEN4-P5-Pulse-ICT-RS232-B2)  
8. ALLAN Bill Acceptor – High-Speed Cash Validator for Vending Machines, Arcade & Kiosks, accessed May 7, 2026, [https://shopee.ph/ALLAN-Bill-Acceptor-%E2%80%93-High-Speed-Cash-Validator-for-Vending-Machines-Arcade-Kiosks-i.609565947.28988199251](https://shopee.ph/ALLAN-Bill-Acceptor-%E2%80%93-High-Speed-Cash-Validator-for-Vending-Machines-Arcade-Kiosks-i.609565947.28988199251)  
9. ICT L70 Bill Acceptor Validator Banknote Validation Cash Handling Vending Mech, accessed May 7, 2026, [https://www.ubuy.com.ph/product/31HREZ5W-ict-l70-bill-acceptor-validator-banknote-validation-cash-handling-vending-mech](https://www.ubuy.com.ph/product/31HREZ5W-ict-l70-bill-acceptor-validator-banknote-validation-cash-handling-vending-mech)  
10. Proceedings of the National Engineering Research Symposium \- nerdc.lk, accessed May 7, 2026, [https://nerdc.lk/wp-content/uploads/2022/11/proceeding-2021.pdf](https://nerdc.lk/wp-content/uploads/2022/11/proceeding-2021.pdf)  
11. Troubleshooting CH-926 Coin Acceptor \- Programming \- Arduino Forum, accessed May 7, 2026, [https://forum.arduino.cc/t/troubleshooting-ch-926-coin-acceptor/1103571](https://forum.arduino.cc/t/troubleshooting-ch-926-coin-acceptor/1103571)  
12. How to use CH-926 Coin Acceptor with Arduino \- YouTube, accessed May 7, 2026, [https://www.youtube.com/watch?v=sfE7yqtd8TA](https://www.youtube.com/watch?v=sfE7yqtd8TA)  
13. Beelink Mini PC N100 S12 Pro 16G500G Mini S Intel 11th Gen N5095 8GB 128GB SSD Desktop Gaming Comput | Shopee Philippines, accessed May 7, 2026, [https://shopee.ph/Beelink-Mini-PC-N100-S12-Pro-16G500G-Mini-S-Intel-11th-Gen-N5095-8GB-128GB-SSD-Desktop-Gaming-Comput-i.1591666685.44312687740](https://shopee.ph/Beelink-Mini-PC-N100-S12-Pro-16G500G-Mini-S-Intel-11th-Gen-N5095-8GB-128GB-SSD-Desktop-Gaming-Comput-i.1591666685.44312687740)  
14. proxmox realtek driver issues \- GitHub Gist, accessed May 7, 2026, [https://gist.github.com/SQLJames/fe6fcd5e819d864986ce2eff6ad350da](https://gist.github.com/SQLJames/fe6fcd5e819d864986ce2eff6ad350da)  
15. Realtek 8125 NIC not working on Proxmox with X870E motherboard (no network), accessed May 7, 2026, [https://forum.proxmox.com/threads/realtek-8125-nic-not-working-on-proxmox-with-x870e-motherboard-no-network.164817/](https://forum.proxmox.com/threads/realtek-8125-nic-not-working-on-proxmox-with-x870e-motherboard-no-network.164817/)  
16. Is N100 better than i\* for Proxmox? \- Reddit, accessed May 7, 2026, [https://www.reddit.com/r/Proxmox/comments/1empj4b/is\_n100\_better\_than\_i\_for\_proxmox/](https://www.reddit.com/r/Proxmox/comments/1empj4b/is_n100_better_than_i_for_proxmox/)  
17. Performance: Native/Proxmox on N100 \- Installation \- Home Assistant Community, accessed May 7, 2026, [https://community.home-assistant.io/t/performance-native-proxmox-on-n100/612595](https://community.home-assistant.io/t/performance-native-proxmox-on-n100/612595)  
18. Proxmox VMs running very slow and not sure what else to try \- Reddit, accessed May 7, 2026, [https://www.reddit.com/r/Proxmox/comments/1p2z4w5/proxmox\_vms\_running\_very\_slow\_and\_not\_sure\_what/](https://www.reddit.com/r/Proxmox/comments/1p2z4w5/proxmox_vms_running_very_slow_and_not_sure_what/)  
19. TP-Link Eap610 Outdoor Wi-Fi 6 Ax1800 Indoor Access Point \- Ap | Shopee Philippines, accessed May 7, 2026, [https://shopee.ph/TP-Link-Eap610-Outdoor-Wi-Fi-6-Ax1800-Indoor-Access-Point-Ap-i.102379336.21852782135](https://shopee.ph/TP-Link-Eap610-Outdoor-Wi-Fi-6-Ax1800-Indoor-Access-Point-Ap-i.102379336.21852782135)  
20. TP-Link | TL-SG2008P | JetStream | 8-Port | Gigabit | Smart | Network | Switch | PoE+ | Shopee Philippines, accessed May 7, 2026, [https://shopee.ph/TP-Link-TL-SG2008P-JetStream-8-Port-Gigabit-Smart-Network-Switch-PoE--i.117867014.7780597177](https://shopee.ph/TP-Link-TL-SG2008P-JetStream-8-Port-Gigabit-Smart-Network-Switch-PoE--i.117867014.7780597177)  
21. OLED SSD1306 I2C IIC SPI Serial 128X64 \- Shopee Philippines, accessed May 7, 2026, [https://shopee.ph/OLED-SSD1306-I2C-IIC-SPI-Serial-128X64-i.542813777.24758690106](https://shopee.ph/OLED-SSD1306-I2C-IIC-SPI-Serial-128X64-i.542813777.24758690106)  
22. LCD 1602 16x2 Character LCD Display Module (Blue Backlight) \- Shopee Philippines, accessed May 7, 2026, [https://shopee.ph/LCD-1602-16x2-Character-LCD-Display-Module-(Blue-Backlight)-i.98591228.10905451551](https://shopee.ph/LCD-1602-16x2-Character-LCD-Display-Module-\(Blue-Backlight\)-i.98591228.10905451551)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACIAAAAYCAYAAACfpi8JAAACOklEQVR4Xu2VP0iWURTGn6gwyQhTDJEwoiX/kNiUhUhE4KCEBAVObSI6CUYtuThGUU0uYtBUuYiEISo4SDQZQYMEBSI0qBA5iFg+j+fevN/97vdnaJLvgR8f73vOd++5555zXqCkQ6YT5Cw5HhsSkk8juUNukRpyJMMjh86Te/FLpwbylfwl32DB5FI5GSbr5DkskF7ygayQG0gEdIn0kzmySyYyzRk6RRbJW3IssnmdJu/JJmmLbNpcAf5xvxnBKJDbsD+tIn8g8tUpH8SGQH2wrL1E4tRUJflEtsnVyLavWvID+QPpgZ3mZmxwqiALsEDkm0vaQz6jsUEqJhDd93dS555Pworwonv2a2iTLvcuJR9Icq9CgfiUTsM6p4W8IY/JEqx4FdgsbBMVZ0q6rtcwn+QVFwokrA/d7SNyDtZBYRcNwDZR9lLyB1IxN0W2fRUKRCdUfcg+BJsR4j65FvhpVnyBbaZNY10hW+QZ0sVcMBCdUO29QWZIO3IsRN0lv5DuCmV0DQd1laV8gYTzo4w8JDukI/CRzpBWWKbGkV0D6qp5WIvLR3WWNY/yBRLPD59eXZcWf0qqYHXyAlbM8nkHK2AvrTMFG3oXyBMksuoDUUXHxm7YALrunrXJT/es9GtKStp0kryCZeQjbF0vtfQyGYNNX2X2nzScNFF1/6p28Zt8Js3OZwT2nfGdoROpTfXt0HXVu/eSasmvozq5HNgGA5voDGxFSanWFYQ6SqpR3Fe4pJJK+q/aA5TgeM9sHlv4AAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAYCAYAAACBbx+6AAACw0lEQVR4Xu2WS8hOQRjHH6HI3Vck5Bq5lVxSskRJSViIhYWNZMPik1JIFi4LYUMkC7EQWUghvaEUC5EoFj4lFpISFuTy/5058505c+acSFmdf/3qfZ+Zd87/zDzPM69Zq1b/TX1ElxgeD9SIucvFOjFbDCgP12uiWB8HA00Xh8QpsUEMLA9nOii+iV9iRzQWa6Z4IB6JzeYM7xYfxHExtJhaaIbYKm6LH+JcebhXa8UzMVcMFvvFTTEsnJRrjfgulsQDgZjDi5226otPEC9y+FwShleLxeKNpQ2PFy/FxiA2QjwU24KY1zHRI8ZGca9R4qn4aC4FUuJZnNIF0S8ayzRGvLa0YX78RcwPYuTpedExt+NeQ8Rdcc3qc3GVOTPMY35KPItnvhOTo7FMTYbZsdgwYm68ICdGDu7Mv/Ni08QyK46eMQx3rPyyobzh1HMzNRkmlvphKs5p/BRLRX+xTxwWV60owhXmDJNSpFZKC8VXa0itOsPsQMeqxlDKsM/fKWKPuSLFaNg1Rovn5k6CE0nJ5/AJc6dUUZ3hQeKWVY2h2LAvRArqpBVmSInt5tby2mLOUFjIXhg8K96LWdFYr+oMo9hYXdzn7ydzu0w6JHupuXZ4x9JdgBToMdc6k7uLmgwfsHrDtMJx+few/04110evWLVbzBMjxSJzl0aco3SRx+baH304Hs/UZJgFuFQoJC9M0LrC9hX3X9byhbVSbMrj9G7WYme5NSnCUEetuHF3mSvAirxhemt8DF3mrtC9QYwdZHf9wr44L1lxxBjmO+3siJiUxzF4z5zZG1a0QMQ618VFcUbct+IEM/GmPJgdpAjgs3gi5gTzFohXotvcnc/O8b+B1oU4urdWvvm4zln7ch73G+Fz3T+P69mLNCCV/BgFHxbrX4kf8q+Kq5zrOhRmOPq+UZwd+9N/ba1atWr1D/oNjoqh04sga6sAAAAASUVORK5CYII=>