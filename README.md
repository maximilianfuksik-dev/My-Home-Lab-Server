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


## Tooling & Enineering Stack

To engineer, safely format, and document this infrastructure, the following specialized tools and environments were utilized: 

* **Network Architecture & Design:**
* **Low-Level Flash Recovery:** Windows PowerShell 5.1/7 (Admin) & Microsoft DiskPart (for hardware-level storage purification).
* **Bpptable Media Flashing:** Rufus 4.15 Portable
* **Target Core Kernel:** Ubuntu Server 24.04 LTS (AMD64 infrastructure ISO)
* **Documentation Ledger:** Visual Studio Code (Markdown) & Git/GitHub. 


## Architectural Design & OS Deployment

### 1. Operatin System Strategy 
* **Target OS:** Ubuntu Server (TLS)
* **Rationale:** The factory-installed *Windows 11 Home in S Mode* introduces high idle-resource consumption and execution restrictions. Transitioning to a miniaml, non-GUI Linux kernel guarantees that maximum hardware resources (specifically the 4 GB RAM capacity) are allocated directly to container workloads rather than desktop enviroments.

### 2. Network Layout & Accesibility 
* **IP Configuration:** Static IP or Static DHCP Assignment via loacal router mapping to prevent identity shifts in the local area network (LAN)
* **Access Protocol:** Headless configuration managed exclusively via Secure Shell (SSH) over Port 22.
* **Container Ingress:** Services will beseparated locally via unique Port Bindings (e.g., Port 80/443 for web traffic, Port 53 for local DNS sinkholing).

## Project Journal 
### Day 1: Storage Media Recover & Bootable Media Creation 
* **The Challenge:** The targeted 8GB USB flash driver was unrecognized by the Windows File Explorer and threw critical "Unknown Capacity" errors within the graphical Disk Management interface due to remnants of legacy        partitioning.
* **Low-Level-Troubleshooting:**
    * Attempted to force-erase the block device using `diskpart` via an administrative Command Prompt (CMD), which triggered access-denied errors caused by strict Windows filesystem locks on removable media.
    * Switched execution environments to **Windows PowerShell (Admin)** to bypass standard OS restrictions.
* **The Resolution:**
    * Successfully wiped the partition table using the advanced `Clear-Disk -Number 1 -RemoveData -RemoveOEM`cmdlet.
    * Restored the device to a clean storage state, enabling the flash drive to be fully mapped by the host operating system.
* **Flashing the Kernel:** Utilized **Rufus 4.15** to write the official **Ubuntu Server (LTS)** ISO onto the recovered drive. Configured the target properies explicitly to the **GPT partition scheme** and **UEFI (non-        CSM** target system architecture to align with modern ASUS firware compliance.    




