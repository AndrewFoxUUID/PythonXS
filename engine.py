from .classes import *

factspace: dict[str, Fact] = {}
rulespace: dict[str, Rule] = {}

class Node():

    pattern: Pattern
    rules: list[str]
    facts: list[str]
    sources: list[str]

    retracted_facts: list[str]
    asserted_facts: list[str]
    satisfying_facts: list[str]

    def __init__(self, pattern):
        self.pattern: Pattern = pattern
        self.rules = []
        self.facts = []
        self.sources = []
        self.retracted_facts = []
        self.asserted_facts = []
        self.satisfying_facts = []

    def satisfied(self):
        if len(self.retracted_facts) + len(self.asserted_facts) > 0:
            for fact in self.retracted_facts:
                self.facts.remove(fact)
                self.satisfying_facts.remove(fact)
            self.retracted_facts = []
            for fact in self.asserted_facts:
                self.facts.append(fact)
                if self.pattern.test(factspace[fact]):
                    self.satisfying_facts.append(fact)
            self.asserted_facts = []

        return len(self.satisfying_facts) == 0 if self.pattern.matchtype == MatchType.NOT else len(self.satisfying_facts) > 0

    def __str__(self):
        return "{" + str(self.pattern) + ", " + str(len(self.rules)) + " rules, " + str(len(self.facts)) + " facts, " + str(len(self.satisfying_facts)) + " of which satisfy the pattern}"

network: dict[Pattern, Node] = {}

agenda = []

def buildAgenda():
    global agenda
    agenda = []
    to_test = set(rulespace.keys())
    sources_to_test = set()
    for node in network.values():
        if not node.satisfied():
            sources_to_test.update(node.sources)
            for rule in node.rules:
                to_test.discard(rule)
    to_test.update(sources_to_test)
    for id in to_test:
        satisfied = True
        args = {}
        for pattern in rulespace[id].lhs:
            if pattern.matchtype != MatchType.STORE and len(pattern.seen_facts) != 0:
                satisfied = False
                break
            elif pattern.matchtype == MatchType.NULL:
                break
            match = False
            for fact in network[pattern].facts:
                match = pattern.execute(fact, factspace[fact])
                if match != False:
                    for key in match:
                        args["{" + str(len(args) + 1) + "}"] = match[key]
                    break
            if pattern.matchtype == MatchType.NOT:
                if len(network[pattern].facts) == 0 or match:
                    pattern.seen_facts.append("")
            elif match == False:
                satisfied = False
                break
        if satisfied:
            agenda.append((id, args))
    agenda = sorted(agenda, key = lambda x: rulespace[x[0]].salience, reverse = True)
