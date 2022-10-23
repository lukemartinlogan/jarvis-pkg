
from jarvis_cd import *
from jarvis_pkg.package.package import *

class AptPackage(Package):
    @phase('apt')
    def install(self, spec, prefix):
        pass