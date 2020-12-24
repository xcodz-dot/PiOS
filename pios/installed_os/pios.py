import os

if not os.path.isdir(os.path.expanduser("~/.pios")):
    os.mkdir(os.path.expanduser("~/.pios"))
f = open(os.path.expanduser("~/.pios/root.json"), "w")
f.write(
    f"""
{{
    "root": "{os.getcwd().replace(os.sep, os.altsep)}"
}}"""
)
f.close()


from time import sleep

from pios.core import *
from pios.core.remote import *

sys.path.insert(0, os.path.abspath(f"{__file__}/.."))


def start_os():
    clear()
    print("Booting PiOS", fore="green")
    generate_default_directories_and_files()
    print("Welcome")
    sleep(1)
    clear()

    settings = json.loads(read_file_str("system/settings.json"))
    start_ui(settings["system"]["user-interface"])


def main():
    global root
    root = os.getcwd()
    rcode = 0
    try:
        start_os()
    except PiosShutdown:
        clear()
        print("Shutting Down", fore="red")
        rcode = 0
    except PiosReboot:
        clear()
        print("Rebooting", fore="red")
        rcode = 1
    except KeyboardInterrupt:
        clear()
        print("Forced Rebooting", fore="red")
        rcode = 1
    except Exception as e:
        clear()
        print(f"{repr(e)} [rebooting]", fore="red")
        sleep(2)
        rcode = 1
    sleep(1)
    clear()
    os.chdir(root)
    return rcode
