import argparse
import base64
import glob
import json
import os
import re
import secrets
import shlex
import subprocess
import traceback
import types

import denverapi.colored_text as ctext

from pios.core import *

from . import core_utils


def generate_empty_environment(name="__main__", doc=""):
    return types.ModuleType(name, doc).__dict__


class AppEnvironment:
    def __init__(self, env):
        self.env = env

    def add_lib_to_path(self, path: str):
        exec(
            f"""
import sys

sys.path.insert(0, {repr(path)})
""",
            self.env,
        )

    def add_headers(self, **kwargs):
        newline = "\n"
        exec(
            f"""
{newline.join([f"{k} = {repr(v)}" for k, v in kwargs.items()])}
""",
            self.env,
        )


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


def repo_type(n: str):
    n = n.split("#", 1)[0].split("://", 1)
    if len(n) != 2:
        raise ValueError(
            "Value does not specifies a valid address {protocol}:{address}"
        )
    protocol = n[0]
    path = n[1]
    if protocol not in [
        "bdtpfserv",
    ]:
        raise ValueError(f"Invalid protocol '{protocol}'")
    for x in []:
        if x in path:
            raise ValueError(f"{x} is not allowed in the repository path")

    return {"protocol": protocol, "path": path.strip().split("/")}


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
    return modules


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
        while True:
            match = re.match(r"(\${(\w*?)})", "".join(s))
            if not match:
                break
            variable_value = match.group(1)  # ${VARIABLE_NAME}
            try:
                variable_value = environment_variables[match.group(2)]
            except KeyError:
                variable_value = f"{{{match.group(2)}}}"
            finally:
                s[match.start() : match.end()] = variable_value
        new_command.append("".join(s))
    return new_command


def search_in_paths(name: str, path):
    for x in path:
        if os.path.basename(os.path.splitext(x)[0]) == name:
            return x


def run_command(command, environment=None, pi_path=None):
    if environment is None:
        environment = load_environment_variables()
    if pi_path is None:
        pi_path = environment["PATH"].split(";")
    py_modules = [x.replace(os.sep, "/") for x in discover_modules(pi_path)]
    command = parse_command(command, environment)
    # noinspection PyBroadException
    try:
        if len(command) == 0:
            return 0
        elif command[0] == "exit":
            return "e"
        elif command[0] == "setenv":
            with open(f"{root}/system/env/{command[1]}", "w") as file:
                file.write(command[2])
        elif command[0] == "cd":
            os.chdir(command[1])
        elif command[0] == "delenv":
            os.remove(f"{root}/system/env/{command[1]}")
        elif command[0] == "echo":
            print(" ".join(command[1:]))
        elif command[0] == "pecho":
            print(*command[1].split(";"), sep="\n")
        elif command[0] == "ls":
            if len(command) == 1:
                command.append(os.getcwd())
            for x in os.listdir(command[1]):
                path = os.path.join(command[1], x)
                if os.path.isdir(path):
                    print(x, fore="cyan")
                else:
                    print(x)
        elif command[0] == "dlp":
            parser = argparse.ArgumentParser("dlp")
            subparsers = parser.add_subparsers(
                title="Commands", metavar="", dest="command"
            )

            install = subparsers.add_parser("install", help="Install a package")
            install.add_argument(
                "-f",
                "--force-install",
                help="Install a package regardless of it being installed " "or not",
                action="store_true",
            )
            install.add_argument(
                "-r", "--reinstall", help="Reinstall a package", action="store_true"
            )
            install.add_argument(
                "-i",
                "--install-recommend",
                help="Install all the recommended packages provided by "
                "the package you want to install",
                action="store_true",
            )
            install.add_argument(
                "-r",
                "--repository",
                help="Repository to search in",
                default=[],
                type=repo_type,
                action="append",
            )
            install.add_argument(
                "-n",
                "--no-defaults",
                help="Do not include default repository index in search",
                action="store_true",
            )
            install.add_argument(
                "-d",
                "--download",
                help="Download to a specific directory and do not install",
            )
            install.add_argument("package", help="package to download and install")

            uninstall = subparsers.add_parser("uninstall", help="Uninstall packages")
            uninstall.add_argument("package", help="Package to uninstall")

            args = parser.parse_args(command[1:])

            if args.command == "install":
                pass
        elif command[0] == "help-core-utils":
            for x in [x for x in dir(core_utils) if not x.startswith("_")]:
                print(x)

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
        dlp [options ...]                Download a package and install
        ls directory                     List a directory
        help-core-utils                  Print a clean list of all core utilities
        """
            )
        else:
            if command[0] in dir(core_utils):
                getattr(core_utils, command[0]).main(command)
            else:
                d = search_in_paths(
                    command[0], py_modules + discover_modules(os.getcwd())
                )
                if not d:
                    print(f"No such command '{command[0]}'", fore="yellow")
                elif not os.path.isfile(d):
                    print(f"'{command[0]} is not a file'")
                else:
                    result = subprocess.run([sys.executable, d, *command[1:]])
                    if result.returncode != 0:
                        return 1
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
    print(ctext.escape("Copyright (c) 2020 xcodz."))
    # noinspection PyCallByClass
    print(ctext.escape(f"{{fore_blue}}PiTerminal {{fore_green}}[{terminal_version}]"))
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
