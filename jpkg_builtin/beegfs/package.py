from jarvis_cd import *
from jarvis_pkg import *


class Beegfs(Package,YumPackage):
    def define_versions(self):
        super().define_versions()
        self.version('7.3.1',
                pkg_list=['epel-release',
                     'beegfs-mgmtd', 'beegfs-meta', 'beegfs-storage',
                     'beegfs-client', 'libbeegfs-ib', 'beegfs-mon', 'beegfs-utils', 'beegfs-common'],
                repo_url='https://www.beegfs.io/release/beegfs_7.3.1/dists/beegfs-rhel8.repo',
                gpg='https://www.beegfs.io/release/beegfs_7.3.1/gpg/GPG-KEY-beegfs',
                install='yum')

    def define_deps(self):
        pass

    def define_conflicts(self):
        pass

