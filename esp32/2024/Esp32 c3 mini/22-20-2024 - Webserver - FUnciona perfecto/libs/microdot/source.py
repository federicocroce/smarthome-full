# (c) 2014-2019 Paul Sokolovsky. MIT license.
from . import compiled


class Compiler:

    START_CHAR = "{"
    STMNT = "%"
    STMNT_END = "%}"
    EXPR = "{"
    EXPR_END = "}}"

    def __init__(self, file_in, file_out, indent=0, seq=0, loader=None):
        self.file_in = file_in
        self.file_out = file_out
        self.loader = loader
        self.seq = seq
        self._indent = indent
        self.stack = []
        self.in_literal = False
        self.flushed_header = False
        self.args = "*a, **d"

    def indent(self, adjust=0):
        if not self.flushed_header:
            self.flushed_header = True
            self.indent()
            self.file_out.write("def render%s(%s):\n" % (str(self.seq) if self.seq else "", self.args))
            self.stack.append("def")
        self.file_out.write("    " * (len(self.stack) + self._indent + adjust))

    def literal(self, s):
        if not s:
            return
        if not self.in_literal:
            self.indent()
            self.file_out.write('yield """')
            self.in_literal = True
        self.file_out.write(s.replace('"', '\\"'))

    def close_literal(self):
        if self.in_literal:
            self.file_out.write('"""\n')
        self.in_literal = False

    def render_expr(self, e):
        self.indent()
        self.file_out.write('yield str(' + e + ')\n')

    def parse_statement(self, stmt):
        tokens = stmt.split(None, 1)
        if tokens[0] == "args":
            if len(tokens) > 1:
                self.args = tokens[1]
            else:
                self.args = ""
        elif tokens[0] == "set":
            self.indent()
            self.file_out.write(stmt[3:].strip() + "\n")
        elif tokens[0] == "include":
            if not self.flushed_header:
                # If there was no other output, we still need a header now
                self.indent()
            tokens = tokens[1].split(None, 1)
            args = ""
            if len(tokens) > 1:
                args = tokens[1]
            if tokens[0][0] == "{":
                self.indent()
                # "1" as fromlist param is uPy hack
                self.file_out.write('_ = __import__(%s.replace(".", "_"), None, None, 1)\n' % tokens[0][2:-2])
                self.indent()
                self.file_out.write("yield from _.render(%s)\n" % args)
                return

            with self.loader.input_open(tokens[0][1:-1]) as inc:
                self.seq += 1
                c = Compiler(inc, self.file_out, len(self.stack) + self._indent, self.seq)
                inc_id = self.seq
                self.seq = c.compile()
            self.indent()
            self.file_out.write("yield from render%d(%s)\n" % (inc_id, args))
        elif len(tokens) > 1:
            if tokens[0] == "elif":
                assert self.stack[-1] == "if"
                self.indent(-1)
                self.file_out.write(stmt + ":\n")
            else:
                self.indent()
                self.file_out.write(stmt + ":\n")
                self.stack.append(tokens[0])
        else:
            if stmt.startswith("end"):
                assert self.stack[-1] == stmt[3:]
                self.stack.pop(-1)
            elif stmt == "else":
                assert self.stack[-1] == "if"
                self.indent(-1)
                self.file_out.write("else:\n")
            else:
                assert False

    def parse_line(self, l):
        while l:
            start = l.find(self.START_CHAR)
            if start == -1:
                self.literal(l)
                return
            self.literal(l[:start])
            self.close_literal()
            sel = l[start + 1]
            #print("*%s=%s=" % (sel, EXPR))
            if sel == self.STMNT:
                end = l.find(self.STMNT_END)
                assert end > 0
                stmt = l[start + len(self.START_CHAR + self.STMNT):end].strip()
                self.parse_statement(stmt)
                end += len(self.STMNT_END)
                l = l[end:]
                if not self.in_literal and l == "\n":
                    break
            elif sel == self.EXPR:
    #            print("EXPR")
                end = l.find(self.EXPR_END)
                assert end > 0
                expr = l[start + len(self.START_CHAR + self.EXPR):end].strip()
                self.render_expr(expr)
                end += len(self.EXPR_END)
                l = l[end:]
            else:
                self.literal(l[start])
                l = l[start + 1:]

    def header(self):
        self.file_out.write("# Autogenerated file\n")

    def compile(self):
        self.header()
        for l in self.file_in:
            self.parse_line(l)
        self.close_literal()
        return self.seq


class Loader(compiled.Loader):

    def __init__(self, pkg, dir):
        super().__init__(pkg, dir)
        self.dir = dir
        if pkg == "__main__":
            # if pkg isn't really a package, don't bother to use it
            # it means we're running from "filesystem directory", not
            # from a package.
            pkg = None

        self.pkg_path = ""
        if pkg:
            p = __import__(pkg)
            if isinstance(p.__path__, str):
                # uPy
                self.pkg_path = p.__path__
            else:
                # CPy
                self.pkg_path = p.__path__[0]
            self.pkg_path += "/"

    def input_open(self, template):
        path = self.pkg_path + self.dir + "/" + template
        print("path", path)
        return open(path)

    def compiled_path(self, template):
        return self.dir + "/" + template.replace(".", "_") + ".py"

    def load(self, name):
        try:
            return super().load(name)
        except (OSError, ImportError):
            pass

        compiled_path = self.pkg_path + self.compiled_path(name)

        f_in = self.input_open(name)
        f_out = open(compiled_path, "w")
        c = Compiler(f_in, f_out, loader=self)
        c.compile()
        f_in.close()
        f_out.close()
        return super().load(name)
