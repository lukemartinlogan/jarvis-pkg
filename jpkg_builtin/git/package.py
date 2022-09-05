
from jarvis_pkg import *
import shutil
import os

class Git(Package,CPackage,CppPackage):
    def define_versions(self):
        super().define_versions()