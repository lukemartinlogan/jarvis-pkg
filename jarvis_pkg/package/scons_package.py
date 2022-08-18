from jarvis_pkg.package.package import Package
from jarvis_cd import *

class SConsPackage(Package):
    def __init__(self):
        super().__init__()
        self.phases = ['build', 'install']
        self.depends_on('scons')

    def build(self, spec, prefix):
        scons_args = " ".join(self.build_args(spec, prefix))
        cmd = f"scons {scons_args}"
        ExecNode(cmd).Run()

    def install(self, spec, prefix):
        ExecNode("scons install").Run()

    def build_args(self):
        return []