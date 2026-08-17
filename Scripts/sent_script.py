import os
import paramiko
from dotenv import load_dotenv

# Load sensitive environment variables from the local .env file
load_dotenv()

# --- CONFIGURATION FROM ENVIRONMENT VARIABLES ---
SOURCE_DIR = os.getenv("SOURCE_DIR")
SERVER_IP = os.getenv("SERVER_IP")
ADMIN_USER = os.getenv("ADMIN_USER")
BACKUP_USER = os.getenv("BACKUP_USER")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
# =====================================================================



# ===============================================================0

def main():
    print(f"[i] Starting automated note transfer to Home-Lab-Server...")
    print(f"[i] Source directory: {SOURCE_DIR}")
    print(f"-" * 69)
    
    # Verify local source directory exists
    if not os.path.exists(SOURCE_DIR):
        print(f"[ERROR] directory was not found")
        return
    
    try: 
        # Connect to the isolated backup account via SFTP
        print(f"[*] Transferring files to {BACKUP_USER}")
        
        # Load private crpyto SSH key from Windows
        key = paramiko.Ed25519Key.from_private_key_file(PRIVATE_KEY_PATH)
        
        # Setup direct SFTP connection to bypass ForceCommand internal-sftp
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(SERVER_IP, username=BACKUP_USER, pkey=key, disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
        sftp = ssh_client.open_sftp()

        
        #Upload : os.walk loops through ALL subdirectories, folders, and files
        for root, dirs, files in os.walk(SOURCE_DIR):
            for filename in files:
                
                local_file_path= os.path.join(root, filename)
                
                relative_path = os.path.relpath(local_file_path, SOURCE_DIR)
                
                # Format the remote path for Linux 
                remote_file_path = f"/home/{BACKUP_USER}/{relative_path}".replace('\\','/')
                remote_dir = os.path.dirname(remote_file_path)
                
                try: 
                    sftp.stat(remote_dir)
                except IOError:
                    
                    parts = remote_dir.split('/')
                    current_path = ""
                    for part in parts:
                        if part:
                            current_path += "/" + part
                            try: 
                                sftp.stat(current_path)
                            except IOError:
                                sftp.mkdir(current_path)
                
                sftp.put(local_file_path, remote_file_path)
                print(f" Uploades: {relative_path}")
                
        sftp.close()
        ssh_client.close()

        print("-" * 69)
        print("[*] Transfer complete. Triggering server-side processing...")

        ssh_admin = paramiko.SSHClient()
        ssh_admin.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_admin.connect(SERVER_IP, username=ADMIN_USER, pkey=key)

        stdin, stdout, stderr = ssh_admin.exec_command(f"sudo bash /home/{ADMIN_USER}/backup_process.sh")
        exit_status = stdout.channel.recv_exit_status()

        if exit_status == 0: 
            print("-" * 69)
            print("[SUCCESS]")
        else:
            print("-" * 69)
            print("[ERROR] Server-side processing failed")
        
    except Exception as e:
        print("-" * 69)
        print(f"[Critical ERROR] Pipeline failed: {e}")
        
        
if __name__ == "__main__":
    main()