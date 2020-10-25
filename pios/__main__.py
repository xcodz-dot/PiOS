
from argparse import ArgumentParser
from pios import version
from socket import gethostbyname
from sys import exit
from requests import get
from configparser import ConfigParser
from packaging.version import Version
from importlib import import_module
from shutil import copytree
import os


def check_for_updates():
    if not check_for_internet():
        print("Internet is required to check for updates")
        exit(1)
    print("Searching for updates")
    print("  Getting version file")
    response = get("https://github.com/xcodz-dot/PiOS/raw/main/version.ini")
    if not response.ok:
        print(f"    Error: Response code was not as expected ({response.status_code})")
        exit(1)
    print("Reading the file")
    version_info = ConfigParser()
    version_info.read_string(response.content.decode())
    pypi_version = Version(version_info["PiOS"]["pypi_version"])
    github_version = Version(version_info["PiOS"]["github_version"])
    recommended_version = Version(version_info["PiOS"]["recommended_version"])
    current_version = Version(version)
    print()
    if pypi_version > current_version and not pypi_version.pre:
        print("A New Stable release is available, upgrade via this command: 'pip install PiOS --upgrade'")
    if github_version > current_version:
        if github_version.pre:
            if github_version > current_version:
                print("A Github Beta release is available, upgrade via this command: "
                      "'pip install https://github.com/xcodz-dot/PiOS/tarball/main'")
        elif github_version > pypi_version and github_version > current_version:
            print("A Stable Github release is available, the release have not been uploaded to PyPI, upgrade "
                  "via this command: 'pip install https://github.com/xcodz-dot/PiOS/tarball/main'")
    if recommended_version > current_version:
        print("This version is no longer supported, please update using one of the commands above (stable release is "
              "recommended)")


def check_for_internet():
    # noinspection PyBroadException
    try:
        gethostbyname("https://www.google.com/")
    except:
        return False
    finally:
        return True


if __name__ == '__main__':
    parser = ArgumentParser(description="PiOS boot manager. This boot manager allows the user to run PiOS with other"
                                        "configurations", fromfile_prefix_chars="@")

    parser.version = f"PiOS ({version})"

    parser.add_argument("-f", "--operating-system", help="Specify a Operating System to load and run",
                        default="pios1")
    parser.add_argument("-c", "--check-upgrade", help="Check for upgrades", action="store_true")
    parser.add_argument("-v", "--version", action="version")

    args = parser.parse_args()

    if args.check_upgrade:
        check_for_updates()
    else:
        try:
            os.chdir(f"{__file__}/../os_instance/{args.operating_system}")
        except OSError:
            copytree(f"{__file__}/../os_recreation_data/{args.operating_system}",
                     f"{__file__}/../os_instance/{args.operating_system}")
            os.chdir(f"{__file__}/../os_instance/{args.operating_system}")
        operating_system = import_module(f"pios.installed_os.{args.operating_system}")
        operating_system.main()
