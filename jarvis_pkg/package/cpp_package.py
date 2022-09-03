
from jarvis_pkg.package.package import Package

class CppPackage(Package):
    def define_deps(self):
        self.depends_on('cpp_compiler')