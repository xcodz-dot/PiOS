"""
A small and simple text editor for basic use

this is a year old creation of mine added to pios core utilities set
"""

__author__ = "xcodz"
__version__ = "1.0.0"


import os
from time import sleep

from denverapi.colored_text import input, print


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def main():
    print(f"PEdit {__version__}", fore="magenta")
    sleep(2)
    clear()
    d = []
    sp = None

    def form(d, t=""):
        f = []
        for i in range(len(d)):
            f.append(t.format(i=i, val=d[i]))
        return "".join(f)

    def ti(d):
        try:
            f = int(d)
        except:
            f = 0
        return f

    while True:
        clear()
        print(
            form(d, t="{i} > {val}\n")
            + "---------------------\n\
i:[index]:[val]\n\
d:[index]\n\
[val]\n\
save, done, open are special commands"
        )
        i = input("---------------------\n>")
        if i == "save":
            if not sp == None:
                f = open(sp, "w")
                f.write("\n".join(d))
                f.close()
            else:
                i = input("SAVE PATH>")
                sp = i
                f = open(sp, "w")
                f.write("\n".join(d))
                f.close()
        elif i == "done":
            break
        elif i == "open":
            try:
                i = input("PATH>")
                with open(i) as file:
                    d = file.read().split("\n")
                sp = i
            except Exception as e:
                print(f"{e.__class__.__name__}: {str(e)}")
        elif len(i) != 0:
            if i[0:2] == "i:":
                i = i.split(":", 2)
                if len(i) == 3:
                    d.insert(ti(i[1]), i[2])
            elif i[0:2] == "d:":
                try:
                    exec("del d[" + i.split(":", 1)[1] + "]")
                except:
                    pass
            else:
                d.append(i)
        else:
            d.append(i)
        clear()
