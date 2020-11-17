import os

if not os.path.isdir(os.path.expanduser("~/.pios")):
    os.mkdir(os.path.expanduser("~/.pios"))
f = open(os.path.expanduser("~/.pios/root.json"), "w")
f.write(
    f"""
{{
    "root": "{os.getcwd()}"
}}"""
)
f.close()


from time import sleep

from pios.core import *
from pios.core.remote import *

sys.path.append(os.path.abspath(f"{__file__}/.."))

with open("system/_installer.u256", "r+b") as file_i_sha:
    sha256_installer = file_i_sha.read()


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
    pios_running = True
    while pios_running:
        try:
            start_os()
            pios_running = False
        except PiosShutdown:
            clear()
            print("Shutting Down", fore="red")
            pios_running = False
        except PiosReboot:
            clear()
            print("Rebooting", fore="red")
        except KeyboardInterrupt:
            clear()
            print("Forced Rebooting", fore="red")
        except Exception as e:
            clear()
            print(f"{repr(e)} [rebooting]", fore="red")
            sleep(2)
        sleep(1)
        clear()
        os.chdir(root)
