"""

"""

from jarvis_cd import *
from jarvis_cd.serialize.yaml_file import YAMLFile
import os, sys
import pathlib
import pandas as pd
from .jpkg_manager import JpkgManager
import pathlib


class JpkgManifestManager:
    instance_ = None

    @staticmethod
    def get_instance():
        if JpkgManifestManager.instance_ is None:
            JpkgManifestManager.instance_ = JpkgManifestManager()
        return JpkgManifestManager.instance_

    def __init__(self):
        columns = [
            'namespace', 'cls', 'name', 'repo_path'
        ]
        self.df = pd.DataFrame(columns=columns)
        self.jpkg = JpkgManager.get_instance()
        if os.path.exists(self.jpkg.manifest_path):
            self.df = pd.load_parquet(self.jpkg.manifest_path)

    def add_repo(self, path):
        namespace = os.path.basename(path)
        repo_path = os.path.join(path, namespace)
        pkgs = os.listdir(repo_path)
        pkg = self.import_pkg()

    def rm_repo(self, path):
        pass

    def list(self, namespace=None):
        df = self.df
        if namespace is not None:
            df = df[df.namespace == namespace]
        pkgs = list(df['namespace'])
        print("REPOS:")
        for pkg in pkgs:
            print(pkg)

    def import_pkg(self, path):
        pass