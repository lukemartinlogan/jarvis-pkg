from jarvis_pkg import *
import shutil
import os

class Gcc(Package):
    def define_versions(self):
        self.version('2.0',
                distro=['debian', 'ubuntu', 'linux-mint'],
                pkg_list=['gcc', 'g++', 'gfortran', 'build-essential'],
                installer='apt')
        self.version('2.0',
                distro=['centos7', 'centos8'],
                pkg_list=['gcc', 'g++', 'gfortran'],
                installer='yum')