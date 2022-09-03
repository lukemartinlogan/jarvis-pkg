from jarvis_pkg.package.package import Package

class CPackage(Package):
    def define_deps(self):
        self.depends_on('c_compiler')
