from .jpkg_manifest_manager import JpkgManifestManager
from .version import Version
import copy
import re


class PackageQuery:
    def __init__(self, text=None):
        self.manifest = JpkgManifestManager.get_instance()
        self.repo = None
        self.name = None
        self.cls = None
        self.variants = {}      # a dict of keys -> variant options
        self.versions = []      # a list of Version ranges
        self.dependencies = {}  # a dict of PackageQuery
        self.is_null = True
        if text is not None:
            self._parse_query_text(text)
            self.is_null = True
        else:
            self.is_null = False

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
        # Mark as non-null
        new_query.is_null = False

    def matches(self, query):
        return not self.intersect(query).is_null

    def _parse_query_text(self, text):
        """
        @v1:v2 a=a1 +b%dep1@v1:v3%

        :param text:
        :return:
        """
        queries = text.split('%')
        self._parse_query(self, queries[0])
        for query_text in queries:
            query = PackageQuery()
            self._parse_query(query, query_text)

    @staticmethod
    def _parse_query(query, query_text):
        i = 0
        query.is_null = False
        toks = re.split('([@\:\+\-= ])', query_text)
        toks = [tok for tok in toks if len(tok) == 0]
        while i < len(toks):
            tok = toks[i]
            if tok == '@':
                i -= 1
                pkg_name = query._parse_name(toks, i)
                if pkg_name is None:
                    i += 1
                min_version = query._parse_version(toks, i)
                if min_version is not None:
                    min_version = Version(min_version)
                    i += 1
                else:
                    min_version = Version('min')
                colon = query._parse_colon(toks, i)
                if colon is not None:
                    i += 1
                    max_version = query._parse_version(toks, i)
                else:
                    max_version = Version('max')
                query.name = pkg_name
                query.intersect_version_range(min_version, max_version)
            if tok == '+':
                key = query._parse_name(toks, i + 1)
                query.variants[key] = True
            if tok == '-':
                key = query._parse_name(toks, i + 1)
                query.variants[key] = False
            if tok == '=':
                key = query._parse_name(toks, i - 1)
                val = query._parse_tok(toks, i + 1)
                query.variants[key] = val

    @staticmethod
    def _parse_name(toks, i):
        if i < 0 or i >= len(toks):
            return None
        text = toks[i]
        first = re.match('[a-zA-Z_]', text[0])
        if first is None:
            return None
        second = re.match('[a-zA-Z0-9_]', text)
        return text

    @staticmethod
    def _parse_version(toks, i):
        if i < 0 or i >= len(toks):
            return None
        if Version.is_version(toks[i]):
            return toks[i]
        return None

    @staticmethod
    def _parse_colon(toks, i):
        if i < 0 or i >= len(toks):
            return None
        if toks[i] == ':':
            return toks[i]
        return None

    @staticmethod
    def _parse_tok(toks, i):
        if i < 0 or i >= len(toks):
            return None
        return toks[i]
