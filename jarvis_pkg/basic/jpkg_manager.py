from jarvis_cd import *
from jarvis_cd.serialize.yaml_file import YAMLFile
from jarvis_cd.util.expand_paths import ExpandPaths

class JpkgManager:
    instance_ = None

    @staticmethod
    def get_instance():
        if JpkgManager.instance_ is None:
            JpkgManager.instance_ = JpkgManager()
        return JpkgManager.instance_

    def __init__(self):
        self.jpkg_root = os.path.dirname(os.path.dirname(pathlib.Path(__file__).parent.resolve()))
        self.manifest_file = os.path.join(self.jpkg_root, 'manifest.yaml')
        if os.path.exists(self.manifest_file):
            self.manifest = YAMLFile(self.manifest_file).Load()
            self.repos = ExpandPaths(self.manifest).Run()
            self.repos = self.manifest['REPOS']
            self.installed = self.manifest['INSTALLED']
        else:
            self.manifest = {'REPOS': {}, 'INSTALLED': {}}
            self.repos = {}
            self.installed = {}
            YAMLFile(self.manifest_file).Save(self.manifest)
        self.installer_root = os.path.join(self.jpkg_root, 'jpkg_installers')
        self.sys_hash = hash(SystemInfoNode().Run())

    def add_repo(self, repo_dir, namespace=None):
        if namespace is None:
            namespace = os.path.basename(repo_dir)
        self.repos[namespace]

    def _package_import(self, pkg_name):
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
