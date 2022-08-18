class CPackage:
    def _c_deps(self):
        self.depends_on('c_compiler')