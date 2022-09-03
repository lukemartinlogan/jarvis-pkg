from jarvis_pkg import *
import shutil
import os

class Io500(Package):
    #Versions
    def define_versions(self):
        self.version('isc22', git='https://github.com/IO500/io500.git', branch='io500-isc22')
        self.variant('daos', default=True, msg="Install the DAOS-specific IO500")
        self.phases = ['prepare', 'install']

    def prepare(self, spec, prefix):
        self.env.set('MY_DAOS_INSTALL_PATH', spec['daos'].prefix)
        self.env.set('MY_MFU_INSTALL_PATH', spec['mfu'].prefix)
        if spec.variants['daos']:
            self.patch('daos')
        ExecNode('./prepare.sh', shell=True).Run()

    def install(self, spec, prefix):
        CopyNode('bin', prefix).run()
        CopyNode('io500', os.path.join(prefix, 'bin')).Run()