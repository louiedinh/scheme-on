import re

# Environment
class Entry(object):
    def __init__(self, names, values):
        self.mapping = dict(names, values)

def lookup(self, name):
    """
        Raises KeyError on missing name
    """
    return self.mapping[name]

class Table(object):
    def __init__(self):
        self.entries = []

    def extend(self, entry):
        self.entries.append(entry)

    def lookup(self, name):
        value = None
        for entry in self.entries:
            try:
                value = entry.lookup(name)
                break
            except KeyError:
                pass

        if value:
            return value
        else:
            raise KeyError("name %s cannot be found in the table" % name)

# Functions and Closures
class Function(object):
    PRIMITIVE = 1
    CLOSURE = 2

    def __init__(self, type, name=None):
        self.name = name
        self.type = type
        self.body = None
        self.closure_env = None
        self.parameters = []

def eval(sexp):
    return _eval(sexp, environment=Table())

def _eval(sexp, environment):
    action = expression_to_action(sexp)
    return action(sexp, environment)

def expression_to_action(sexp):
    if is_atom(sexp):
        return atom_to_action(sexp)
    else:
        return list_to_action(sexp)

def is_atom(sexp):
    return not re.match("\(.*\)", sexp)

CONSTS = ["#t", "#f", "cons", "car", "cdr", "atom?", "zero?", "empty?", "number?", "add1", "sub1"]
def atom_to_action(sexp):
    if re.match(r"^\d+$", sexp):
        return _const
    elif sexp in CONSTS:
        return _const
    else:
        return _identifier

def list_to_action(sexp):
    match = re.match(r"\((?P<first>.*?)\s+.*\)", sexp)
    func = match.group("first")
    if func == "lambda":
        return _lambda
    elif func == "quote":
        return _quote
    elif func == "cond":
        return _cond
    else:
        return _application

# Atom actions
def _const(sexp, env):
    if sexp.isdigit():
        return int(sexp)
    elif sexp == "#t":
        return True
    elif sexp == "#f":
        return False
    else:
        return Function(type=Function.PRIMITIVE, name=sexp)

def _identifier(sexp, env):
    print "identifier"

# List actions

def _lambda(sexp, env):
    print "lambda"

def _cond(sexp, env):
    print "cond"

def _quote(sexp, env):
    print "quote!"

def _application(sexp, env):
    sexpl = sexp[1:-1].split()
    first = sexpl[0]
    arg_sexps = sexpl[1:]
    func = _eval(first, env)
    arg_vals = [_eval(arg_sexp, env) for arg_sexp in arg_sexps]
    return _apply(func, arg_vals, env)

def _apply(func, arg_vals, env):
    if func.type == Function.CLOSURE:
        closure_env = func.closure_env
        body = func.body
        new_entry = Entry(func.parameters, arg_vals)
        new_env = env.copy()
        new_env.extend(new_entry)
        return _eval(func.body, new_env)
    elif func.type== Function.PRIMITIVE:
        return _apply_primitive(func.name, arg_vals)
    else:
        raise ValueError("%s is not a function" % func)

def _apply_primitive(func_name, arg_values):
    if func_name == "cons":
        return (arg_values[0], arg_values[1])
    elif func_name == "car":
        return arg_values[0][0]
    elif func_name == "cdr":
        return tuple(arg_values[0][1:])
    elif func_name == "add1":
        return arg_values[0] + 1
    elif func_name == "sub1":
        return arg_values[0] - 1
    elif func_name == "zero?":
        return arg_values[0] == 0
    elif func_name == "number?":
        return type(arg_values[0]) is int
    elif func_name == "atom?":
        pass
    elif func_name == "empty?":
        pass
    else:
        raise ValueError("%s - No such function func_name" % func_name)


if __name__ == '__main__':
    print eval("(add1 1)")
