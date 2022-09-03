
from jarvis_cd import *
from jarvis_pkg.package.package import Package


class MakeNode(ExecNode):
    def __init__(self, path=None, jobs=8, *args):
        args = " ".join(args)
        cmds = [
            f"cd {path}" if path is not None else None,
            f"make -j{jobs} {args}"
        ]
        super().__init__(cmds, shell=True)

class MakeInstallNode(ExecNode):
    def __init__(self, path=None):
        cmds = [
            f"cd {path}" if path is not None else None,
            f"make install"
        ]
        super().__init__(cmds, shell=True)

class MakePackage(Package):
    def define_versions(self):
        self.phases = ['build', 'install']

    def define_deps(self):
        self.depends_on('make')

    def build(self, spec, prefix):
        MakeNode().Run()

    def install(self, spec, prefix):
        MakeInstallNode().Run()