
from jarvis_pkg.basic.exception import Error,ErrorCode
import re

class QueryParser:
    def _is_sep(self, tok):
        seps = {'@', '%', '+', '-', '~', ':', '='}
        return tok in seps

    def _interpret_tok(self, pkg_spec, toks, tok, i):
        if i == 0 or i + 1 >= len(toks):
            start = i-3 if i > 3 else 0
            end = i+1 if i+1 < len(toks) else len(toks)
            " ".join(toks[i-3:i+1])
            raise Error(ErrorCode.MALFORMED_QUERY).format(toks[start:end])
        next_tok = toks[i+1]
        if tok == '@':
            if pkg_spec.GetVersionRange() is None:
                pkg_spec.SetVersionRange(next_tok)
            else:
                pkg_spec.GetBuildDependency(self.last_build_dep).SetVersionRange(next_tok)
        if tok == '%':
            self.last_build_dep = next_tok
            pkg_spec.AddBuildDependency(PackageSpec(next_tok))
        if tok == '+':
            pkg_spec.SetVariant(next_tok, True)
        if tok == '-':
            pkg_spec.SetVariant(next_tok, False)
        if tok == '~':
            pkg_spec.SetVariant(next_tok, False)
        #if tok == '='
        #if tok == ':'

    def Parse(self, query_string):
        if query_string is None:
            return None
        pkg_queries = []
        pkg_spec_strs = query_string.split('^')
        self.last_build_dep = None
        for pkg_spec_str in pkg_spec_strs:
            toks = re.split('([@=%\+\-\~]|[ ]+)', pkg_spec_str)
            toks = [tok for tok in toks if len(tok) and tok[0] != ' ']
            if self._is_sep(toks[0]):
                pkg_spec = PackageSpec(toks[0])
            else:
                pkg_spec = PackageSpec()
            for i,tok in enumerate(toks):
                if self._is_sep(tok):
                    self._interpret_tok(pkg_spec, toks, tok, i)
            pkg_queries.append(pkg_spec)
        return pkg_queries
