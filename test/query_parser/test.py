
from jarvis_pkg.basic.query_parser import QueryParser

QueryParser('orangefs@2.9.1%gcc@9.2 variant=1').Parse().print()
QueryParser('orangefs').Parse().print()
QueryParser('orangefs@2.9.1').Parse().print()
QueryParser('orangefs@2.9.1%gcc').Parse().print()


try:
    QueryParser('orangefs@2.9.1%gcc@').Parse()
except:
    pass

try:
    QueryParser('orangefs@2.9.1%').Parse()
except:
    pass

try:
    QueryParser('orangefs@').Parse()
except:
    pass