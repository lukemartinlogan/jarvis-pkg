from jarvis_pkg import *
import shutil
import os
from jarvis_pkg.package.package import Package

class Mpich(AutotoolsPackage):
    #Package class
    package_class('mpi')

    #Versions
    version('3.2', url='http://www.mpich.org/static/downloads/3.2/mpich-3.2.tar.gz')

    variant('pvfs2', default=False, message="Install the OrangeFS-specific mpich")

    depends_on('orangefs')

    def configure_args(self, spec):
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