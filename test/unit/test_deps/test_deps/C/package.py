from jarvis_pkg.package.package import Package
from jarvis_pkg.basic.package_id import PackageId
from jarvis_pkg.basic.package_query import PackageQuery

class CPackage(Package):
    def define_versions(self):
        self.version("v3.0.0")
        self.version("v2.5.0")
        self.version("v2.4.0")
        self.version("v2.2.0")

    def define_variants(self):
        self.variant("v1", bool, default=False)
        self.variant("v2", bool, default=False)
        self.variant("v3", bool, default=False)

    def define_dependencies(self):
        Aquery = PackageQuery()
        Aquery.pkg_id = PackageId(None, None, 'A')
        self.depends_on(Aquery)

        Bquery = PackageQuery()
        Bquery.pkg_id = PackageId(None, None, 'B')
        self.depends_on(Bquery)

    def define_conflicts(self):
        pass