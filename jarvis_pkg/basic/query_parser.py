
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
        self.jpkg_manager = JpkgManager().GetInstance()

    def IsVariant(self, tok):
        seps = {'+', '-', '~', '='}
        for sep in seps:
            if sep in tok:
                return True
        return False

    def RemoveWhitespace(self, pkg_query):
        toks = re.split('([@%\+\-~:=^])|([ ])+', pkg_query)
        return [tok for tok in toks if tok is not None]

    def ParseFindPkg(self, pkg_dep, pkg_find):
        if len(pkg_find) == 0:
            pkg_find = self.pkg_name
        pkg_find_tuple = pkg_find.split('.')
        if len(pkg_find_tuple) == 1:
            pkg_namespace = None
            pkg_name = pkg_find_tuple[0]
        elif len(pkg_find_tuple) == 2:
            pkg_namespace = pkg_find_tuple[0]
            pkg_name = pkg_find_tuple[1]
        else:
            raise Error(ErrorCode.MALFORMED_PKG_NAME_QUERY).format(pkg_dep)
        return pkg_namespace,pkg_name

    def ParsePkgVersionRange(self, pkg_dep, pkg_vrange):
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

    def ParsePkgDep(self, pkg_dep):
        pkg_find,pkg_vrange = pkg_dep.split('@')
        pkg_namespace,pkg_name = self.ParseFindPkg(pkg_dep, pkg_find)
        min,max = self.ParsePkgVersionRange(pkg_dep, pkg_vrange)

        pkg_class = self.jpkg_manager._PackageImport(pkg_name)
        if pkg_class is None:
            raise Error(ErrorCode.UNKOWN_PACKAGE).format(pkg_name)
        pkg = pkg_class()
        pkg.IntersectVersionRange(min,max)
        return pkg

    def IsDep(self, tok):
        return '%' in tok or '^' in tok

    def SplitPkgDeps(self, pkg_query):
        toks = [tok for tok in re.split('([%^])', pkg_query) if tok is not None]
        build_deps = []
        run_deps = []
        if not self.IsDep(toks[0]):
            root_pkg = toks[0]
            toks = toks[1:]
        else:
            root_pkg = self.pkg_name
        for dep_type,pkg_dep in zip(toks[1:-1], toks[2:]):
            if dep_type == '%':
                build_deps.append(pkg_dep)
            else:
                run_deps.append(pkg_dep)
        return root_pkg, build_deps, run_deps

    def ParseVariant(self, root_pkg, variant):
        if '=' in variant:
            toks = variant.split('=')
            if len(toks) != 2:
                raise Error(ErrorCode.MALFORMED_VARIANT).format(root_pkg.GetName(), variant)
            key = toks[0]
            val = toks[1]
        elif '+' in variant:
            toks = variant.split('+')
            if len(toks) != 2:
                raise Error(ErrorCode.MALFORMED_VARIANT).format(root_pkg.GetName(), variant)
            key = toks[1]
            val = True
        elif '-' in variant or '~' in variant:
            toks = variant.split('-')
            if len(toks) != 2:
                raise Error(ErrorCode.MALFORMED_VARIANT).format(root_pkg.GetName(), variant)
            key = toks[1]
            val = False
        else:
            raise Error(ErrorCode.MALFORMED_VARIANT).format(root_pkg.GetName(), variant)
        return key,val

    def ParsePkgQuery(self, pkg_query, variants):
        root_pkg,build_deps,run_deps = self.SplitPkgDeps(pkg_query)
        root_pkg = self.ParsePkgDep(root_pkg)
        for pkg_dep in build_deps:
            root_pkg.AddBuildDep(self.ParsePkgDep(pkg_dep))
        for pkg_dep in run_deps:
            root_pkg.AddRunDep(self.ParsePkgDep(pkg_dep))
        for variant in variants:
            key,value = self.ParseVariant(root_pkg, variant)
            root_pkg.SetVariant(key,value)
        return root_pkg

    def SplitPackages(self, query_str):
        query_str = "".join(self.RemoveWhitespace(query_str))
        toks = query_str.split()
        pkgs = []
        for tok in toks:
            if self.IsVariant(tok):
                if len(pkgs) == 0:
                    pkgs.append([''])
                pkgs[-1].append(tok)
            else:
                pkgs.append([tok])
        return pkgs

    def Parse(self):
        pkg_queries = self.SplitPackages(self.query_str)
        for (pkg_query,variants) in pkg_queries:
            self.pkgs.append(self.ParsePkgQuery(pkg_query, variants))
        return self

    def print(self):
        for pkg in self.pkgs:
            pkg.print()
            print()



