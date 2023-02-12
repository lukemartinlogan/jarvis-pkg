"""
This will divide the file into tokens and produce an initial labeling.
"""
from jarvis_pkg.basic.version import Version
from .query_node import QueryNode, QueryTok
import re


class QueryParser0:
    def __init__(self, text):
        self.text = text
        self.hidden = QueryNode(QueryTok.ROOT)
        self.root_node = QueryNode(QueryTok.ROOT)

    def lex(self):
        self._lex(self.text)
        return self

    def _lex(self, query_text):
        """
        Divides the query text into tokens.

        :param query_text:
        :return:
        """
        i = 0
        off = 0
        self.is_null = False
        toks = re.split('([\(\)\{\}\[\]\^%@\:\+\-=])|(\s+)', query_text)
        toks = [tok for tok in toks if tok is not None and len(tok) != 0]
        while i < len(toks):
            tok = toks[i]
            if tok == '@':
                self.root_node.add_node(QueryTok.AT, tok, off)
            elif tok == ':':
                self.root_node.add_node(QueryTok.COLON, tok, off)
            elif tok == '^':
                self.root_node.add_node(QueryTok.CARROT, tok, off)
            elif tok == '%':
                self.root_node.add_node(QueryTok.MODULO, tok, off)
            elif tok == '+':
                self.root_node.add_node(QueryTok.PLUS, tok, off)
            elif tok == '-':
                self.root_node.add_node(QueryTok.MINUS, tok, off)
            elif tok == '=':
                self.root_node.add_node(QueryTok.EQUALS, tok, off)
            elif tok == '(':
                self.root_node.add_node(QueryTok.PAREN_LEFT, tok, off)
            elif tok == ')':
                self.root_node.add_node(QueryTok.PAREN_RIGHT, tok, off)
            elif tok == '[':
                self.root_node.add_node(QueryTok.BRACKET_LEFT, tok, off)
            elif tok == ']':
                self.root_node.add_node(QueryTok.BRACKET_RIGHT, tok, off)
            elif tok == '{':
                self.root_node.add_node(QueryTok.BRACKET_LEFT, tok, off)
            elif tok == '}':
                self.root_node.add_node(QueryTok.BRACKET_RIGHT, tok, off)
            elif self._is_version(toks, i):
                self.root_node.add_node(QueryTok.VERSION, tok, off)
            elif self._is_space(toks, i):
                self.hidden.add_node(QueryTok.SPACE, tok, off)
            else:
                self.root_node.add_node(QueryTok.TEXT, tok, off)
            off += len(tok)
            i += 1

    @staticmethod
    def _is_space(toks, i):
        tok = toks[i]
        return re.match('\s+', tok) is not None

    @staticmethod
    def _is_name(toks, i):
        text = toks[i]
        first = re.match('[a-zA-Z_]', text[0])
        if first is None:
            return False
        second = re.match('[a-zA-Z0-9_]', text)
        return True

    @staticmethod
    def _is_version(toks, i):
        return Version.is_version(toks[i])
