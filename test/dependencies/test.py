from jarvis_pkg import *
from jarvis_pkg.package.package import Package

class A(Package):
    @staticmethod
    def _Init(pkg):
        pkg.version('v2.0.0')
        pkg.version('v1.5.0')
        pkg.version('v1.0.0')

class B(Package):
    @staticmethod
    def _Init(pkg):
        pkg.version('v2.0.0')
        pkg.version('v1.5.0')
        pkg.version('v1.0.0')

        pkg.variant('test', default='test1', choices=['test1', 'test2', 'test3'], msg='Test case to use')

    def _InitDynamic(self):
        a1 = A()
        a1.IntersectVersionRange('v0.0.0', 'v1.5.0')
        cond1 = self.RecurseCopy()
        cond1.SetVariant('test', 'test1')

        a2 = A()
        a2.IntersectVersionRange('v1.5.0', 'v2.0.0')
        cond2 = self.RecurseCopy()
        cond2.SetVariant('test', 'test2')

        a3 = A()
        a3.IntersectVersionRange('v0.0.0', 'v1.0.0')
        cond3 = self.RecurseCopy()
        cond3.SetVariant('test', 'test3')

        self.depends_on(a1, when=[cond1])
        self.depends_on(a2, when=[cond2])
        self.depends_on(a3, when=[cond3])

class C(Package):
    @staticmethod
    def _Init(pkg):
        pkg.version('v2.0.0')
        pkg.version('v1.5.0')
        pkg.version('v1.0.0')

    def _InitDynamic(self):
        a = A()
        a.IntersectVersionRange('v1.5.0', 'v2.5.0')
        self.depends_on(a)

class D(Package):
    @staticmethod
    def _Init(pkg):
        pkg.version('v2.0.0')
        pkg.version('v1.5.0')
        pkg.version('v1.0.0')

        pkg.variant('test', default='test1', choices=['test1', 'test2', 'test3'], msg='Test case to use')

    def _InitDynamic(self):
        b1 = B()
        cond1 = self.RecurseCopy()
        cond1.SetVariant('test', 'test1')

        b2 = B()
        cond2 = self.RecurseCopy()
        cond2.SetVariant('test', 'test2')

        b3 = B()
        cond3 = self.RecurseCopy()
        cond3.SetVariant('test', 'test3')

        self.depends_on(A())
        self.depends_on(b1, when=[cond1])
        self.depends_on(b2, when=[cond2])
        self.depends_on(b3, when=[cond3])
        self.depends_on(C())

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