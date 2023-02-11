"""
This will parse the following:
1. Variants
2. Groupings

[TEXT]@[VERSION]:[VERSION]%[TEXT]
"""

from jarvis_pkg.basic.package import PackageQuery
from jarvis_pkg.basic.version import Version
from .query_node import QueryNode, QueryTok
from .parse_tree import ParseTree


class QueryParser1(ParseTree):
    def __init__(self, tree):
        self.root_node = tree.root_node

    def parse(self):
        self._parse(self.root_node)
        return self

    def _parse(self, root_node, i=0, term=None):
        while i < len(root_node):
            if term is not None and root_node[i].type == term:
                return i
            elif self._is_variant(root_node, i):
                i = self._parse_variant(root_node, i)
            elif self._is_grouping(root_node, i):
                i = self._parse_grouping(root_node, i)
            else:
                i += 1
        return i

    def _is_grouping(self, root_node, i):
        node = root_node[i]
        if node.type == QueryTok.PAREN_LEFT:
            return True
        if node.type == QueryTok.BRACE_LEFT:
            return True
        if node.type == QueryTok.BRACKET_LEFT:
            return True
        return False

    def _parse_grouping(self, root_node, i):
        i0 = i
        new_query = QueryNode(QueryTok.ROOT)
        node = root_node[i]
        if node.type == QueryTok.PAREN_LEFT:
            i = self._parse(root_node, i+1, term=QueryTok.PAREN_RIGHT)
        if node.type == QueryTok.BRACE_LEFT:
            i = self._parse(root_node, i+1, term=QueryTok.BRACE_RIGHT)
        if node.type == QueryTok.BRACKET_LEFT:
            i = self._parse(root_node, i+1, term=QueryTok.BRACKET_RIGHT)
        return root_node.group_nodes(new_query, i0, i)

    def _is_variant(self, root_node, i):
        if self.check_pattern(root_node, i, QueryTok.PLUS, QueryTok.TEXT):
            return True
        elif self.check_pattern(root_node, i, QueryTok.MINUS, QueryTok.TEXT):
            return True
        elif self.check_pattern(root_node, i,
                                QueryTok.TEXT, QueryTok.EQUALS, QueryTok.TEXT):
            return True
        elif self.check_pattern(root_node, i,
                                QueryTok.TEXT, QueryTok.EQUALS,
                                QueryTok.VERSION):
            return True
        return False

    def _parse_variant(self, root_node, i):
        if self.check_pattern(root_node, i, QueryTok.PLUS, QueryTok.TEXT):
            node = QueryNode(QueryTok.VARIANT)
            node.variant_key = root_node[i + 1].tok
            node.variant_val = True
            return root_node.group_nodes(node, i, i + 1)
        elif self.check_pattern(root_node, i, QueryTok.MINUS, QueryTok.TEXT):
            node = QueryNode(QueryTok.VARIANT)
            node.variant_key = root_node[i + 1].tok
            node.variant_val = False
            return root_node.group_nodes(node, i, i + 1)
        else:
            node = QueryNode(QueryTok.VARIANT)
            node.variant_key = root_node[i].tok
            node.variant_val = root_node[i + 2].tok
            return root_node.group_nodes(node, i, i + 2)
