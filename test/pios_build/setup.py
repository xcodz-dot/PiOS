import pickle
import shutil

import denverapi


def install_app(root: str, assets_root: str, file_root: str):
    with open(f"{file_root}/requirements.pickle", "r+b") as file:
        requirements = pickle.load(file)
    print(f"Installing Requirements: {requirements}")
    for x in requirements:
        if denverapi.install_pip_package(requirements) != 0:
            print(f"Error: Unable to install: {x}")
            return False

    shutil.copyfile(f"{file_root}/main.py", f"{root}/main.py")
    shutil.copytree(f"{file_root}/packages", f"{root}/packages")
    shutil.copyfile(f"{file_root}/app.json", f"{root}/app.json")
    shutil.copyfile(f"{file_root}/icon.cpg", f"{root}/icon.cpg")
    shutil.copytree(f"{file_root}/assets", assets_root)
