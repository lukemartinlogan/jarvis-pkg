
from jarvis_pkg.basic.query_parser import QueryParser

print(QueryParser().Parse('orangefs'))
print(QueryParser().Parse('orangefs@2.9.1'))
print(QueryParser().Parse('orangefs@2.9.1%gcc'))
print(QueryParser().Parse('orangefs@2.9.1%gcc@9.2'))

try:
    print(QueryParser().Parse('orangefs@2.9.1%gcc@'))
except:
    pass

try:
    print(QueryParser().Parse('orangefs@2.9.1%'))
except:
    pass

try:
    print(QueryParser().Parse('orangefs@'))
except:
    pass