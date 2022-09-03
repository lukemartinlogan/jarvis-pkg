
from jarvis_pkg import *
import shutil
import os

class Orangefs(AutotoolsPackage):
    def define_versions(self):
        self.version('2.9.8', url='http://download.orangefs.org/current/source/orangefs-2.9.8.tar.gz')

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