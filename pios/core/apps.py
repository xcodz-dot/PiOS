import json
import os
import runpy
import secrets
import shutil
import traceback
from time import sleep

from denverapi.ctext import input, print

from .sysinterface import *
from .terminal import root


def generate_empty_environment():
    return runpy._run_code("", {})


def generate_pios_app_environment():
    env = generate_empty_environment()
    env["__name__"] = "__pios__"
    return env


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
{newline.join([f"{k} = {v}" for k, v in kwargs.items()])}
""",
            self.env,
        )


def install_app(file_name, interactive=False):
    try:
        shutil.copyfile(file_name, f"{root}/.app.zip")
    except FileNotFoundError:
        raise InstallerFileNotFound(file_name)
    try:
        shutil.unpack_archive(f"{root}/.app.zip", f"{root}/.temp")
    except Exception as e:
        raise InstallerUnknownPpkFormat(
            f"Exception raised while unpacking archive: {e.__class__.__name__}"
        )

    with open(f"{root}/.temp/app.json") as file:
        app_info = json.load(file)

    try:
        if not os.path.isdir(f"{root}/user/programs/{app_info['name']}"):
            os.mkdir(f"{root}/user/programs/{app_info['name']}")
        else:
            shutil.rmtree(f"{root}/user/programs/{app_info['name']}")
            os.mkdir(f"{root}/user/programs/{app_info['name']}")
        if os.path.isdir(f"{root}/user/programs/{app_info['name']}/instance"):
            shutil.rmtree(f"{root}/user/programs/{app_info['name']}/instance")
    except Exception as e:
        if interactive:
            print(
                "WARNING: Exception while creating program directory",
                e.__class__.__name__,
                ": ",
                str(e),
                sep="",
                fore="yellow",
            )
    app_root = f"{root}/user/programs/{app_info['name']}"
    instance_root = f"{root}/user/programs/{app_info['name']}/instance"
    file_root = f"{root}/.temp"

    env = generate_empty_environment()
    try:
        with open(file_root + "/setup.py", "r") as installer:
            exec(installer.read(), env)
            installer_rval = eval(
                f"install_app({repr(app_root)}, {repr(instance_root)}, {repr(file_root)})",
                env,
            )
    except Exception as e:
        raise InstallerScriptError(f"{e.__class__.__name__}: {str(e)}")
    return installer_rval


def install_interface():
    print("PiOS Install")
    archive_path = input("PiOS Package Kit (*.ppk): ", fore="magenta")
    print(f"Installing {os.path.basename(archive_path)}")
    print(f"Installing Archive - Verifying Archive")
    if not os.path.isfile(archive_path):
        print("Installing Archive - Verification Failed (File Not Found)", fore="red")
    exc = None
    installed = False
    try:
        ex = False
        installed = install_app(archive_path, False)
    except Exception as e:
        print("Installing Archive - Error", fore="red")
        ex = True
        exc = e
    if ex:
        exceptions = {
            "InstallerError": "UNKNOWN INSTALLER ERROR",
            "InstallerScriptError": "CORRUPTED SETUP.PY",
            "InstallerInvalidPackage": "INVALID PACKAGE TREE",
            "InstallerFileNotFound": "FILE NOT FOUND",
            "InstallerUnknownPpkFormat": "FILE IS NOT PPK",
        }
        if exc.__class__.__name__ in exceptions.keys():
            error_context = exceptions[exc.__class__.__name__]
        else:
            error_context = "UNKNOWN ERROR"
        log_name = f"LOG-{secrets.token_hex(3)}.txt"
        sleep(1)
        print(f"Installing Archive - Log Written to {log_name}")
        with open(log_name, "w") as file:
            error_info = {
                "type": error_context,
                "error": {
                    "name": exc.__class__.__name__,
                    "str_repr": str(exc),
                    "args": exc.args,
                },
            }
            json.dump(error_info, file, indent=4, sort_keys=True)
            file.write("\n\n# Ask for help at https://github.com/xcodz-dot/PiOS/")
    elif not installed:
        print(
            "\nIt seems like installer refused to install your application"
            "\nCheck the above statements printed bye installer to know more"
        )
    else:
        print("Installing Archive Done")
    input("Press Enter To Continue")


def uninstall_interface():
    print("PiOS Uninstall")


def run_app(name: str):
    crdir = os.getcwd()
    programs = list_apps()
    env = generate_pios_app_environment()
    program = programs[name]
    env["__file__"] = program[0] + "/main.py"
    os.chdir(program[0] + "/instance")
    envi = AppEnvironment(env)
    envi.add_lib_to_path(program[0] + "/instance")
    envi.add_lib_to_path(program[0] + "/packages")
    returned_sys_exit = False
    sys_exit = None
    with open(envi.env["__file__"]) as source:
        # noinspection PyBroadException
        errored = False
        try:
            exec(source.read(), envi.env)
        except SystemExit as sys_exit:
            returned_sys_exit = True
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            errored = True
            traceback.print_exc()

    var = envi.env
    os.chdir(crdir)
    if "PIOS_EXIT_INTERFACE" in var.keys():
        exit_interface = var["PIOS_EXIT_INTERFACE"]
    else:
        exit_interface = {}

    # Check exit code if exit is made using SystemExit
    if returned_sys_exit:
        excode = 1
        if len(sys_exit.args) == 0:
            excode = 0
        elif len(sys_exit.args) == 1:
            if isinstance(sys_exit.args[0], int):
                excode = sys_exit.args[0]
        exit_interface["EXIT_CODE"] = excode
    # If program exits without using SystemExit
    else:
        exit_interface.setdefault("EXIT_CODE", 1 if errored else 0)
    return exit_interface


def list_apps():
    d = {}
    dirlist = os.listdir(f"{root}/user/programs/")
    for x in dirlist:
        if os.path.isdir(f"{root}/user/programs/{x}"):
            dirx = os.listdir(f"{root}/user/programs/{x}")
            if "app.json" in dirx:
                with open(f"{root}/user/programs/{x}/app.json") as file:
                    di = json.load(file)
                    d[x] = (f"{root}/user/programs/{x}", di["name"], di["version"])
    return d
