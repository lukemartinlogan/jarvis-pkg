from jarvis_pkg.query.dependencies import DependencyGraph
import json

def pprint(deps):
    for dep in deps:
        print(dep)
    print()

deps = DependencyGraph("daos").Build()
pprint(deps)

deps = DependencyGraph("daos@2.9").Build()
pprint(deps)

deps = DependencyGraph("daos@2.9%gcc").Build()
pprint(deps)