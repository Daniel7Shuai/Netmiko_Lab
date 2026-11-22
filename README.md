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
