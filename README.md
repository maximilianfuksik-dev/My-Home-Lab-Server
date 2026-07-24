# My-Home-Lab-Server
An ultra-low-power home server project built on a repurposed ASUS consumer laptop. This server functions headless within the local network to host isolated containerized microservices, automate local network management, and serve development environments.


## Hardware Configuration

The infrastructure leverages a fanless, highly power-efficient hardware profile optimiued for 24/7 continuous uptime.

*   **Host System:** ASUS Vivobook Go 15 (E510KA-EJ225WS)
*   **Processor (CPU):** Intel® Celeron® N4500 (2 Cores, 2 Threads, 1.10 GHz Base / 2.80 GHz Burst, 6W TDP)
*   **Memory (RAM):** 4 GB DDR4 (On-board)
*   **Storage (ROM):** 128 GB eMMC (Embedded MultiMediaCard)
*   **Graphics:** Intel® UHD Graphics (Integrated)
*   **Network:** Wi-Fi 5 (802.11ac) 


## Architectural Design & OS Deployment

### 1. Operatin System Strategy 
* **Target OS:** Ubuntu Server (TLS)
* **Rationale:** The factory-installed *Windows 11 Home in S Mode* introduces high idle-resource consumption and execution restrictions. Transitioning to a miniaml, non-GUI Linux kernel guarantees that maximum hardware resources (specifically the 4 GB RAM capacity) are allocated directly to container workloads taher than desktop enviroments.

### 2. Network Layout & Accesibility 
* **IP Configuration:** Static IP or Static DHCP Assignment via loacal router mapping to prevent identity shifts in the local area network (LAN)
* **Access Protocol:** Headless configuration managed exclusively via Secure Shell (SSH) over Port 22.
* **Container Ingress:** Services will beseparated locally via unique Port Bindings (e.g., Port 80/443 for web traffic, Port 53 for local DNS sinkholing).
