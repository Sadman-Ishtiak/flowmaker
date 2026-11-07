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
        elif char == '#' and not in_string:
            return line[:index].rstrip()
        return line.lstrip()
