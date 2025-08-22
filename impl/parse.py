import random
import re
from typing import List, Tuple

Token = Tuple[str, str]

class Node: pass

class Tag(Node):
    def __init__(self, text: str):
        self.text = text.strip()

class Ref(Node):
    def __init__(self, name: str):
        self.name = name.strip()

class Dot(Node):
    def __init__(self, children: List[Node]):
        self.children = children

class And(Node):
    def __init__(self, children: List[Node]):
        self.children = children

class Or(Node):
    def __init__(self, children: List[Node], weights: List[int] = None):
        self.children = children
        self.weights = weights

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, kind=None):
        token = self.peek()
        if not token:
            raise ValueError("Unexpected end of input")
        if kind and token[0] != kind:
            raise ValueError(f"Expected {kind}, got {token}")
        self.pos += 1
        return token

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        node = self.parse_and()
        children = [node]
        while self.peek() and self.peek()[0] == "OR":
            self.consume("OR")
            children.append(self.parse_and())
        if len(children) == 1:
            return node
        weights = []
        for c in children:
            w = getattr(c, "weight", None)
            if w is None:
                w = 1
            weights.append(w)
        return Or(children, weights=weights)

    def parse_and(self):
        node = self.parse_dot()
        children = [node]
        while self.peek() and self.peek()[0] == "AND":
            self.consume("AND")
            children.append(self.parse_dot())
        if len(children) == 1:
            return node
        return And(children)

    def parse_dot(self):
        node = self.parse_primary()
        children = [node]
        while self.peek() and self.peek()[0] == "DOT":
            self.consume("DOT")
            children.append(self.parse_primary())
        if len(children) == 1:
            return node
        return Dot(children)

    def parse_primary(self):
        tok = self.peek()
        if not tok:
            raise ValueError("Unexpected end of input")
        if tok[0] == "REF":
            self.consume("REF")
            node = Ref(tok[1][1:-1])
            return self._maybe_weight(node)
        elif tok[0] == "LBRACE":
            self.consume("LBRACE")
            node = self.parse_expression()
            self.consume("RBRACE")
            return self._maybe_weight(node)
        elif tok[0] == "TAG":
            self.consume("TAG")
            node = Tag(tok[1])
            return self._maybe_weight(node)
        else:
            raise ValueError(f"Unexpected token {tok}")

    def _maybe_weight(self, node: Node):
        tok = self.peek()
        if tok and tok[0] == "WEIGHT":
            self.consume("WEIGHT")
            node.weight = int(tok[1][1:])
        return node

def parse_tag_expression(s: str) -> Node:
    tokens = tokenize(s)
    parser = Parser(tokens)
    return parser.parse_expression()

def tokenize(s: str) -> List[Token]:
    token_spec = [
        ("REF",     r"<[^>]+>"),
        ("LBRACE",  r"\{"),
        ("RBRACE",  r"\}"),
        ("OR",      r"\|"),
        ("AND",     r"&"),
        ("DOT",     r"\."),
        ("WEIGHT",  r":[0-9]+"),
        ("TAG",     r"[^<>{}.&|: \t\n]+"),
        ("SPACE",   r"[ \t\n]+"),
    ]
    regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_spec)
    tokens = []
    for m in re.finditer(regex, s):
        kind = m.lastgroup
        if kind == "SPACE":
            continue
        tokens.append((kind, m.group()))
    return tokens

def evaluate_ast(node: Node, files_by_name: dict, ref_stack: List[str] = None) -> List[str]:
    if ref_stack is None:
        ref_stack = []
    if isinstance(node, Tag):
        return [node.text]
    elif isinstance(node, Ref):
        if node.name in ref_stack:
            return []
        ref_file = files_by_name.get(node.name)
        if not ref_file or not ref_file.tags:
            return []
        line = random.choice(ref_file.tags)
        return evaluate_ast(parse_tag_expression(line), files_by_name, ref_stack + [node.name])
    elif isinstance(node, Dot):
        parts = []
        for child in node.children:
            parts.extend(evaluate_ast(child, files_by_name, ref_stack))
        return ["".join(parts)]
    elif isinstance(node, And):
        result = []
        for child in node.children:
            result.extend(evaluate_ast(child, files_by_name, ref_stack))
        return result
    elif isinstance(node, Or):
        chosen = (random.choices(node.children, weights=node.weights, k=1)[0]
                  if node.weights and len(node.weights) == len(node.children)
                  else random.choice(node.children))
        return evaluate_ast(chosen, files_by_name, ref_stack)
    return []

def is_ast_expression(s: str) -> bool:
    tokens = tokenize(s)
    for kind, _ in tokens:
        if kind in ("REF", "LBRACE", "AND", "OR"):
            return True
    return False
