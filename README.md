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

### Day 6: Bash Automation, First Bash Script & Memory-Based Progress Tracking
* **The Challenge:** Designed a local server-side processing system to automatically catalog, compress, and track incoming data logs. The goal was to provide an analytical delta progression summary (tracking character increases since the last backup) without standard OS presistent database solutions.
* **Pre-Engineering Research:**
    * Spent several days deep-diving into Unix shell-scripting fundamentals, understanding variable scopes, conditional exextution tress, and pipe-redirection paradigms before writing the production code.
* **Data Metrics Engineering:**
    * Developed a comprehensive Bash automation script (`backup_process.sh`) utilizing low-level command pipelines.
    * Leveraged `find` and `wc -l` to map directory structure counts while filtering out hidden core SSH components. 
    * Implemented a data-agnostic character analytics "engine" using `find -exec cat {} + | wc -m` to evaluate global alphanumeric sizes across multi-nested plaintext layers. 
    * Engineered a stateless persistence mechanism by utilizing a local point-in-time hidden file tracker (`.backup_last_chars.txt`), dynamically calculating mathematical delta values (`$((CURRENT_CHARS  - LAST_CHARS))`) during raw system runtime. 

### Day 7: Syntax Debugging, Decoupled Payload Hardening & Discord Monitoring
* **The Challenge:** During initial script execution, the shell enivroment threw critical faults (`Permission denied (os error 13)` and `unexpected EOF while looking for matching "'"`), halting the JSON text data processing required for external communication pipelines.
* **Low-Level Code Debugging & Refactoring:**
    * Identified character drops ans escape-sequence parsing anomalies caused by SSH terminal nesting limits inside standard environment variables. 
    * Solved string evaluation failures by decoupling the payload generation entirely from programm execution memory. Restructured the script to pipe text streams directly into an isolated temporary state file at `/tmp/discord.json`. 
    * Leveraged `curl -d @/tmp/discord.json` to safely stream structured JSON text objects, guaranteein absolute parsing immunity against character dropouts. 
* **The Resolution:** Successfully automated system management operations. Configured an absolute background cron schedule (`crontab -e `) pointing to `0 3 * * *`for autonomous nightly compression routines (`.tar.gz`). Verified end-to-end telemetry compliance with a manual execution test, resulting in plaintext server metrics delicered instantly to an external Discord monitoring channel.

### Day 8: Local Storage Archiving & Linux Directory Permission Debugging
* **The Challenge:** Wanted the server to automatically compress the received files into a timestamp archive (`.tar.gz`) to preserve disk space. During execution tests, the automation halted with a critical "Permission denied" error.
* **The Resolution:**
    * Integrated a automated `tar -czf` backup pipeline into the server script, saving the compressed packages under `/home/max/archives/`.
   * Learned that Linux enforces strict directory ownership. Since the uploaded files belonged to the unprivileged `backupuser`, the admin user `max` was initially blocked from accessing them until folder permissions were corrected.

### Day 9: Python Virtual Environments & Client-Side Workspace Isolation (venv)
* **The Challenge:** Transitioned to the Windows host workstation to build the file-transfer automation. During the initial setup, required python libraries were accidentally installed into the global operating system layer, risking dependency pollution.
* **The Resolution:**
   * Cleared the global Windows environment by uninstalling the external packages via the Command Prompt using `pip uninstall`.
   * Implemented a clean workspace environment by initializing a local Python Virtual Environment (`python -m venv .venv`) directly on the desktop. All project dependencies are now safely isolated within this sandboxed workspace.

### Day 10: Recursive Ingestion & Whitespace Path Parsing for Obsidian Vaults
* **The Challenge:** The automation script had to synchronize a local Obsidian Knowledge Base (`FIAE VAULT`). This caused standard file-copying scripts to fail due to unescaped whitespaces in the directory name and structural blindness to nested subfolders.
* **The Resolution:**
   * Upgraded the Python script architecture from flat file matching to a recursive directory traversal tree using the `os.walk()` engine.
   * Handled filesystem compatibility by transforming Windows backslashes (`\`) into POSIX forward slashes (`/`) and encapsulated the directory string as a raw path (`r"..."`), ensuring folder names with spaces are processed correctly.

   ### Day 11: Dynamic SFTP Directory Construction & Binary Asset Filtering
* **The Challenge:** Uploading nested files via SFTP failed because the subfolders did not exist yet on the Linux destination. Additionally, binary assets (like screenshots inside the Obsidian vault) flooded the server's text counters, corrupting the character statistics with unreadable code symbols.
* **The Resolution:**
   * Programmed a directory validation loop in `send_notes.py` using `sftp.stat()` and error handling. The script now dynamically creates missing subfolders via `sftp.mkdir()` before uploading the actual files.
   * Patched the server-side Bash script with a logical OR-expression filter (`\( -name "*.md" -o -name "*.txt" \)`). The pipeline now backs up all images normally, but ignores them during character metrics to keep the text statistics accurate.

### Day 12: Cryptographic Identity Recovery after Password Modification
* **The Challenge:** After updating the server-side administrator password, the automated script failed with an "Authentication failed" error because the security keys on the host machine were out of sync.
* **The Resolution:**
   * Generated a fresh, high-security Ed25519 cryptographic key pair within the Windows PowerShell directory using `ssh-keygen -t ed25519`.
   * Transferred the new public identity asset (`id_ed25519.pub`) to the server's `authorized_keys` file and secured the hidden directories using proper ownership (`chown`) and strict file permissions (`chmod 600`).   

### Day 13: Protocol Bypassing & Administrative Privilege Escalation (visudo)
* **The Challenge:** The pipeline remained blocked due to a double-security lock: the server's shell restrictions conflicted with standard connection rules, and the Linux kernel paused the background automation to demand a manual administrative password.
* **The Resolution:**
   * Refactored the network logic in `send_notes.py` to initiate a native, direct SFTP client pipeline, bypassing the server's interactive shell restrictions completely.
   * Solved background runtime blockages by accessing the system's core privilege manager via `sudo visudo` and appending a precise `NOPASSWD` rule for this specific script path, allowing automated execution without manual prompts.

### Day 14: Decoupled JSON Payloads, Real-Time Monitoring & Environment Sanitization
* **The Challenge:** The script crashed with an `unexpected EOF` error because the expanded Discord text message became too complex for the standard console variable memory. Also, private configuration data (IP addresses and paths) had to be hidden before publishing the code.
* **The Resolution:**
   * Fixed string parsing anomalies by decoupling the notification layout from execution memory. The script now writes metrics into a temporary `/tmp/discord.json` file and streams it via `curl`, delivering a clean, emoji-free status message directly to Discord.
   * Sanitized the open-source files using the `python-dotenv` framework. Moved all sensitive operational parameters into a local hidden `.env` file blocked via `.gitignore`, while providing a public configuration template called `.env.example`.

## Planned Services (Target Architecture)

- [ ] **Docker Engine & Compose:** Core containerization runtime for app isolation.
- [ ] **Pi-hole:** Network-wide ad-blocking and local DNS resolution.
- [ ] **Nginx Reverse Proxy:** Secure traffic routing to internal container ports.
- [ ] **Flask / Node.js Dev Environments:** Hosting local sandboxed web APIs.


