from jarvis_pkg import *
import shutil
import os
from jarvis_pkg.package.package import Package

class Mpich(AutotoolsPackage):
    #Package class
    def define_versions(self):
        super().define_versions()
        self.set_class('mpi')
        self.version('3.2', url='http://www.mpich.org/static/downloads/3.2/mpich-3.2.tar.gz')
        self.variant('pvfs2', default=False, msg="Install the OrangeFS-specific mpich")
        self.depends_on('orangefs')

    @conf('autotools')
    def configure_args(self, spec, prefix):
        args = []
        if self.spec['orangefs']:
            args += [
                f"--enable-fast=O3",
                f"--enable-romio",
                f"--enable-shared",
                f"--with-pvfs2={spec['orangefs'].prefix}",
                f"--with-file-system=pvfs2"
            ]
        return args