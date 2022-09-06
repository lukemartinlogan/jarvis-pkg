
from jarvis_pkg.basic.exception import Error,ErrorCode
from jarvis_pkg.basic.jpkg_manager import JpkgManager
import re

"""
Syntax: pkg_namespace.pkg_name@vmin:vmax%build_dep@vmin:max^run_dep@vmin:vmax v1=val +v2 -v3 ~v4 ...
"""

class QueryParser:
    def __init__(self, query_str, pkg_name=None):
        self.query_str = query_str
        self.pkg_name=pkg_name
        self.pkgs = []
        self.jpkg_manager = JpkgManager().get_instance()

    @staticmethod
    def _is_variant(tok):
        seps = {'+', '-', '~', '='}
        for sep in seps:
            if sep in tok:
                return True
        return False

    @staticmethod
    def _remove_whitespace(pkg_query):
        toks = re.split('([@%\+\-~:=^])|([ ])+', pkg_query)
        return [tok for tok in toks if tok is not None]

    def _parse_pkg_id(self, pkg_dep, pkg_id):
        if len(pkg_id) == 0:
            pkg_id = self.pkg_name
        pkg_id_tuple = pkg_id.split('.')
        if len(pkg_id_tuple) == 1:
            pkg_namespace = None
            pkg_name = pkg_id_tuple[0]
        elif len(pkg_id_tuple) == 2:
            pkg_namespace = pkg_id_tuple[0]
            pkg_name = pkg_id_tuple[1]
        else:
            raise Error(ErrorCode.MALFORMED_PKG_NAME_QUERY).format(pkg_dep)
        return pkg_namespace,pkg_name

    @staticmethod
    def _parse_pkg_version_range(pkg_dep, pkg_vrange):
        if pkg_vrange is None:
            return 'min','max'
        pkg_vrange = pkg_vrange.split(':')
        if len(pkg_vrange) == 1:
            min = pkg_vrange[0]
            max = min
        elif len(pkg_vrange) == 2:
            min = pkg_vrange[0]
            max = pkg_vrange[1]
        else:
            raise Error(ErrorCode.MALFORMED_VERSION_QUERY).format(pkg_dep)
        if len(min) == 0:
            min = 'min'
        if len(max) == 0:
            max = 'max'
        return min,max

    def _parse_pkg_id_version(self, pkg_dep):
        toks = pkg_dep.split('@')
        if len(toks) == 1:
            return toks[0], None
        if len(toks) > 2:
            raise Error(ErrorCode.MULTIPLE_VERSIONS_IN_QUERY).format(pkg_dep)
        return toks

    def _parse_pkg_dep(self, pkg_dep):
        pkg_id, pkg_vrange = self._parse_pkg_id_version(pkg_dep)
        pkg_namespace,pkg_name = self._parse_pkg_id(pkg_dep, pkg_id)
        min,max = self._parse_pkg_version_range(pkg_dep, pkg_vrange)
        pkg_classes = self.jpkg_manager.find_imports(pkg_namespace, pkg_name)
        if len(pkg_classes) == 0:
            raise Error(ErrorCode.UNKOWN_PACKAGE).format(pkg_name)
        pkgs = []
        for pkg_class in pkg_classes:
            pkg = pkg_class()
            pkg.set_namespace(pkg_namespace)
            pkg.intersect_version_range(min,max)
            pkgs.append(pkg)
        return pkgs

    @staticmethod
    def _is_dep(tok):
        return '%' in tok or '^' in tok

    def _split_pkg_deps(self, pkg_query):
        toks = [tok for tok in re.split('([%^])', pkg_query) if tok is not None]
        build_deps = []
        run_deps = []
        if not self._is_dep(toks[0]):
            root_pkg_query = toks[0]
            toks = toks[1:]
        else:
            root_pkg_query = self.pkg_name
        it = iter(toks)
        for dep_type,pkg_dep in zip(it,it):
            if dep_type == '%':
                build_deps.append(pkg_dep)
            else:
                run_deps.append(pkg_dep)
        return root_pkg_query, build_deps, run_deps

    @staticmethod
    def _parse_variant(root_pkg, variant):
        if '=' in variant:
            toks = variant.split('=')
            if len(toks) != 2:
                raise Error(ErrorCode.MALFORMED_VARIANT).format(root_pkg.get_name(), variant)
            key = toks[0]
            val = toks[1]
        elif '+' in variant:
            toks = variant.split('+')
            if len(toks) != 2:
                raise Error(ErrorCode.MALFORMED_VARIANT).format(root_pkg.get_name(), variant)
            key = toks[1]
            val = True
        elif '-' in variant or '~' in variant:
            if '-' in variant:
                toks = variant.split('-')
            else:
                toks = variant.split('~')
            if len(toks) != 2:
                raise Error(ErrorCode.MALFORMED_VARIANT).format(root_pkg.get_name(), variant)
            key = toks[1]
            val = False
        else:
            raise Error(ErrorCode.MALFORMED_VARIANT).format(root_pkg.get_name(), variant)
        return key,val

    def _parse_pkg_query(self, pkg_query, variants):
        root_pkg_query,build_deps,run_deps = self._split_pkg_deps(pkg_query)
        root_pkgs = self._parse_pkg_dep(root_pkg_query)
        build_deps = [self._parse_pkg_dep(pkg_dep) for pkg_dep in build_deps]
        run_deps = [self._parse_pkg_dep(pkg_dep) for pkg_dep in run_deps]
        variants = [self._parse_variant(pkg_query, v) for v in variants]
        for root_pkg in root_pkgs:
            for pkg_dep in build_deps:
                root_pkg.depends_on(pkg_dep, time='build')
            for pkg_dep in run_deps:
                root_pkg.depends_on(pkg_dep, time='run')
            for (key,value) in variants:
                root_pkg.set_variant(key,value)
        return root_pkgs

    def _split_packages(self, query_str):
        query_str = "".join(self._remove_whitespace(query_str))
        toks = query_str.split()
        pkgs = []
        for tok in toks:
            if self._is_variant(tok):
                if len(pkgs) == 0:
                    pkgs.append((self.pkg_name, []))
                pkgs[-1][1].append(tok)
            else:
                pkgs.append((tok, []))
        return pkgs

    def parse(self):
        pkg_queries = self._split_packages(self.query_str)
        for (pkg_query,variants) in pkg_queries:
            self.pkgs += self._parse_pkg_query(pkg_query, variants)
        return self

    def print(self):
        for pkg in self.pkgs:
            pkg.print()
            print()
