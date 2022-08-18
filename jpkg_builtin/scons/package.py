
from jarvis_pkg import *
import shutil
import os

class Scons(Package,CPackage,CppPackage):
    def __init__(self):
        super().__init__()
        #Distro package managers
        self.version('2.0', pip='scons')