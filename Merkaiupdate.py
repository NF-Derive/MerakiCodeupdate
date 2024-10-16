import requests
import sys

def get_api_key():
    return input("Enter your Meraki API key: ")

def read_devices_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def get_organization_id(api_key):
    url = "https://api.meraki.com/api/v1/organizations"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        organizations = response.json()
        if organizations:
            return organizations[0]['id']
    print("Failed to retrieve organization ID.")
    sys.exit(1)

def get_network_devices(api_key, org_id):
    url = f"https://api.meraki.com/api/v1/organizations/{org_id}/devices"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    print("Failed to retrieve network devices.")
    sys.exit(1)

def get_available_firmware_versions(api_key, serial):
    url = f"https://api.meraki.com/api/v1/devices/{serial}/available_firmware_upgrades"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    print(f"Failed to retrieve available firmware versions for device {serial}.")
    return None

def update_device_firmware(api_key, serial, version):
    url = f"https://api.meraki.com/api/v1/devices/{serial}/upgrade"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "product": "appliance",
        "version": version
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 202:
        print(f"Successfully initiated firmware update for device {serial} to version {version}")
    else:
        print(f"Failed to update firmware for device {serial}. Status code: {response.status_code}")

def main():
    api_key = get_api_key()
    devices = read_devices_from_file("devices.txt")
    org_id = get_organization_id(api_key)
    network_devices = get_network_devices(api_key, org_id)

    for device_name in devices:
        matching_device = next((device for device in network_devices if device['name'] == device_name), None)
        if matching_device:
            serial = matching_device['serial']
            print(f"\nProcessing device: {device_name} (Serial: {serial})")
            
            available_versions = get_available_firmware_versions(api_key, serial)
            if available_versions:
                print("Available firmware versions:")
                for idx, version in enumerate(available_versions, 1):
                    print(f"{idx}. {version['version']}")
                
                choice = int(input("Enter the number of the version you want to update to: ")) - 1
                if 0 <= choice < len(available_versions):
                    selected_version = available_versions[choice]['version']
                    update_device_firmware(api_key, serial, selected_version)
                else:
                    print("Invalid selection. Skipping this device.")
            else:
                print("No available firmware versions found. Skipping this device.")
        else:
            print(f"Device not found: {device_name}")

if __name__ == "__main__":
    main()