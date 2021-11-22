from dataclasses import dataclass


@dataclass
class Lexer:
    data: str
    pointer: int = 0

    def __str__(self):
        return data[self.pointer::]

    def peek(self) -> None:
        return self.data[self.pointer]

    def skip(self) -> None:
        self.pointer += 1

    def is_eof(self) -> bool:
        return self.pointer == len(self.data)

    def find_next_token(self, token: str) -> None:
        while (not self.is_eof() and self.peek() != token):
            self.skip()
        return


if __name__ == '__main__':
    f = open("test.tex", "r")
    data = f.read()
    lex = Lexer(data)
    lex.find_next_token('%')
    print(lex)
