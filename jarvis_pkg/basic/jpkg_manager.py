"""
This file is an index to all important paths in jpkg

1. manifests: the set of all packages
2. installed: the set of all installed packages
3. setup.log: records the installation process to avoid repetition in
case of failure
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
        os.mkdir(self.jpkg_state_dir)
        self.manifest_path = os.path.join(self.jpkg_state_dir,
                                          'manifest.parquet')
        self.installed_path = os.path.join(self.jpkg_state_dir,
                                           'installed.parquet')

    def _create_installed(self, path):
        if not os.path.exists(self.installed_path):
            columns = [
                'name', 'cls', 'version', 'ref', 'pkg'
            ]
            df = pd.DataFrame(columns=columns)
            df.to_parquet()

    def _create_manifests(self, path):
        if not os.path.exists(self.manifest_path):
            columns = [
                'name', 'cls', 'pkg'
            ]
            df = pd.DataFrame(columns=columns)
