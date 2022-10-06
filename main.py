# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import inspect
import functools
import platform
import logging
import socket
from datetime import datetime, timezone
import math
from azure.iot.device.aio import IoTHubDeviceClient

logging.basicConfig(level=logging.ERROR)

# allows colored characters in terminal using ANSI escape sequences
os.system("")

COLOR = {
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "YELLOW": "\033[93m",
    "ENDC": "\033[0m",
}

def print_ok():
    print(COLOR["GREEN"], "OK", COLOR["ENDC"], end = "")
    
def print_fail():
    print(COLOR["RED"], "Failed", COLOR["ENDC"], end = "")

def print_warning():
    print(COLOR["YELLOW"], "Warning", COLOR["ENDC"], end = "")

HOST_NAME = "HostName"
SHARED_ACCESS_KEY_NAME = "SharedAccessKeyName"
SHARED_ACCESS_KEY = "SharedAccessKey"
SHARED_ACCESS_SIGNATURE = "SharedAccessSignature"
DEVICE_ID = "DeviceId"
MODULE_ID = "ModuleId"
GATEWAY_HOST_NAME = "GatewayHostName"
X509 = "x509"

valid_keys = [
    HOST_NAME,
    SHARED_ACCESS_KEY_NAME,
    SHARED_ACCESS_KEY,
    SHARED_ACCESS_SIGNATURE,
    DEVICE_ID,
    MODULE_ID,
    GATEWAY_HOST_NAME,
    X509,
]

def main():
    conn_str = input("Input connection string: ")
    print()
    print("Connectivity Checks")
    print("-------------------")
    platform_check()
    validate_conn_str_format(conn_str)
    internet_check()
    time_check()

def platform_check():
    if platform.system() == "Windows":
        print_ok()
        print("- Device operating system is supported (" + platform.system() + ")")
    elif platform.system() == "Linux":
        print_ok()
        print("- Device operating system is supported (" + platform.system() + ")")
    elif platform.system() == "Darwin":
        # macOS users may not recognize Darwin, so we display their OS name independently
        print_ok()
        print("- Device operating system is supported (macOS)")
    else:
        # device may work, even if not explicitly supported
        print_warning()
        print("- Device operating system may not be supported (" + platform.system() + ")")

def validate_conn_str_format(conn_str):
    # this function only validates format, so we're only concerned that all the key components of a connection string are present
    try:
        split_string = conn_str.split(";")
    except (AttributeError, TypeError):
        print_fail()
        print("- Connection string must be of type str")
    try:
        d = dict(arg.split("=", 1) for arg in split_string)
    except ValueError:
        print_fail()
        print("- Connection string cannot be parsed, check for missing arg name or bad syntax")
    if len(split_string) != len(d):
        print_fail()
        print("- Connection string cannot be parsed, check for duplicate args or bad syntax")
    if not all(key in valid_keys for key in d.keys()):
        print_fail()
        print("- Invalid key present, check connection string components match with valid_keys")
    else:
        print_ok()
        print("- Device connection string is properly formatted")
        validate_conn_str_args(d)

def validate_conn_str_args(d):
    # Raise ValueError if incorrect combination of keys in dict d
    host_name = d.get(HOST_NAME)
    shared_access_key_name = d.get(SHARED_ACCESS_KEY_NAME)
    shared_access_key = d.get(SHARED_ACCESS_KEY)
    device_id = d.get(DEVICE_ID)
    x509 = d.get(X509)

    if shared_access_key and x509:
        print_fail()
        print("- Connection string is invalid due to mixed authentication scheme")

    if host_name and device_id and (shared_access_key or x509):
        print_ok()
        print("- Device connection string components are valid")
        pass
    elif host_name and shared_access_key and shared_access_key_name:
        print_ok()
        print("- Device connection string components are valid")
        pass
    else:
        print_fail()
        print("- Connection string is incomplete")

def internet_check():
    try: 
        sock = socket.create_connection(("1.1.1.1", 80))
        if sock is not None:
            print_ok()
            print("- Device can DNS resolve and reach an outside URL on HTTP port")
            return True
    except ConnectionError:
        print_fail()
        print("- Connection error when attempting to connect with HTTP port")
        pass
    except OSError:
        print_fail()
        print("- Non-connection OS error when attempting to connect with HTTP port")
        pass
    else:
        print_fail()
        print("- Non-OS error when attempting to connect with HTTP port")
        pass
    finally:
        sock.close()
    return False

def time_check():
    try:
        sock = socket.create_connection(("time.nist.gov", 13))

        rawTime = sock.recv(1024)
        dayAndTime = rawTime.decode("utf-8")
        split_dayTime = dayAndTime.split()
        conc_dayTime = split_dayTime[1] + " " + split_dayTime[2]
        dt_dayTime = datetime.strptime(conc_dayTime, "%y-%m-%d %H:%M:%S")
        nist_dayTime = (dt_dayTime.timestamp())

        local = datetime.now(timezone.utc)
        local_dayTime = local.timestamp()

        if math.isclose(nist_dayTime, local_dayTime, abs_tol = 300000):
            print_ok()
            print("- System time is synced properly")
        else:
            print_fail()
            print("- System time is not synced properly")
    except:
        print_fail()
        print("- Could not properly test system time sync")
    finally:
        sock.close()



if __name__ == "__main__":
    main()