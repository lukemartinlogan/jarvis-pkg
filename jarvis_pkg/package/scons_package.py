from jarvis_pkg.package.package import *
from jarvis_cd import *

class SConsPackage(Package):
    def define_versions(self):
        super().define_versions()
        self.phases = ['build', 'install']

    def define_deps(self):
        super().define_deps()
        self.depends_on('scons')

    @conf('scons')
    def build_args(self, spec, prefix):
        pass

    @phase('scons')
    def build(self, spec, prefix):
        scons_args = " ".join(self.build_args(spec, prefix))
        cmd = f"scons {scons_args}"
        ExecNode(cmd).Run()

    @phase('scons')
    def install(self, spec, prefix):
        ExecNode("scons install").Run()