import re
import copy

### ENVIRONMENT ###

class Entry(dict):
    def __init__(self, names, values):
        for name, value in zip(names, values):
            self[name] = value


class Table:
    def __init__(self, entries=None):
        if entries is None:
            self.entries = []
        else:
            self.entries = entries

    def extend(self, entry):
        self.entries.append(entry)

    def lookup(self, name):
        """
        Look through all entries and return the first binding for <name>.
        If not found, raise a KeyError
        """
        containing_entries = [entry for entry in self.entries if name in entry]
        if not containing_entries:
            raise KeyError("name %s cannot be found in the table" % name)
        else:
            return containing_entries[0][name]

    def copy(self):
        return Table(copy.deepcopy(self.entries))

    def all_bindings(self):
        """
        Returns all the bindings.
        Sorted in order of binding scope and then lexical ordering.
        """
        bindings = []
        for entry in self.entries:
            bindings.extend(sorted(entry.items(), key=lambda x: x[0]))
        return bindings



### SEXPS ###

Symbol = str

class SExp:
    @classmethod
    def read(cls, s):
        """
        Parses a lisp sexp into our internal representation
        """
        tokens = s.replace("(", " ( ").replace(")", " ) ").split()
        return cls.read_from(tokens)

    @classmethod
    def read_from(cls, token_list):
        """
        Given a list of tokens, return our representation of an sexp.
        Our representation mirrors lisp sexps with the following structures:
            - Lists are python lists
            - ints are python int objects
            - Strings are python str objects
        """
        if len(token_list) == 0:
            raise ValueError("Error - Unexpected EOF")
        token = token_list.pop(0)
        if token == '(':
            L = []
            while token_list[0] != ')':
                L.append(cls.read_from(token_list))
            token_list.pop(0)    # Remove the ')'
            return L
        elif token == ')':
            raise SyntaxError("Unexpected )")
        else:
            return cls.to_atom(token)

    @classmethod
    def to_atom(cls, token):
        """
        Tries to convert a token into an atom
        """
        try:
            return int(token)
        except ValueError:
            return Symbol(token)

    @classmethod
    def to_lstr(cls, sexp):
        """
        Convert our representation of sexps back into a lisp sexp.
        """
        if type(sexp) is list:
            return  "(" + " ".join([cls.to_lstr(s) for s in sexp]) + ")"
        else:
            return str(sexp)

### FUNCTIONS ###

class Function:
    PRIMITIVE = 1
    CLOSURE = 2

    def __init__(self, type, name=None):
        self.name = name
        self.type = type
        self.body = None
        self.closure_env = None
        self.parameters = []

### Interpreter ###

class Interpreter:
    def eval(self, sexp):
        return self._eval(SExp.read(sexp), environment=Table())

    def _eval(self, sexp, environment):
        action = self.expression_to_action(sexp)
        return action(sexp, environment)

    def is_atom(self, sexp):
        return type(sexp) is int or type(sexp) is Symbol

    def expression_to_action(self, sexp):
        if self.is_atom(sexp):
            return self.atom_to_action(sexp)
        else:
            return self.list_to_action(sexp)

    # Atom actions
    def atom_to_action(self, sexp):
        CONSTS = ["#t", "#f", "cons", "car", "cdr", "atom?", "zero?", "empty?", "number?", "add1", "sub1", "eq?"]
        if type(sexp) == int:
            return self._const
        elif sexp in CONSTS:
            return self._const
        else:
            return self._identifier

    def _const(self, sexp, env):
        if type(sexp) == int:
            return sexp
        elif sexp == "#t":
            return True
        elif sexp == "#f":
            return False
        else:
            return Function(type=Function.PRIMITIVE, name=sexp)

    def _identifier(self, sexp, env):
        return env.lookup(sexp)

    def list_to_action(self, sexp):
        func = sexp[0]
        if func == "lambda":
            return self._lambda
        elif func == "quote":
            return self._quote
        elif func == "cond":
            return self._cond
        else:
            return self._application

    def _quote(self, sexp, env):
        return sexp[1]

    def _lambda(self, sexp, env):
        f = Function(type=Function.CLOSURE)
        f.parameters = sexp[1]
        f.body = sexp[2]
        f.closure_env = env.copy()
        return f

    def _cond(self, sexp, env):
        cond_clauses = sexp[1]
        for predicate, conseq in cond_clauses:
            if self._eval(predicate, env):
                return self._eval(conseq, env)
        raise StopIteration("End of cond")

    def _application(self, sexp, env):
        func = self._eval(sexp[0], env)
        arg_vals = [self._eval(arg_sexp, env) for arg_sexp in sexp[1:]]
        return self._apply(func, arg_vals, env)

    def _apply(self, func, arg_vals, env):
        if func.type == Function.CLOSURE:
            closure_env = func.closure_env
            body = func.body
            new_entry = Entry(func.parameters, arg_vals)
            new_env = env.copy()
            new_env.extend(new_entry)
            return self._eval(func.body, new_env)
        elif func.type== Function.PRIMITIVE:
            return self._apply_primitive(func.name, arg_vals)
        else:
            raise ValueError("%s is not a function" % func)

    def _apply_primitive(self, func_name, arg_values):
        if func_name == "cons":
            return [arg_values[0]] + arg_values[1]
        elif func_name == "car":
            return arg_values[0][0]
        elif func_name == "cdr":
            return arg_values[0][1:]
        elif func_name == "add1":
            return arg_values[0] + 1
        elif func_name == "sub1":
            return arg_values[0] - 1
        elif func_name == "zero?":
            return arg_values[0] == 0
        elif func_name == "number?":
            return type(arg_values[0]) is int
        elif func_name == "atom?":
            return type(arg_values[0]) is not list
        elif func_name == "empty?":
            return isinstance(arg_values[0], list) and len(arg_values[0]) == 0
        elif func_name == "eq?":
            return arg_values[0] == arg_values[1]
        else:
            raise ValueError("%s - No such function func_name" % func_name)

if __name__ == '__main__':
    interpreter = Interpreter()
    while True:
        value = interpreter.eval(raw_input(">"))
        print(SExp.to_lstr(value))
