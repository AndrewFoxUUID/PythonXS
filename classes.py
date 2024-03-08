class Fact():

    name: str
    args: tuple[any]
    backwards_chaining: bool

    def __init__(self, fact: tuple[any], backwards_chaining=True):
        self.name = fact[0]
        self.args = fact[1:]
        self.backwards_chaining = backwards_chaining

    def __str__(self):
        string = "(" + self.name
        if len(self.args) > 0:
            string += ": " +  ", ".join([str(arg) for arg in self.args])
        return string + ")"

class Match():

    store: bool
    value: any
    condition: any # function

    def __init__(self, store: bool = False, value: any = None, condition = None):
        self.store = store
        self.value = value
        self.condition = condition

    def execute(self, value):
        if self.value is not None:
            return value == self.value
        elif self.condition is not None:
            return self.condition(value)
        else:
            return value

    def __str__(self):
        string = ""
        if self.store:
            string += "x"
        if self.value is not None:
            string += " = " + str(self.value)
        if self.condition is not None:
            string += " & " + str(self.condition)
        return "[" + string + "]"

    def __eq__(self, other):
        if other is Match:
            return self.value == other.value and self.condition == other.condition
        return False

    def __hash__(self):
        hash = self.store.__hash__()
        if self.value is not None:
            hash += self.value.__hash__()
        if self.condition is not None:
            hash += self.condition.__hash__()
        return hash

class MatchType:
    NULL = -1
    STORE = 0
    NOT = 1
    EXISTS = 2

class Pattern():

    matchtype: int
    name: str
    matches: list[Match]

    seen_facts: list[Fact] # cleared at the start of run

    possibly_seen: list[Fact] # staging for seen_facts

    def __init__(self, matchtype, name=None, *matches):
        self.matchtype = matchtype
        self.name = name
        self.matches = matches
        self.seen_facts = []
        self.possibly_seen = []

    def test(self, fact):
        if self.matchtype == MatchType.NULL:
            return True
        elif fact.name == self.name:
            for i in range(len(self.matches)):
                if (i >= len(fact.args)) or (self.matches[i].execute(fact.args[i]) is False):
                    return False
            return True
        return False

    def execute(self, fact_id, fact):
        self.possibly_seen = []
        args = {}

        if self.matchtype == MatchType.NULL:
            self.possibly_seen.append(fact_id)
            if len(self.seen_facts) == 0:
                return args
            else:
                return False

        if self.matchtype == MatchType.STORE:
            args["{1}"] = fact_id
        
        if self.matchtype == MatchType.EXISTS and len(self.seen_facts) > 0:
            return False
        elif fact_id not in self.seen_facts and fact.name == self.name:
            for i in range(len(self.matches)):
                if i >= len(fact.args):
                    return False
                match = self.matches[i].execute(fact.args[i])
                if match is False:
                    return False
                elif self.matchtype == MatchType.STORE and self.matches[i].store:
                    args["{" + str(len(args.keys()) + 1) + "}"] = match
            if self.matchtype != MatchType.NOT:
                self.possibly_seen.append(fact_id)
            return args
        else:
            return False

    def __str__(self):
        if self.matchtype == MatchType.NULL:
            return ""
        elif self.matchtype == MatchType.STORE:
            string = "x = ("
        elif self.matchtype == MatchType.NOT:
            string = "(not "
        elif self.matchtype == MatchType.EXISTS:
            string = "(exists "
        string += str(self.name)
        for match in self.matches:
            string += ", " + str(match)
        return string + ")"

    def __eq__(self, other):
        if other is Pattern:
            return self.matchtype == other.matchtype and self.name == other.name and self.matches == other.matches
        return False

    def __hash__(self):
        hash = self.matchtype + self.name.__hash__()
        for match in self.matches:
            hash += match.__hash__()
        return hash

class Rule():

    name: str
    lhs: list[Pattern]
    rhs: any # function
    assertions: list[str]
    salience: int

    def __init__(self, name: str, lhs: list[Pattern], rhs, assertions: list[str], salience: int = 0):
        self.name = name
        self.lhs = lhs
        self.rhs = rhs
        self.assertions = assertions
        self.salience = salience

    def execute(self, args):
        for pattern in self.lhs:
            pattern.seen_facts += pattern.possibly_seen
            pattern.possibly_seen = []
        self.rhs(*args.values())

    def __str__(self):
        string = str(self.name)
        for pattern in self.lhs:
            string += "\n  " + str(pattern)
        string += "\n=> " + ",".join(self.assertions)
        return string
