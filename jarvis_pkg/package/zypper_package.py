
from jarvis_cd import *
from jarvis_pkg.package.package import *

class ZypperPackage(Package):
    @phase('zypper')
    def install(self, spec, prefix):
        pass