import os, inspect, pathlib, sys
from jarvis_cd import *
from jarvis_cd.serialize.yaml_file import YAMLFile
from jarvis_cd.util.expand_paths import ExpandPaths

class JpkgManager:
    instance_ = None

    @staticmethod
    def GetInstance():
        if JpkgManager.instance_ is None:
            JpkgManager.instance_ = JpkgManager()
        return JpkgManager.instance_

    def __init__(self):
        self.jpkg_root = os.path.dirname(os.path.dirname(pathlib.Path(__file__).parent.resolve()))
        self.repos = YAMLFile(os.path.join(self.jpkg_root, 'repos.yaml')).Load()['REPOS']
        self.repos = ExpandPaths(self.repos).Run()
        self.installer_root = os.path.join(self.jpkg_root, 'jpkg_installers')

    def _PackageImport(self, pkg_name):
        path = None
        import_str = None
        pkg_name = ToSnakeCase(pkg_name)
        for ns in self.repos:
            if pkg_name in ns['pkgs']:
                ns_id = os.path.basename(ns['path'])
                import_str = f"{ns_id}.{pkg_name}"
                path = os.path.join(ns['path'], pkg_name)
        if path is None:
            return None
        class_name = ToCamelCase(pkg_name)
        sys.path.insert(0,path)
        module = __import__(f"{import_str}.package", fromlist=[class_name])
        sys.path.pop(0)
        return getattr(module, class_name)
