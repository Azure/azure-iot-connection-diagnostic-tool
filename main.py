# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

import os
import platform
import logging
import socket
from datetime import datetime, timezone, timedelta

# adjust level depending on what level of logging you want to see
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

# soft import as users may forget to install necessary packages
try:
    from azure.iot.device import IoTHubDeviceClient
except ImportError:
    print(COLOR["RED"], "You need to run 'pip install azure-iot-device' first.", COLOR["ENDC"], end = "")

def print_ok(message):
    print(COLOR["GREEN"], "OK", COLOR["ENDC"], end = "")
    print("- " + message)
    
def print_fail(message):
    print(COLOR["RED"], "Failed", COLOR["ENDC"], end = "")
    print("- " + message)

def print_warning(message):
    print(COLOR["YELLOW"], "Warning", COLOR["ENDC"], end = "")
    print("- " + message)

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
    conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
    if conn_str == None:
        conn_str = input("No connection string environment variable detected. Input connection string: ")
    print()
    print("Connectivity Checks")
    print("-------------------")
    platform_check()
    internet_check()
    time_check()
    validate_conn_str(conn_str)
    client_connect(conn_str)

def platform_check():
    if platform.system() == "Windows":
        print_ok("Device operating system is supported (" + platform.system() + ")")
    elif platform.system() == "Linux":
        print_ok("Device operating system is supported (" + platform.system() + ")")
    elif platform.system() == "Darwin":
        # macOS users may not recognize Darwin, so we display their OS name independently
        print_ok("Device operating system is supported (macOS)")
    else:
        # device may work, even if not explicitly supported
        print_warning("Device operating system may not be supported (" + platform.system() + ")")

def validate_conn_str(conn_str):
    # parses connection string then calls additional function that uses output string/dict
    try:
        split_string = conn_str.split(";")
    except (AttributeError, TypeError):
        print_fail("Connection string must be of type str")
    try:
        d = dict(arg.split("=", 1) for arg in split_string)
    except ValueError:
        print_fail("Connection string cannot be parsed, check for missing arg name or bad syntax")

    validate_conn_str_format(d, split_string)
    validate_conn_str_args(d)
    hub_check(d)

def validate_conn_str_format(d, split_string):
    # this function only validates format, so we're only concerned that all the key components of a connection string are present
    if len(split_string) != len(d):
        print_fail("Connection string cannot be parsed, check for duplicate args or bad syntax")
    if not all(key in valid_keys for key in d.keys()):
        print_fail("Invalid key present, check connection string components match with valid_keys")
    else:
        print_ok("Device connection string is properly formatted")

def validate_conn_str_args(d):
    # Raise ValueError if incorrect combination of keys in dict d
    host_name = d.get(HOST_NAME)
    shared_access_key_name = d.get(SHARED_ACCESS_KEY_NAME)
    shared_access_key = d.get(SHARED_ACCESS_KEY)
    device_id = d.get(DEVICE_ID)
    x509 = d.get(X509)

    if shared_access_key and x509:
        print_fail("Connection string is invalid due to mixed authentication scheme")

    if host_name and device_id and (shared_access_key or x509):
        print_ok("Device connection string components are valid")
        pass
    elif host_name and shared_access_key and shared_access_key_name:
        print_ok("Device connection string components are valid")
        pass
    else:
        print_fail("Connection string is incomplete")

def hub_check(d):
    host_name = d.get(HOST_NAME)
    try: 
        sock = socket.create_connection((host_name, 443))
        if sock is not None:
            print_ok("Device can resolve Hub IP")
            return True
    except ConnectionError:
        print_fail("Hub IP check failed: connection error")
        pass
    except OSError:
        print_fail("Hub IP check failed: non-connection OS error")
        pass
    else:
        print_fail("Hub IP check failed: non-OS error")
        pass
    finally: sock.close()
    return False

def internet_check():
    try: 
        sock = socket.create_connection(("1.1.1.1", 80))
        if sock is not None:
            print_ok("Device can DNS resolve and reach an outside URL on HTTP port")
            return True
    except Exception:
        try:
            print_warning("First DNS resolution/HTTP port check failed...attempting secondary check")
            sock.close()
            
            sock = socket.create_connection(("google.com", 80))
            if sock is not None:
                print_ok("Second DNS resolution/HTTP port check succeeded")
                return True
        except ConnectionError:
            print_fail("Secondary check failed: connection error")
            pass
        except OSError:
            print_fail("Secondary check failed: non-connection OS error")
            pass
        else:
            print_fail("Secondary check failed: non-OS error")
            pass
    finally:
        sock.close()
    return False

def time_check():
    try:
        # get datetime from NIST
        sock = socket.create_connection(("time.nist.gov", 13))
        rawTime = sock.recv(1024)
    except:
        print_fail("Could not connect to NIST to test time sync")

    try:
        # convert to a string and pull out only the needed segments
        dayAndTime = rawTime.decode("utf-8")
        split_dayTime = dayAndTime.split()
        conc_dayTime = split_dayTime[1] + " " + split_dayTime[2]

        # convert to datetime object, make aware of UTC time zone
        dt_dayTime = datetime.strptime(conc_dayTime, "%y-%m-%d %H:%M:%S")
        dt_dayTime = dt_dayTime.replace(tzinfo=timezone.utc)

        # take current system time in UTC
        local = datetime.now(timezone.utc)

        # get the time difference as a time delta object
        difference = dt_dayTime - local

        # sets the time difference tolerance to 5 min
        if difference < timedelta(minutes=5):
            print_ok("System time is synced properly")
        else:
            print_fail("System time is not synced properly")

        print("Time difference between NIST and local time (HH:MM:SS):")
        print(difference)

    except:
        print_fail("Could not properly test system time sync")
    finally:
        sock.close()

def client_connect(conn_str):
    try:
        # Create instance of the device client using the connection string
        device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)
        print_ok("Device can create an IoT Hub Device Client")
    except:
        print_fail("Could not create device client from connection string")

    try:
        # Connect the device client.
        device_client.connect()
        print_ok("Device can connect client to IoT Hub")
        return True    
    except ConnectionError:
        print_fail("Client creation failed: connection error")
        pass
    except OSError:
        print_fail("Client creation failed: non-connection OS error")
        pass
    else:
        print_fail("Client creation failed: non-OS error")
        pass
    finally:
        device_client.shutdown()
    return False

if __name__ == "__main__":
    main()