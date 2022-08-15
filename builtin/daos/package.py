
from jarvis_pkg import *
import shutil
import os

class Daos(SConsPackage,CPackage,CppPackage):
    #Distro package managers
    version('2.0',
            distro='centos8',
            yum=['epel-release', 'daos-server', 'daos-client'],
            repo_url='https://packages.daos.io/v2.0/EL8/packages/x86_64/daos_packages.repo',
            gpg='https://packages.daos.io/RPM-GPG-KEY')
    version('2.0',
            distro='centos7',
            yum=['epel-release', 'daos-server', 'daos-client'],
            repo_url='https://packages.daos.io/v2.0/CentOS7/packages/x86_64/daos_packages.repo',
            gpg='https://packages.daos.io/RPM-GPG-KEY')

    #Source build versions
    version('2.1.104-tb', git="https://github.com/daos-stack/daos.git", branch='v2.1.104-tb', submodules=True)
    version('2.0.3', git="https://github.com/daos-stack/daos.git", branch='v2.0.3', submodules=True)
    version('2.0.2', git="https://github.com/daos-stack/daos.git", branch='v2.0.2', submodules=True)
    version('2.0.1', git="https://github.com/daos-stack/daos.git", branch='v2.0.1', submodules=True)
    version('master-2.0', git="https://github.com/daos-stack/daos.git", branch='release/2.0', submodules=True)

    #depends_on('defusedxml')
    #depends_on('distro')
    #depends_on('junit_xml')
    #depends_on('pyxattr')
    #depends_on('tabulate')
    #depends_on('scons')
    #depends_on('pyyaml')
    #depends_on('pyelftools')

    def build_args(self, spec, prefix):
        args = [
            "PREFIX={}".format(prefix),
            '--config=force',
            '--build-deps=yes'
        ]
        return args
