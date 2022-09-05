from jarvis_pkg import *
import shutil
import os

class Gcc(AptPackage,YumPackage):
    def define_versions(self):
        super().define_versions()
        self.version('2.0',
                distro=['debian', 'ubuntu', 'linux-mint'],
                pkg_list=['gcc', 'g++', 'gfortran', 'build-essential'],
                install='apt')
        self.version('2.0',
                distro=['centos7', 'centos8'],
                pkg_list=['gcc', 'g++', 'gfortran'],
                install='yum')