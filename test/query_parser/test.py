
from jarvis_pkg.basic.query_parser import QueryParser

QueryParser('orangefs').parse().print()
QueryParser('orangefs@2.9.8').parse().print()
QueryParser('orangefs@2.9.8%gcc').parse().print()
QueryParser('jpkg_builtin.orangefs@2.9.8%gcc@9.2^gcc@9.2 v1=1 +v2 -v3 ~v4').parse().print()

try:
    QueryParser('orangefs@2.9.1%gcc@').parse().print()
except:
    print("orangefs@2.9.1%gcc@ failed")

try:
    QueryParser('orangefs@2.9.1%').parse().print()
except:
    print("orangefs@2.9.1% failed")

try:
    QueryParser('orangefs@').parse().print()
except:
    print("orangefs@ failed")