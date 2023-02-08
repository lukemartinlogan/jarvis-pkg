"""
This file is an index to all important paths in jpkg

1. manifests: the set of all packages
2. installed: the set of all installed packages
3. setup.log: records the installation process to avoid repetition in
case of failure
"""

from jarvis_cd import *
from jarvis_cd.serialize.yaml_file import YAMLFile
import os, sys
import pathlib
import pandas as pd


class JpkgInstallManager:
    instance_ = None

    @staticmethod
    def get_instance():
        if JpkgInstallManager.instance_ is None:
            JpkgInstallManager.instance_ = JpkgInstallManager()
        return JpkgInstallManager.instance_

    def __init__(self):
        columns = [
            'namespace', 'cls', 'name', 'version', 'ref', 'pkg'
        ]
        self.df = pd.DataFrame(columns=columns)
        self.jpkg = JpkgInstallManager.get_instance()
        if os.path.exists(self.jpkg.manifest_path):
            self.df = pd.load_parquet(self.jpkg.manifest_path)
