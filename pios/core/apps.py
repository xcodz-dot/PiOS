import json
import os
import runpy
import shutil

from denverapi.ctext import print

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

sys.path.append({repr(path)})
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
    shutil.copy(file_name, f"{root}/.app.zip")
    shutil.unpack_archive(f"{root}/.app.zip", f"{root}/.temp")

    with open(f"{root}/.temp/app.json") as file:
        app_info = json.load(file)

    try:
        if not os.path.isdir(f"{root}/user/programs/{app_info['name']}"):
            os.mkdir(f"{root}/user/programs/{app_info['name']}")
        else:
            shutil.rmtree(f"{root}/user/programs/{app_info['name']}")
            os.mkdir(f"{root}/user/programs/{app_info['name']}")
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
    file_root = f"{root}/.temp"

    env = generate_empty_environment()
    with open(file_root + "/setup.py", "r") as installer:
        exec(installer.read(), env)
    return eval(f"install_app({repr(app_root)}, {repr(file_root)})", env)
