
from jarvis_pkg import *
import shutil
import os

class Python(Package,CPackage,CppPackage):
    def __init__(self):
        super().__init__()
        #Distro package managers
        self.version('3.6.4', tag='yum', yum='python3')