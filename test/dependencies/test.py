from jarvis_pkg import *
from jarvis_pkg.package.package import Package

class A(Package):
    def _DefineVersions(self):
        self.version('v2.0.0')
        self.version('v1.5.0')
        self.version('v1.0.0')

    def _DefineDeps(self):
        pass

    def _DefineConflicts(self):
        pass

class B(Package):
    def _DefineVersions(self):
        self.version('v2.0.0')
        self.version('v1.5.0')
        self.version('v1.0.0')
        self.variant('test', default='test1', choices=['test1', 'test2', 'test3'], msg='Test case to use')

    def _DefineDeps(self):
        a1 = A()
        a1.IntersectVersionRange('v0.0.0', 'v1.5.0')
        cond1 = B()
        cond1.SetVariant('test', 'test1')

        a2 = A()
        a2.IntersectVersionRange('v1.5.0', 'v2.0.0')
        cond2 = B()
        cond2.SetVariant('test', 'test2')

        a3 = A()
        a3.IntersectVersionRange('v0.0.0', 'v1.0.0')
        cond3 = B()
        cond3.SetVariant('test', 'test3')

        self.depends_on(a1, when=[cond1])
        self.depends_on(a2, when=[cond2])
        self.depends_on(a3, when=[cond3])

    def _DefineConflicts(self):
        pass

class C(Package):
    def _DefineVersions(self):
        self.version('v2.0.0')
        self.version('v1.5.0')
        self.version('v1.0.0')

    def _DefineDeps(self):
        a = A()
        a.IntersectVersionRange('v1.5.0', 'v2.5.0')
        self.depends_on(a)

    def _DefineConflicts(self):
        pass

class D(Package):
    def _DefineVersions(self):
        self.version('v2.0.0')
        self.version('v1.5.0')
        self.version('v1.0.0')
        self.variant('test', default='test1', choices=['test1', 'test2', 'test3'], msg='Test case to use')

    def _DefineDeps(self):
        b1 = B()
        b1.SetVariant('test', 'test1')
        cond1 = D()
        cond1.SetVariant('test', 'test1')

        b2 = B()
        b2.SetVariant('test', 'test2')
        cond2 = D()
        cond2.SetVariant('test', 'test2')

        b3 = B()
        b3.SetVariant('test', 'test3')
        cond3 = D()
        cond3.SetVariant('test', 'test3')

        self.depends_on(A())
        self.depends_on(b1, when=[cond1])
        self.depends_on(b2, when=[cond2])
        self.depends_on(b3, when=[cond3])
        self.depends_on(C())

    def _DefineConflicts(self):
        pass

def print_schema(schema):
    for pkg in schema:
        pkg.print()

d = D()
graph = DependencyGraph()
schema = graph.Build([d])
for pkg in schema:
    if pkg.GetName() == 'A':
        if pkg.version_['version'] != Version('v1.5.0'):
            print(f"A has the wrong version: {pkg.version_['version']}")