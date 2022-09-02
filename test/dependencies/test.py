from jarvis_pkg import *
from jarvis_pkg.package.package import Package

class A(Package):
    def __init__(self):
        super().__init__()
        self.version('v2.0.0')
        self.version('v1.5.0')
        self.version('v1.0.0')

class B(Package):
    def __init__(self):
        super().__init__()
        self.version('v2.0.0')
        self.version('v1.5.0')
        self.version('v1.0.0')

        a = A()
        a.IntersectVersionRange('v0.0.0', 'v1.0.0')
        self.depends_on(a)

class C(Package):
    def __init__(self):
        super().__init__()
        self.version('v2.0.0')
        self.version('v1.5.0')
        self.version('v1.0.0')

        a = A()
        a.IntersectVersionRange('v1.5.0', 'v2.5.0')
        self.depends_on(a)

class D(Package):
    def __init__(self):
        super().__init__()
        self.version('v2.0.0')
        self.version('v1.5.0')
        self.version('v1.0.0')
        self.depends_on(A())
        self.depends_on(B())
        self.depends_on(C())

def print_schema(schema):
    for pkg in schema:
        pkg.print()

d = D()
graph = DependencyGraph()
schema = graph.Build([d])
#print_schema(schema)

for pkg in schema:
    if pkg.GetName() == 'A':
        if pkg.version_['version'] != Version('v1.5.0'):
            print('A has the wrong version')