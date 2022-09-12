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
    "ENDC": "\033[0m",
}

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
        print(COLOR["GREEN"], "OK", COLOR["ENDC"] + "- Device operating system is supported (" + platform.system() + ")")
    elif platform.system() == "Linux":
        print(COLOR["GREEN"], "OK", COLOR["ENDC"] + "- Device operating system is supported (" + platform.system() + ")")
    elif platform.system() == "Darwin":
        # macOS users may not recognize Darwin, so we display their OS name independently
        print("OK - Device operating system is supported (macOS)")
        print(COLOR["GREEN"], "OK", COLOR["ENDC"] + "- Device operating system is supported (macOS)")
    else:
        print(COLOR["RED"], "Failed", COLOR["ENDC"] + "- Device operating system not supported (" + platform.system() + ")")

def validate_conn_str_format(conn_str):
    split_string = conn_str.split(";")
    # this function only validates format, so we're only concerned that all the key components of a connection string are present
    if "HostName=" in split_string[0] and "DeviceId=" in split_string[1] and "SharedAccessKey=" in split_string[2]:
        print(COLOR["GREEN"], "OK", COLOR["ENDC"] + "- Device connection string is valid")
    else:
        print(COLOR["RED"], "Failed", COLOR["ENDC"] + "- Device connection string is not valid")

def internet_check():
    try:
        sock = socket.create_connection(("www.google.com", 80))
        if sock is not None:
            print(COLOR["GREEN"], "OK", COLOR["ENDC"] + "- Device can DNS resolve and reach an outside URL")
            sock.close
        return True
    except OSError:
        print(COLOR["RED"], "Failed", COLOR["ENDC"] + "- Device cannot DNS resolve and reach an outside URL")
        pass
    return False

def time_check():
    sock = socket.create_connection(("time.nist.gov", 13))

    rawTime = sock.recv(1024)
    dayAndTime = rawTime.decode("utf-8")
    split_dayTime = dayAndTime.split()
    split_time = split_dayTime[2].split(":")

    local = datetime.now(timezone.utc)

    if split_dayTime[1] == local.strftime("%y-%m-%d"):
        if split_time[0] == local.strftime("%H") and split_time[1] == local.strftime("%M") and math.isclose(float(split_time[2]), float(local.strftime("%S")), abs_tol = 20):
            print(COLOR["GREEN"], "OK", COLOR["ENDC"] + "- System time is synced properly")
        else:
            print(COLOR["RED"], "Failed", COLOR["ENDC"] + "- System time is not synced properly")
    else:
            print(COLOR["RED"], "Failed", COLOR["ENDC"] + "- System time is not synced properly")



if __name__ == "__main__":
    main()