
from jarvis_pkg.package.package import Package

class CppPackage(Package):
    def define_deps(self):
        super().define_deps()
        self.depends_on('cpp_compiler')