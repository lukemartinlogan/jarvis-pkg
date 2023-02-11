"""
Parser Format:

repo.cls.name@v1:v2%clang%[openssl%gcc] +v1 -v2 v3=text
"""
from .parse0 import QueryParser0
from .parse1 import QueryParser1
from .parse2 import QueryParser2
from .parse3 import QueryParser3


class QueryParser:
    def __init__(self, text):
        q0 = QueryParser0(text).lex()
        q1 = QueryParser1(q0).parse()
        q2 = QueryParser2(q1).parse()
        q3 = QueryParser3(q2).parse()
        self.queries = q3.queries

    def first(self):
        return self.queries[0]