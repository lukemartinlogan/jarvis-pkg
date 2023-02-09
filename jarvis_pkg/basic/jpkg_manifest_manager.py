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
        """
        Initialize the manifest manager. Will load the manifest dataset
        if it exists. Will create a new one if it does not.
        """
        self.columns = [
            'repo', 'cls', 'name', 'installer', 'repo_path'
        ]
        self.repos = pd.DataFrame(columns=self.columns)
        self.jpkg = JpkgManager.get_instance()
        if os.path.exists(self.jpkg.manifest_path):
            self.repos = pd.load_parquet(self.jpkg.manifest_path)

    def add_repo(self, repo_path):
        """
        Add the repo rooted at path.
        A repo has the following structure:
            /path/to/repo_name/repo_name/pkg_name/installer_name/package.py

        :param path: root of the repo
        :return:
        """
        repo = os.path.basename(repo_path)
        pkg_names = os.listdir(os.path.join(repo_path, repo))
        repos = []
        for pkg_name in pkg_names:
            pkg_dir = os.path.join(repo_path, repo, pkg_name)
            installers = os.listdir(pkg_dir)
            for installer in installers:
                pkg = self._load_pkg(repo, pkg_name, installer,
                                     repo_path=repo_path)
                repos += [repo, pkg.cls, pkg_name, installer, repo_path]
        self.repos += pd.DataFrame(repos, columns=self.columns)

    def rm_repo(self, repo):
        df = self.repos
        self.repos = df[df.repo != repo]

    def list(self, repo=None):
        df = self.repos
        if repo is not None:
            df = df[df.repo == repo]
        nses = list(df['repo'])
        clses = list(df['cls'])
        names = list(df['name'])
        for ns, cls, pkg_name in zip(nses, clses, names):
            print(f"{ns}.{cls}.{pkg_name}")

    def _import_pkg(self, repo, name, installer, repo_path=None):
        """
        Import the package module. If the package is registered in the
        manifest manager, path is optional.

        :param repo: repo (repo) of the package
        :param name: name of the package
        :param installer: installer variant of the package
        :param path:
        :return:
        """
        import_str = f"{repo}.{name}.{installer}.package"
        if repo_path is None:
            df = self.repos
            path_df = self.repos[
                (df.repo == repo) &
                (df.name == name) &
                (df.installer == installer)
            ]
            repo_path = path_df.iloc[0]
        if repo_path is None:
            return None
        class_name = to_camel_case(name)
        sys.path.insert(0, repo_path)
        module = __import__(import_str, fromlist=[class_name])
        sys.path.pop(0)
        return getattr(module, class_name)

    def _load_pkg(self, repo, name, installer, repo_path=None):
        pkg_cls = self._import_pkg(repo, name, installer,
                                   repo_path=repo_path)
        if pkg_cls is None:
            raise Exception(f"Could not import invalid package: "
                            f"{repo}.{name}.{installer}")
        return pkg_cls()

    def load_pkgs(self, repo, name):
        df = self.repos
        df = df[(df.repo == repo) & (df.name == name)]
        installers = list(df.installer)
        pkgs = []
        for installer in installers:
            pkg = self._load_pkg(repo, name, installer)
            pkgs.append(pkg)
        return pkgs

    def match(self, pkg_query):
        df = self.repos
        if pkg_query.repo is not None:
            df = df[df.repo == pkg_query.repo]
        if pkg_query.cls is not None:
            df = df[df.cls == pkg_query.cls]
        if pkg_query.name is not None:
            df = df[df.name == pkg_query.name]
        if len(df) == 0:
            return []
        pkg_names = list(df['name'])
        pkg_nses = list(df['repo'])
        installers = list(df['installer'])
        matches = []
        for name, repo, installer in zip(pkg_names, pkg_nses, installers):
            pkg = self._load_pkg(repo, name, installer)
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

    def save(self):
        self.repos.to_parquet(self.jpkg.manifest_path)
