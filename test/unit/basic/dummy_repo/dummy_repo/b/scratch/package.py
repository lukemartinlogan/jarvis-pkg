
from jarvis_pkg.basic.package import Package, install, uninstall
from jarvis_pkg.basic.package_query_list import PackageQueryList


class BPackage(Package):
    def define_class(self):
        self.classify('b')

    def define_versions(self):
        self.version('3.0.0')
        self.version('2.0.0')
        self.version('1.0.0')

    def define_variants(self):
        self.variant('a', default=1, choices=[1, 2, 3])
        self.variant('b', default=4, choices=[4, 5, 6])

    def define_dependencies(self):
        pass

    def get_dependencies(self, spec):
        return PackageQueryList()

    @install
    def phase1(self, spec):
        print(f"In {self.name} phase 1")

    @install
    def phase2(self, spec):
        print(f"In {self.name} phase 2")

    @uninstall
    def uphase1(self, spec):
        print(f"In {self.name} uphase 1")

    @uninstall
    def uphase2(self, spec):
        print(f"In {self.name} uphase 2")
