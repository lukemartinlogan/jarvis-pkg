
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

class AutotoolsPackage(Package):
    def define_deps(self):
        super().define_deps()
        self.depends_on('make')

    @phase('autotools')
    def autoreconf(self):
        cmd = f"autoreconf -ivf"
        ExecNode(cmd)

    @phase('autotools')
    def autogen(self):
        cmd = f"./autogen.sh"
        ExecNode(cmd, shell=True)

    @conf('autotools')
    def configure_args(self, spec, prefix):
        return []

    @phase('autotools')
    def configure(self, spec, prefix):
        args = [
            f"--prefix={prefix}",
            *self.configure_args(spec, prefix)
        ]
        args = " ".join(args)
        cmd = f"./configure {args}"
        ExecNode(cmd).Run()

    @phase('autotools')
    def build(self, spec, prefix):
        MakeNode().Run()

    @phase('autotools')
    def install(self, spec, prefix):
        MakeInstallNode().Run()