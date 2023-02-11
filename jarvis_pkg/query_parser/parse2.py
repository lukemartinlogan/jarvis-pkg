"""
Find all package queries (QueryTok.ROOT)
"""

from .parse_tree import ParseTree
from .query_node import QueryNode, QueryTok


class QueryParser2(ParseTree):
    def __init__(self, tree):
        self.root_node = tree.root_node

    def parse(self):
        self._parse(self.root_node)

    def _parse(self, root_node):
        i = 0
        i0 = 0
        while i < len(root_node):
            if root_node[i].type == QueryTok.ROOT:
                self._parse(root_node[i])
                i += 1
            elif self.check_pattern(root_node, i, QueryTok.MODULO,
                                    QueryTok.TEXT):
                i += 2
            elif self.check_pattern(root_node, i, QueryTok.CARROT,
                                    QueryTok.TEXT):
                i += 2
            elif root_node[i].type == QueryTok.TEXT and i0 != i:
                node = QueryNode(QueryTok.ROOT)
                i = root_node.group_nodes(node, i0, i - 1)
                i0 = i
                i += 1
            else:
                i += 1
        if i0 != i - 1:
            node = QueryNode(QueryTok.ROOT)
            root_node.group_nodes(node, i0, i - 1)
