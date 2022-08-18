from jarvis_pkg.query.dependencies import DependencyGraph

deps = DependencyGraph("daos").Build()
print(deps)