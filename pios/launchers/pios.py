import os
from importlib import import_module
from shutil import copytree


class Args:
    operating_system = "pios"


if not os.path.exists(os.path.expanduser("~/.pios")):
    os.mkdir(os.path.expanduser("~/.pios"))
if not os.path.exists(os.path.expanduser("~/.pios/os_instance")):
    os.mkdir(os.path.expanduser("~/.pios/os_instance"))
try:
    os.chdir(os.path.expanduser(f"~/.pios/os_instance/{Args.operating_system}"))
except OSError:
    copytree(
        os.path.abspath(f"{__file__}/../../os_recreation_data/{Args.operating_system}"),
        os.path.expanduser(f"~/.pios/os_instance/{Args.operating_system}"),
    )
    os.chdir(os.path.expanduser(f"~/.pios/os_instance/{Args.operating_system}"))

operating_system = import_module(f"pios.installed_os.{Args.operating_system}")
raise SystemExit(operating_system.main())
