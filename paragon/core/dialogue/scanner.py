class ScannerError(Exception):
    def __init__(self, line, line_index, message):
        super().__init__(f"Error at line {line}, index {line_index}: {message}")
        self.line = line
        self.line_index = line_index


class Scanner:
    def __init__(self, input: str):
        self.input = input
        self.line = 1
        self.line_index = 0
        self.pos = 0

    def error(self, message):
        raise ScannerError(self.line, self.line_index, message)

    def advance(self, count=1):
        for _ in range(0, count):
            self.next()

    def next(self) -> str:
        if self.at_end():
            self.error("Reached EOI while parsing.")
        result = self.peek()
        if result == "\n":
            self.line += 1
            self.line_index = 0
        self.pos += 1
        self.line_index += 1
        return result

    def expect(self, expected: str):
        actual = self.next()
        if actual != expected:
            self.error("Expected \"%s\" but found \"%s\" instead." % (expected, actual))

    def peek(self, amount: int = 0) -> str:
        index = self.pos + amount
        if index >= len(self.input):
            return "\0"
        else:
            return self.input[index]

    def position(self) -> (int, int):
        return self.line, self.line_index

    def at_end(self):
        return self.pos >= len(self.input)

    def scan_until(self, chars: set) -> str:
        res = ""
        while self.peek() not in chars:
            res += self.next()
        return res

    def scan_while(self, fn):
        res = ""
        while fn(self.peek()):
            res += self.next()
        return res

    def skip_while(self, chars: set):
        while self.peek() in chars:
            self.next()

    def scan_number(self):
        res = ""
        if self.peek() == "-":
            res += self.next()
        while self.peek().isdigit():
            res += self.next()
        if not res:
            self.error("Expected number.")
        return int(res)

    def scan_alnum(self):
        return self.scan_while(lambda c: c.isalnum())

    def skip_whitespace(self):
        self.skip_while({" ", "\t", "\n", "\r"})
