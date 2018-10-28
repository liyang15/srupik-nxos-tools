#!/usr/bin/env python3

"""
On-board Nexus variant of the below question, inspired by below question:
  https://supportforums.cisco.com/t5/unified-computing-system/nexus-interface-bulk-range-selection/m-p/3217057
Ideas borrowed from https://github.com/ChristopherJHart/srupik-nxos-tools
"""

from cli import *
import cisco
import argparse
import json

parser = argparse.ArgumentParser(description="Isolates Nexus 9000 interfaces that do not have an SFP plugged in or are not connected into a user-defined, non-routed VLAN.")
parser.add_argument("--vlan", "-v", metavar="XXX", action="store", default="999", help="The non-routable VLAN that all eligible interfaces will be assigned to. This value defaults to 999.")
parser.add_argument("--no-sfp-only", "-s", action="store_true", help="With this option enabled, only interfaces that are lacking an SFP will be added to a non-routable VLAN")
parser.add_argument("--notconnect-only", "-n", action="store_true", help="With this option enabled, only interfaces that are in a notconnect state will be added to a non-routable VLAN")
args = parser.parse_args()

non_routed_vlan = args.vlan

no_sfp_target_state = ["sfpAbsent", "xcvrAbsent"]
notconnect_target_state = ["notconnect"]

int_command = "int {0} ; switchport ; switchport access vlan {1} ; switchport mode access ; shutdown ; "
interfaces = []

''' Ctrl-C Signal Handler '''
def sigIntHandler(signal, frame):
    print('Exiting Script...')
    sys.exit(0)

def create_config_commands():
    config_commands = "conf t ; "
    output = json.loads(cli("show interface status | json"))
    for interface in output["TABLE_interface"]["ROW_interface"]:
        int_state = interface["state"]
        int_name = interface["interface"]
        if not args.notconnect_only and not args.no_sfp_only:
            if ((int_state in no_sfp_target_state) or (int_state in notconnect_target_state)):
                config_commands += int_command.format(interface["interface"], non_routed_vlan)
                interfaces.append(int_name)
        elif args.notconnect_only and int_state in notconnect_target_state:
            config_commands += int_command.format(interface["interface"], non_routed_vlan)
            interface.append(int_name)
        elif args.no_sfp_only and int_state in no_sfp_target_state:
            config_commands += int_command.format(interface["interface"], non_routed_vlan)
            interface.append(int_name)
    if config_commands.endswith("; "):
        config_commands = config_commands[:-2]
    if len(config_commands) > 0:    
        return config_commands
    else:
        return None

def apply_config_commands(config_commands):
    cli(config_commands)

def main():
    config_commands = create_config_commands()
    if config_commands:
        apply_config_commands(config_commands)
        print_str = ""
        print("Changes applied to the following interfaces:")
        for interface in interfaces:
            print_str += "{}, ".format(interface)
        print(print_str)

if __name__ == "__main__":
    main()