
from jarvis_cd import *
from jarvis_pkg.package.make_package import MakeNode,MakeInstallNode
from jarvis_pkg.package.package import Package

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

    def __init__(self):
        self.phases = ['autoreconf', 'autogen', 'configure', 'build', 'install']
        self.depends_on('make')

    def autoreconf(self):
        cmd = f"autoreconf -ivf"
        ExecNode(cmd)

    def autogen(self):
        cmd = f"./autogen.sh"
        ExecNode(cmd, shell=True)

    def configure_args(self, spec, prefix):
        return []

    def configure(self, spec, prefix):
        args = [
            f"--prefix={prefix}",
            *self.configure_args(spec, prefix)
        ]
        args = " ".join(args)
        cmd = f"./configure {args}"
        ExecNode(cmd).Run()

    def build(self, spec, prefix):
        MakeNode().Run()

    def install(self, spec, prefix):
        MakeInstallNode().Run()