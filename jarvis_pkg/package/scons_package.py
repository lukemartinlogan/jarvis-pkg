
from jarvis_cd import *

class SConsPackage(Package):
    phases = ['build', 'install']
    depends_on('scons')

    def build(self, spec, prefix):
        cmd = f"scons {*self.build_args(spec, prefix)}"
        ExecNode(cmd).Run()

    def install(self, spec, prefix):
        ExecNode("scons install").Run()

    def build_args(self):
        return []