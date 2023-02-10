from .jpkg_manifest_manager import JpkgManifestManager
from .version import Version
import copy
import re
from enum import Enum


class QueryTok:
    VERSION_TOK = 'VERSION_TOK'
    COLON = 'COLON'
    VERSION = 'VERSION'
    TEXT = 'TEXT'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    EQUALS = 'EQUALS'


class QueryNode:
    def __init__(self, type, tok):
        self.tok = tok
        self.type = type


class PackageQuery:
    def __init__(self, text=None):
        self.manifest = JpkgManifestManager.get_instance()
        self.text = text
        self.repo = None
        self.name = None
        self.cls = None
        self.variants = {}      # a dict of keys -> variant options
        self.versions = []      # a list of Version ranges
        self.dependencies = {}  # a dict of PackageQuery
        self.is_null = True

        if text is not None:
            self._parse_query_text(text)
            self.is_null = False
        else:
            self.is_null = True

    def intersect_version_range(self, min, max):
        self.versions.append((min, max))

    def intersect(self, other):
        new_query = copy.deepcopy(self)
        # Namespace
        if other.repo is not None:
            if self.repo is None or other.repo == self.repo:
                new_query.repo = other.repo
            else:
                return PackageQuery()
        # Class
        if other.cls is not None:
            if self.cls is None or other.cls == self.cls:
                new_query.cls = other.cls
            else:
                return PackageQuery()
        # Name
        if other.name is not None:
            if self.name is None or other.name == self.name:
                new_query.name = other.name
            else:
                return PackageQuery()
        # Variants
        for key, val in other.variants.items():
            if key not in self.variants or self.variants[key] == val:
                new_query.variants[key] = val
            else:
                return PackageQuery()
        # Dependencies
        for key, val in other.dependencies.items():
            if key not in self.dependencies:
                new_query.dependencies[key] = val
            else:
                my_dep_query = self.dependencies[key]
                other_dep_query = other.dependencies[key]
                isect = my_dep_query.intersect(other_dep_query)
                if isect.is_null:
                    return PackageQuery()
                else:
                    new_query.dependencies[key] = isect
        # Versions
        new_query.versions += other.versions
        if not new_query._verify_version_range():
            return PackageQuery()
        # Mark as non-null
        new_query.is_null = False
        return new_query

    def _verify_version_range(self):
        """
        Check whether the version range is empty set

        :return: True if not empty
        """
        if len(self.versions) == 0:
            return True
        min_max = max(self.versions, key=lambda x: x[0])
        max_min = min(self.versions, key=lambda x: x[1])
        return min_max <= max_min

    def matches(self, query):
        """
        Check whether or not two queries are intersectable

        :param query:
        :return:
        """
        return not self.intersect(query).is_null

    def __str__(self):
        return str(self.text)

    def __repr__(self):
        return str(self.text)

    def _parse_query_text(self, text):
        """
        @v1:v2 a=a1 +b%dep1@v1:v3%

        :param text:
        :return:
        """
        queries = text.split('%')
        self._parse_query(queries[0])
        for query_text in queries[1:]:
            dep_query = PackageQuery(query_text)
            self.dependencies[dep_query.cls] = dep_query

    def _parse_query(self, query_text):
        """
        Parses the text relating to a single package

        repo.pkg_name@v1:v2 +v1 -v2 v3=x

        :param query:
        :param query_text:
        :return:
        """
        self.nodes = []
        self._parse1(query_text)
        self._parse2()

    def _parse1(self, query_text):
        """
        Divides the query text into tokens.

        :param query_text:
        :return:
        """
        i = 0
        self.is_null = False
        toks = re.split('([@\:\+\-=])|\s+', query_text)
        toks = [tok for tok in toks if tok is not None and len(tok) != 0]
        while i < len(toks):
            tok = toks[i]
            if tok == '@':
                self.nodes.append(QueryNode(QueryTok.VERSION_TOK, tok))
            elif tok == ':':
                self.nodes.append(QueryNode(QueryTok.COLON, tok))
            elif tok == '+':
                self.nodes.append(QueryNode(QueryTok.PLUS, tok))
            elif tok == '-':
                self.nodes.append(QueryNode(QueryTok.MINUS, tok))
            elif tok == '=':
                self.nodes.append(QueryNode(QueryTok.EQUALS, tok))
            elif self._is_version(toks, i):
                self.nodes.append(QueryNode(QueryTok.VERSION, tok))
            else:
                self.nodes.append(QueryNode(QueryTok.TEXT, tok))
            i += 1

    def _parse2(self):
        i = self._parse_name()
        while i < len(self.nodes):
            if self.check_node_type(i, QueryTok.VERSION_TOK):
                i = self._parse_version_range(i + 1)
            elif self.check_node_type(i, QueryTok.TEXT):
                i = self._parse_variant(i)
            elif self.check_node_type(i, QueryTok.PLUS):
                i = self._parse_plus_minus_variant(i)
            elif self.check_node_type(i, QueryTok.MINUS):
                i = self._parse_plus_minus_variant(i)
            else:
                raise Exception(f"Invalid token: {self.nodes[i].tok}")

    def _parse_name(self):
        if self.check_pattern(0, QueryTok.TEXT, QueryTok.EQUALS):
            # This is a variant, not a package name
            return 0
        if self.check_pattern(0, QueryTok.TEXT):
            name_toks = self.get_tok(0).split('.')
            # [NAME] [.] [NAME] [.] [NAME]
            if len(name_toks) == 3:
                self.repo = name_toks[0]
                self.cls = name_toks[1]
                self.name = name_toks[2]
            # [NAME] [.] [NAME]
            elif len(name_toks) == 2:
                self.repo = name_toks[0]
                self.cls = self.manifest.get_class(name_toks[1])
                if self.cls != name_toks[1]:
                    self.name = name_toks[1]
            # [NAME]
            else:
                self.cls = self.manifest.get_class(name_toks[0])
                if self.cls != name_toks[0]:
                    self.name = name_toks[0]
            return 1
        return 0

    def _parse_version_range(self, i):
        # [VERSION] [:] [VERSION]
        if self.check_pattern(i, QueryTok.VERSION,
                              QueryTok.COLON, QueryTok.VERSION):
            min = Version(self.get_tok(i))
            max = Version(self.get_tok(i + 2))
            self.intersect_version_range(min, max)
            return i + 3
        # [VERSION] [:]
        elif self.check_pattern(i, QueryTok.VERSION, QueryTok.COLON):
            min = Version(self.get_tok(i))
            max = Version('max')
            self.intersect_version_range(min, max)
            return i + 2
        # [:] [VERSION]
        elif self.check_pattern(i, QueryTok.COLON, QueryTok.VERSION):
            min = Version('min')
            max = Version(self.get_tok(i + 1))
            self.intersect_version_range(min, max)
            return i + 2
        # [:]
        elif self.check_pattern(i, QueryTok.COLON, QueryTok.VERSION):
            min = Version('min')
            max = Version('max')
            self.intersect_version_range(min, max)
            return i + 1
        # [VERSION]
        elif self.check_pattern(i, QueryTok.VERSION):
            min = Version(self.get_tok(i))
            max = Version(self.get_tok(i))
            self.intersect_version_range(min, max)
            return i + 1
        else:
            raise Exception("Couldn't parse version range")

    def _parse_variant(self, i):
        # [TEXT] = [TEXT]
        p1 = self.check_pattern(i, QueryTok.TEXT,
                                QueryTok.EQUALS,
                                QueryTok.TEXT)
        # [TEXT] = [VERSION]
        p2 = self.check_pattern(i, QueryTok.TEXT,
                                QueryTok.EQUALS,
                                QueryTok.VERSION)
        if p1 or p2:
            key = self.get_tok(i)
            val = self.get_tok(i + 2)
            self.variants[key] = val
            return i + 3
        else:
            raise Exception(f"Invalid variant definition: {self.get_tok(i)}")

    def _parse_plus_minus_variant(self, i):
        # [+] [TEXT]
        if self.check_pattern(i, QueryTok.PLUS, QueryTok.TEXT):
            key = self.get_tok(i + 1)
            self.variants[key] = True
            return i + 2
        # [-] [TEXT]
        elif self.check_pattern(i, QueryTok.MINUS, QueryTok.TEXT):
            key = self.get_tok(i + 1)
            self.variants[key] = False
            return i + 2
        else:
            raise Exception(f"Invalid variant definition: "
                            f"{self.get_tok(i + 1)}")

    def check_node_type(self, i, type):
        if i >= len(self.nodes):
            return False
        return self.nodes[i].type == type

    def check_pattern(self, i, *types):
        for type in types:
            if not self.check_node_type(i, type):
                return False
            i += 1
        return True

    def get_tok(self, i):
        if i < len(self.nodes):
            return self.nodes[i].tok
        return None

    @staticmethod
    def _is_name(toks, i):
        text = toks[i]
        first = re.match('[a-zA-Z_]', text[0])
        if first is None:
            return False
        second = re.match('[a-zA-Z0-9_]', text)
        return True

    @staticmethod
    def _is_int(toks, i):
        try:
            int(toks[i])
        except ValueError:
            return False
        else:
            return True

    @staticmethod
    def _is_version(toks, i):
        return Version.is_version(toks[i])

