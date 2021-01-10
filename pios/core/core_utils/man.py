import os

from rich.console import Console
from rich.markdown import Markdown


def main(args):
    args.pop(0)
    if not args:
        args.append("help")
    if len(args) > 0:
        with open(os.path.abspath(f"{__file__}/../doc/{args[0]}.md")) as file:
            c = Console()
            md = Markdown(file.read())
            c.print(md)
