"""

"""

from jarvis_pkg.util.naming import to_camel_case
import os, sys
import pathlib
import pandas as pd
from .jpkg_manager import JpkgManager
import pathlib
import enum
import argparse


class JarvisPkgManifestOp(Enum):
    ADD = "add"
    RM = "rm"
    LIST = "ls"


class JpkgManifestManager:
    instance_ = None

    @staticmethod
    def get_instance():
        if JpkgManifestManager.instance_ is None:
            JpkgManifestManager.instance_ = JpkgManifestManager()
        return JpkgManifestManager.instance_

    def __init__(self):
        self.columns = [
            'namespace', 'cls', 'name', 'repo_path'
        ]
        self.repos = pd.DataFrame(columns=self.columns)
        self.jpkg = JpkgManager.get_instance()
        if os.path.exists(self.jpkg.manifest_path):
            self.repos = pd.load_parquet(self.jpkg.manifest_path)

    def add_repo(self, path):
        namespace = os.path.basename(path)
        pkgs = os.listdir(os.path.join(path, namespace))
        repos = []
        for pkg_name in pkgs:
            pkg = self.import_pkg(namespace, pkg_name)
            repos += [namespace, pkg.cls, pkg_name, path]
        self.repos += pd.DataFrame(repos, columns=self.columns)

    def rm_repo(self, namespace):
        df = self.repos
        self.repos = df[df.namespace != namespace]

    def list(self, namespace=None):
        df = self.repos
        if namespace is not None:
            df = df[df.namespace == namespace]
        nses = list(df['namespace'])
        clses = list(df['cls'])
        names = list(df['name'])
        for ns, cls, pkg_name in zip(nses, clses, names):
            print(f"{ns}.{cls}.{pkg_name}")

    def import_pkg(self, namespace, name, path=None):
        import_str = f"{namespace}.{name}"
        if path is None:
            df = self.repos
            path_df = self.repos[
                (df.namespace == namespace) &
                (df.name == name)
            ]
            path = path_df.iloc[0]
        if path is None:
            return None
        class_name = to_camel_case(name)
        sys.path.insert(0, path)
        module = __import__(f"{import_str}.package", fromlist=[class_name])
        sys.path.pop(0)
        return getattr(module, class_name)

    def load_pkg(self, namespace, name):
        pkg_cls = self.import_pkg(namespace, name)
        if pkg_cls is None:
            raise Exception(f"Could not import invalid package: "
                            f"{namespace}.{name}")
        return pkg_cls()

    def match(self, pkg_query):
        df = self.repos
        if pkg_query.namespace is not None:
            df = df[df.namespace == pkg_query.namespace]
        if pkg_query.cls is not None:
            df = df[df.cls == pkg_query.cls]
        if pkg_query.name is not None:
            df = df[df.name == pkg_query.name]
        if len(df) == 0:
            return []
        pkg_names = list(df['name'])
        pkg_nses = list(df['namespace'])
        matches = []
        for name, namespace in zip(pkg_names, pkg_nses):
            pkg = self.load_pkg(namespace, name)
            solid_pkg = pkg.from_query(pkg_query)
            if solid_pkg is not None:
                matches.append(solid_pkg)
        return matches

    def solidify(self, pkg_query):
        matches = self.match(pkg_query)
        if len(matches):
            return matches[0]
        else:
            return None
