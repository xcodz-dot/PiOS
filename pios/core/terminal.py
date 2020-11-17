import base64
import glob
import json
import os
import re
import secrets
import shlex
import subprocess
import traceback

import denverapi.ctext

from pios.core import *


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


def execute_command(statement):
    exec(statement, globals())


f = json.load(open(os.path.expanduser("~/.pios/root.json")))
root = f["root"]


def discover_modules(path):
    modules = []
    for directory in path:
        if os.path.isdir(directory):
            modules.extend(glob.glob(f"{directory}/*.py"))
            modules.extend(glob.glob(f"{directory}/*.pyc"))
            modules.extend(glob.glob(f"{directory}/*.pyw"))
            modules.extend(glob.glob(f"{directory}/*.pyo"))


def load_environment_variables(env_dir=None):
    if env_dir is None:
        env_dir = f"{root}/system/env"
    env = os.listdir(env_dir)
    environment_variables = {k: read_file_str(f"{env_dir}/{k}") for k in env}
    return environment_variables


def parse_command(command, environment_variables=None):
    if environment_variables is None:
        environment_variables = load_environment_variables()

    command = shlex.split(command, True)
    new_command = []
    for x in command:
        s = list(x)
        while match := re.match(
            r"(\${(\w*?)})", "".join(s)
        ):  # Regex Expression to match this syntax
            variable_value = match.group(1)  # ${VARIABLE_NAME}
            try:
                variable_value = environment_variables[match.group(2)]
            except KeyError:
                variable_value = match.group(1)
            finally:
                s[match.start() : match.end()] = variable_value
        new_command.append("".join(s))
    return new_command


def run_command(command, environment=None, pi_path=None):
    if environment is None:
        environment = load_environment_variables()
    if pi_path is None:
        pi_path = pi_path = environment["PATH"].split(";")
    command = parse_command(command, environment)
    # noinspection PyBroadException
    try:
        if len(command) == 0:
            return 0
        elif command[0] == "exit":
            return "e"
        elif command[0] == "setenv":
            with open(f"{root}/system/env/{command[1]}") as file:
                file.write(command[2])
        elif command[0] == "cd":
            os.chdir(command[1])
        elif command[0] == "delenv":
            os.remove(f"{root}/system/env/{command[1]}")
        elif command[0] == "echo":
            print(command[1])
        elif command[0] == "pecho":
            print(*command[1].split(";"), sep="\n")
        elif command[0] == "dlp":
            print("DLP is not complete")  # TODO Complete DLP
        elif command[0] == "help":
            print(
                """
    Builtin Commands:
        setenv name value                Set an environment variable
        help                             See this help message
        exit                             Exit current session
        cd path                          Change directory
        delenv name                      Delete an environment variable
        echo value                       Print a value
        pecho value                      Print a value split at ';'
        dlp url                          Download a package and install"""
            )
    except Exception:
        error_msg = traceback.format_exc()
        print(error_msg)
        return 1
    return 0


def interactive_terminal_session():
    terminal_version = "1.0.0"
    os.chdir(root)

    clear()
    # noinspection PyCallByClass
    print(denverapi.ctext.ColoredText.escape("Copyright (c) 2020 xcodz."))
    # noinspection PyCallByClass
    print(
        denverapi.ctext.ColoredText.escape(
            f"{{fore_blue}}PiTerminal {{fore_green}}[{terminal_version}]"
        )
    )
    terminal_running = True
    while terminal_running:
        user_command = input(es(os.getcwd().replace(os.sep, "/") + "{fore_magenta}$ "))
        if run_command(user_command) == "e":
            return
        print()


def execute_script(arguments: list):
    return subprocess.run(
        arguments, stderr=sys.stderr, stdout=sys.stdout, stdin=sys.stdin
    )
