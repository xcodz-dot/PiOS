
from argparse import ArgumentParser
from pios import version
from socket import gethostbyname
from sys import exit
from requests import get


def check_for_updates():
    if not check_for_internet():
        print("Internet is required to check for updates")
        exit(1)
    print("Searching for updates")
    print("  Getting version file")
    get("https://github.com/xcodz-dot/PiOS/")



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
                        default="pios")
    parser.add_argument("-c", "--check-upgrade", help="Check for upgrades", action="store_true")
    parser.add_argument("-v", "--version", action="version")

    args = parser.parse_args()

    if args.check_upgrade:pass


