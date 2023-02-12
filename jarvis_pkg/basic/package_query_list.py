from jarvis_pkg.query_parser.parse import QueryParser


class PackageQueryList:
    def __init__(self):
        self.queries = []

    def append(self, text):
        self.queries += QueryParser(text).queries

    def to_list(self):
        return self.queries
