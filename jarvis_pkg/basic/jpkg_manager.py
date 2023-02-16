"""
This file is an index to all important paths in jpkg

1. manifests: the set of all packages
2. installed: the set of all installed packages
"""

import os, sys
import pathlib
import pandas as pd


class JpkgManager:
    instance_ = None

    @staticmethod
    def get_instance():
        if JpkgManager.instance_ is None:
            JpkgManager.instance_ = JpkgManager()
        return JpkgManager.instance_

    def __init__(self):
        self.jpkg_root = pathlib.Path(__file__).parent.parent.parent.resolve()
        self.jpkg_state_dir = os.path.join(self.jpkg_root, '.jpkg_state')
        if not os.path.exists(self.jpkg_state_dir):
            os.mkdir(self.jpkg_state_dir)
        self.manifest_path = os.path.join(self.jpkg_state_dir,
                                          'manifest.pickle')
        self.installed_path = os.path.join(self.jpkg_state_dir,
                                           'installed.pickle')
        self.pkg_dir = os.path.join(self.jpkg_state_dir, 'pkgs')
        if not os.path.exists(self.pkg_dir):
            os.mkdir(self.pkg_dir)
