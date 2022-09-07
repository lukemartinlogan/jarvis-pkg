"""
Test the dependency graph
"""

from jarvis_pkg import *
from jarvis_pkg.package.package import Package


class A(Package):
    """
    Class A
    """
    def define_versions(self):
        self.version('v2.0.0')
        self.version('v1.5.0', install='m1')
        self.version('v1.2.0', install='m2')
        self.version('v1.0.0', install='m3')

    def define_deps(self):
        pass

    def define_conflicts(self):
        pass

    @phase()
    def method0(self, spec, prefix):
        print('here0')

    @phase('m1')
    def method1(self, spec, prefix):
        print('here1')

    @phase('m2')
    def method2(self, spec, prefix):
        print('here2')

    @phase('m3')
    def method3(self, spec, prefix):
        print('here3')


class B(Package):
    """
    Class B
    """

    def define_versions(self):
        self.version('v2.0.0')
        self.version('v1.5.0')
        self.version('v1.0.0')
        self.variant('test', default='test1',
                     choices=['test1', 'test2', 'test3'],
                     msg='Test case to use')

    def define_deps(self):
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

    def define_conflicts(self):
        pass


class C(Package):
    """
    Class C
    """
    def define_versions(self):
        self.version('v2.0.0')
        self.version('v1.5.0')
        self.version('v1.0.0')

    def define_deps(self):
        a = A()
        a.intersect_version_range('v1.5.0', 'v2.5.0')
        self.depends_on(a)

    def define_conflicts(self):
        pass


class D(Package):
    """
    Class D
    """

    def define_versions(self):
        self.version('v2.0.0')
        self.version('v1.5.0')
        self.version('v1.0.0')
        self.variant('test', default='test1',
                     choices=['test1', 'test2', 'test3'],
                     msg='Test case to use')

    def define_deps(self):
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

    def define_conflicts(self):
        pass

def run_test():
    d = D()
    graph = DependencyGraph().build([d])
    for pkg in graph.install_schema:
        if pkg.name == 'A':
            if pkg.version_['version'] != Version('v1.5.0'):
                print(f"A has the wrong version: {pkg.version_['version']}")
    graph.print()

run_test()
