import sys
from pathlib import Path

class FlowSyntaxError(Exception):
    def __init__(self, message, line):
        super().__init__(f"line {line}: {message}")
        self.message = message
        self.line = line


def strip_comment(line):
    in_string = False
    for index, char in enumerate(line):
        if char == '"':
            in_string = not in_string
        elif char == "#" and not in_string:
            return line[:index].rstrip()
    return line.rstrip()


def split_keyword(line):
    line = strip_comment(line)
    if not line.strip():
        return None
    parts = line.strip().split(" ", 1)
    keyword = parts[0].lower()
    rest = parts[1] if len(parts) == 2 else ""
    return keyword, rest




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
    if len(sys.argv) == 1 :
        no_args_function()
    elif len(sys.argv) == 2:
        arg_given_function(sys.argv[1])
    else :
        print("Too many arguments")
        sys.exit(2)
