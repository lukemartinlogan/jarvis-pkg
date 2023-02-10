
from jarvis_pkg.basic.package import Package
from jarvis_pkg.basic.package_query import PackageQuery


class CPackage(Package):
    def define_class(self):
        self.classify('C')

    def define_versions(self):
        self.version('3.0.0')
        self.version('2.0.0')
        self.version('1.0.0')

    def define_variants(self):
        self.variant('a', default=1, choices=[1, 2, 3])
        self.variant('b', default=4, choices=[4, 5, 6])

    def define_dependencies(self):
        self.depends_on('A')
        self.depends_on('B')

    def get_dependencies(self, spec):
        deps = []
        if not spec['A'].matches(PackageQuery("@3.0.0")):
            deps.append(PackageQuery("@3.0.0"))
        else:
            deps.append(PackageQuery("@2.0.0"))
        deps.append(PackageQuery("B"))
        return deps
