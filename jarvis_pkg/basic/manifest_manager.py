
from jarvis_cd import *
from jarvis_cd.serialize.pickle import PickleFile
from jarvis_cd.util.expand_paths import ExpandPaths
from jarvis_pkg.basic.exception import Error,ErrorCode
import pathlib

from .jpkg_manager import JpkgManager

class ManifestManager:
    """
    The manifest file contains a table with the following structure:
    REPO_NAME:
        REPO_PATH: ...
        ENTRIES: [names]
    """

    instance_ = None

    @staticmethod
    def get_instance():
        if ManifestManager.instance_ is None:
            ManifestManager.instance_ = ManifestManager()
        return ManifestManager.instance_

    def __init__(self):
        self.jpkg = JpkgManager.get_instance()
        self.manifest = PickleFile(self.jpkg.manifest_path).Load()
        self.pkg_by_class = {}
        for namespace,record in self.manifest.items():
            self.pkg_by_class


    def __delete__(self):
        PickleFile(self.manifest).Save(self.jpkg.manifest_path)

    def add_repo(self, repo_path, namespace=None):
        if namespace is None:
            namespace = os.path.basename(repo_path)
        if namespace in self.manifest:
            print(f"Error: {namespace} already exists")
            exit(1)
        record = {
            'path': repo_path,
            'entries': set(),
            'enabled': True
        }
        self.manifest[namespace] = record
        self.update_repo(namespace)

    def disable_repo(self, namespace):
        self.manifest[namespace]['enabled'] = False

    def update_repo(self, namespace):
        record = self.manifest[namespace]
        root_path = os.path.join(record['path'], namespace)
        for pkg_filename in os.listdir(root_path):
            pkg_path = pathlib.Path(os.path.join(root_path, str(pkg_filename)))
            if pkg_path.is_file() and pkg_path.suffix == 'py':
                record['entries'].add(pkg_path.name)

    def rm_repo(self, namespace):
        del self.manifest[namespace]

    def query_pkgs(self, pkg_name, namespace=None):
        return

    def open_pkg(self, namespace, name):
        record = self.manifest[namespace]
        sys.path.append(record['path'])
        pkg_class = __import__(f"{namespace}.")
        sys.path.pop()