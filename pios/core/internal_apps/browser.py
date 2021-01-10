import os

import html2text
import requests


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def main():
    while True:
        url = input("URL> ")
        if url == "exit":
            clear()
            break
        try:
            print("-----------------------------------------")
            print(html2text.html2text(requests.get(url).text))
            input("-----------------------------------------")
            clear()
        except:
            clear()
            print(
                "Error Occurred while getting the page, type 'exit' to exit the browser"
            )


if __name__ == "__main__":
    main()
