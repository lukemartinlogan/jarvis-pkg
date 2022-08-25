from jarvis_cd import *
from jarvis_pkg import *

class Beegfs(Package):
    #Distro package managers
    def __init__(self):
        super().__init__()
        self.version('7.3.1',
                distro='centos8',
                yum=['epel-release',
                     'beegfs-mgmtd', 'beegfs-meta', 'beegfs-storage',
                     'beegfs-client', 'libbeegfs-ib', 'beegfs-mon', 'beegfs-utils', 'beegfs-common'],
                repo_url='https://www.beegfs.io/release/beegfs_7.3.1/dists/beegfs-rhel8.repo',
                gpg='https://www.beegfs.io/release/beegfs_7.3.1/gpg/GPG-KEY-beegfs')
