import subprocess
import time
import os

TARGET_WIFI = "LK-GUEST"
PASSWORD = ""  # Lämna tomt för öppet nätverk
WIFI_INTERFACE = "Wi-Fi"  # Vanligt namn, ändra om din adapter heter annat

def run_command(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def disable_wifi():
    run_command(["netsh", "interface", "set", "interface", WIFI_INTERFACE, "admin=disable"])
    print("Wi-Fi inaktiverad")

def enable_wifi():
    run_command(["netsh", "interface", "set", "interface", WIFI_INTERFACE, "admin=enable"])
    print("Wi-Fi aktiverad")

def get_current_wifi():
    result = run_command(["netsh", "wlan", "show", "interfaces"])
    for line in result.stdout.splitlines():
        if "SSID" in line and "BSSID" not in line:
            return line.split(":")[1].strip()
    return None

def get_saved_networks():
    result = run_command(["netsh", "wlan", "show", "profiles"])
    networks = []
    for line in result.stdout.splitlines():
        if "All User Profile" in line:
            networks.append(line.split(":")[1].strip())
    return networks

def delete_other_networks(target):
    for network in get_saved_networks():
        if network != target:
            run_command(["netsh", "wlan", "delete", "profile", f"name={network}"])
            print(f"Raderade nätverket: {network}")

def create_open_profile(ssid):
    profile = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>open</authentication>
                <encryption>none</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
        </security>
    </MSM>
</WLANProfile>"""
    filename = f"{ssid}_open.xml"
    with open(filename, "w") as f:
        f.write(profile)
    run_command(["netsh", "wlan", "add", "profile", f"filename={filename}"])
    os.remove(filename)

def connect_to_wifi(ssid, password=""):
    enable_wifi()  # Säkerställ att Wi-Fi är på
    if password:
        run_command(["netsh", "wlan", "connect", f"name={ssid}"])
    else:
        create_open_profile(ssid)
        run_command(["netsh", "wlan", "connect", f"name={ssid}"])

def main():
    delete_other_networks(TARGET_WIFI)
    
    while True:
        current = get_current_wifi()
        if current != TARGET_WIFI:
            print(f"Byter från {current} till {TARGET_WIFI}...")
            connect_to_wifi(TARGET_WIFI, PASSWORD)
        else:
            print(f"Alltid ansluten till {TARGET_WIFI}")
        time.sleep(5)

if __name__ == "__main__":
    main()
