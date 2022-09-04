from jarvis_pkg.package.package import Package

class CPackage(Package):
    def define_deps(self):
        super().define_deps()
        self.depends_on('c_compiler')
