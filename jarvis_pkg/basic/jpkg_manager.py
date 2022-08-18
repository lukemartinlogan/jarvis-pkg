import os, inspect, pathlib
from jarvis_cd import *

class JpkgManager:
    instance_ = None

    @staticmethod
    def GetInstance():
        if JpkgManager.instance_ is None:
            JpkgManager.instance_ = JpkgManager()
        return JpkgManager.instance_

    def __init__(self):
        self.jpkg_root = os.path.dirname(os.path.dirname(pathlib.Path(__file__).parent.resolve()))
        self.repos = YAMLFile(os.path.join(self.jpkg_root, 'repos.yaml')).Load()
        ExpandPaths(self.repos)
        self.installer_root = os.path.join(self.jpkg_root, 'jpkg_installers')

    def _PackagePathTuple(self, package_name):
        for namespace in os.listdir(self.repo_root):
            ns_pkgs = os.path.join(self.repo_root, namespace)
            for ns_pkg_name in os.listdir(ns_pkgs):
                if package_name == ns_pkg_name:
                    return (self.jpkg_root, 'jpkg_repos', namespace, ns_pkg_name)
        return None

    def _PackageImport(self, pkg_name):
        path_tuple = self._PackagePathTuple(pkg_name)
        if path_tuple is None:
            return None
        import_str = '.'.join(path_tuple[1:])
        class_name = ToCamelCase(pkg_name)
        return __import__(f"{import_str}.package", fromlist=[class_name])
