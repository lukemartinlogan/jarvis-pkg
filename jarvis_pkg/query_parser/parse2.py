"""
Divides entire package queries, including dependencies.
The ROOT node should contain only QUERY token types.
"""

from .parse_tree import ParseTree
from .query_node import QueryNode, QueryTok


class QueryParser2(ParseTree):
    def __init__(self, tree):
        self.root_node = tree.root_node
        self.hidden = tree.hidden

    def parse(self):
        self._parse(self.root_node)
        self._deduplicate(self.root_node)
        return self

    def _parse(self, root_node):
        i = 0
        i0 = 0
        while i < len(root_node):
            if root_node[i].type == QueryTok.QUERY:
                self._parse(root_node[i])
                i += 1
            elif self.check_pattern(root_node, i, QueryTok.MODULO,
                                    QueryTok.TEXT):
                i += 2
            elif self.check_pattern(root_node, i, QueryTok.CARROT,
                                    QueryTok.TEXT):
                i += 2
            elif root_node[i].type == QueryTok.TEXT and i0 != i:
                node = QueryNode(QueryTok.QUERY)
                i = root_node.group_nodes(node, i0, i - 1)
                i0 = i
                i += 1
            else:
                i += 1
        if root_node[i0].type != QueryTok.QUERY:
            node = QueryNode(QueryTok.QUERY)
            root_node.group_nodes(node, i0, i - 1)

    def _deduplicate(self, root_node):
        i = 0
        while i < len(root_node):
            if root_node.type == QueryTok.QUERY and \
                    root_node[i].type == QueryTok.QUERY:
                if len(root_node) == 1:
                    root_node.cut(i)
                else:
                    self._deduplicate(root_node[i])
            else:
                i += 1
