
from jarvis_pkg import *
import shutil
import os

class Daos(SConsPackage,CPackage,CppPackage,YumPackage):
    def define_versions(self):
        super().define_versions()
        #Distro package managers
        self.version('2.0',
                distro='centos8',
                pkg_list=['epel-release', 'daos-server', 'daos-client'],
                repo_url='https://packages.daos.io/v2.0/EL8/packages/x86_64/daos_packages.repo',
                gpg='https://packages.daos.io/RPM-GPG-KEY',
                install='yum')
        self.version('2.0',
                distro='centos7',
                pkg_list=['epel-release', 'daos-server', 'daos-client'],
                repo_url='https://packages.daos.io/v2.0/CentOS7/packages/x86_64/daos_packages.repo',
                gpg='https://packages.daos.io/RPM-GPG-KEY',
                install='yum')

        #Source build versions
        self.version('3.0.0', tag='master', git="https://github.com/daos-stack/daos.git", branch='release/2.0', submodules=True)
        self.version('2.1.104', tag='2.1.104-tb', git="https://github.com/daos-stack/daos.git", branch='v2.1.104-tb', submodules=True)
        self.version('2.0.3', git="https://github.com/daos-stack/daos.git", branch='v2.0.3', submodules=True)
        self.version('2.0.2', git="https://github.com/daos-stack/daos.git", branch='v2.0.2', submodules=True)
        self.version('2.0.1', git="https://github.com/daos-stack/daos.git", branch='v2.0.1', submodules=True)

        #self.depends_on('defusedxml')
        #self.depends_on('distro')
        #self.depends_on('junit_xml')
        #self.depends_on('pyxattr')
        #self.depends_on('tabulate')
        #self.depends_on('scons')
        #self.depends_on('pyyaml')
        #self.depends_on('pyelftools')

    @conf('scons')
    def build_args(self, spec, prefix):
        args = [
            "PREFIX={}".format(prefix),
            '--config=force',
            '--build-deps=yes'
        ]
        return args
