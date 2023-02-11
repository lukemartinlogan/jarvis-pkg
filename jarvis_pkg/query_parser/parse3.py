"""
Create the actual PackageQuery structures
"""
from jarvis_pkg.basic.package import PackageQuery
from jarvis_pkg.basic.jpkg_manifest_manager import JpkgManifestManager
from jarvis_pkg.basic.version import Version
from .parse_tree import ParseTree
from .query_node import QueryNode, QueryTok


class QueryParser3(ParseTree):
    def __init__(self, tree):
        self.root_node = tree.root_node
        self.queries = []
        self.manifest = JpkgManifestManager.get_instance()

    def parse(self):
        self._parse(self.root_node)

    def _parse(self, root_node, pkg_query=None):
        i = 0
        if pkg_query is not None:
            i = self._parse_name(root_node, 0, pkg_query)
        while i < len(root_node):
            if root_node[i].type == QueryTok.ROOT:
                if pkg_query is None:
                    query = PackageQuery()
                    self.queries.append(query)
                    self._parse(root_node[i], query)
                else:
                    raise Exception("Package query followed was not "
                                    "preceeded by %")
            elif root_node[i].type == QueryTok.AT:
                self._parse_version_range(root_node, i, pkg_query)
            elif root_node[i].type == QueryTok.MODULO:
                self._parse_dependency(root_node, i, pkg_query)
            elif root_node[i].type == QueryTok.VARIANT:
                self._parse_variant(root_node, i, pkg_query)
            else:
                raise

    def _parse_name(self, root_node, i, pkg_query):
        name_toks = root_node.tok.split('.')
        if len(name_toks) == 3:
            # [NAME].[NAME].[NAME]
            pkg_query.repo = name_toks[0]
            pkg_query.name = name_toks[1]
            pkg_query.cls = name_toks[2]
            return i + 3
        if len(name_toks) == 2:
            # [NAME].[NAME]
            pkg_query.name = name_toks[0]
            pkg_query.cls = self.manifest.get_class(name_toks[1])
            if pkg_query.cls != name_toks[1]:
                pkg_query.name = name_toks[1]
            return i + 2
        elif len(name_toks) == 1:
            # [NAME]
            pkg_query.cls = self.manifest.get_class(name_toks[0])
            if pkg_query.cls != name_toks[0]:
                pkg_query.name = name_toks[0]
            return i + 1
        return i

    def _parse_version_range(self, root_node, i, pkg_query):
        if self.check_pattern(root_node, i,
                              QueryTok.VERSION, QueryTok.COLON,
                              QueryTok.VERSION):
            # [VERSION] [:] [VERSION]
            vmin = Version(root_node[i].tok)
            vmax = Version(root_node[i+2].tok)
            pkg_query.intersect_version_range(vmin, vmax)
            return i + 2
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

    def _parse_dependency(self, root_node, i, pkg_query):
        if self.check_pattern(root_node, i,
                              QueryTok.MODULO, QueryTok.ROOT):
            dep_query = PackageQuery()
            self._parse(root_node[i + 1], dep_query)
            pkg_query.dependencies[dep_query.cls] = dep_query
            dep_query.is_null = False
            return i + 2
        raise Exception("Couldn't parse dependency")

    def _parse_variant(self, root_node, i, pkg_query):
        vnode = root_node[i]
        pkg_query[vnode.variant_key] = vnode.variant_val
