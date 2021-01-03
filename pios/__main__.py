import datetime
import json
import os
import subprocess
import sys
from argparse import ArgumentParser
from configparser import ConfigParser
from socket import gethostbyname

from packaging.version import Version
from requests import get

from pios import version


def check_for_updates(silece=False):
    if not check_for_internet():
        if not silece:
            print("Internet is required to check for updates")
        return
    print("Searching for updates")
    print("  Getting version file")
    response = get("https://github.com/xcodz-dot/PiOS/raw/main/version.ini")
    if not response.ok:
        print(f"    Error: Response code was not as expected ({response.status_code})")
        return
    print("Reading the file")
    version_info = ConfigParser()
    version_info.read_string(response.content.decode())
    pypi_version = Version(version_info["PiOS"]["pypi_version"])
    github_version = Version(version_info["PiOS"]["github_version"])
    recommended_version = Version(version_info["PiOS"]["recommended_version"])
    current_version = Version(version)
    print()
    if pypi_version > current_version and not pypi_version.pre:
        print(
            "A New Stable release is available, upgrade via this command: 'pip install PiOS --upgrade'"
        )
    if github_version > current_version:
        if github_version.pre:
            if github_version > current_version:
                print(
                    "A Github Beta release is available, upgrade via this command: "
                    "'pip install https://github.com/xcodz-dot/PiOS/tarball/main -U'"
                )
        elif github_version > pypi_version and github_version > current_version:
            print(
                "A Stable Github release is available, the release have not been uploaded to PyPI, upgrade "
                "via this command: 'pip install https://github.com/xcodz-dot/PiOS/tarball/main -U'"
            )
    if recommended_version > current_version:
        print(
            "This version is no longer supported, please update using one of the commands above (stable release is "
            "recommended)"
        )


def check_for_internet():
    # noinspection PyBroadException
    try:
        gethostbyname("www.google.com")
    except Exception:
        return False
    return True


if __name__ == "__main__":
    parser = ArgumentParser(
        description="PiOS boot manager. This boot manager allows the user to run PiOS with other"
        "configurations",
        fromfile_prefix_chars="@",
    )

    parser.version = f"PiOS ({version})"

    parser.add_argument(
        "-f",
        "--operating-system",
        help="Specify a Operating System to load and run",
        default="pios",
    )
    parser.add_argument(
        "-c", "--check-upgrade", help="Check for upgrades", action="store_true"
    )
    parser.add_argument("-v", "--version", action="version")

    args = parser.parse_args()

    try:
        with open(os.path.expanduser("~/.pios.json")) as file:
            config = json.load(file)
    except:
        config = {"date": datetime.datetime.now().toordinal() - 1}

    last_check = datetime.datetime.fromordinal(config["date"])
    today = datetime.datetime.fromordinal(datetime.datetime.now().toordinal())

    difference = today - last_check

    if args.check_upgrade or difference.days > 0:
        check_for_updates(True)
        config["date"] = datetime.datetime.now().toordinal()
        with open(os.path.expanduser("~/.pios.json"), "w") as file:
            json.dump(config, file)
    if difference.days > 0 and not args.check_upgrade:
        input("Enter to continue to PiOS")
    if not args.check_upgrade:
        while True:
            try:
                process = subprocess.run(
                    [sys.executable, "-m", f"pios.launchers.{args.operating_system}"]
                )
                if process.returncode == 0:
                    break
                elif process.returncode == 255:
                    continue
                elif process.returncode == 1:
                    break
            except KeyboardInterrupt:
                pass
            except SystemExit:
                pass
            except Exception:
                pass
