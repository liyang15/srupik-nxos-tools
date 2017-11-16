#!/usr/bin/env python3
"""
NXAPI script inspired by this question:
  https://supportforums.cisco.com/t5/unified-computing-system/nexus-interface-bulk-range-selection/m-p/3217057
"""

import json
import argparse
import requests

nx_hosts = ["Insert IP here"]
nx_username = "Insert username here"
nx_password = "Insert password here"
nx_port = "443"

request_header = {"content-type": "application/{0}"}

no_sfp_target_state = ["sfpAbsent", "xcvrAbsent"]
notconnect_target_state = ["notconnect"]

int_command = "int {0} ; switchport ; switchport access vlan {1} ; switchport mode access ; shutdown ; "
interfaces = []

parser = argparse.ArgumentParser(description="Isolates Nexus 9000 interfaces that do not have an SFP plugged in or are not connected into a user-defined, non-routed VLAN.")
parser.add_argument("--vlan", "-v", metavar="XXX", action="store", default="999", help="The non-routable VLAN that all eligible interfaces will be assigned to. This value defaults to 999.")
parser.add_argument("--sfp", "-s", action="store_true", help="With this option enabled, only interfaces that are lacking an SFP will be added to a non-routable VLAN")
parser.add_argument("--notconnect", "-n", action="store_true", help="With this option enabled, only interfaces that are in a notconnect state will be added to a non-routable VLAN")
args = parser.parse_args()

non_routed_vlan = args.vlan

def nxapi_request(host, payload, content_type="json"):
    url = "https://{0}:{1}/ins".format(host, nx_port)
    try:
        response = requests.post(url,
                                 data=json.dumps(payload),
                                 headers={"content-type": "application/{0}".format(content_type)},
                                 auth=(nx_username, nx_password),
                                 timeout=60,
                                 verify=False)
    except requests.exceptions.ConnectTimeout as exc_info:
        print(exc_info)
        return None
    except requests.exceptions.HTTPError as exc_info:
        if exc_info.response.status_code == 401:
            print('Authentication Failed. Please provide valid username/password.')
        else:
            print('HTTP Status Code {code}. Reason: {reason}'.format(
                code=exc_info.response.status_code,
                reason=exc_info.response.reason))
        return None
    return response.json()


def apply_config_commands(host, config_commands):
    payload = {"ins_api": {"version": "1.0",
                           "type": "cli_conf",
                           "chunk": "0",
                           "sid": "1",
                           "input": config_commands,
                           "output_format": "json"}}

    response = nxapi_request(host, payload)

def create_config_commands(host):
    payload = [
        {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "show int status", "version": 1.2}, "id": 1},
    ]
    config_commands = "conf t ; "

    response = nxapi_request(host, payload, "json-rpc")
    if response is None:
        return None

    for interface in response["result"]["body"]["TABLE_interface"]["ROW_interface"]:
        int_state = interface["state"]
        int_name = interface["interface"]
        if not args.notconnect and not args.sfp:
            if ((int_state in no_sfp_target_state) or (int_state in notconnect_target_state)):
                config_commands += int_command.format(interface["interface"], non_routed_vlan)
                interfaces.append(int_name)
        elif args.notconnect and int_state in notconnect_target_state:
            config_commands += int_command.format(interface["interface"], non_routed_vlan)
            interface.append(int_name)
        elif args.sfp and int_state in no_sfp_target_state:
            config_commands += int_command.format(interface["interface"], non_routed_vlan)
            interface.append(int_name)

    if config_commands.endswith("; "):
        config_commands = config_commands[:-2]

    if len(config_commands) > 0:
        return config_commands
    else:
        return None

def main():
    for host in nx_hosts:
        print("Trying {0}".format(host))

        config_commands = create_config_commands(host)
        if config_commands is not None:
            apply_config_commands(host, config_commands)
            print_str = ""
            print("Changes applied to the following interfaces:")
            for interface in interfaces:
                print_str += "{}, ".format(interface)
            print(print_str)




if __name__ == "__main__":
    main()
