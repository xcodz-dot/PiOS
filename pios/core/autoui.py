from pios.core.terminal import *


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


class AutoUi:
    def __init__(self, ui: dict, command):
        self.ui = ui
        self.command = command
        self.ui_path = []

    def start_interface(self):
        while True:
            current_dir = self.get()
            sub_dirs = []
            actions = []
            for k, v in current_dir.items():
                if isinstance(v, dict):
                    sub_dirs.append(k)
                elif isinstance(v, str):
                    actions.append(k)
            sub_dirs.sort()
            actions.sort()
            sum_up = [(x, "d") for x in sub_dirs] + [(x, "a") for x in actions]
            if len(self.ui_path) > 0:
                print(", ..", fore="cyan")
            for item in range(len(sum_up)):
                x, t = sum_up[item]
                print(
                    ("," if t == "d" else ".") + str(item) + " " + x,
                    fore="cyan" if t == "d" else "green",
                )
            user_input = input(">", fore="magenta")
            if user_input == "..":
                if not len(self.ui_path) == 0:
                    self.ui_path.pop(-1)
            elif user_input.isnumeric():
                user_input = int(user_input)
                if user_input < len(sum_up):
                    x, t = sum_up[user_input]
                    if t == "d":
                        self.ui_path.append(x)
                    else:
                        self.command(current_dir[x])
            clear()

    def get(self):
        current_object = self.ui
        for sub_path in self.ui_path:
            current_object = current_object[sub_path]
        return current_object
