```
    _   __     __            _ __            __          __
   / | / /__  / /_____ ___  (_) /______     / /   ____ _/ /_
  /  |/ / _ \/ __/ __ `__ \/ / //_/ __ \   / /   / __ `/ __ \
 / /|  /  __/ /_/ / / / / / / ,< / /_/ /  / /___/ /_/ / /_/ /
/_/ |_/\___/\__/_/ /_/ /_/_/_/|_|\____/  /_____/\__,_/_.___/
```

# Netmiko Lab: Auto VLANs

A Python script that connects to one or more Cisco IOS switches over SSH and
creates the same set of VLANs on each of them, then saves the configuration.

| VLAN | Name           |
|------|----------------|
| 10   | IT_Department  |
| 20   | HR_Department  |
| 30   | Engineering    |

## What it does

- Prompts for a username, a login password and an enable password.
  Passwords are read with `getpass`, so they are not shown on screen and are
  never stored in the script or on disk.
- Accepts several switch IPs at once (comma-separated) and configures them one
  after another.
- Enters enable mode, pushes the VLAN commands in global config mode and prints
  the switch's output.
- Saves the running config to startup config (`write memory`) on each switch.
- If a switch can't be reached or rejects the login, it prints the error and
  carries on with the next switch.

## What it cannot do (limitations)

- **Cisco IOS / IOS XE only.** It uses Netmiko's `cisco_ios` driver. NX-OS,
  Juniper, Aruba and other vendors are not supported without changes.
- **Switches only.** Routers (for example the Cisco DevNet always-on Catalyst
  8000v sandbox) have no VLAN database and will reject `vlan 10` with
  `% Invalid input`.
- **The VLAN list is hardcoded.** To change VLAN IDs or names, edit
  `config_commands` in `Auto_vlans.py`.
- **It doesn't check whether the commands worked.** It prints
  "VLANs added and config saved" even if the switch rejected a command. Read
  the printed output to confirm.
- **Same credentials for every switch.** One username and password set is used
  for all hosts.
- **Only creates VLANs.** It does not assign VLANs to ports, configure trunks,
  or delete existing VLANs.
- **Some errors stop the whole run.** Connection timeouts and failed logins are
  handled, but other errors (such as a wrong enable password or a slow device
  timing out on a command) end the script, and any remaining switches are
  skipped.
- **SSH only.** Telnet and serial console connections are not supported.
- **Interactive only.** It must be run from a terminal where you can type the
  prompts; it can't run unattended or from a scheduler as-is.

## Prerequisites

**On your computer**

- Python 3.9 or newer (tested with Python 3.14)
- `pip` and the `venv` module (on Kali/Debian: `sudo apt install python3-venv python3-pip`)
- Network reachability to the switches on TCP port 22

**On each switch**

- SSH enabled (`ip ssh version 2`, a domain name and RSA keys generated)
- A local user account, or AAA, that can log in over SSH
  (`username admin privilege 15 secret ...`)
- `line vty 0 4` set to `transport input ssh` and `login local`
- An enable secret configured
- A management IP address the computer can reach

## Installation

```bash
git clone https://github.com/<your-username>/Netmiko_Lab.git
cd Netmiko_Lab
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Kali, installing with `pip` outside a virtual environment is blocked
("externally-managed-environment"), so use the venv as shown above.

## Usage

```bash
source .venv/bin/activate
python Auto_vlans.py
```

Example session:

```
Enter your username: admin
Enter your password:
Enter your enable password:
Switch IPs (comma-separated): 192.168.1.10, 192.168.1.11
Connected to 192.168.1.10
Adding VLANs...
...
VLANs added and config saved on 192.168.1.10
```

Check the result on a switch with `show vlan brief`.

## Troubleshooting

| Message | Likely cause |
|---------|--------------|
| `TCP connection to device failed` | Wrong IP, SSH not enabled, or a firewall blocking port 22 |
| `Authentication to device failed` | Wrong username or password, or `login local` missing on the VTY lines |
| `% Invalid input detected` in the output | The device isn't a switch, or the IOS version doesn't support the command |
| Script stops with a `ValueError` or `ReadTimeout` | Wrong enable password, or the device responded too slowly |

## Safety

This script changes and **saves** device configuration. Try it on a lab or
sandbox switch (for example an IOSvL2 switch in Cisco Modeling Labs, GNS3 or
EVE-NG) before using it on production equipment. Cisco Packet Tracer won't
work, because a script on your computer can't SSH into its simulated devices.

## Project files

```
Netmiko_Lab/
├── Auto_vlans.py      # the script
├── requirements.txt   # Python dependencies
├── .gitignore         # keeps .venv out of git
└── README.md
```

## Setup & Usage (Cisco DevNet Sandbox)

### Prerequisites
- Python 3.8+
- Netmiko: `pip install netmiko`
- A free [Cisco DevNet](https://developer.cisco.com/) account
- A VPN client that supports AnyConnect-style VPNs (Cisco Secure Client or OpenConnect)

### 1. Reserve the sandbox
1. Log in to the DevNet Sandbox catalog and reserve **Cisco Modeling Labs (CML)**.
2. Wait for the reservation to become active, then open the **Quick Access** tab
   for the VPN address, VPN credentials and CML login.

<img width="1278" height="891" alt="image" src="https://github.com/user-attachments/assets/16f7bc36-b436-49ad-a0fe-ef9dd4d67f62" />

### 2. Connect to the VPN
Connect using the VPN address (including the port) and credentials from the
reservation. Confirm the lab is reachable:

```bash
ping 10.10.20.173
```

### 3. Open the lab
Log in to the CML web UI and open `default-lab`. It includes two IOL-L2 XE
switches:

| Device | IP address   |
|--------|--------------|
| SW1    | 10.10.20.173 |
| SW2    | 10.10.20.174 |

Lab login: `cisco` / `cisco`.

### 4. Enable SSH on the switches
SSH is disabled by default. Open each switch console in CML and run:

```
conf t
 ip domain name lab.local
 crypto key generate rsa modulus 2048
 ip ssh version 2
 line vty 0 4
  transport input ssh telnet
  login local
end
```

### 5. Run the script
```bash
python vlan_config.py
```
Enter the username, password, enable password, and the switch IPs
(comma-separated), for example `10.10.20.173,10.10.20.174`.

<img width="527" height="76" alt="image" src="https://github.com/user-attachments/assets/bad9107d-2328-4a3b-aa35-5bf249805fe7" />

<img width="978" height="482" alt="image" src="https://github.com/user-attachments/assets/df738330-1c23-482e-b58d-73b16f7c872d" />

### 6. Verify
On each switch console:

```
show vlan brief
```

<img width="603" height="139" alt="image" src="https://github.com/user-attachments/assets/ede77a42-cda6-41c0-9bf3-a1ee9caf992d" />

The VLAN names should now match the script (for example, `IT_Department`
on VLAN 10).

### 7. Clean up
Disconnect the VPN and end the reservation from **Manage reservation**.
Switch configuration is erased when the reservation ends.

### Troubleshooting
| Symptom | Likely cause / fix |
|---|---|
| `TCP connection to device failed` | VPN not connected, or SSH not enabled on the switch |
| Authentication failure | Check username/password (`cisco` / `cisco`) |
| SSH key exchange errors | Use `"device_type": "cisco_ios_telnet"` in the script |
