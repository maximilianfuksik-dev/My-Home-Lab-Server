import os 
import paramiko

# ============================================================================================
# Python to Linux Notes Script
#=============================================================================================

# CONFIG

SOURCE_DIR = os.path.expanduser("C:\Users\Student\Desktop\Obsidian\FIAE VAULT")

# SERVER DETAILS
SERVER_IP = "192.168.178.40"
ADMIN_USER = "max"
BACKUP_USER = "backupuser"
PRIVATE_KEY_PATH = os.path.expanduser(r"~\.ssh\id_ed25519")

# ===============================================================0

def main():
    print(f"[i] Starting automated note transfer to Home-Lab-Server...")
    print(f"[i] Source directory: {SOURCE_DIR}")
    print(f"-" * 69)
    
    # Verify local source directory exists
    if not os.path.exists{SOURCE_DIR}:
        print(f"[ERROR] directory was not found")
        return
    
    try: 
        # Connect to the isolated backup account via SFTP
        print(f"[*] Transferring files to {BACKUP_USER}")
        
        # Load private crpyto SSH key from Windows
        key = paramiko.Ed25519Key.from_private_key_file(PRIVATE_KEY_PATH)
        
        # Setup SSH Transport Channel
        ssh_transport = paramiko.Transport((SERVER_IP, 22))
        ssh_transport.connect(username=BACKUP_USER, pkey=key)
        sftp = paramiko.SFTPClient.from_transport(ssh_transport)
        
        #Upload all files from the local directory loop 
        for filename in os.listdir(SOURCE_DIR):
            local_file = os.path.join(SOURCE_DIR, filename)
        
    except:
        pass