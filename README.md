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
> *Note: This project represents my ver first bare-metal Linux server installation. As a milestone in my engineering journey, it required extensive research, deep-diving into official Linux man-pages, and troubleshooting architectural restrictions step by step.*

### Day 1: Storage Media Recover & Bootable Media Creation 
* **The Challenge:** The targeted 8GB USB flash driver was unrecognized by the Windows File Explorer and threw critical "Unknown Capacity" errors within the graphical Disk Management interface due to remnants of legacy        partitioning.
* **Low-Level-Troubleshooting:**
    * Attempted to force-erase the block device using `diskpart` via an administrative Command Prompt (CMD), which triggered access-denied errors caused by strict Windows filesystem locks on removable media.
    * Switched execution environments to **Windows PowerShell (Admin)** to bypass standard OS restrictions.
      
* **The Resolution:**
    * Successfully wiped the partition table using the advanced `Clear-Disk -Number 1 -RemoveData -RemoveOEM`cmdlet.
    * Restored the device to a clean storage state, enabling the flash drive to be fully mapped by the host operating system.
* **Flashing the Kernel:** Utilized **Rufus 4.15** to write the official **Ubuntu Server (LTS)** ISO onto the recovered drive. Configured the target properies explicitly to the **GPT partition scheme** and **UEFI (non-        CSM** target system architecture to align with modern ASUS firware compliance.
     
### Day 2: Radical Minimal OS Deployment & Headless Network Engineering
* **The Challenge:** Executed a full destructive bare-metal installation of **Ubuntu Server (minimized)** onto the ASUS eMMC storage. Due to ultra-stripped nature of the kernel, no local text editiors (`nano`, `vi`) or network dependencies were pre-installed, and wireless device drivers were halted post-install.
* **Low-Level System Engineering:**
   * Successfully reconfigured the keyboard layout mapping permanently to Western German standard specifications via `dpkg-reconfigure`.
   * Bypass the lack of text-editiors by utilizing an advanced shell redirection technique. Configured the Netplan core configuration file `00-installer-config.yaml`) using a `cat << 'EOF' | sudo tee` pipeline to force          administrative write operations.
   * **Lid Switch Optimization:** Modified `/etc/system/logind.conf` to set `HandleLidSwitch=ignore` and restarted the daemon via `sudo systemctl restart system-logind` to prevent the laptop from suspending when the lid          is closed.
* **Post-Installation Envronment Prep:**
   * Updated the local package repositories (`sudo apt update`) and installed foundational quality-of-life tools and core diagnostic packages: `nano`, `curl`, `wget`, `git` and `iputils-ping`.
     
* **The Resolution:** Defined the declarative YAML infrastructure parameters for the `wlo1`interface, binding it securely via local DHCP access points. Executed `sudo netplan apply`, verified a fully operating TCP/IP stack within the isolated Linux environment, and succesfully established a remote headless **SSH session* from the main Windows PC, validating full functionality with the hardware lid close. 

### Day 3: User Isolation & Restrictive Access Strategy (Least Privilege)
* **The Challenge:** Initiated the setup for cross-platform automated backups from the Windows workstation. To adhere to "Principle of Least Privilege", an isolated user account was required that could securely ingest data but poses zero security risk to the bas operating system. 
* **System Isolation Enineering:**
    * Created a deicate unprivileged user via `sudo adduser backupuser`. 
    * Enforced strict console isolation by changing the account's operational shell to non-interactive using `sudo usermod -s /usr/sbin/nologin backupuser`. This effectively prevents any interactive terminal logins. 
* **The Obstacle:** Initial cross-platform file transfers via the Windows-PC triggered password prompts and execution failures because the minimal Linux enivorment actively blocked standard SSH access due to the `nologin`shell restriction. 

### Day 4: SSH Key-Based Hardening & Storage Directory Debugging
* **The Challenge:** Attempted to implement passwordless cryptographic authentication by generating an Ed25519 keypair (`ssh-keygen -t ed 25519`) on the windows host and pushing the public key to the server. 
* **Troubleshooting Logs & Blockers:**
    * **Directory Not Found & Typos:** Initial attempts to stage the authorization files using the `nano` editor threw directory creation faults due to an input syntay typo (`.shh` instead of `.ssh`). Resolved this by running structured directory generation commands: `sudo mkdir -p /home/backupuser/.ssh`. 
    * **Linux Permissions Lockout:** File trnsfer payloads continuously failed with `Received message too long` or access denied. Diagnosed this as an ownership conflict because the hidden directoris were created with root privileges. 
* **The Resolution:** Repaired the Unix file permission architecture by transferring absolute ownership to the target account and sealing the paths:
    * `sudo chown -R backupuser:backupuser /home/backupuser/`
    * `sudo chmod 700 /home/backupuser/.ssh`
    * `sudo chmod 600 /home/backupuser/.ssh/.authorized_keys`

### Day 5: SSH Daemon Customization & Succesful Ent-to-End SFTP Verification
* **The Challenge:** Despite fixing directory permissions, the `nologin`shell security policy kept forcing the connection back to standard password queries automation tests. 
* **Advanced Infrastructure Hardening:**
    * Deep-dived into the primary SSH server configuration at `/etc/ssh/sshd_config`.
    * Apprnded a dedicated conditional block restricting the account to secure file system interactions while blocking interactive terminal subsystems:
    ```text
    Match User backupuser
        ForceCommand internal-sftp
        AllowTcpForwarding no
        X11Forwarding no
    ``` 
    * Applied the configuration changes by restarting the server daemon: `sudo systemctl restart sshd`. 
    * Tuned the cryptographic key ledger inside `/home/backupuser/.ssh/authorized_keys`by appending the `restrict` clause directly in fornt of the public key string.
* **The Resolution:** Successfully validated the entire infrastructure workflow. Executed an automated pipeline from the Windows host using native `sftp` redirection, resulting in a passwordless, authenticated, fully secure file delivery of `test.txt`straight into the isolated storage volume of the headless laptop server. 


## Planned Services (Target Architecture)

- [ ] **Docker Engine & Compose:** Core containerization runtime for app isolation.
- [ ] **Pi-hole:** Network-wide ad-blocking and local DNS resolution.
- [ ] **Nginx Reverse Proxy:** Secure traffic routing to internal container ports.
- [ ] **Flask / Node.js Dev Environments:** Hosting local sandboxed web APIs.


