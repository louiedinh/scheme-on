# Environment will be a list of dictionaries.

class Entry(object):
    def __init__(self, names, values):
        self.mapping = dict(names, values)

    def lookup(self, name)
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


def eval(sexp, environment):
    action = expression_to_action(sexp)
    return action(sexp, environment)

def expression_to_action(sexp):
    if is_atom(sexp):
        return atom_to_action(sexp)
    else:
        return list_to_action(sexp)

def atom_to_action(sexp):
    pass

def list_to_action(sexp):
    pass
