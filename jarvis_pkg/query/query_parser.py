
from jarvis_pkg.query.package_query import PackageQuery
from jarvis_pkg.query.version import Version
from jarvis_pkg.basic.exception import Error,ErrorCode
import re

"""
pkg_name@version%compiler variant=a variant=b +variant ^ dep_pkg_name...

[text]@[text]%[text]@[text]

jpkg install daos
------------------
[
- name: daos
  version_range: null
  variants: {}
  build_deps: []
]
-------------------

jpkg install daos@2.1%gcc@9.2 +optimize ^ mpich@3.2 +pvfs2
---------------
[
- name: daos
  version_range: (2.1.0, 2.1.9)
  variants: {
    optimize: true
  }
  build_deps: [
    - name: gcc
      version_min: 9.2.0
      version_max: 9.2.9
  ]
- name: orangefs-mpich
  version_range: (3.2.0, 3.2.9)
  build_deps: null
  variants: {
    pvfs2: true
  }
]
---------------
"""

class QueryParser:
    def _is_sep(self, tok):
        seps = {'@', '%', '+', '-', '~'}
        return tok in seps

    def _interpret_tok(self, pkg_query, toks, tok, i):
        if i == 0 or i + 1 >= len(toks):
            start = i-3 if i > 3 else 0
            end = i+1 if i+1 < len(toks) else len(toks)
            " ".join(toks[i-3:i+1])
            raise Error(ErrorCode.MALFORMED_QUERY).format(toks[start:end])
        next_tok = toks[i+1]
        if tok == '@':
            if pkg_query.GetVersionRange() is None:
                pkg_query.SetVersion(next_tok)
            else:
                pkg_query.GetBuildDependency(self.last_build_dep).SetVersion(next_tok)
        if tok == '%':
            self.last_build_dep = next_tok
            pkg_query.AddBuildDependency(PackageQuery(next_tok))
        if tok == '+':
            pkg_query.SetVariant(next_tok, True)
        if tok == '-':
            pkg_query.SetVariant(next_tok, False)
        if tok == '~':
            pkg_query.SetVariant(next_tok, False)
        #if tok == '='

    def Parse(self, query_string, require_pkg_name=True):
        if query_string is None:
            return None
        pkg_queries = []
        pkg_query_strs = query_string.split('^')
        self.last_build_dep = None
        for pkg_query_str in pkg_query_strs:
            toks = re.split('([@=%\+\-\~]|[ ]+)', pkg_query_str)
            toks = [tok for tok in toks if len(tok) and tok[0] != ' ']
            if require_pkg_name:
                pkg_query = PackageQuery(toks[0])
            else:
                pkg_query = PackageQuery()
            for i,tok in enumerate(toks):
                if self._is_sep(tok):
                    self._interpret_tok(pkg_query, toks, tok, i)
            pkg_queries.append(pkg_query)
        return pkg_queries
