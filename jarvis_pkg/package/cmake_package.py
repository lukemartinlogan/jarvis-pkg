
from jarvis_cd import *
from jarvis_pkg.package.make_package import MakeNode,MakeInstallNode
from jarvis_pkg.package.package import *

class CMakeNode(ExecNode):
    def __init__(self, args=[], path=None):
        build_args = " ".join(args)
        cmds = [
            f"cd {path}" if path is not None else None,
            f"mkdir build",
            f"cd build",
            f"cmake ../ {build_args}"
        ]
        super().__init__(cmds, shell=True)

class CMakePackage(Package):
    def define_versions(self):
        super().define_versions()
        self.depends_on('cmake')

    @conf('cmake')
    def cmake_args(self, spec, prefix):
        return []

    @phase('cmake')
    def cmake(self, spec, prefix):
        args = [
            f"-DCMAKE_INSTALL_PREFIX={prefix}",
            *self.cmake_args(spec, prefix)
        ]
        CMakeNode(args=args).Run()

    @phase('cmake')
    def build(self, spec, prefix):
        MakeNode(jobs=8).Run()

    @phase('cmake')
    def install(self, spec, prefix):
        MakeInstallNode().Run()