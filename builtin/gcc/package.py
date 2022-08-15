from jarvis_pkg import *
import shutil
import os

class Gcc(Package):
    #Distro package managers
    version('2.0',
            distro=['debian', 'ubuntu', 'linux-mint'],
            apt=['gcc', 'g++', 'gfortran', 'build-essential'])
    version('2.0',
            distro=['centos7', 'centos8'],
            yum=['gcc', 'g++', 'gfortran'])