#!/usr/bin/env python3
"""
NXAPI script inspired by this question:
  https://supportforums.cisco.com/t5/unified-computing-system/nexus-interface-bulk-range-selection/m-p/3217057
"""

import json
import requests

nx_hosts = ["10.209.31.67", "10.209.31.100"]
nx_username = "admin"
nx_password = "password"
nx_port = "8080"

headers_jsonrpc = {"content-type": "application/json-rpc"}
headers_json = {"content-type": "application/json"}

int_target_state = "sfpAbsent"

non_routed_vlan = 5
int_command = "int {0}; switchport access vlan {1}; switchport mode access; shutdown; "


def nxapi_call(host, payload, headers):
    url = "http://{0}:{1}/ins".format(host, nx_port)
    try:
        response = requests.post(url,
                                 data=json.dumps(payload),
                                 headers=headers,
                                 auth=(nx_username, nx_password),
                                 timeout=4)
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
    payload = {"ins_api": {"version": "1.2",
                           "type": "cli_conf",
                           "chunk": "0",
                           "sid": "1",
                           "input": config_commands,
                           "output_format": "json"}}

    response = nxapi_call(host, payload, headers_json)

    print(response)


def create_config_commands(host):
    payload = [
        {"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "show int status", "version": 1.2}, "id": 1},
    ]
    config_commands = ""

    response = nxapi_call(host, payload, headers_jsonrpc)
    if response is None:
        return None

    for interface in response["result"]["body"]["TABLE_interface"]["ROW_interface"]:
        if interface["state"] == int_target_state:
            config_commands += int_command.format(interface["interface"], non_routed_vlan)

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
        print(config_commands)
        if config_commands is not None:
            apply_config_commands(host, config_commands)


if __name__ == "__main__":
    main()
