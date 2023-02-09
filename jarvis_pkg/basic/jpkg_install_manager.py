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
        self.columns = [
            'namespace', 'cls', 'name', 'version', 'ref', 'pkg'
        ]
        self.df = pd.DataFrame(columns=self.columns)
        self.jpkg = JpkgInstallManager.get_instance()
        if os.path.exists(self.jpkg.manifest_path):
            self.df = pd.load_parquet(self.jpkg.manifest_path)

    def register_package(self, pkg):
        self.df += pd.DataFrame(
            [[pkg.namespace, pkg.cls, pkg.name, pkg.version_, 1, pkg]],
            columns=self.columns)

    def reference_package(self, pkg):
        if pkg.is_installed

    def solidify(self, pkg_query):
        """
        Find an existing package which matches this query

        :param pkg_query: the query to match
        :return:
        """
        df = self.df
        if pkg_query.namespace is not None:
            df = df[df.namespace == pkg_query.namespace]
        if pkg_query.cls is not None:
            df = df[df.cls == pkg_query.cls]
        if pkg_query.name is not None:
            df = df[df.name == pkg_query.name]
        if pkg_query.versions is not None:
            for rng in pkg_query.versions:
                df = df[(rng[0] <= df.version) &
                        (df.version <= rng[1])]
        if len(df) == 0:
            return None
        pkgs = list(df['pkg'])
        for pkg in pkgs:
            new_query = pkg.to_query()
            if not new_query.intersect(pkg_query).is_null:
                return pkg
        return None