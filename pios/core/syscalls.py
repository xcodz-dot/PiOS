import time

import pios.core.apps as apps
from pios.core.autoui import AutoUi
from pios.core.terminal import *


class PiosShutdown(Exception):
    pass


class PiosReboot(Exception):
    pass


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def make_directory_if_not_present(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)


def make_file_if_not_present(file, data):
    if not os.path.isfile(file):
        with open(file, "w" if isinstance(data, str) else "w+b") as fp:
            fp.write(data)


def generate_default_directories_and_files():
    default_settings = {
        "remote": {
            "enabled": False,
            "host-ipv4": "127.0.0.1",
            "host-port": 3700,
            "join-password": base64.encodebytes(secrets.token_bytes(4)).decode(),
        },
        "system": {
            "user-interface": "auto-ui",
        },
    }
    make_directory_if_not_present("home")
    make_directory_if_not_present("user")
    make_directory_if_not_present("user/programs")
    make_directory_if_not_present("system")
    make_directory_if_not_present("user/bin")
    if not os.path.isfile("system/settings.json"):
        with open("system/settings.json", "w") as file:
            json.dump(default_settings, file, indent=4, sort_keys=True)


def read_file_str(file_name):
    with open(file_name) as file:
        return file.read()


def read_file_bytes(file_name):
    with open(file_name, "w+b") as file:
        return file.read()


def write_file(file, data):
    with open(file, "w" if isinstance(data, str) else "w+b") as fp:
        fp.write(data)


def start_ui(ui_type):
    if ui_type == "auto-ui":
        ui = {
            "Power": {"Shut Down": "raise PiosShutdown", "Reboot": "raise PiosReboot"},
            "Terminal": "start_ui('terminal')",
            "System": {
                "App Manager": {
                    "Install": "apps.install_interface()",
                    "Uninstall": "apps.uninstall_interface()",
                }
            },
            "Apps": {k: f"run_app({repr(k)})" for k in apps.list_apps().keys()},
        }
        clear()
        ui = AutoUi(ui, execute_command)
        ui.start_interface()
    elif ui_type == "terminal":
        interactive_terminal_session()


def run_app(name: str):
    before_app = time.perf_counter()
    exit_interface = apps.run_app(name)
    after_app = time.perf_counter()
    print()
    time_used = after_app - before_app
    print(
        "Process returned",
        exit_interface["EXIT_CODE"],
        "in",
        str(round(time_used, 2)) + "s",
    )
    input("Press enter to continue")


def execute_command(statement):
    clear()
    exec(statement, globals())
