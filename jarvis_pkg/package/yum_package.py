
from jarvis_cd import *
from jarvis_pkg.package.package import *

class YumPackage(Package):
    @phase('yum')
    def install(self, spec, prefix):
        pass