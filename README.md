# srupik-nxos-tools

The purpose of these scripts is to locate interfaces on a Cisco Nexus switch that are in a down/down state and place them in a non-routed VLAN. Two variants of scripts are contained in this repository that accomplish this goal. One utilizes NX-API and is executed on a user's local machine, while the other is executed through the Cisco Nexus NX-OS CLI itself.

## NX-API

1. Ensure that NX-API is enabled on your Cisco Nexus device via the `feature nxapi` global configuration command.

```
N9K# show run | i nxapi
feature nxapi
```

2. Verify the port that the NX-API server is listening on with  `show nxapi`.

```
N9K# show nxapi
nxapi enabled
HTTPS Listen on port 443 <<<
Certificate Information:
    Issuer:   /C=US/ST=CA/L=San Jose/O=Cisco Systems Inc./OU=dcnxos/CN=nxos    
    Expires:  Oct 23 15:35:41 2018 GMT   
```

3. Determine the management IP address of the Cisco Nexus switch. Typically, this will be the IP address configured on the out-of-band mgmt0 interface, but this will vary depending on your network environment and configuration. For this example, we are using the IP address configured on the out-of-band mgmt0 interface.

```
N9K# show run interface mgmt0

!Command: show running-config interface mgmt0
!Running configuration last done at: Tue Oct 23 22:44:30 2018
!Time: Sun Oct 28 16:58:36 2018

version 9.2(1) Bios:version 07.64 

interface mgmt0
  vrf member management
  ip address 192.168.1.10/24
```

4. On your local machine, clone the contents of this repository to a desired location.

```
git clone https://github.com/sebrupik/srupik-nxos-tools.git
```

5. Move into the newly-created directory.

```
cd srupik-nxos-tools/
```

6. Execute the NX-API variant of the script.

### Required Positional Parameters

* IP address of the device
* NX-API server port
* Username used to log into the device
* Password used to log into the device

### Optional Parameters

* `--vlan` - By default, all interfaces in a down/down state will be moved to VLAN999. Pass an integer into this parameter to change the VLAN where down/down interfaces are placed.
* `--no-sfp-only` - When this parameter is invoked, the script will only modify interfaces that do not have a transceiver inserted. Interfaces that are in a "notconnect" status according to the output of `show interface status` will not be modified. By default, this is False.
* `--notconnect-only` - When this parameter is invoked, the scrpt will only modify interfaces that are in a "notconnect" status according to the output of `show interface status`. Interfaces that are lacking a transceiver will not be modified. By default, this is False.

### Examples

* Moves all down/down interfaces into VLAN999:

```
python3 nxapi/nxapi_unused_interface_vlan.py 192.168.1.10 443 admin example_password
```

* Moves all down/down interfaces into VLAN250, which is configured to be a non-routed VLAN:

```
python3 nxapi/nxapi_unused_interface_vlan.py 192.168.1.10 443 admin example_password --vlan 250
```

* Moves all interfaces that do not have a transceiver inserted into VLAN999:

```
python3 nxapi/nxapi_unused_interface_vlan.py 192.168.1.10 443 admin example_password --no-sfp-only
```

* Moves all interfaces that are down/down, but have a transceiver inserted into VLAN999:

```
python3 nxapi/nxapi_unused_interface_vlan.py 192.168.1.10 443 admin example_password --notconnect-only
```

* Moves all interfaces that do not have a transceiver inserted into VLAN250, which is configured to be a non-routed VLAN:

```
python3 nxapi/nxapi_unused_interface_vlan.py 192.168.1.10 443 admin example_password --vlan 250 --no-sfp-only
```

* Moves all interfaces that are down/down, but have a transceiver inserted into VLAN250, which is configured to be a non-routed VLAN:

```
python3 nxapi/nxapi_unused_interface_vlan.py 192.168.1.10 443 admin example_password --vlan 250 --notconnect-only
```

## NX-OS

1. On your local machine, clone the contents of this repository to a desired location.

```
git clone https://github.com/sebrupik/srupik-nxos-tools.git
```

2. Move into the newly-created directory.

```
cd srupik-nxos-tools/
```

3. Move the script at nxos/nxos_unused_interface_vlan.py into the bootflash:scripts/ directory of your NX-OS device.

```
N9K# dir bootflash:scripts
       3080    Oct 28 17:55:26 2018  nxos_unused_interface_vlan.py

Usage for bootflash://sup-local
 4507103232 bytes used
49079222272 bytes free
53586325504 bytes total
```

4. Execute the NX-OS variant of the script.

### Required Positional Parameters

This variant of the script does not have any required positional parameters.

### Optional Parameters

* `--vlan` - By default, all interfaces in a down/down state will be moved to VLAN999. Pass an integer into this parameter to change the VLAN where down/down interfaces are placed.
* `--no-sfp-only` - When this parameter is invoked, the script will only modify interfaces that do not have a transceiver inserted. Interfaces that are in a "notconnect" status according to the output of `show interface status` will not be modified. By default, this is False.
* `--notconnect-only` - When this parameter is invoked, the scrpt will only modify interfaces that are in a "notconnect" status according to the output of `show interface status`. Interfaces that are lacking a transceiver will not be modified. By default, this is False.

### Examples

* Moves all down/down interfaces into VLAN999:

```
source nxos_unused_interface_vlan.py
```

* Moves all down/down interfaces into VLAN250, which is configured to be a non-routed VLAN:

```
source nxos_unused_interface_vlan.py --vlan 250
```

* Moves all interfaces that do not have a transceiver inserted into VLAN999:

```
source nxos_unused_interface_vlan.py --no-sfp-only
```

* Moves all interfaces that are down/down, but have a transceiver inserted into VLAN999:

```
source nxos_unused_interface_vlan.py --notconnect-only
```

* Moves all interfaces that do not have a transceiver inserted into VLAN250, which is configured to be a non-routed VLAN:

```
source nxos_unused_interface_vlan.py --vlan 250 --no-sfp-only
```

* Moves all interfaces that are down/down, but have a transceiver inserted into VLAN250, which is configured to be a non-routed VLAN:

```
source nxos_unused_interface_vlan.py --vlan 250 --notconnect-only
```