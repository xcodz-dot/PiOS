def main(args):
    if len(args) == 1:
        return
    args.pop(0)
    for x in args:
        with open(x) as file:
            print(file.read())
