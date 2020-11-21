def main():
    import pios_sdk_info

    # All Your code goes here
    print(f"Hello, World with {pios_sdk_info.sdk_tools}")


def main2():
    print(f"Hello, World as a script")


if __name__ == "__main__":
    main2()  # This function is called when you run your application as a script
elif __name__ == "__pios__":
    main()  # This function is called when pios runs your application
