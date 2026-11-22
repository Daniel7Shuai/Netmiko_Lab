from netmiko import ConnectHandler
import getpass
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

username = input("Enter your username: ")
password = getpass.getpass("Enter your password: ") 
enable_password = getpass.getpass("Enter your enable password: ")

hosts = input("Switch IPs (comma-separated): ").split(",")
HOSTS = [h.strip() for h in hosts if h.strip()]

config_commands = [
    "vlan 10",
    "name IT_Department",
    "vlan 20",
    "name HR_Department",
]

for host in HOSTS:
    switch = {
        "device_type": "cisco_ios",
        "host": host,
        "username": username,
        "password": password,
        "secret": enable_password,  
    }

    try: 
        with ConnectHandler(**switch) as net_connect:
            print(f"Connected to {host}")
            net_connect.enable()  
            print("Adding VLANs...")
            output = net_connect.send_config_set(config_commands)
            print(output)
            net_connect.save_config()
            print(f"VLANs added and config saved on {host}\n")
            print(net_connect.send_command("show vlan brief"))
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        print(f"Failed to connect to {host}: {e}")
