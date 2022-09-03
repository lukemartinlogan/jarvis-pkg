"""
Test the dependency graph
"""

from jarvis_pkg import *
from jarvis_pkg.package.package import Package


class A(Package):
    """
    Class A
    """
    def _define_versions(self):
        self.version('v2.0.0')
        self.version('v1.5.0')
        self.version('v1.0.0')

    def _define_deps(self):
        pass

    def _define_conflicts(self):
        pass


class B(Package):
    """
    Class B
    """

    def _define_versions(self):
        self.version('v2.0.0')
        self.version('v1.5.0')
        self.version('v1.0.0')
        self.variant('test', default='test1',
                     choices=['test1', 'test2', 'test3'],
                     msg='Test case to use')

    def _define_deps(self):
        a1 = A()
        a1.intersect_version_range('v0.0.0', 'v1.5.0')
        cond1 = B()
        cond1.set_variant('test', 'test1')

        a2 = A()
        a2.intersect_version_range('v1.5.0', 'v2.0.0')
        cond2 = B()
        cond2.set_variant('test', 'test2')

        a3 = A()
        a3.intersect_version_range('v0.0.0', 'v1.0.0')
        cond3 = B()
        cond3.set_variant('test', 'test3')

        self.depends_on(a1, when=[cond1])
        self.depends_on(a2, when=[cond2])
        self.depends_on(a3, when=[cond3])

    def _define_conflicts(self):
        pass


class C(Package):
    """
    Class C
    """
    def _define_versions(self):
        self.version('v2.0.0')
        self.version('v1.5.0')
        self.version('v1.0.0')

    def _define_deps(self):
        a = A()
        a.intersect_version_range('v1.5.0', 'v2.5.0')
        self.depends_on(a)

    def _define_conflicts(self):
        pass


class D(Package):
    """
    Class D
    """

    def _define_versions(self):
        self.version('v2.0.0')
        self.version('v1.5.0')
        self.version('v1.0.0')
        self.variant('test', default='test1',
                     choices=['test1', 'test2', 'test3'],
                     msg='Test case to use')

    def _define_deps(self):
        b1 = B()
        b1.set_variant('test', 'test1')
        cond1 = D()
        cond1.set_variant('test', 'test1')

        b2 = B()
        b2.set_variant('test', 'test2')
        cond2 = D()
        cond2.set_variant('test', 'test2')

        b3 = B()
        b3.set_variant('test', 'test3')
        cond3 = D()
        cond3.set_variant('test', 'test3')

        self.depends_on(A())
        self.depends_on(b1, when=[cond1])
        self.depends_on(b2, when=[cond2])
        self.depends_on(b3, when=[cond3])
        self.depends_on(C())

    def _define_conflicts(self):
        pass


def print_schema(schema):
    for pkg in schema:
        pkg.print()


def run_test():
    d = D()
    graph = DependencyGraph()
    schema = graph.build([d])
    for pkg in schema:
        if pkg.get_name() == 'A':
            if pkg.version_['version'] != Version('v1.5.0'):
                print(f"A has the wrong version: {pkg.version_['version']}")


run_test()
