"""
Parser Format:

repo.cls.name@v1:v2%clang%[openssl%gcc] +v1 -v2 v3=text
"""

class QueryParser:
    def __init__(self, text):
        q1 = QueryParser0(text)
        q2 = QueryParser1(q1)
