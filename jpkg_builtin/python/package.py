
from jarvis_pkg import *
import shutil
import os

class Python(Package,CPackage,CppPackage):
    def define_versions(self):
        self.version('3.6.4', tag='yum', yum='python3')