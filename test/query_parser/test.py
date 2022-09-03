
from jarvis_pkg.basic.query_parser import QueryParser

QueryParser('orangefs@2.9.1%gcc@9.2^gcc@9.2 variant=1').parse().print()
exit(1)
QueryParser('orangefs').parse().print()
QueryParser('orangefs@2.9.1').parse().print()
QueryParser('orangefs@2.9.1%gcc').parse().print()


try:
    QueryParser('orangefs@2.9.1%gcc@').parse()
except:
    pass

try:
    QueryParser('orangefs@2.9.1%').parse()
except:
    pass

try:
    QueryParser('orangefs@').parse()
except:
    pass