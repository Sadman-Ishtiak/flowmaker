import sys
from pathlib import Path


def no_args_function():
    default = Path(__file__).resolve().parent / "algorithm.txt"
    if not default.is_file() :
        print("No input found please put algorithm.txt next to main.py or pass a directory")
        sys.exit(2)
    print(f"Would convert : {default}")


def arg_given_function(arg):
    directory = Path(arg)
    if not directory.is_dir():
        print(f"{arg} is not a directory")
        sys.exit(2)
    files = sorted(directory.glob("*.flow"))
    if not files:
        print(f"No .flow files are in the {directory}")
        return
    for f in files:
        print(f"Would convert : {f}")

if __name__ == "__main__" :
    print("This is the tkinter user interface program that is going to work as an interactive development environment for the flowmaker.")
    print(sys.argv)
    if len(sys.argv) == 1 :
        no_args_function()
    elif len(sys.argv) == 2:
        arg_given_function(sys.argv[1])
    else :
        print("Too many arguments")
        sys.exit(2)
