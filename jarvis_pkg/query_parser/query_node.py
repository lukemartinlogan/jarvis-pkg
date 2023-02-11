from enum import Enum


class QueryTok(Enum):
    ROOT = 'ROOT'
    VERSION = 'VERSION'
    TEXT = 'TEXT'
    AT = 'AT'
    COLON = 'COLON'
    CARROT = 'CARROT'
    MODULO = 'MODULO'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    EQUALS = 'EQUALS'
    SPACE = 'SPACE'
    PAREN_LEFT = 'PAREN_LEFT'
    PAREN_RIGHT = 'PAREN_RIGHT'
    BRACKET_LEFT = 'BRACKET_LEFT'
    BRACKET_RIGHT = 'BRACKET_RIGHT'
    BRACE_LEFT = 'BRACE_LEFT'
    BRACE_RIGHT = 'BRACE_RIGHT'

    VARIANT = "VARIANT"

class QueryNode:
    def __init__(self, node_type, tok=None, off=0):
        self.tok = tok
        self.off = off
        self.type = node_type
        self.children = []

    def add_node(self, node_type, tok=None, off=0):
        self.children.append(QueryNode(node_type, tok, off))

    def group_nodes(self, node, i0, i):
        node.children = self.children[i0:i+1]
        self.children = self.children[:i0] + [node] + self.children[i+1:]

    def __getitem__(self, i):
        return self.children[i]

    def __len__(self):
        return len(self.children)
