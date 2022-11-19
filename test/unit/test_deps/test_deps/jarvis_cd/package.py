from jarvis_pkg.package.package import *
from jarvis_pkg.basic.package_id import PackageId
from jarvis_pkg.basic.package_query import PackageQuery
from jarvis_pkg.package.pip_package import PipPackage


class JarvisCdPackage(PipPackage):
    def define_versions(self):
        self.version("v0.1.0", git="https://github.com/lukemartinlogan/jarvis-cd", branch="development")

    def define_variants(self):
        pass

    def define_dependencies(self):
        pass

    def define_conflicts(self):
        pass

    @conf(install="pip")
    def pip_conf(self):
        return
