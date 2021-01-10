import os
from pathlib import Path

from denverapi.ctext import input, print

from ..terminal import root


def main():
    try:
        file_name = input("[glob]>", fore="red")
        for x in Path(root).rglob(file_name):
            if os.path.isdir(x):
                print("dir:", os.sep.join(x.parts).split(root, 1)[1], fore="cyan")
            else:
                print("file:", x, fore="green")
        input("")
    except:
        pass
