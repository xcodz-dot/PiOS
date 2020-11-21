import os

import pios.core.terminal as _terminal

environment_variables = _terminal.load_environment_variables()


def run_script(script: str):
    for x in script.split("\n"):
        _terminal.run_command(x)


def put_env(env: str, value: str):
    run_script(f'setenv "{env}" "{value}"')


def list_env():
    os.listdir(f"{_terminal.root}/system/env")


def get_env(env: str):
    return environment_variables[env]
