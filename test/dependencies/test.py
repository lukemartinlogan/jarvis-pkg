from jarvis_pkg.query.dependencies import DependencyGraph

deps = DependencyGraph("daos").Build()
print(deps)

deps = DependencyGraph("daos@2.9").Build()
print(deps)

deps = DependencyGraph("daos@2.9%gcc").Build()
print(deps)