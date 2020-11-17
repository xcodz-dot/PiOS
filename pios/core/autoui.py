import base64
import json
import os
import secrets

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
        "security": {"installation": {"allow-unofficial-installer": False}},
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
        }
        clear()
        ui = AutoUi(ui, execute_command)
        ui.start_interface()
    elif ui_type == "terminal":
        interactive_terminal_session()


def execute_command(statement):
    exec(statement, globals())


class AutoUi:
    def __init__(self, ui: dict, command):
        self.ui = ui
        self.command = command
        self.ui_path = []

    def start_interface(self):
        while True:
            current_dir = self.get()
            sub_dirs = []
            actions = []
            for k, v in current_dir.items():
                if isinstance(v, dict):
                    sub_dirs.append(k)
                elif isinstance(v, str):
                    actions.append(k)
            sub_dirs.sort()
            actions.sort()
            if len(self.ui_path) > 0:
                print(", ..")
            index = 0
            for index, name in zip(range(len(sub_dirs)), sub_dirs):
                print(",{} {}".format(index, name))
            last_index = index + 1
            for index, name in zip(
                range(last_index, len(actions) + last_index + 1), actions
            ):
                print(".{} {}".format(index, name))
            user_input = input("->", fore="magenta")
            if user_input == ".." and len(self.ui_path) > 0:
                self.ui_path.pop(-1)
            elif user_input.isnumeric():
                if int(user_input) in range(0, last_index):
                    self.ui_path.append(sub_dirs[int(user_input)])
                elif int(user_input) in range(last_index, index + 1):
                    self.command(current_dir[actions[last_index - int(user_input)]])
            clear()

    def get(self):
        current_object = self.ui
        for sub_path in self.ui_path:
            current_object = current_object[sub_path]
        return current_object
