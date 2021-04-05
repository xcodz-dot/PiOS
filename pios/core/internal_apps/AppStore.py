import datetime
import os
import re
import string
import time
from hashlib import sha256

import requests
import toml
import wget
from denverapi.colored_text import input, print
from denverapi.keyboard import getch

from pios.core.apps import install_interface

appstore_list = {}
scene = ""
sha256_hashes = []
appstore_names = list(appstore_list.keys())


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def main_menu():
    print("App Store")
    print("\nCommands:")
    print("* (L) Show AppList", fore="green")
    print("* (S) Search", fore="green")
    print("* (Q) Quit", fore="green")


def print_list():
    global appstore_names
    global scene
    global appstore_list

    page = 0
    while True:
        clear()
        print("App Store\n")
        ls = appstore_names[page * 10 : page * 10 + 10]
        for x, y in zip(ls, range(10)):
            print(f"[{y}] {appstore_list[x]['name']}")
        print("\n [Z] Previous [X] Next [L] Hide", fore="green")
        opt = getch()
        if opt.lower() == b"x":
            if len(ls) > page * 10 + 10:
                page += 1
        if opt.lower() == b"z":
            if page - 1 >= 0:
                page -= 1
        if opt.lower() == b"l":
            scene = "menu"
            break
        if opt.isdigit():
            opt = int(opt.decode())
            if opt in range(len(ls)):
                sel = appstore_list[ls[opt]]
                while True:
                    clear()
                    print("App Store\n")
                    print(f"{sel['name']} - {sel['version']}")
                    print(f"\n{sel['description']}\n")
                    print(f" [I] Install [B] Back", fore="green")
                    opt = getch().lower()
                    if opt == b"i":
                        while True:
                            clear()
                            print("App Store\n")
                            print(f"Do you want to really install '{sel['name']}'?")
                            print(
                                f" [Y] Yes, with security [N] No      [S] Yes, without security",
                                fore="green",
                            )
                            opt = getch().lower()
                            clear()
                            if opt == b"n":
                                break
                            elif opt == b"y":
                                install_app_from_store(sel, True)
                                break
                            elif opt == b"s":
                                install_app_from_store(sel, False)
                                break
                    elif opt == b"b":
                        break


def search():
    global scene
    clear()
    print("App Store\n")
    q = input("Search: ", fore="green")
    results = []
    for x in appstore_names:
        if advanced_search(q, x):
            results.append(x)

    page = 0
    while True:
        clear()
        print("App Store\n")
        ls = results
        for x, y in zip(ls, range(10)):
            print(f"[{y}] {appstore_list[x]['name']}")
        print("\n [Z] Previous [X] Next [L] Hide", fore="green")
        opt = getch()
        if opt.lower() == b"x":
            if len(ls) > page * 10 + 10:
                page += 1
        if opt.lower() == b"z":
            if page - 1 >= 0:
                page -= 1
        if opt.lower() == b"l":
            scene = "menu"
            break
        if opt.isdigit():
            opt = int(opt.decode())
            if opt in range(len(ls)):
                sel = appstore_list[ls[opt]]
                while True:
                    clear()
                    print("App Store\n")
                    print(f"{sel['name']} - {sel['version']}")
                    print(f"\n{sel['description']}\n")
                    print(f" [I] Install [B] Back", fore="green")
                    opt = getch().lower()
                    if opt == b"i":
                        while True:
                            clear()
                            print("App Store\n")
                            print(f"Do you want to really install '{sel['name']}'?")
                            print(
                                f" [Y] Yes, with security [N] No      [S] Yes, without security",
                                fore="green",
                            )
                            opt = getch().lower()
                            clear()
                            if opt == b"n":
                                break
                            elif opt == b"y":
                                install_app_from_store(sel, True)
                                break
                            elif opt == b"s":
                                install_app_from_store(sel, False)
                                break
                    elif opt == b"b":
                        break


def advanced_search(query, string2):
    delimiters = list(string.punctuation) + [" "]
    regex_pattern = "|".join(map(re.escape, delimiters))
    split_string = [
        x.strip().lower() for x in re.split(regex_pattern, string2) if x != ""
    ]
    split_delimeter = [
        x.strip().lower() for x in re.split(regex_pattern, query) if x != ""
    ]

    found = []
    for x in split_delimeter:
        found_c = False
        for y in split_string:
            if y.startswith(x):
                found_c = True
        found.append(found_c)

    return all(found)


def install_app_from_store(app: dict, secure: bool = True):
    if ".temp.ppk" in os.listdir():
        os.remove(".temp.ppk")
    download_link = app["download_file"]
    dl = ""
    try:
        proto, addr = download_link.split(":", 1)
        if proto == "appstore":
            dl = "http://github.com/xcodz-dot/PiOS-Apps/raw/main/" + addr
        elif proto == "http":
            dl = "http://" + addr
        elif proto == "github":
            repo, branch, addr = addr.split(":", 2)
            dl = "http://github.com/" + repo + "/raw/" + branch + "/" + addr
    except Exception:
        print(f"Error While parsing the URL: {download_link}", fore="red")
        input("Enter to Continue")
        return
    try:
        wget.download(dl, ".temp.ppk")
    except Exception:
        print(f"Download Failed, Internet Unstable or Invalid URL: " + dl)
        if os.path.isfile(".temp.ppk"):
            os.remove(".temp.ppk")
        return
    if secure:
        file = open(".temp.ppk", "rb")
        hash_ = generate_sha256(file)
        if hash_ not in sha256_hashes:
            inp = input(
                "The file is unsecure and unverified, would you want to continue (N, y): "
            ).lower()
            if inp != "y":
                return
        file.close()
    install_interface(".temp.ppk")


def generate_sha256(file):
    sha = sha256()
    while True:
        chunk = file.read(1024 * 1024)
        if not chunk:
            break
        sha.update(chunk)
    return sha.hexdigest()


def main():
    global appstore_list
    global appstore_names
    global scene
    global sha256_hashes

    require_refresh = True
    print("Loading Catalog")
    if ".appstore-cache" not in os.listdir():
        os.mkdir(".appstore-cache")
    if "cache.toml" in os.listdir(".appstore-cache"):
        with open(".appstore-cache/date.txt") as file:
            data = file.read()
            data = int(data)
            cdate = datetime.datetime.now().toordinal()
            if cdate - data >= 1:
                require_refresh = True
            else:
                require_refresh = False
    if require_refresh:
        print("  - Downloading Catalog")
        try:
            file_data = requests.get(
                "https://github.com/xcodz-dot/PiOS-Apps/raw/main/appstore.toml"
            )
        except Exception:
            print("  - Unable to Download Catalog, Internet Required")
            time.sleep(2)
            return
        print("  - Saving Catalog")
        with open(".appstore-cache/cache.toml", "w+b") as file:
            file.write(file_data.content)
        print("  - Downloading SHA-256 Checksums")
        try:
            file_data = requests.get(
                "https://github.com/xcodz-dot/PiOS-Apps/raw/main/sha256.txt"
            )
        except Exception:
            print("  - Unable to Download SHA-256 Checksums, Internet Required")
            time.sleep(2)
            return
        with open(".appstore-cache/cache.sha256.txt", "wb") as file:
            file.write(file_data.content)
        with open(".appstore-cache/date.txt", "w") as file:
            file.write(str(datetime.datetime.now().toordinal()))
    print("  - Loading Catalog")
    with open(".appstore-cache/cache.toml") as file:
        appstore_list = toml.load(file)
        appstore_names = list(appstore_list.keys())
    print("  - Loading Checksums")
    with open(".appstore-cache/cache.sha256.txt") as file:
        sha256_hashes = file.read().split("\n")

    # Interface
    scene = "menu"
    while True:
        clear()
        main_menu()
        if scene == "menu":
            opt = getch()
            if opt.lower() == b"q":
                break
            elif opt.lower() == b"l":
                scene = "list"
            elif opt.lower() == b"s":
                scene = "search"
        elif scene == "list":
            print_list()
        elif scene == "search":
            search()


if __name__ == "__main__":
    main()
