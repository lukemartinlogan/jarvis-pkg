"""
Create the actual PackageQuery structures
"""
from jarvis_pkg.basic.package_query import PackageQuery
from jarvis_pkg.basic.jpkg_manifest_manager import JpkgManifestManager
from jarvis_pkg.basic.version import Version
from .parse_tree import ParseTree
from .query_node import QueryTok


class QueryParser3(ParseTree):
    def __init__(self, tree):
        self.root_node = tree.root_node
        self.queries = []
        self.query_roots = []
        self.manifest = JpkgManifestManager.get_instance()

    def parse(self):
        self._find_main_queries(self.root_node)
        for node in self.query_roots:
            pkg_query = PackageQuery()
            self.queries.append(pkg_query)
            pkg_query.is_null = False
            self._parse_query(node, pkg_query)
        return self

    def _find_main_queries(self, root_node):
        i = 0
        while i < len(root_node):
            node = root_node[i]
            if node.type == QueryTok.QUERY:
                if len(node) and node[0].type != QueryTok.QUERY:
                    self.query_roots.append(node)
            i += 1

    def _parse_query(self, root_node, pkg_query, i=0,
                     in_modulo=False,
                     in_grouping=False):
        while i < len(root_node):
            if root_node[i].type == QueryTok.TEXT:
                i = self._parse_name(root_node, i, pkg_query)
            elif root_node[i].type == QueryTok.GROUPING:
                self._parse_query(root_node[i], pkg_query,
                                  in_grouping=True)
                i += 1
            elif self._is_dependency(root_node, i):
                if in_modulo and not in_grouping:
                    return i
                i = self._parse_dependency(root_node, i, pkg_query)
            elif root_node[i].type == QueryTok.VARIANT:
                i = self._parse_variant(root_node, i, pkg_query)
            elif root_node[i].type == QueryTok.AT:
                i = self._parse_version_range(root_node, i, pkg_query)
            else:
                raise Exception(f"Invalid token type: {root_node[i].type}")
        return i

    def _parse_name(self, root_node, i, pkg_query):
        if root_node[i].type != QueryTok.TEXT:
            return i
        name_toks = root_node[i].tok.split('.')
        if len(name_toks) == 3:
            # [NAME].[NAME].[NAME]
            pkg_query.repo = name_toks[0]
            pkg_query.cls = name_toks[1]
            pkg_query.name = name_toks[2]
            return i + 1
        elif len(name_toks) == 2:
            # [NAME].[NAME]
            pkg_query.repo = None
            pkg_query.cls = name_toks[0]
            pkg_query.name = name_toks[1]
            return i + 1
        elif len(name_toks) == 1:
            # [NAME]
            pkg_query.cls = self.manifest.get_class(name_toks[0])
            if pkg_query.cls != name_toks[0]:
                pkg_query.name = name_toks[0]
            return i + 1
        return i

    def _parse_version_range(self, root_node, i, pkg_query):
        i += 1
        if self.check_pattern(root_node, i,
                              QueryTok.VERSION, QueryTok.COLON,
                              QueryTok.VERSION):
            # [VERSION] [:] [VERSION]
            vmin = Version(root_node[i].tok)
            vmax = Version(root_node[i+2].tok)
            pkg_query.intersect_version_range(vmin, vmax)
            return i + 3
        elif self.check_pattern(root_node, i,
                                QueryTok.COLON,
                                QueryTok.VERSION):
            # [:] [VERSION]
            vmin = Version('min')
            vmax = Version(root_node[i+1].tok)
            pkg_query.intersect_version_range(vmin, vmax)
            return i + 2
        elif self.check_pattern(root_node, i,
                                QueryTok.VERSION,
                                QueryTok.COLON):
            # [VERSION] [:]
            vmin = Version(root_node[i].tok)
            vmax = Version('max')
            pkg_query.intersect_version_range(vmin, vmax)
            return i + 2
        elif self.check_pattern(root_node, i,
                                QueryTok.COLON):
            # [:]
            vmin = Version('min')
            vmax = Version('max')
            pkg_query.intersect_version_range(vmin, vmax)
            return i + 1
        elif self.check_pattern(root_node, i,
                                QueryTok.VERSION):
            # [VERSION]
            vmin = Version(root_node[i].tok)
            vmax = Version(root_node[i].tok)
            pkg_query.intersect_version_range(vmin, vmax)
            return i + 1
        else:
            raise Exception("Invalid version range")

    def _is_dependency(self, root_node, i):
        return root_node[i].type == QueryTok.CARROT or \
               root_node[i].type == QueryTok.MODULO

    def _parse_dependency(self, root_node, i, pkg_query):
        dep_query = PackageQuery()
        i = self._parse_query(root_node, dep_query, i + 1,
                              in_modulo=True)
        pkg_query.dependencies[dep_query.cls] = dep_query
        dep_query.is_null = False
        return i

    def _parse_variant(self, root_node, i, pkg_query):
        vnode = root_node[i]
        pkg_query.variants[vnode.variant_key] = vnode.variant_val
        return i + 1
