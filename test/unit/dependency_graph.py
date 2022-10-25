from jarvis_pkg.basic.package_query import PackageQuery
from jarvis_pkg.basic.package_id import PackageId
from jarvis_pkg.dependency_graph.dependency_graph import DependencyGraph

graph = DependencyGraph()
query = PackageQuery()
query.pkg_id = PackageId(None, None, 'C')
pkg_list = graph.build([query])
print(pkg_list)
