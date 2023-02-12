
from jarvis_pkg.basic.package import Package
from jarvis_pkg.basic.package_query_list import PackageQueryList


class APackage(Package):
    def define_class(self):
        self.classify('a')

    def define_versions(self):
        self.version('3.1.0')
        self.version('2.1.0')
        self.version('1.1.0')

    def define_variants(self):
        self.variant('a', default=1, choices=[1, 2, 3])
        self.variant('b', default=4, choices=[4, 5, 6])

    def define_dependencies(self):
        pass

    def get_dependencies(self, spec):
        return PackageQueryList()
