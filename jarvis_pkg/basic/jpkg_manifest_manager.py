"""

"""

from jarvis_pkg.util.naming import to_camel_case
import os, sys
import pandas as pd
from .jpkg_manager import JpkgManager


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
        a repo has the following structure:
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
                repos.append([repo, pkg.cls, pkg_name, installer, repo_path])
        self.repos = pd.concat([self.repos,
                                pd.DataFrame(repos, columns=self.columns)])

    def rm_repo(self, repo):
        """
        Untrack all packages relating to the repo

        :param repo: the repo to remove
        :return:
        """

        df = self.repos
        self.repos = df[df.repo != repo]

    def list_repo(self, repo=None):
        """
        List all packages corresponding to a repo
        
        :param repo: 
        :return: 
        """
        
        df = self.repos
        if repo is not None:
            df = df[df.repo == repo]
        repos = list(df['repo'])
        clses = list(df['cls'])
        names = list(df['name'])
        installers = list(df['installer'])
        return list(zip(repos, clses, names, installers))

    def print_repo(self, repo=None):
        rows = self.list_repo(repo)
        for repo, cls, pkg_name, installer in rows:
            print(f"{repo}.{cls}.{pkg_name}/{installer}")

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
        class_name = to_camel_case(f"{name}_package")
        sys.path.insert(0, repo_path)
        module = __import__(import_str, fromlist=[class_name])
        sys.path.pop(0)
        return getattr(module, class_name)

    def _load_pkg(self, repo, name, installer, repo_path=None):
        """
        Create an instance of a package.

        :param repo: the repo where the package is located
        :param name: the name of the package
        :param installer: the installer to use for the package
        :param repo_path: the path on the filesystem where the repo resides
        :return:
        """

        pkg_cls = self._import_pkg(repo, name, installer,
                                   repo_path=repo_path)
        if pkg_cls is None:
            raise Exception(f"Could not import invalid package: "
                            f"{repo}.{name}.{installer}")
        if repo_path is None:
            return pkg_cls(True)
        else:
            return pkg_cls(False)

    def load_pkgs(self, repo, name):
        """
        Load all installation methods of a package for a particular repo

        :param repo: The repo to search
        :param name: The name of the package to load
        :return:
        """

        df = self.repos
        df = df[(df.repo == repo) & (df.name == name)]
        installers = list(df.installer)
        pkgs = []
        for installer in installers:
            pkg = self._load_pkg(repo, name, installer)
            pkgs.append(pkg)
        return pkgs

    def match(self, pkg_query):
        """
        The set of all packages which match the query

        :param pkg_query: the query to resolve
        :return:
        """

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

    def get_class(self, name_or_cls):
        """
        Determines whether a string is a package name or class

        :param name_or_cls: the text to check
        :return: True or false
        """
        if name_or_cls in self.repos['cls']:
            return name_or_cls
        else:
            df = self.repos
            df = df[df.name == name_or_cls]
            if len(df) == 0:
                raise Exception(f"Couldn't find package with name: "
                                f"{name_or_cls}")
            return list(df['cls'])[0]

    def solidify(self, pkg_query):
        """
        Any package which matches the query

        :param pkg_query:
        :return:
        """

        matches = self.match(pkg_query)
        if len(matches):
            matches.sort(key=lambda x: x.version_,
                         reverse=True)
            return matches[0]
        else:
            return None

    def save(self):
        self.repos.to_parquet(self.jpkg.manifest_path)
