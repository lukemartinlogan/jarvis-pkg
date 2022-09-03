
from jarvis_pkg import *
import shutil
import os

class Scons(Package,CPackage,CppPackage):
    def define_versions(self):
        self.version('2.0', pip='scons')
