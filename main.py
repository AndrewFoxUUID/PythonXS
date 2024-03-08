from .classes import *
from . import engine
from .utilities import *

def assertfacts(*facts: tuple[any]):
    for fact in facts:
        fact = Fact(fact)
        position = uuid()
        engine.factspace[position] = fact
        for node in engine.network.values():
            if node.pattern.name == fact.name:
                node.asserted_facts.append(position)

def defrule(name: str, patterns: list[Pattern], action, assertions: list[str] = [], salience: int = 0):
    position = uuid()

    for assertion in assertions:
        patterns.append(Pattern(MatchType.NOT, assertion))

    if len(patterns) == 0:
        patterns.append(Pattern(MatchType.NULL))

    for pattern in patterns:
        found = False
        for node_pattern in engine.network:
            if pattern == node_pattern:
                engine.network[node_pattern].rules.append(position)
                found = True
            elif node_pattern.name in assertions:
                engine.network[node_pattern].sources.append(position)
        if not found:
            node = engine.Node(pattern)
            node.rules.append(position)
            for id in engine.factspace:
                if pattern.name == engine.factspace[id].name:
                    node.asserted_facts.append(id)
            for id in engine.rulespace:
                if pattern.name in engine.rulespace[id].assertions:
                    node.sources.append(id)
            engine.network[pattern] = node

    engine.rulespace[position] = Rule(name, patterns, action, assertions, salience)

def run():
    for rule in engine.rulespace.values():
        for pattern in rule.lhs:
            pattern.seen_facts = []

    engine.buildAgenda()
    while len(engine.agenda) > 0:
        engine.rulespace[engine.agenda[0][0]].execute(engine.agenda[0][1])
        engine.buildAgenda()
