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
        q0 = QueryParser0(text)
        q1 = QueryParser1(q0)
        q2 = QueryParser2(q1)
        q3 = QueryParser3(q2)
        self.queries = q3.queries
