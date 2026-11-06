import sys
from pathlib import Path


def arg_given_function():
    default = Path(__file__).resolve().parent / "algorithm.txt"


def no_args_function():
    ...

if __name__ == "__main__" :
    print("This is the tkinter user interface program that is going to work as an interactive development environment for the flowmaker.")
    print(sys.argv)
