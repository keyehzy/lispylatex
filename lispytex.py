import sys
import os
import re
from collections import defaultdict

TK_RE = re.compile(
    r"""[\s,]*(~@|[\[\]{}()'`~^@]|"(?:[\\].|[^\\"])*"?|;.*|[^\s\[\]{}()'"`@,;]+)"""
)

INT_RE = re.compile(r"-?[0-9]+$")
FLOAT_RE = re.compile(r"-?[0-9][0-9.]*$")


class Symbol(str):
    pass


class LispParser:

    pointer = 0

    def __init__(self, code: str, indentation: int):
        self.code = code
        self.tokens = re.findall(TK_RE, code)
        self.back = self.tokens[self.pointer]
        self.indentation = indentation
        self.bindings = defaultdict(str)

    def peek(self):
        return self.back

    def skip(self):
        self.pointer += 1
        assert (self.pointer < len(self.tokens))
        self.back = self.tokens[self.pointer]

    def parse1(self):
        if (re.match(INT_RE, self.peek())):
            return int(self.peek())
        elif (re.match(FLOAT_RE, self.peek())):
            return float(self.peek())
        else:
            return Symbol(self.peek())

    def parse_list(self, l_d='(', r_d=')'):
        ast = []
        assert self.peek() == l_d
        self.skip()
        while (self.peek() != r_d):
            ast.append(self.parse())
            self.skip()
        return ast

    def parse(self) -> list:
        if self.peek() == '(':
            return self.parse_list()
        elif self.peek() == '[':
            return self.parse_list(l_d='[', r_d=']')
        else:
            return self.parse1()

    def many_curlies(self, a):
        return f"{{{a}}}"

    def lookup(self, symbol):
        if symbol in self.bindings.keys():
            return self.bindings[symbol]
        elif symbol == '+' or symbol == 'plus':
            return lambda a, b: f"{a} + {b}"
        elif symbol == '-' or symbol == 'minus':
            return lambda a, b: f"{a} - {b}"
        elif symbol == '*' or symbol == 'times':
            return lambda a, b: f"{a} * {b}"
        elif symbol == '/' or symbol == 'div':
            return lambda a, b: f"{a} / {b}"
        elif symbol == '=' or symbol == 'eq':
            return lambda a, b: f"{a} = {b}"
        elif symbol == '%' or symbol == 'mod':
            return lambda a, b: f"{a} % {b}"
        elif symbol == '^' or symbol == 'up':
            return lambda a, b: f"{a}^{{{b}}}"
        elif symbol == '_' or symbol == 'sub':
            return lambda a, b: f"{a}_{{{b}}}"
        elif symbol == '<' or symbol == 'lt':
            return lambda a, b: f"{a} < {{{b}}}"
        elif symbol == '>' or symbol == 'gt':
            return lambda a, b: f"{a} > {{{b}}}"
        elif symbol.endswith('!'):
            return lambda *a: f"\\{symbol.rstrip('!')}" + "".join(
                [self.many_curlies(i) for i in a])
        else:
            return symbol

    def eval1(self, ast) -> str:
        if type(ast) == Symbol:
            return self.lookup(ast)
        elif type(ast) == list:
            return list(map(lambda a: self.eval(a), ast))
        else:
            return ast

    def indent(self, i):
        return " " * (2 * i + self.indentation)

    def eval(self, ast, level=0) -> str:
        if not type(ast) == list:
            return self.eval1(ast)

        if len(ast) == 0:
            return ast

        if (ast[0] == "documentclass!"):
            section, args, result = ast[1], ast[2], self.eval(ast[3],
                                                           level).strip()
            if args:
                a = ", ".join([_ for _ in args])
                header = self.indent(
                    level) + f"\\documentclass{{{section}}}[{a}]\n"
            else:
                header = self.indent(level) + f"\\documentclass{{{section}}}\n"
            body = self.indent(level) + f"{result}"
            return header + body
        elif ast[0] == "begin!":
            section, result = ast[1], self.eval(ast[2], level + 1).strip()
            header = self.indent(level) + f"\\begin{{{section}}}\n"
            body = self.indent(level + 1) + f"{result}\n"
            close = self.indent(level) + f"\\end{{{section}}}"
            return header + body + close
        elif ast[0] == "let":
            varlist, body = ast[1], ast[2]
            for vardecl in varlist:
                var, val = vardecl[0], vardecl[1]
                self.bindings[var] = self.eval(val, level)
            return self.eval(body, level)
        elif ast[0] == "quote":
            return ast[1]
        else:
            element = self.eval1(ast)
            function = element[0]
            return function(*element[1:])

    def scaffold(self):
        return self.eval(self.parse())


class Parser:
    def __init__(self, data, stream):
        self.data = data
        self.pointer = 0
        self.stream = stream

    def eprint(self, *args, **kwargs):
        print(*args, **kwargs, file=self.stream)

    def __str__(self):
        return self.data[self.pointer::]

    def peek(self) -> None:
        return self.data[self.pointer]

    def skip(self) -> None:
        self.pointer += 1

    def is_eof(self) -> bool:
        return self.pointer == len(self.data)

    def find_next_token(self, token: str) -> bool:
        while (not self.is_eof() and self.peek() != token):
            self.skip()
        return False if self.is_eof() else True

    def find_next_token_no_walk(self, token: str) -> int:
        ptr = self.pointer
        while (ptr < len(self.data) and self.data[ptr] != token):
            ptr += 1
        return ptr

    def find_indentation_level(self) -> int:
        ptr = self.pointer
        while (ptr >= len(self.data) and self.data[ptr] != '\n'):
            ptr -= 1
        level = 0
        while (ptr < len(self.data) and self.data[ptr] == ' '):
            ptr += 1
            level += 1
        return level - 1

    def skip_ws(self) -> str:
        begin_of_ws = self.pointer
        while (not self.is_eof() and self.peek().isspace()):
            self.skip()
        return self.data[begin_of_ws:self.pointer]

    def next_word(self) -> str:
        self.skip_ws()
        begin_of_word = self.pointer
        while (not self.is_eof() and self.peek().isalpha()):
            self.skip()
        return self.data[begin_of_word:self.pointer]

    def parse_comments(self) -> None:
        begin_ptr = self.pointer
        while (self.find_next_token('@')):
            self.eprint(self.data[begin_ptr:self.pointer].rstrip())
            self.skip()    # skip '@'
            if (self.next_word() == "lisp"):
                lisp_code = LispParser(
                    self.data[self.pointer:self.find_next_token_no_walk('\n')],
                    self.find_indentation_level())
                self.eprint(lisp_code.scaffold())
                self.pointer += len(lisp_code.code)
            begin_ptr = self.pointer + 1    # also skip '\n'
        self.eprint(self.data[begin_ptr::].rstrip())


class Args:
    def __init__(self, argv):
        if (len(argv) < 2):
            print("Error: No arguments!", file=sys.stderr)
            self.help()

        self.outfile = sys.stdout
        modifiers = [f for f in argv[1::] if f.startswith('-')]

        for mod in modifiers:
            if mod == "-f":
                input_argument_index = argv.index("-f")
                if (input_argument_index + 1 < len(argv)):
                    filepath = argv[input_argument_index + 1]
                    if os.path.exists(filepath):
                        self.path = filepath
                        self.file = open(self.path, "r")
                    else:
                        print("Error: File not found!", file=sys.stderr)
                        self.help()
                else:
                    print("Error: Missing filepath argument for input!",
                          file=sys.stderr)
                    self.help()
            elif mod == "-o":
                output_argument_index = argv.index("-o")
                if (output_argument_index + 1 < len(argv)):
                    self.outpath = argv[output_argument_index + 1]
                    self.outfile = open(self.outpath, "w")
                else:
                    print("Error: Missing filepath argument for output!",
                          file=sys.stderr)
                    self.help()
            elif mod == "-h":
                self.help()
            else:
                print("Error: Invalid argument modifier %s" % mod)
                self.help()

    def read(self):
        return self.file.read()

    def help(self):
        print("Lispy Latex: Expands lisp snippets to latex", file=sys.stderr)
        print("Usage: python lispytex [FILE]", file=sys.stderr)
        print("Options:", file=sys.stderr)
        print("-f [FILE]" + 10 * " " + "Input to program", file=sys.stderr)
        print("-o [FILE]" + 10 * " " + "Redirect output to [FILE]",
              file=sys.stderr)
        print("-h" + 17 * " " + "Help/usage page", file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    args = Args(sys.argv)
    lex = Parser(data=args.read(), stream=args.outfile)
    lex.parse_comments()
